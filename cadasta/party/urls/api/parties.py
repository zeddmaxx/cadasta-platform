from django.conf.urls import url

from party.views import api

urlpatterns = [
    url(
        r'^$',
        api.PartyList.as_view(),
        name='list'),
    url(
        r'^(?P<party>[-\w]+)/$',
        api.PartyDetail.as_view(),
        name='detail'),
    url(
        r'^(?P<party>[-\w]+)/relationships/$',
        api.RelationshipList.as_view(),
        name='rel_list'),
]
