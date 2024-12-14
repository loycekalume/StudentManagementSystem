from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import Course, Announcement
from .forms import CourseForm, UserRegistrationForm, AnnouncementForm
from django.http import Http404

# User Authentication and Registration Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = None  # Set role to None explicitly
            user.save()
            return redirect('login')  # Redirect to login after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user if authentication is successful
            login(request, user)
            return redirect('home')  # Redirect to the home page or another URL
        else:
            # Add an error message if authentication fails
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

# Home and Profile Views
@login_required
def home(request):
    user = request.user
    role = None
    functions = []

    if user.groups.filter(name='lecturers').exists():
        role = "lecturers"
        functions = [
            "View Announcements",
            "Create Announcement",
            "Edit Announcement",
            "Delete Your Announcement",
        ]
    elif user.groups.filter(name='students').exists():
        role = "students"
        functions = ["View Announcements"]

    announcements = Announcement.objects.all().order_by('-created_at')

    context = {
        'role': role,
        'functions': functions,
        'announcements': announcements,
    }
    return render(request, 'home.html', context)


@login_required
def profile(request):
    user = request.user
    groups = user.groups.values_list('name', flat=True)

    # Debugging output to ensure groups are correct
    print(f"User Groups: {groups}")

    # Assign role based on the user's group, only 'lecturers' or 'students'
    if 'lecturers' in groups:
        role = 'lecturers'
    elif 'students' in groups:
        role = 'students'
    else:
        role = None  # No role will be assigned if neither group is found

    # More debugging to ensure role is correctly set
    print(f"Assigned Role: {role}")

    context = {
        'role': role,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }
    return render(request, 'profile.html', context)
# Announcement Views
@login_required
def create_announcement(request):
    if request.user.groups.filter(name='lecturers').exists():
        if request.method == 'POST':
            form = AnnouncementForm(request.POST)
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.creator = request.user
                announcement.save()
                return redirect('home')
        else:
            form = AnnouncementForm()
        return render(request, 'create_announcement.html', {'form': form})
    return redirect('home')

@login_required
def edit_announcement(request, id):
    announcement = get_object_or_404(Announcement, id=id)
    if announcement.creator != request.user:
        return redirect('home')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'edit_announcement.html', {'form': form, 'announcement': announcement})

@login_required
def delete_announcement(request, id):
    announcement = get_object_or_404(Announcement, id=id)
    if announcement.creator != request.user:
        return redirect('home')
    if request.method == 'POST':
        announcement.delete()
        return redirect('home')
    return render(request, 'confirm_delete.html', {'announcement': announcement})

def course(request):
    courses = Course.objects.all()  # Fetch all courses
    return render(request, 'course.html', {'courses': courses})

def enrollment(request):
    # Fetch all courses and prefetch students for optimization
    courses = Course.objects.prefetch_related('students').all()

    # Optionally, pass detailed data for a specific course if needed
    # For demonstration, fetch the first course's details (replace logic as needed)
    course_details = courses.first() if courses.exists() else None

    return render(request, 'enrollment.html', {
        'courses': courses,
        'course_details': course_details,
    })
def custom_logout(request):
    logout(request)
    return redirect('users:login')  # Redirect to the homepage or wherever you want


def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            # Add a success message
            messages.success(request, 'Course added successfully!')
            return redirect('home')  # Redirect to the home page after adding a course
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {'form': form})



def delete_course(request, pk):
    try:
        # Try to get the course, and raise 404 if it doesn't exist
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        # If course doesn't exist, show a 404 or handle it accordingly
        raise Http404("Course does not exist")

    if request.method == 'POST':
        # Delete the course
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('home')  # Redirect to the home page after deleting

    return render(request, 'delete_course.html', {'course': course})


# In your views.py
def unenroll_in_course(request, course_id):
    # Fetch the course using the provided course_id
    course = get_object_or_404(Course, id=course_id)

    # Check if the current user is enrolled in the course
    if request.user in course.students.all():
        course.students.remove(request.user)  # Remove the user from the course's students

    # Add a success message (optional)
    messages.success(request, 'You have successfully unenrolled from the course!')

    # Redirect to the home page after unenrolling
    return redirect('home')  # Adjust this to the appropriate URL name if needed

def courses_list(request):
    courses = Course.objects.all()  # Fetch all courses
    return render(request, 'courses_list.html', {'courses': courses})

def enroll_in_course(request, course_id):
    # Fetch the course using the provided course_id
    course = get_object_or_404(Course, id=course_id)

    # Check if the current user is not already enrolled in the course
    if request.user not in course.students.all():
        course.students.add(request.user)  # Add the user to the course's students
        messages.success(request, 'You have successfully enrolled in the course!')
    else:
        messages.info(request, 'You are already enrolled in this course.')

    # Redirect to home page after enrolling
    return redirect('users:enrollment')


def course_details(request, course_id):
    # Fetch the course based on course_id
    course = get_object_or_404(Course, id=course_id)

    # Pass the course and its students to the template
    return render(request, 'course_details.html', {
        'course': course,
        'students': course.students.all(),
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Course, User  # Adjust based on your user model

def remove_student(request, course_id, student_id):
    # Fetch the course and student
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(User, id=student_id)

    # Check if the student is enrolled in the course
    if student in course.students.all():
        course.students.remove(student)  # Remove the student from the course
        messages.success(request, f"Student {student.username} was removed from the course {course.title}.")
    else:
        messages.warning(request, f"Student {student.username} is not enrolled in the course {course.title}.")

    # Redirect back to the course details page or enrollment page
    return redirect('users:course_details', course_id=course.id)
