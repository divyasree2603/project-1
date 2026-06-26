from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome'), # This sets the Welcome Page as the main home view
    path('login/', views.user_login, name='login'), # Moved the login screen path down here
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/mark/', views.mark_attendence, name='mark_attendence'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('faculty/export/', views.export_attendence_csv, name='export_csv'),
]