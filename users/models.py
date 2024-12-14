from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=[('students', 'Student'), ('lecturers', 'Lecturer')], null=True, blank=True)

    def get_role(self):
        if self.groups.filter(name='Lecturers').exists():
            return 'Lecturer'
        elif self.groups.filter(name='Students').exists():
            return 'Student'
        return 'Unknown Role'

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('student', 'Student'), ('lecturer', 'Lecturer')])

    def __str__(self):
        return self.user.username


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the user model as the lecturer
        on_delete=models.CASCADE,  # Delete courses if the lecturer is deleted
        related_name='taught_courses'  # Reverse relation for users
    )
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title