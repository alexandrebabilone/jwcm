from django.contrib import admin
from jwcm.core.models import Person, Congregation, Meeting


admin.site.register(Person)
admin.site.register(Congregation)
admin.site.register(Meeting)