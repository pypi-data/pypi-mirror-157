import time
from multiprocessing import Process
from django.db import transaction
from django import db
import sys
from django.contrib.postgres.search import SearchVector
import traceback
from django.utils import timezone


class RebuildCollectionCache:
    def run(self):
        from torque import models as torque_models
        from enhanced_curation import models

        for collection in torque_models.Collection.objects.all():
            (cache, created) = models.CollectionCache.objects.get_or_create(
                collection=collection
            )

            if not cache.last_run or cache.last_run < collection.last_updated:
                # We do this, so that if it errors, we aren't looping forever
                cache.last_run = timezone.now()
                cache.save()

                print(
                    "Rebuilding Enhanced Curation Cache for colletion "
                    + collection.name
                    + "...",
                    end="",
                )
                cache.rebuild_cache()
                print("Rebuilt")


class CacheRebuilder(Process):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        db.connections.close_all()

        while True:
            try:
                RebuildCollectionCache().run()
            except:
                print("Rebuilder failed a loop due to %s" % sys.exc_info()[0])
                print(traceback.format_exc())

            time.sleep(5)
