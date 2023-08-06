from django.urls import path
from enhanced_curation import views

urlpatterns = [
    path("enhanced_curation/ranked_proposals", views.ranked_proposals),
    path("enhanced_curation/csv", views.get_csv),
]
