from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["country", "name"], name="uq_location_country_name")
        ]

    def __str__(self):
        return f"{self.country} / {self.name}"


class Volcano(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="volcanoes")
    name = models.CharField(max_length=255)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    elevation_m = models.IntegerField(null=True, blank=True)

    volcano_type = models.CharField(max_length=200, null=True, blank=True)  # CSV: Type
    status = models.CharField(max_length=200, null=True, blank=True)       # CSV: Status

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["location", "name"], name="uq_volcano_location_name")
        ]

    def __str__(self):
        return self.name


class Eruption(models.Model):
    volcano = models.ForeignKey(Volcano, on_delete=models.CASCADE, related_name="eruptions")

    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)

    tsu_flag = models.BooleanField(default=False)  # CSV: TSU (значение "TSU" или пусто)
    eq_flag = models.BooleanField(default=False)   # CSV: EQ  (значение "EQ" или пусто)

    time_code = models.CharField(max_length=20, null=True, blank=True)  # CSV: Time (D1, U и т.п.)
    vei = models.IntegerField(null=True, blank=True)                    # CSV: VEI
    agent = models.CharField(max_length=20, null=True, blank=True)      # CSV: Agent

    def __str__(self):
        return f"{self.volcano} {self.year}-{self.month}-{self.day}"


class Impact(models.Model):
    eruption = models.OneToOneField(Eruption, on_delete=models.CASCADE, related_name="impact")

    deaths = models.IntegerField(null=True, blank=True)
    deaths_description = models.CharField(max_length=200, null=True, blank=True)

    missing = models.IntegerField(null=True, blank=True)
    missing_description = models.CharField(max_length=200, null=True, blank=True)

    injuries = models.IntegerField(null=True, blank=True)
    injuries_description = models.CharField(max_length=200, null=True, blank=True)

    damage_musd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    damage_description = models.CharField(max_length=200, null=True, blank=True)

    houses_destroyed = models.IntegerField(null=True, blank=True)
    houses_destroyed_description = models.CharField(max_length=200, null=True, blank=True)

    total_deaths = models.IntegerField(null=True, blank=True)
    total_deaths_description = models.CharField(max_length=200, null=True, blank=True)

    total_missing = models.IntegerField(null=True, blank=True)
    total_missing_description = models.CharField(max_length=200, null=True, blank=True)

    total_injuries = models.IntegerField(null=True, blank=True)
    total_injuries_description = models.CharField(max_length=200, null=True, blank=True)

    total_damage_musd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_damage_description = models.CharField(max_length=200, null=True, blank=True)

    total_houses_destroyed = models.IntegerField(null=True, blank=True)
    total_houses_destroyed_description = models.CharField(max_length=200, null=True, blank=True)