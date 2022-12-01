from django.contrib import admin
from jwcm.lpw.models import PersonAvailability, CongregationAvailability, DayLPW

admin.site.register(PersonAvailability)
admin.site.register(CongregationAvailability)
admin.site.register(DayLPW)