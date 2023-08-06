import os
from pathlib import Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'q-zhs9+dk&c%zr@q0mz)omcmpjr*ksp5(kc_jz-0z&koh%24*y')
DEBUG = bool(os.environ.get("DJANGO_DEBUG",True))

# if DEBUG:
#     print("调试环境")
# else:
#     print("生产环境")



ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'ingredients',
    'mtx',
    # # 'debug_toolbar', # debug_toolbar 感染了graphql的正常行为，先去掉。
    'users',
    'vpngate',
    'mtproxy',
    'chat',                 # django channels 练习
    'guardian',
    'rest_framework',
    'captcha',              # django-simple-captcha 插件，简单的图形验证码。
    'corsheaders',          # django-cors-headers
    'oauth2_provider',      # django-oauth-toolkit
    'channels',             # 直接用channels好像跟 graphene django模块不兼容。
    # 'graphene_subscriptions', 
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',                    #允许跨域请求的中间件。django-cors-headers
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',          # django-oauth-toolkit
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware", # debug_toolbar 感染了graphql的正常行为，先去掉。
    # "graphene_django.debug.DjangoDebugMiddleware", #graphene的调试中间件(不知什么原因，使用就出错)。
]

ROOT_URLCONF = 'mainapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI 是同步版的服务器，就目前来说没有什么理由使用同步版的。所以干脆直接去掉。
# WSGI_APPLICATION = 'mainapp.wsgi.application'

# 异步版的用起来，就算是开发环境中运行，都感觉一模一样。
ASGI_APPLICATION = 'mainapp.asgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# dbhost="mt-compose"
# if Path("/.dockerenv").exists():
#     dbhost="127.0.0.1"

DATABASES = {    
    #  'default': {
    #     'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
    #     'NAME': 'mtx',   
    #     'USER': 'root', 
    #     'PASSWORD': 'feihuo321', 
    #     'HOST': os.environ.get("DB_HOST","mt.tailnet-1f77.ts.net"), 
    #     'PORT': os.environ.get("DB_PORT","3306"),
    # },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


## 
AUTHENTICATION_BACKENDS = (
    # 视情况添加
    'oauth2_provider.backends.OAuth2Backend',    # django-oauth-toolkit
    "graphql_jwt.backends.JSONWebTokenBackend",  # # django-graphql-jwt (认证中间件)
    'django.contrib.auth.backends.ModelBackend', # default
    'guardian.backends.ObjectPermissionBackend', # guardian (对象级别权限管理)
)

LOGIN_URL='/admin/login/'
## 修改用户模型
AUTH_USER_MODEL='users.User'

# APPEND_SLASH=True # (默认是没有这个设置的)注意这个可能有什么影响。

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, "static")  # 即静态文件存放在 BASE_DIR/static 下（和manage.py同级目录下），注意BASE_DIR指django工程的绝对路径
]

#############################################################################
##
##
GRAPHENE = {
    # "SCHEMA": "mainapp.schema.schema" #schema 的设置，目前在mainapp urls 指定了。所以settings这里可以不指定。
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware", # django-graphql-jwt (认证中间件)
    ],
    "SUBSCRIPTION_PATH": "/graphql/",
}


#############################################################################
## debug_toolbar 之后在下面指定的IP访问时才生效。
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

#############################################################################
##  REST_FRAMEWORK 相关配置
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

#############################################################################
##  django-cors-headers 相关配置
CORS_ORIGIN_WHITELIST = (
 'http://127.0.0.1:8000',
 'http://localhost:8000',
)
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS = True # 指明在跨域访问中，后端是否支持对cookie的操作。
CORS_ALLOW_METHODS = (
 'DELETE',
 'GET',
 'OPTIONS',
 'PATCH',
 'POST',
 'PUT',
 'VIEW',
)
CORS_ALLOW_HEADERS = (
 'XMLHttpRequest',
 'X_FILENAME',
 'accept-encoding',
 'authorization',
 'content-type',
 'dnt',
 'origin',
 'user-agent',
 'x-csrftoken',
 'x-requested-with',
 'Pragma',
)

#############################################################################
##  graphene-subscriptions 相关配置
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}