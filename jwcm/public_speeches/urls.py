"""jwcm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from jwcm.public_speeches.views import SpeechList, SpeechCreate, SpeechUpdate, SpeechDelete, PublicAssignmentList, \
    public_assignment_create, public_assignment_update, PublicAssignmentDelete, person_guest_create, \
    congregation_guest_pop_up_create, WatchtowerReadertList, WatchtowerReaderUpdate

urlpatterns = [
    path('speech/', SpeechList.as_view(), name='speech-list'),
    path('speech/create/', SpeechCreate.as_view(), name='speech-create'),
    path('speech/update/<int:pk>/', SpeechUpdate.as_view(), name='speech-update'),
    path('speech/delete/<int:pk>/', SpeechDelete.as_view(), name='speech-delete'),

    path('public_assignment/', PublicAssignmentList.as_view(), name='public-assignment-list'),
    path('public_assignment/create/', public_assignment_create, name='public-assignment-create'),
    path('public_assignment/update/<int:pk>/', public_assignment_update, name='public-assignment-update'),
    path('public_assignment/delete/<int:pk>/', PublicAssignmentDelete.as_view(), name='public-assignment-delete'),

    path('person_guest/create/', person_guest_create, name ='person-guest-create'),
    path('congregation_guest/create/', congregation_guest_pop_up_create, name ='congregation-guest-create'),

    path('watchtower_reader/', WatchtowerReadertList.as_view(), name='watchtower-reader-list'),
    path('watchtower_reader/update/<int:pk>/', WatchtowerReaderUpdate.as_view(), name='watchtower-reader-update'),
]
