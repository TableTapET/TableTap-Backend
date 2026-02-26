"""
URL configuration for TableTap-Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.urls import path

from config.views import NotImplementedView

urlpatterns = [
    # These are template API, replace when actual functions are built out
    path("login/", NotImplementedView.as_view(), name="login"),
    path("logout/", NotImplementedView.as_view(), name="logout"),
    path("edit_user/", NotImplementedView.as_view(), name="edit_user"),
    path("refresh_token/", NotImplementedView.as_view(), name="refresh_token"),
    path("validate_token/", NotImplementedView.as_view(), name="validate_token"),
]
