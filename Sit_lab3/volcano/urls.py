from django.urls import path
from .views import (
    index,
    VolcanoListView,
    VolcanoCreateView,
    VolcanoUpdateView,
    VolcanoDeleteView,
)

urlpatterns = [
    path("", index, name="index"),

    # CRUD (Django Forms) для Volcano
    path("volcanoes/", VolcanoListView.as_view(), name="volcano_list"),
    path("volcanoes/add/", VolcanoCreateView.as_view(), name="volcano_add"),
    path("volcanoes/<int:pk>/edit/", VolcanoUpdateView.as_view(), name="volcano_edit"),
    path("volcanoes/<int:pk>/delete/", VolcanoDeleteView.as_view(), name="volcano_delete"),
]