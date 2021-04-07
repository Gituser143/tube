"""oyt_python URL Configuration

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
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.urls import path
from oyt.views import HomeView
from oyt.views import NewVideo
from oyt.views import LoginView
from oyt.views import RegisterView
from oyt.views import ErrorView
import debug_toolbar


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view()),
    path('new_video', NewVideo.as_view()),
    path('login', LoginView.as_view()),
    path('register', RegisterView.as_view()),
    path('error', ErrorView.as_view()),
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
