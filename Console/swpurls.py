b0VIM 7.4      ���_[.�Z  dl                                      Double-TITAN-V                          ~dl/users/wangruifeng/05MisleadingWidgets/MisleadingWidgetsDetective/Console/urls.py                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         utf-8 3210    #"! U                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 tp           )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ad  �  �	     )       �  �  �  �  �  M  L  (    �  �  �  �  j  0    �  �  �  �  g  P  2    �  �  >  �  i    �
  �
  �
  �
  j
  =
  �	  �	  �	  �	  �	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ]     path('changeDB',views.changeDB)     path('evaluateSubmit',views.evaluateSubmit),      path('evaluate/<str:projectName>/<str:subtask_name>',views.evaluate),      path('evaluateHome',views.evaluateHome),     path('deleteUser',views.deleteUser),     path('addUser',views.addUser),     path('users',views.users),     path('login',views.login),     # Console/evaluate.html     path('tagging/<str:projectName>/<str:subtask_name>/<str:widget_id>',views.tagging),      # Console/album_tagging.html     #re_path(r'^album/(?P<projectName>[0-9a-z]*)/(?P<subtask_name>[0-9a-z]*)/<(?P<galleryId>[0-9a-z]*)/(?P<hightlightCluster>[0-9a-z]*)/(?P<hightlightId>[0-9a-z]*)',views.album),      path('album/<str:projectName>/<str:subtask_name>/<str:galleryId>/<str:hightlightClusterId>',views.album),      # Console/album_outlier.html     path('subtask/<str:projectName>/<str:subtask_name>',views.subtask),      # Console/subtask.html     path('tags',views.tags),      #Console/tags.html     path('gallerys',views.gallerys),      # Console/gallerys.html     path('projects',views.projects),      # Console/projects.html     path('submitRun',views.submitRun),      # Console/submitRun.html     path('changedb/<str:db_name>',views.chooseDataBase),      path('console',views.console),      # Console/console.html     path('checkRun',views.checkRun),      path('home',views.homepage),      path('',views.index,name='index'), urlpatterns = [ # 本文件设置本应用的路由  #添加这句为了避免'Specifying a namespace in include() without providing an app_name'错误 app_name='[Console]'  from . import views  from django.urls import path,re_path 