from django.urls import path
from jwcm.reports.views import ReportsView

urlpatterns = [
    path('', ReportsView.as_view(), name='reports'),
]
