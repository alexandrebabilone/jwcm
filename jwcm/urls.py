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
from django.urls import path, include
from jwcm.core.views import About, CongregationUpdate, PersonList, PersonCreate, \
    PersonUpdate, PersonDelete, person_batch_create, home, MechanicalPrivilegesView,\
    MechanicalPrivilegesListView, MechanicalPrivilegesUpdateView



urlpatterns = [
    path('public_speeches/', include('jwcm.public_speeches.urls')),
    path('life_and_ministry/', include('jwcm.life_and_ministry.urls')),
    path('users/', include('jwcm.users.urls')),

    path('', home, name='home'),
    path('about/', About.as_view(), name='about'),

    path('congregation/<int:pk>/', CongregationUpdate.as_view(), name='congregation'),

    path('person/', PersonList.as_view(), name='person-list'),
    path('person/create/', PersonCreate.as_view(), name='person-create'),
    path('person/update/<int:pk>/', PersonUpdate.as_view(), name='person-update'),
    path('person/delete/<int:pk>/', PersonDelete.as_view(), name='person-delete'),
    path('person/create/batch/', person_batch_create, name='person-batch-create'),

    #path('mechanical_privileges/', MechanicalPrivilegesView.as_view(), name='mechanical-privileges'),
    path('mechanical_privileges/', MechanicalPrivilegesListView.as_view(), name='mechanical-privileges-list'),
    path('mechanical_privileges/<int:pk>/', MechanicalPrivilegesUpdateView.as_view(), name='mechanical-privileges-update'),

    path('admin/', admin.site.urls),
]
