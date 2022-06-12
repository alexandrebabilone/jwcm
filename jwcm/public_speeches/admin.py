from django.contrib import admin
from jwcm.public_speeches.models import PublicAssignment, Speech, WeekendMeeting

admin.site.register(PublicAssignment)
admin.site.register(Speech)
admin.site.register(WeekendMeeting)