from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from blog.models import Article, UserInfo, Blog, Category, Tag, ArticleUpDown, Comment
from django.db.models import Sum, Avg, Max, Min, Count
from django.db.models import F
import json
from django.http import JsonResponse
from django.db import transaction
import os
from cnblog import settings  # 导入settings。注意:cnblog为项目名


# Create your views here.
def login(request):
    if request.method == "POST":
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        # 用户验证成功,返回user对象,否则返回None
        user = auth.authenticate(username=user, password=pwd)
        if user:
            # 登录,注册session
            # 全局变量 request.user=当前登陆对象(session中)
            auth.login(request, user)
            return redirect("/index/")

    return render(request, "F:/play/cnblog/templates/login.html")


def index(request):
    article_list = Article.objects.all()
    return render(request, "F:/play/cnblog/templates/index.html", {"article_list": article_list})


def logout(request):  # 注销
    auth.logout(request)
    return redirect("/index/")


def query_current_site(request, username):  # 查询当前站点的博客标题
    # 查询当前站点的用户对象
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "F:/play/cnblog/templates/not_found.html")
    # 查询当前站点对象
    blog = user.blog
    return blog


def homesite(request, username, **kwargs):  # 个人站点主页
    print("kwargs", kwargs)

    blog = query_current_site(request, username)

    # 查询当前用户发布的所有文章
    if not kwargs:
        article_list = Article.objects.filter(user__username=username)
    else:
        condition = kwargs.get("condition")
        params = kwargs.get("params")
        # 判断分类、随笔、归档
        if condition == "category":
            article_list = Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition == "tag":
            article_list = Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            year, month = params.split("/")
            article_list = Article.objects.filter(user__username=username).filter(create_time__year=year,
                                                                                  create_time__month=month)
    return render(request, "F:/play/cnblog/templates/homesite.html", {"blog": blog, "username": username, "article_list": article_list})


def article_detail(request,username,article_id):
    blog = query_current_site(request,username)

    #查询指定id的文章
    article_obj = Article.objects.filter(pk=article_id).first()
    user_id = UserInfo.objects.filter(username=username).first().nid

    comment_list = Comment.objects.filter(article_id=article_id)
    dict = {"blog":blog,
            "username":username,
            'article_obj':article_obj,
            "user_id":user_id,
            "comment_list":comment_list,
            }

    return render(request,'F:/play/cnblog/templates/article_detail.html',dict)

def digg(request):
    print(request.POST)
    if request.method == "POST":
        # ajax发送的过来的true和false是字符串，使用json反序列化得到布尔值
        is_up = json.loads(request.POST.get("is_up"))
        article_id = request.POST.get("article_id")
        user_id = request.user.pk

        response = {"state": True, "msg": None}  # 初始状态
        # 判断当前登录用户是否对这篇文章做过点赞或者踩灭操作
        obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
        if obj:
            response["state"] = False  # 更改状态
            response["handled"] = obj.is_up  # 获取之前的操作,返回true或者false
            print(obj.is_up)
        else:
            with transaction.atomic():
                # 插入一条记录
                new_obj = ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
                if is_up:  # 判断为推荐
                    Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
                else:  # 反对
                    Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)

        return JsonResponse(response)

    else:
        return HttpResponse("非法请求")


def comment(request):
    print(request.POST)
    if request.method == "POST":
        # 获取数据
        user_id = request.user.pk
        article_id = request.POST.get("article_id")
        content = request.POST.get("content")
        pid = request.POST.get("pid")
        # 生成评论对象
        with transaction.atomic():  # 增加事务
            # 评论表增加一条记录
            comment = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                             parent_comment_id=pid)
            # 当前文章的评论数加1
            Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

        response = {"state": False}  # 初始状态

        if comment.user_id:  # 判断返回值
            response = {"state": True}

        # 响应体增加3个变量
        response["timer"] = comment.create_time.strftime("%Y-%m-%d %X")
        response["content"] = comment.content
        response["user"] = request.user.username

        return JsonResponse(response)  # 返回json对象

    else:
        return HttpResponse("非法请求")

def backend(request):
    user = request.user
    #当前用户文章列表
    article_list = Article.objects.filter(user=user)
    # 因为是在templates的下一层，所以需要指定目录backend
    return render(request, "F:/play/cnblog/templates/backend/backend.html", {"user":user,"article_list":article_list})

def add_article(request):
    return render(request, "F:/play/cnblog/templates/backend/add_article.html")

def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")  # 获取文件对象
    name = obj.name  # 文件名
    #文件存储的绝对路径
    path = os.path.join(settings.BASE_DIR, "static", "upload", name)
    with open(path, "wb") as f:
        for line in obj:  # 遍历文件对象
            f.write(line)  # 写入文件

    #必须返回这2个key
    res = {
        # 为0表示没有错误,如果有错误,设置为1。增加一个key为message,用来显示指定的错误
        "error": 0,
        # 图片访问路径，必须能够直接访问到
        "url": "/static/upload/" + name
    }

    return HttpResponse(json.dumps(res))  # 必须返回Json