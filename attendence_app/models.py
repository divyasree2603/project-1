from django.db import models
from django.contrib.auth.models import User

# 1. User Profile extending Django's built-in User model for specific roles
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin/HOD'),
        ('faculty', 'Faculty Member'),
        ('student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# 2. Student Master Details Table
class StudentDetail(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=50, unique=True)
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.user_profile.user.first_name} ({self.roll_number})"

# 3. Course/Subject Details Table
class SubjectDetail(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    faculty = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'userprofile__role': 'faculty'})

    def __str__(self):
        return self.subject_name

# 4. Daily Attendence Tracking Table
class AttendenceRecord(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    student = models.ForeignKey(StudentDetail, on_delete=models.CASCADE)
    subject = models.ForeignKey(SubjectDetail, on_delete=models.CASCADE)
    date = models.DateField()
    hour = models.IntegerField()  # Represents the lecture hour (e.g., 1, 2, 3, etc.)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        # Prevents marking double entry for same student, same subject, same hour on the same day
        unique_together = ('student', 'subject', 'date', 'hour')

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.subject_name} - {self.date} - {self.status}"