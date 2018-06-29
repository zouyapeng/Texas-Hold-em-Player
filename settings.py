# -*- coding: utf-8 -*-
# @Time    : 2018/6/29 11:34
# @Author  : Bob Zou
# @Mail    : bob_zou@trendmicro.com
# @File    : settings
# @Software: PyCharm
# @Function:

SECRET_KEY = 'csr1!1p6v3h#7pc$6j1@5vfz3vy%wa7p3xwcp=j+fqkv$7%asfw'

INSTALLED_APPS = [
    'core',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mars',
        'USER': 'mars',
        'PASSWORD': 'mars',
        'HOST': '10.213.42.170',
        'PORT': '3306'
    }
}

USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'