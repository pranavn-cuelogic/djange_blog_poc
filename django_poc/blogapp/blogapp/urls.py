"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, patterns, include
from django.contrib import admin
from blogapp.views import *

urlpatterns = patterns(
    '',
    url(r'^admin/', admin.site.urls),
    url(r'^$', home_view, name='home'),
    url(r'^signup/', signup_view, name='signup'),
    url(r'^activate/(?P<activation_token>\w+)/$', activate_user, name='activate'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': 'home'}, name='logout'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^reset-password/', reset_password, name='reset-password'),
    url(r'^myblog/', include('myblog.urls', namespace='myblog')),
)
