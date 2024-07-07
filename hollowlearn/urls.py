"""
URL configuration for hollowlearn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from learningApp import views
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from learningApp.schema import schema
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.loging , name="login"),
    path('home/', views.home , name="home"),
    path("register/",views.register , name="register"),
    path('profile/<str:pk>/', views.profile , name="profile"),
    path('enrollment/<str:pk>', views.enrollment , name="enrollment"),
    path('course/', views.course_managment , name="course"),
    path('add_permission/<str:pk>', views.add_permission , name="add_permission"),
    path('remove_permission/<str:pk>', views.remove_permission , name="remove_permission"),
    path('dashboard/', views.dashboard , name="dashboard"),
    path('Error/', views.access_denied, name='access_denied'),
    path('add_course/', views.add_course, name='add_course'),
    path('get_lessons/<int:id>', views.get_lessons, name='get_lessons'),
    path('get_lesson/<int:id>', views.get_lesson, name='get_lesson'),
    path('quiz/<int:id>', views.check_quiz, name='quiz'),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True , schema=schema))),
]
