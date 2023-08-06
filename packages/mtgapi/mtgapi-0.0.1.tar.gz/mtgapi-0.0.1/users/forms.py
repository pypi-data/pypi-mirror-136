from django.forms import Form
from django import forms
from django.forms import fields
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField

class RegisterForm(Form):
    username = fields.CharField(
        required=True,
        min_length=3,
        max_length=18,
        error_messages={
            "required":"用户名不可以为空！",
            "min_length":"用户名不能低于3位！",
            "max_length":"用户名不能超过18位！"
        }
    )
    password1 = fields.CharField(
        required=True,
        min_length=3,
        max_length=18,
        error_messages={
            "required":"密码不可以空",
            "min_length": "密码不能低于3位！",
            "max_length": "密码不能超过18位！"
        }
    )
    password2 = fields.CharField(required=False)
    email = fields.EmailField(
        required=True,
        error_messages={
            "required":"邮箱不可以为空！"
        },
    )

    def clean_password2(self):
        if not self.errors.get("password1"):
            if self.cleaned_data["password2"] != self.cleaned_data["password1"]:
                raise ValidationError("您输入的密码不一致，请重新输入！")
            return self.cleaned_data


class LoginForm(Form):
    username = fields.CharField(
        required=True,
        min_length=3,
        max_length=18,
        error_messages={
            "required":"用户名不可以为空！",
            "min_length":"用户名不能低于3位！",
            "max_length":"用户名不能超过18位！"
        }
    )
    password = fields.CharField(
        required=True,
        error_messages={
            "required":"密码不可以空",
        }
    )
    

class UserForm(forms.Form):
    username = forms.CharField(
        label="用户名", 
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    password = forms.CharField(
        label="密码", 
        max_length=256, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
        )
    captcha = CaptchaField(label='验证码')

class RegisterForm2(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='性别', choices=gender)
    captcha = CaptchaField(label='验证码')