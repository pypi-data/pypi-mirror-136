
import traceback
from django.shortcuts import render
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm
from django.http import JsonResponse
from django.contrib.auth import authenticate,login, logout, get_user_model
from django.shortcuts import render,redirect
import hashlib
from . import views
from . import forms
from . import models

User = get_user_model() # 获取User模型

def register(request):
    if request.method == "GET":
        return render(request,"register.html")
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            email = form.cleaned_data["email"]
            username_exists = User.objects.filter(username=username).exists()
            if username_exists:
            	return JsonResponse({"code":400,"message":"验证失败","data":{"username":"您输入的用户名已存在!","password1":"","password2":"","email":""}})
            email_exists = User.objects.filter(email=email).exists()
            if email_exists:
                return JsonResponse({"code": 400, "message":"验证失败","data":{"username": "","password1":"","password2":"", "email": "您输入的邮箱已存在！"}})
            User.objects.create_user(username=username,password=password,email=email)
            return JsonResponse({"code": 200,"message":"验证通过", "data":{"username": "","password1":"","password2":"", "email": ""}})
        else:
            return JsonResponse({"code":400,"message":"验证失败","data":{"username":form.errors.get("username"),"password1":form.errors.get("password1"),"password2":form.errors.get("password2"),"email":form.errors.get("email")}})


# 登录视图名称不能起成login，与自带login函数重名
def loginView(request):
    if request.method == "GET":
        return render(request,"login.html")
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember = int(request.POST.get("remember"))
            user = authenticate(request,username=username,password=password) # 使用authenticate进行登录验证，验证成功会返回一个user对象，失败则返回None
            # 使用authenticate验证时如果is_active为False也会返回None，导致无法判断激活状态，
            # 此时可以在seetings中配置：
            # AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
            if user and user.is_active: # 如果验证成功且用户已激活执行下面代码
                login(request,user) # 使用自带的login函数进行登录，会自动添加session信息
                request.session["username"] = username # 自定义session，login函数添加的session不满足时可以增加自定义的session信息。
                if remember:
                    request.session.set_expiry(None) # 设置session过期时间，None表示使用系统默认的过期时间 
                else:
                    request.session.set_expiry(0) # 0代表关闭浏览器session失效
                return JsonResponse({"code": 200,"message":"验证通过","data":{ "error":""}})
            elif user and not user.is_active:
              	return JsonResponse({"code": 400, "message": "用户未激活", "data": {"error": "该用户还没有激活，请<a href='#'>激活</a>"}})
            else:
                return JsonResponse({"code": 400, "message": "验证失败", "data": {"error": "用户名或密码错误"}})
        else:
            return JsonResponse({"code":400,"message":"用户名或密码格式错误","data":{"error":"用户名或密码错误"}})
            

# 视图名不能起成logout
def logoutView(request):
    logout(request) # 调用django自带退出功能，会帮助我们删除相关session
    return redirect(request.META["HTTP_REFERER"])
    

# def hash_code(s, salt='mysitepassword123'):# 加点盐
#     h = hashlib.sha256()
#     s += salt
#     h.update(s.encode())  # update方法只接收bytes类型
#     return h.hexdigest()

 
def index(request):
    return render(request,'users/index.html')
 
 
def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/users/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm2(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'users/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'users/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'users/register.html', locals())
                # 当一切都OK的情况下，创建新用户
                models.User.objects.create_user(email, password1)
                return redirect('/users/login/')  # 自动跳转到登录页面
    register_form = forms.RegisterForm2()
    return render(request, 'users/register.html', locals())
 
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")

def login(request):
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if request.session.get('is_login',None):
            return redirect("/index/")
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']            
            try:
                user = models.User.objects.get(username=username)
                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except Exception  as e:
                traceback.print_stack()
                print(f"错误消息：{e}")
                message = "用户不存在！"
        return render(request, 'users/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'users/login.html', locals())

def whoami(r):
    return HttpResponse(r.user.email)