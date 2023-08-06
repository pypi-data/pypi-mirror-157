from django.http import HttpResponse, JsonResponse, FileResponse
from torque import models as torque_models
from django.db.models import Q
from django.conf import settings
from enhanced_curation import models
import random
import json
import csv


def get_proposals(request):
    group = request.GET["group"]
    q = request.GET["q"]
    global_wiki_key = request.GET["wiki_key"]
    global_collection_name = request.GET["collection_name"]
    wiki_keys = request.GET["wiki_keys"].split(",")
    collection_names = request.GET["collection_names"].split(",")
    org_sizes = request.GET["org_sizes"].split(",") if request.GET["org_sizes"] else []
    selections = json.loads(request.GET["selections"])
    org_budgets = (
        request.GET["org_budgets"].split(",") if request.GET["org_budgets"] else []
    )
    proposal_types = (
        request.GET["proposal_types"].split(",") if request.GET["proposal_types"] else []
    )
    global_config = torque_models.WikiConfig.objects.get(
        collection__name=global_collection_name,
        wiki__wiki_key=global_wiki_key,
        group=group,
    )
    configs = torque_models.WikiConfig.objects.filter(
        collection__name__in=collection_names, wiki__wiki_key__in=wiki_keys, group=group
    ).all()

    filters = [
        Q(collection_cache__collection__name__in=collection_names),
    ]
    if "All Proposals" not in proposal_types:
        filters.append(Q(top25percent=True)),

    if len(org_sizes) > 0:
        filters.append(Q(org_size__in=org_sizes))

    if len(org_budgets) > 0:
        filters.append(Q(org_budget__in=org_budgets))

    proposal_type_q = Q()

    if "Top Proposals" in proposal_types and "All Proposals" not in proposal_types:
        proposal_type_q = proposal_type_q | Q(top1percent=True)
    if "BSN" in proposal_types and "All Proposals" not in proposal_types:
        proposal_type_q = proposal_type_q | Q(has_achievement_level=True)
    if "Non-awardees" in proposal_types and "All Proposals" not in proposal_types:
        proposal_type_q = proposal_type_q | Q(has_achievement_level=False)
    filters.append(proposal_type_q)

    if q:
        search_results = (
            torque_models.SearchCacheDocument.objects.filter(
                collection__name__in=collection_names,
                wiki__wiki_key__in=configs.values_list("wiki__wiki_key", flat=True),
                group__in=configs.values_list("group", flat=True),
                wiki_config__in=configs,
                data_vector=q,
            )
            .select_related("document")
        )

        searched_documents = [ result.document for result in search_results ]

        filters.append(Q(document__in=searched_documents))

    proposals = list(models.DocumentCache.objects.filter(*filters))
    for proposal in proposals:
        proposal.score(selections)

    proposals.sort()

    return proposals


def ranked_proposals(request):
    proposals = get_proposals(request)
    wiki_keys = request.GET["wiki_keys"].split(",")
    group = request.GET["group"]

    collection_names = request.GET["collection_names"].split(",")
    configs = torque_models.WikiConfig.objects.filter(
        collection__name__in=collection_names, wiki__wiki_key__in=wiki_keys, group=group
    ).all()

    resp = []
    for proposal in proposals[0:20]:
        for config in configs:
            if config.collection == proposal.document.collection:
                resp.append(proposal.document.to_dict(config))

    return JsonResponse({"result": resp})

def get_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="enhanced-curation.csv"'
        },
    )

    field_names = [
        "Competition Name",
        "Organization Name",
        "Organization Location",
        "Project Title",
        "Project Description",
        "Executive Summary",
        "Solution Overview",
        "Priority Populations",
        "Current Work Locations",
        "Future Work Locations",
        "Primary Subject Area",
        "Key Words and Phrases",
        "Sustainable Development Goals",
        "Annual Operating Budget",
        "Number of Employees",
    ]

    proposals = get_proposals(request)
    writer = csv.writer(response)

    columns = []
    for field_name in field_names:
        if field_name in getattr(settings, "TORQUE_CSV_PROCESSORS", {}):
            columns.extend(
                settings.TORQUE_CSV_PROCESSORS[field_name].field_names(field_name)
            )
        else:
            columns.append(field_name)

    writer.writerow(columns)

    for proposal in proposals:
        row = []
        values_by_field = {
            v.field.name: v
            for v in proposal.document.values.prefetch_related("field")
        }
        for field_name in field_names:
            if field_name in values_by_field and field_name in getattr(
                settings, "TORQUE_CSV_PROCESSORS", {}
            ):
                row.extend(
                    settings.TORQUE_CSV_PROCESSORS[field_name].process_value(
                        values_by_field[field_name].to_python()
                    )
                )
            elif field_name in getattr(
                settings, "TORQUE_CSV_PROCESSORS", {}
            ):
                row.extend(
                    [""] * len(settings.TORQUE_CSV_PROCESSORS[field_name].field_names(field_name))
                )
            elif field_name in values_by_field:
                row.append(values_by_field[field_name].to_python())
            else:
                row.append("")
        writer.writerow(row)

    return response
