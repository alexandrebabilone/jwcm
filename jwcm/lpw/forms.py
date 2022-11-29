from django.forms import ModelForm
from jwcm.lpw.models import PersonAvailability, CongregationAvailability


class PersonAvailabilityForm(ModelForm):

    class Meta:
        model = PersonAvailability
        exclude = ['lpw']


class CongregationAvailabilityForm(ModelForm):

    class Meta:
        model = CongregationAvailability
        exclude = ['lpw']
