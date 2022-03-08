from django.contrib import admin
from jwcm.core.models import Person, Speech, Congregation, Profile, PublicAssignment


admin.site.register(Person)
admin.site.register(Speech)
admin.site.register(Congregation)
admin.site.register(Profile)
admin.site.register(PublicAssignment)