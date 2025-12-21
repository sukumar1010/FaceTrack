from django.urls import path
from . import views
from .views import LoginView,UserDashboardAPIView,MarkAttendanceAPIView,AdminEnrollUserAPIView,AdminLoginView,AdminLogoutView

import os
urlpatterns = [
    path('',views.loginn,name='show_login'),
    path('login', LoginView.as_view(), name='login'),
    path('home',views.home,name='home'),
    path('usercontent',UserDashboardAPIView.as_view(),name='usercontent'),
    path("logout/", views.logout_view, name="logout"),
    path('update-password',views.update_password_view,name='update-password'),
    
    path('adminLoginPage',views.adminLoginPage,name='adminLoginPage'),
    path('api/adminLogin',AdminLoginView.as_view(),name='adminLogin'),
    path('adminDashboard',views.adminDashboard,name='adminDashboard'),
    path("api/admin/enroll-user", AdminEnrollUserAPIView.as_view(), name="admin_enroll_user"),
    path("admin-logout", AdminLogoutView.as_view(), name="admin_logout"),
    
    path("api/attendance/mark", MarkAttendanceAPIView.as_view(), name="mark_attendance"),




]