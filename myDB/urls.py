from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^db/api/clear', views.clear, name = 'clear'),
url(r'^db/api/status', views.status, name = 'status'),
url(r'^db/api/[a-z]+/create', views.create, name = 'create'),
url(r'^db/api/[a-z]+/details', views.details, name = 'details'),
url(r'^db/api/forum/listUsers', views.listUsersf, name = 'forum posts'),
url(r'^db/api/forum/listThreads', views.listThreadsf, name = 'forum threads'),
url(r'^db/api/forum/listPosts', views.listPostsf, name = 'forum users'),

]
