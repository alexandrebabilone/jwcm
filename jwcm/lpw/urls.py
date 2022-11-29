from django.urls import path

from jwcm.lpw.views import PersonAvailabilityUpdate, CongregationAvailabilityUpdate

urlpatterns = [
    path('person/update/<int:pk>/', PersonAvailabilityUpdate.as_view(), name='lpw-person-update'),
    path('congregation/update/<int:pk>/', CongregationAvailabilityUpdate.as_view(), name='lpw-congregation-update'),
]
