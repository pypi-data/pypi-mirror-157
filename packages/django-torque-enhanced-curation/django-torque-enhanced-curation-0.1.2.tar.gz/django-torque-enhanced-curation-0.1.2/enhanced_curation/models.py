from django.db import models

from django.contrib.postgres.fields import ArrayField

from torque import models as torque_models
from math import floor


class CollectionCache(models.Model):
    collection = models.ForeignKey(torque_models.Collection, on_delete=models.CASCADE)
    last_run = models.DateTimeField(null=True)

    def rebuild_cache(self):
        DocumentCache.objects.filter(collection_cache=self).delete()
        cached_documents = []

        def document_score(document):
            try:
                return float(document.values.get(field__name="Panel Score").to_python()["Normalized"])
            except ValueError:
                return 0
            except torque_models.Value.DoesNotExist:
                pass

            try:
                return float(document.values.get(field__name="Peer Score").to_python()["Normalized"])
            except ValueError:
                return 0
            except torque_models.Value.DoesNotExist:
                pass

            return 0

        scores = [document_score(d) for d in self.collection.documents.all()]
        scores.sort()
        score_cutoff_25percent = scores[floor(len(scores) * .75)]
        score_cutoff_1percent = scores[floor(len(scores) * .99)]

        for document in self.collection.documents.all():
            has_achievement_level = False
            try:
                has_achievement_level = bool(document.values.get(field__name="Achievement Level").to_python())
            except torque_models.Value.DoesNotExist:
                pass
            try:
                cached_documents.append(
                    DocumentCache(
                        document=document,
                        collection_cache=self,
                        org_size=DocumentCache.categorize_org_size(document),
                        org_budget=DocumentCache.categorize_org_budget(document),
                        subject=DocumentCache.categorize_subject(document),
                        priority_populations=DocumentCache.categorize_priority_populations(document),
                        work_locations=DocumentCache.categorize_work_locations(document),
                        org_name=document.values.get(
                            field__name="Organization Name"
                        ).to_python(),
                        top25percent=(score_cutoff_25percent != 0 and document_score(document) > score_cutoff_25percent),
                        top1percent=(score_cutoff_1percent != 0 and document_score(document) > score_cutoff_1percent),
                        has_achievement_level=has_achievement_level,
                    )
                )
            except torque_models.Value.DoesNotExist:
                # Values here are required! (like org name)
                pass

        DocumentCache.objects.bulk_create(cached_documents)


class DocumentCache(models.Model):
    document = models.ForeignKey(torque_models.Document, on_delete=models.CASCADE)
    collection_cache = models.ForeignKey(
        CollectionCache, on_delete=models.CASCADE, related_name="documents"
    )
    org_size = models.TextField(null=True)
    org_budget = models.TextField(null=True)
    org_name = models.TextField()
    subject = models.TextField(null=True)
    priority_populations = ArrayField(models.TextField(), default=list)
    work_locations = ArrayField(models.TextField(), default=list)
    top25percent = models.BooleanField(default=False)
    top1percent = models.BooleanField(default=False)
    has_achievement_level = models.BooleanField(default=False)

    def categorize_subject(document):
        try:
            return document.values.get(field__name="Primary Subject Area").to_python().get("Level 1", None)
        except torque_models.Value.DoesNotExist:
            return None

    def categorize_priority_populations(document):
        try:
            return document.values.get(field__name="Priority Populations").to_python()
        except torque_models.Value.DoesNotExist:
            return []

    def categorize_work_locations(document):
        try:
            work_locations = []
            for location in (
                    document.values.get(field__name="Future Work Locations").to_python() +
                    document.values.get(field__name="Current Work Locations").to_python()
                ):
                region = location.get("Region", None)
                country = location.get("Country", None)
                subregion = location.get("Subregion", None)

                if region in ["Oceania", "Asia", "Europe", "Africa"] and region not in work_locations:
                    work_locations.append(region)

                if subregion in ["North America", "Caribbean", "Central America"] and "North America" not in work_locations:
                    work_locations.append("North America")

                if subregion == "South America" and subregion not in work_locations:
                    work_locations.append(subregion)
                    
                if country == "United States" and country not in work_locations:
                    work_locations.append(country)

            return work_locations
        except torque_models.Value.DoesNotExist:
            return []

    def categorize_org_size(document):
        categories = {
            "Fewer than 10 Full-time Employees": "small",
            "10 to 25 Full-time Employees": "small",
            "26 to 50 Full-time Employees": "small",
            "51 to 100 Full-time Employees": "medium",
            "101 to 300 Full-time Employees": "medium",
            "301 to 500 Full-time Employees": "medium",
            "501 to 1,000 Full-time Employees": "large",
            "1,000+ Full-time Employees": "large",
        }

        try:
            return categories.get(
                document.values.get(field__name="Number of Employees").to_python(), None
            )
        except torque_models.Value.DoesNotExist:
            return None

    def categorize_org_budget(document):
        categories = {
            "Less than $1 Million": "small",
            "$1 to $5 Million": "small",
            "$5 to $10 Million": "small",
            "$10 to $25 Million": "small",
            "$25 to $50 Million": "medium",
            "$50 to $100 Million": "medium",
            "$100 to $500 Million": "medium",
            "$100 to $250 Million": "medium",
            "$250 to $500 Million": "medium",
            "$500 to $750 Million": "large",
            "$500 Million to $1 Billion": "large",
            "$750 Million to $1 Billion": "large",
            "$1 Billion +": "large",
        }
        try:
            return categories.get(
                document.values.get(field__name="Annual Operating Budget").to_python(),
                None,
            )
        except torque_models.Value.DoesNotExist:
            return None
        document.values.get(field__name="")

    def score(self, selection_groups):
        score = 0
        for selection_group in selection_groups:
            if selection_group["name"] == "Subject":
                for selection in selection_group["selections"]:
                    if selection == self.subject:
                        score += int(selection_group["level"])
            elif selection_group["name"] == "Populations":
                for selection in selection_group["selections"]:
                    if selection in self.priority_populations:
                        score += int(selection_group["level"])
            elif selection_group["name"] == "Work Location":
                for selection in selection_group["selections"]:
                    if selection in self.work_locations:
                        score += int(selection_group["level"])

        self.score = score

    def __eq__(self, other):
        return self.score == other.score and self.org_name == other.org_name

    def __ne__(self, other):
        return self.score != other.score or self.org_name != other.org_name

    def __gt__(self, other):
        if self.score == other.score:
            return self.org_name > other.org_name

        # This is inverted because we want higher scores to come first, but also ealier org names to come first!
        return self.score < other.score
