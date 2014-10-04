from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^campaign/$', views.campaign, name='mtefd-campaign'),
    url(r'^dep/$', views.dep, name='mtefd-dep'),
]
