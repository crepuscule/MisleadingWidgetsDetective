from django.urls import path,re_path

from . import views

app_name='[Console]'
#添加这句为了避免'Specifying a namespace in include() without providing an app_name'错误

# 本文件设置本应用的路由
urlpatterns = [
    path('',views.index,name='index'),
    path('home',views.homepage), 
    path('checkRun',views.checkRun), 
    # Console/console.html
    path('console',views.console), 
    # Console/submitRun.html
    path('submitRun',views.submitRun), 
    # Console/projects.html
    path('projects',views.projects), 
    # Console/gallerys.html
    path('gallerys',views.gallerys), 
    #Console/tags.html
    path('tags',views.tags), 
    # Console/subtask.html
    path('subtask/<str:projectName>/<str:subtask_name>',views.subtask), 
    # Console/album_outlier.html
    path('album/<str:projectName>/<str:subtask_name>/<str:galleryId>/<str:hightlightClusterId>',views.album), 
    #re_path(r'^album/(?P<projectName>[0-9a-z]*)/(?P<subtask_name>[0-9a-z]*)/<(?P<galleryId>[0-9a-z]*)/(?P<hightlightCluster>[0-9a-z]*)/(?P<hightlightId>[0-9a-z]*)',views.album), 
    # Console/album_tagging.html
    path('tagging/<str:projectName>/<str:subtask_name>/<str:widget_id>',views.tagging), 
    # Console/evaluate.html
    path('login',views.login),
    path('users',views.users),
    path('addUser',views.addUser),
    path('deleteUser',views.deleteUser),
    path('evaluateHome',views.evaluateHome),
    path('evaluate/<str:projectName>/<str:subtask_name>',views.evaluate), 
    path('evaluateSubmit',views.evaluateSubmit), 
    path('changeDB',views.changeDB)
]

