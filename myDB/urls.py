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
url(r'^db/api/post/list', views.listp, name = 'post list'),
url(r'^db/api/post/remove', views.removep, name = 'post remove'),
url(r'^db/api/post/restore', views.restorep, name = 'post restore'),
url(r'^db/api/post/vote', views.votep, name = 'vote for post'),
url(r'^db/api/post/update', views.update, name = 'update post'),
url(r'^db/api/user/follow', views.follow, name = 'user follow'),
url(r'^db/api/user/unfollow', views.unfollow, name = 'user unfollow'),
url(r'^db/api/user/updateProfile', views.updateu, name = 'user update'),
url(r'^db/api/user/listFollowers', views.listfollowers, name = 'user list followers'),
url(r'^db/api/user/listFollowing', views.listfollowing, name = 'user list following'),
url(r'^db/api/user/listPosts', views.listpostsu, name = 'user list posts'),
url(r'^db/api/thread/close', views.closet, name = 'thread close'),
url(r'^db/api/thread/open', views.opent, name = 'thread close'),
url(r'^db/api/thread/remove', views.removet, name = 'thread close'),
url(r'^db/api/thread/restore', views.restoret, name = 'thread close'),
url(r'^db/api/thread/vote', views.votet, name = 'thread close'),
url(r'^db/api/thread/update', views.updatet, name = 'thread close'),
url(r'^db/api/thread/subscribe', views.subscribe, name = 'thread close'),
url(r'^db/api/thread/unsubscribe', views.unsubscribe, name = 'thread close'),
url(r'^db/api/thread/listPosts', views.listPostst, name = 'thread close'),
url(r'^db/api/thread/list', views.listt, name = 'thread close'),











]
