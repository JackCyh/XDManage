from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.views import View
from users.forms import RegisterForm, LoginForm, ForgetPwdForm, ModifyPwdForm
from users.models import UserProfile, EmailVerifyRecord

#邮箱和用户名都可以登录
# 基础ModelBackend类，因为它有authenticate方法
from utils.email_send import send_register_eamil


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))

            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):

    def get (self,request):
        return  render(request,'login.html')

    def post (self,request):
        login_form = LoginForm(request.POST)
        if(login_form.is_valid()):
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象,失败None
            user = authenticate(username=user_name, password=pass_word)
            # 如果不是null说明验证成功
            if user is not None:
                if user.is_active:
                    #登录
                    login(request, user)
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form': login_form})

# 激活用户的view
class ActiveUserView(View):
    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code = active_code)

        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
         # 验证码不对的时候跳转到激活失败页面
        else:
            return render(request,'active_fail.html')
        # 激活成功跳转到登录页面
        return render(request, "login.html", )

# 如果是get请求，直接返回注册页面给用户
# 如果是post请求，先生成一个表单实例，并获取用户提交的所有信息（request.POST）
# is_valid()方法，验证用户的提交信息是不是合法
# 如果合法，获取用户提交的email和password
# 实例化一个user_profile对象，把用户添加到数据库
# 默认添加的用户是激活状态（is_active=1表示True），在这里我们修改默认的状态（改为is_active = False），只有用户去邮箱激活之后才改为True
# 对密码加密，然后保存，发送邮箱，username是用户注册的邮箱，‘register’表明是注册
# 注册成功跳转到登录界面
class RegisterView(View):

    def get(self,request):
        register_form = RegisterForm
        return  render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if(register_form.is_valid()):
            user_name = request.POST.get('email', None)
            #如果用户已存在，则提示错误信息
            if UserProfile.objects.filter(email = user_name):
                return render(request, 'register.html', {'register_form' :register_form, 'msg':'用户已存在'})

            pass_word = request.POST.get('password', None)
            # 实例化一个user_profile对象
            userProfile = UserProfile()
            userProfile.username = user_name
            userProfile.email = user_name
            userProfile.password = pass_word
            userProfile.is_active = False
            # 对保存到数据库的密码加密
            userProfile.password = make_password(pass_word)
            userProfile.save()
            send_register_eamil(user_name, 'register')
            return render(request, 'login.html')
        else:
            render(request, 'register.html', {'register_form': register_form})


# 忘记密码
class ForgetPwdView(View):
    '''找回密码'''
    def get(self,request):
        forget_form = ForgetPwdForm()
        return render(request,'forgetpwd.html',{'forget_form':forget_form})

    def post(self,request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email',None)
            send_register_eamil(email,'forget')
            return render(request, 'send_success.html')
        else:
            return render(request,'forgetpwd.html',{'forget_form':forget_form})


#重置密码
class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


#修改密码
class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email":email, "msg":"密码不一致！"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "modify_form":modify_form })








