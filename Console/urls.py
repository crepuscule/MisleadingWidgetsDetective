from django.urls import path

from . import views

app_name='[Console]'
#添加这句为了避免'Specifying a namespace in include() without providing an app_name'错误

# 本文件设置本应用的路由
urlpatterns = [
    path('',views.index,name='index'),
    path('console',views.console), 
    path('gallery',views.gallery), 
    path('tagging',views.tagging), 

]

