from django.urls import path

from jwcm.lpw.views import monthly_lpw, congregation_availability_update, person_availability_update

urlpatterns = [
    path('person/update/<int:pk>/', person_availability_update, name='lpw-person-update'),
    path('congregation/update/<int:pk>/', congregation_availability_update, name='lpw-congregation-update'),
    path('monthly/', monthly_lpw, name='lpw-monthly'),
]
