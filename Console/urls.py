from django.urls import path,re_path

from . import views

app_name='[Console]'
#添加这句为了避免'Specifying a namespace in include() without providing an app_name'错误

# 本文件设置本应用的路由
urlpatterns = [
    # Basic
    path('',views.homepage),
    path('home',views.homepage), 

    # Console
    ## Console/console.html
    path('console',views.console), 
    path('remarkdatabase',views.remarkDataBase),
    path('changedb/<str:db_name>',views.chooseDataBase), 
    path('changeapkforest/<str:apkforest>',views.chooseRawApkForest),
    ## 用于检查有多少算法程序在本机执行
    path('checkRun',views.checkRun), 
    ## Console/submitRun.html
    path('submitRun',views.submitRun), 
    ## 进行数据集的预聚类，标注,去噪
    path('tagrawdatabase/<str:database>',views.tagRawDataBase),
    path('submitrawdatabasetag/<str:database>',views.submitRawDataBaseTag),

    path('apkforestlist',views.apkforestlist),
    path('apkforest/<str:apkforestName>',views.apkforest),
    path('apkForestSubmit',views.apkforestsubmit),
    ## 将app检查列表化简去重
    path('checkapp',views.checkAPPs),

    # Users
    path('login',views.login),
    path('users',views.users),
    path('addUser',views.addUser),
    path('deleteUser',views.deleteUser),

    # Projects
    ## Console/projects.html
    path('projects',views.projects), 
    ## Console/subtask.html
    path('subtask/<str:projectName>/<str:subtask_name>',views.subtask), 
    ## Console/
    path('remarksubtask',views.remarkSubtask),

    # Gallerys
    ## Console/gallerys.html
    path('gallerys',views.gallerys), 

    # Tags
    #Console/tags.html
    path('tags',views.tags), 
    # Console/album_outlier.html
    path('album/<str:projectName>/<str:subtask_name>/<str:galleryId>/<str:hightlightClusterId>/<int:cluster_no>',views.album), 
    #re_path(r'^album/(?P<projectName>[0-9a-z]*)/(?P<subtask_name>[0-9a-z]*)/<(?P<galleryId>[0-9a-z]*)/(?P<hightlightCluster>[0-9a-z]*)/(?P<hightlightId>[0-9a-z]*)',views.album), 
    # Console/album_tagging.html
    path('tagging/<str:projectName>/<str:subtask_name>/<str:widget_id>',views.tagging), 
    # Console/evaluate.html
    path('evaluateHome',views.evaluateHome),
    path('evaluate/<str:projectName>/<str:subtask_name>',views.evaluate), 
    path('evaluateSubmit',views.evaluateSubmit), 
    # 实际上不需要，但是先这样
    path('submitSuspects',views.submitSuspects),
]

