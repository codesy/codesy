from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^repos$', views.RecommendRepoView.as_view(), name='repos'),
]
