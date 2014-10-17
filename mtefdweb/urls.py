from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^campaign/$', views.campaign, name='mtefd-campaign'),
    url(r'^dep/$', views.dep, name='mtefd-dep'),
    url(r'^funders/$', views.funders, name='mtefd-funders'),
    url(r'^funder/$', views.FunderGetToken.as_view(),
        name='mtefd-funder-get-token'),
    url(r'^funder/done/$', views.FunderGetTokenDone.as_view(),
        name='mtefd-funder-get-token-done'),
    url(r'^funder/(?P<token>\w{12})/$', views.FunderInfo.as_view(),
        name='mtefd-funder-info'),
    url(r'^$', views.Updates.as_view(), name='mtefd-updates'),
]
