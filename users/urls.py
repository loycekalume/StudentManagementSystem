from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import logout

from .views import custom_logout

app_name = 'users'

urlpatterns = [
    # General paths
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('enrollment/', views.enrollment, name='enrollment'),
    path('add/', views.add_course, name='add_course'),
    # Course-related paths
    path('courses/', views.course, name='course'),
    path('course/<int:course_id>/', views.course_details, name='course_details'),# List all courses
path('remove_student/<int:course_id>/<int:student_id>/', views.remove_student, name='remove_student'),
     path('create-announcement/', views.create_announcement, name='create_announcement'),
    path('announcement/edit/<int:id>/', views.edit_announcement, name='edit_announcement'),
    path('announcement/delete/<int:id>/', views.delete_announcement, name='delete_announcement'),
    path('delete/<int:pk>/', views.delete_course, name='delete_course'),
    path('course/enroll/<int:course_id>/', views.enroll_in_course, name='enroll_in_course'),
    path('course/unenroll/<int:pk>/', views.unenroll_in_course, name='unenroll_from_course'),  # Update this line

]

# The second block is redundant and can be removed.
