from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Sum, Max
from django.db.models.functions import Coalesce

from .models import Country, Location, Volcano, Eruption, Impact
from .forms import VolcanoForm


# =========================
# Главная страница (Jinja2)
# =========================
def index(request):
    totals = {
        "countries": Country.objects.count(),
        "locations": Location.objects.count(),
        "volcanoes": Volcano.objects.count(),
        "eruptions": Eruption.objects.count(),
        "impacts": Impact.objects.count(),
    }

    # --- Таблицы "как отношения БД" ---
    countries_qs = Country.objects.order_by("name")
    country_rows = [[c.id, c.name] for c in countries_qs]

    locations_qs = Location.objects.select_related("country").order_by("country__name", "name")
    location_rows = [[l.id, l.country.name, l.name] for l in locations_qs]

    volcanoes_qs = Volcano.objects.select_related("location__country").order_by(
        "location__country__name", "location__name", "name"
    )
    volcano_rows = [
        [
            v.id,
            v.location.country.name,
            v.location.name,
            v.name,
            v.latitude,
            v.longitude,
            v.elevation_m,
            v.volcano_type,
            v.status,
        ]
        for v in volcanoes_qs
    ]

    eruptions_qs = (
        Eruption.objects
        .select_related("volcano__location__country")
        .order_by("-year", "-month", "-day")[:50]
    )
    eruption_rows = [
        [
            e.id,
            e.volcano.location.country.name,
            e.volcano.location.name,
            e.volcano.name,
            e.year, e.month, e.day,
            "TSU" if e.tsu_flag else "",
            "EQ" if e.eq_flag else "",
            e.time_code,
            e.vei,
            e.agent,
        ]
        for e in eruptions_qs
    ]

    impacts_qs = (
        Impact.objects
        .select_related("eruption__volcano__location__country")
        .order_by("-eruption__year", "-eruption__month", "-eruption__day")[:50]
    )
    impact_rows = [
        [
            im.id,
            im.eruption.volcano.location.country.name,
            im.eruption.volcano.name,
            im.eruption.year, im.eruption.month, im.eruption.day,
            im.total_deaths,
            im.total_injuries,
            im.total_missing,
            im.total_damage_musd,
            im.total_houses_destroyed,
        ]
        for im in impacts_qs
    ]

    # --- Статистика ---
    top_countries_qs = (
        Country.objects
        .annotate(
            eruptions_count=Count("locations__volcanoes__eruptions", distinct=True),
            volcanoes_count=Count("locations__volcanoes", distinct=True),
            max_vei=Max("locations__volcanoes__eruptions__vei"),
            total_deaths_sum=Coalesce(Sum("locations__volcanoes__eruptions__impact__total_deaths"), 0),
        )
        .order_by("-eruptions_count", "name")[:15]
    )
    top_country_rows = [
        [c.name, c.volcanoes_count, c.eruptions_count, c.max_vei, c.total_deaths_sum]
        for c in top_countries_qs
    ]

    vei_stats_qs = (
        Eruption.objects
        .values("vei")
        .annotate(cnt=Count("id"))
        .order_by("vei")
    )
    vei_rows = [[("Unknown" if x["vei"] is None else x["vei"]), x["cnt"]] for x in vei_stats_qs]

    top_volcanoes_qs = (
        Volcano.objects
        .select_related("location__country")
        .annotate(eruptions_count=Count("eruptions"), max_vei=Max("eruptions__vei"))
        .order_by("-eruptions_count")[:15]
    )
    top_volcano_rows = [
        [v.location.country.name, v.name, v.eruptions_count, v.max_vei]
        for v in top_volcanoes_qs
    ]

    tsu_count = Eruption.objects.filter(tsu_flag=True).count()
    eq_count = Eruption.objects.filter(eq_flag=True).count()

    return render(
        request,
        "index.html",
        {
            "totals": totals,
            "country_rows": country_rows,
            "location_rows": location_rows,
            "volcano_rows": volcano_rows,
            "eruption_rows": eruption_rows,
            "impact_rows": impact_rows,
            "top_country_rows": top_country_rows,
            "vei_rows": vei_rows,
            "top_volcano_rows": top_volcano_rows,
            "tsu_count": tsu_count,
            "eq_count": eq_count,
        },
        using="jinja2",
    )


# ==================================
# CRUD для Volcano (Django Forms)
# ==================================
class VolcanoListView(ListView):
    model = Volcano
    template_name = "volcano/volcano_list.html"
    context_object_name = "volcanoes"

    def get_queryset(self):
        return (
            Volcano.objects
            .select_related("location__country")
            .order_by("location__country__name", "location__name", "name")
        )


class VolcanoCreateView(CreateView):
    model = Volcano
    form_class = VolcanoForm
    template_name = "volcano/volcano_form.html"
    success_url = reverse_lazy("volcano_list")


class VolcanoUpdateView(UpdateView):
    model = Volcano
    form_class = VolcanoForm
    template_name = "volcano/volcano_form.html"
    success_url = reverse_lazy("volcano_list")


class VolcanoDeleteView(DeleteView):
    model = Volcano
    template_name = "volcano/volcano_confirm_delete.html"
    success_url = reverse_lazy("volcano_list")