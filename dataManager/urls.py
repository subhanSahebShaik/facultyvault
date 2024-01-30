"""
URL configuration for dataManager project.

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
from facultyDataManager import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login_view, name="home"),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_faculty, name='add_faculty'),
    path("password_reset_initiator/", views.password_reset_initiator, name="password_reset_initiator"),
    path("password_reset/<str:cipher>/", views.password_reset, name="password_reset"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("basic_info",views.basic_info,name="basic_info_form"),
    path("courses/",views.course_details,name="course_details_form"),
    path("guestlecture/",views.guest_lecture,name="guest_lecture_form"),
    path("fdp/", views.fdp_form, name="fdp_form"),
    path("workshop/", views.workshop_form, name="workshop_form"),
    path("conference_chair/", views.conference_chair_form, name="conference_chair_form"),
    path("certifications",views.certifications, name="certifications_form"),
    path("conferences",views.conferences,name="conferences_form"),
    path("journals",views.journals,name="journals_form"),
    path("books",views.books,name="books_form"),
    path("patents",views.patents,name="patents_form"),
    path("responsibility",views.responsibilities,name="responsibilities"),
    path("query_data/", views.query_data, name="query_data"),
    path("profile_viewer/<str:faculty_id>/",views.profile_viewer,name="profile_viewer"),
    path("download_excel", views.download_excel, name="download_excel"),
    path("download_profile/<str:faculty_id>/", views.download_profile, name="download_profile"),
]
