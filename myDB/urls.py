from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^db/api/[a-z]+/create', views.create, name='create'),

]
