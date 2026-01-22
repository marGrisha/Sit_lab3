from django import forms
from .models import Volcano


class VolcanoForm(forms.ModelForm):
    class Meta:
        model = Volcano
        fields = [
            "location",
            "name",
            "latitude",
            "longitude",
            "elevation_m",
            "volcano_type",
            "status",
        ]