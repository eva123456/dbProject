from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^db/api/clear', views.clear, name='clear'),
url(r'^db/api/[a-z]+/create', views.create, name='create'),
url(r'^db/api/[a-z]+/details', views.details, name='details'),

]
