"""
URL configuration for comment_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path,include
# comment_system/urls.py or wherever you included auth URLs
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comments.urls')),  # Wire up your app's URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Include Django's built-in authentication URLs
    path('accounts/signup/', include('comments.urls')),  # Include signup URL from comments app
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include('comments.api_urls')),

]
