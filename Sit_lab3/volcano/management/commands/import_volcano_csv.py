from django.core.management.base import BaseCommand
from django.db import transaction
from volcano.models import Country, Location, Volcano, Eruption, Impact
import pandas as pd
import math


def is_nan(x):
    return isinstance(x, float) and math.isnan(x)

def s(x):
    if x is None or is_nan(x):
        return None
    v = str(x).strip()
    return v if v != "" else None

def i(x):
    if x is None or is_nan(x) or str(x).strip() == "":
        return None
    try:
        return int(float(x))
    except:
        return None

def f(x):
    if x is None or is_nan(x) or str(x).strip() == "":
        return None
    try:
        return float(x)
    except:
        return None

def flag(x, expected):
    return (s(x) == expected)


class Command(BaseCommand):
    help = "Import volcano eruptions CSV into PostgreSQL"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, required=True)
        parser.add_argument("--reset", action="store_true")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["path"]
        df = pd.read_csv(path, low_memory=False)

        if opts["reset"]:
            Impact.objects.all().delete()
            Eruption.objects.all().delete()
            Volcano.objects.all().delete()
            Location.objects.all().delete()
            Country.objects.all().delete()

        # Кэши для ускорения (чтобы не делать get_or_create миллион раз)
        countries = {}
        locations = {}
        volcanoes = {}

        created = 0

        for _, row in df.iterrows():
            country_name = s(row.get("Country"))
            location_name = s(row.get("Location")) or "Unknown"
            volcano_name = s(row.get("Name"))

            if not country_name or not volcano_name:
                continue

            country = countries.get(country_name)
            if country is None:
                country, _ = Country.objects.get_or_create(name=country_name)
                countries[country_name] = country

            loc_key = (country.id, location_name)
            location = locations.get(loc_key)
            if location is None:
                location, _ = Location.objects.get_or_create(country=country, name=location_name)
                locations[loc_key] = location

            vol_key = (location.id, volcano_name)
            volcano = volcanoes.get(vol_key)
            if volcano is None:
                volcano, _ = Volcano.objects.get_or_create(
                    location=location,
                    name=volcano_name,
                    defaults={
                        "latitude": f(row.get("Latitude")),
                        "longitude": f(row.get("Longitude")),
                        "elevation_m": i(row.get("Elevation")),
                        "volcano_type": s(row.get("Type")),
                        "status": s(row.get("Status")),
                    }
                )
                volcanoes[vol_key] = volcano

            eruption = Eruption.objects.create(
                volcano=volcano,
                year=i(row.get("Year")),
                month=i(row.get("Month")),
                day=i(row.get("Day")),
                tsu_flag=flag(row.get("TSU"), "TSU"),
                eq_flag=flag(row.get("EQ"), "EQ"),
                time_code=s(row.get("Time")),
                vei=i(row.get("VEI")),
                agent=s(row.get("Agent")),
            )

            Impact.objects.create(
                eruption=eruption,
                deaths=i(row.get("DEATHS")),
                deaths_description=s(row.get("DEATHS_DESCRIPTION")),
                missing=i(row.get("MISSING")),
                missing_description=s(row.get("MISSING_DESCRIPTION")),
                injuries=i(row.get("INJURIES")),
                injuries_description=s(row.get("INJURIES_DESCRIPTION")),
                damage_musd=f(row.get("DAMAGE_MILLIONS_DOLLARS")),
                damage_description=s(row.get("DAMAGE_DESCRIPTION")),
                houses_destroyed=i(row.get("HOUSES_DESTROYED")),
                houses_destroyed_description=s(row.get("HOUSES_DESTROYED_DESCRIPTION")),
                total_deaths=i(row.get("TOTAL_DEATHS")),
                total_deaths_description=s(row.get("TOTAL_DEATHS_DESCRIPTION")),
                total_missing=i(row.get("TOTAL_MISSING")),
                total_missing_description=s(row.get("TOTAL_MISSING_DESCRIPTION")),
                total_injuries=i(row.get("TOTAL_INJURIES")),
                total_injuries_description=s(row.get("TOTAL_INJURIES_DESCRIPTION")),
                total_damage_musd=f(row.get("TOTAL_DAMAGE_MILLIONS_DOLLARS")),
                total_damage_description=s(row.get("TOTAL_DAMAGE_DESCRIPTION")),
                total_houses_destroyed=i(row.get("TOTAL_HOUSES_DESTROYED")),
                total_houses_destroyed_description=s(row.get("TOTAL_HOUSES_DESTROYED_DESCRIPTION")),
            )

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Imported rows: {created}"))