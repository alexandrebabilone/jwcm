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
from django.contrib import admin
from django.urls import path
from jwcm.core.views import Home, About, user_register, public_assignment_create, ProfileUpdate, CongregationUpdate, PersonList, \
    PersonCreate, PersonUpdate, PersonDelete, SpeechList, SpeechCreate, PublicAssignmentList, public_assignment_update, PublicAssignmentDelete, SpeechDelete, SpeechUpdate
from django.contrib.auth import views as authview


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),

    path('login/', authview.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', authview.LogoutView.as_view(), name='logout'),
    path('register/', user_register, name='register'),

    path('profile/<int:pk>/', ProfileUpdate.as_view(), name='profile'),
    path('congregation/<int:pk>/', CongregationUpdate.as_view(), name='congregation'),

    path('person/', PersonList.as_view(), name='person-list'),
    path('person/create/', PersonCreate.as_view(), name='person-create'),
    path('person/update/<int:pk>/', PersonUpdate.as_view(), name='person-update'),
    path('person/delete/<int:pk>/', PersonDelete.as_view(), name='person-delete'),

    path('speech/', SpeechList.as_view(), name='speech-list'),
    path('speech/create/', SpeechCreate.as_view(), name='speech-create'),
    path('speech/update/<int:pk>/', SpeechUpdate.as_view(), name='speech-update'),
    path('speech/delete/<int:pk>/', SpeechDelete.as_view(), name='speech-delete'),

    path('public_assignment/', PublicAssignmentList.as_view(), name='public-assignment-list'),
    path('public_assignment/create/', public_assignment_create, name='public-assignment-create'),
    path('public_assignment/update/<int:pk>/', public_assignment_update, name='public-assignment-update'),
    path('public_assignment/delete/<int:pk>/', PublicAssignmentDelete.as_view(), name='public-assignment-delete'),


    path('admin/', admin.site.urls),
]
