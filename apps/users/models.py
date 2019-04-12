from datetime import datetime   #第一区域自带的

from django.db import models    #第二区域是第三方的
from django.contrib.auth.models import AbstractUser
from django.db.models import Model
# Create your models here.

#每个class之间要空两格



class UserProfile(AbstractUser):
    """
    用户信息
    """
    GENDER_CHOICES = (
        ("male", u"男"),
        ("female", u"女")
    )
    #用户用手机注册，所以姓名，生日和邮箱可以为空
    name = models.CharField("姓名",max_length=30, null=True, blank=True)
    birthday = models.DateField("出生年月",null=True, blank=True)
    gender = models.CharField("性别",max_length=6, choices=GENDER_CHOICES, default="female")
    mobile = models.CharField("电话",max_length=11)
    email = models.EmailField("邮箱",max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    send_choices = (
        ('register','注册'),
        ('forget','忘记密码')
    )

    code = models.CharField('验证码',max_length=20)
    email = models.CharField('邮箱',max_length=50)
    send_type = models.CharField('发送类型',choices=send_choices,max_length=10)
    send_time = models.DateTimeField('发送时间',default=datetime.now)


    class Meta:

        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name


class Banner(models.Model):
    title = models.CharField('标题',max_length=100)
    image = models.ImageField('轮播图',upload_to='banner/%Y%m',max_length=100)
    url = models.URLField('访问地址',max_length=200)
    index = models.IntegerField('顺序',default=100)
    add_time = models.DateTimeField('添加时间',default=datetime.now)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

