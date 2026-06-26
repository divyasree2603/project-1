from django.contrib import admin
from .models import UserProfile, StudentDetail, SubjectDetail, AttendenceRecord

# Registering models with your exact spelling choice
admin.site.register(UserProfile)
admin.site.register(StudentDetail)
admin.site.register(SubjectDetail)
admin.site.register(AttendenceRecord)