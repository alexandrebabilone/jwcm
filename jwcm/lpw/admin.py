from django.contrib import admin
from jwcm.lpw.models import PersonAvailability, CongregationAvailability

admin.site.register(PersonAvailability)
admin.site.register(CongregationAvailability)