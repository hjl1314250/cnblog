"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path,re_path
from blog import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('logout/', views.logout),
    path('', views.index),
    #点赞或者踩灭
    path('digg/', views.digg),
    # 评论
    path('comment/', views.comment),
    # 后台管理
    path('backend/', views.backend),
    # 添加文章
    path('backend/add_article/', views.add_article),
    # 上传文件
    path('upload/', views.upload),

    #文章详情
    re_path('(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.article_detail),
    # 跳转
    re_path('(?P<username>\w+)/(?P<condition>category|tag|achrive)/(?P<params>.*)/$', views.homesite),
    # 个人站点
    re_path('(?P<username>\w+)/$', views.homesite),
]