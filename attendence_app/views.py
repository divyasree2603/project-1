import csv
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import UserProfile, StudentDetail, SubjectDetail, AttendenceRecord

# 1. LANDING WELCOME PAGE VIEW
def welcome_page(request):
    return render(request, 'welcome.html')


# 2. MULTI-ROLE LOGIN AUTHENTICATION VIEW
def user_login(request):
    error = None
    selected_role = request.GET.get('role', 'student') 
    
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(username=u_name, password=p_word)
        
        if user is not None:
            login(request, user)
            profile = UserProfile.objects.get(user=user)
            
            if profile.role == 'faculty':
                return redirect('faculty_dashboard')
            elif profile.role == 'student':
                return redirect('student_dashboard')
            elif profile.role == 'admin':
                return redirect('/admin')
        else:
            error = "Invalid Username or Password!"
            
    return render(request, 'login.html', {'error': error, 'role': selected_role})


# 3. FACULTY DASHBOARD MAIN PORTAL VIEW
@login_required
def faculty_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'faculty':
        return redirect('login')
        
    subjects = SubjectDetail.objects.filter(faculty=request.user)
    students = StudentDetail.objects.all()
    return render(request, 'faculty_dashboard.html', {
        'subjects': subjects,
        'students': students,
        'today_date': date.today().strftime('%Y-%m-%d')
    })


# 4. MARK AND SAVE ATTENDENCE VIEW (NO EMAIL ENGINE)
@login_required
def mark_attendence(request):
    if request.method == "POST":
        sub_id = request.POST.get('subject_id')
        lecture_hour = request.POST.get('hour')
        chosen_date = request.POST.get('date')
        present_student_ids = request.POST.getlist('student_present')
        
        subject = SubjectDetail.objects.get(id=sub_id)
        all_students = StudentDetail.objects.all()
        
        for student in all_students:
            status_value = 'Present' if str(student.id) in present_student_ids else 'Absent'
            
            # Save or update database entry logs safely
            AttendenceRecord.objects.update_or_create(
                student=student,
                subject=subject,
                date=chosen_date,
                hour=lecture_hour,
                defaults={'status': status_value}
            )
                    
    return redirect('faculty_dashboard')


# 5. EXCEL SHEET (.CSV) REPORT DOWNLOADER VIEW
@login_required
def export_attendence_csv(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'faculty':
        return redirect('login')
        
    # Prepare spreadsheet configuration response headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Faculty_Attendence_Report.csv"'
    
    writer = csv.writer(response)
    # Excel Column Headers
    writer.writerow(['Roll Number', 'Student Name', 'Subject Name', 'Date', 'Lecture Hour', 'Status'])
    
    my_subjects = SubjectDetail.objects.filter(faculty=request.user)
    records = AttendenceRecord.objects.filter(subject__in=my_subjects).order_by('-date')
    
    for row in records:
        writer.writerow([
            row.student.roll_number,
            row.student.user_profile.user.get_full_name(),
            row.subject.subject_name,
            row.date,
            row.hour,
            row.status
        ])
        
    return response


# 6. STUDENT PORTFOLIO & ANALYTICS DASHBOARD VIEW
@login_required
def student_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'student':
        return redirect('login')
        
    student_meta = StudentDetail.objects.get(user_profile=profile)
    subjects = SubjectDetail.objects.all()
    analytics_dataset = []
    
    total_present_overall = 0
    total_absent_overall = 0
    
    for sub in subjects:
        total_classes = AttendenceRecord.objects.filter(student=student_meta, subject=sub).count()
        present_classes = AttendenceRecord.objects.filter(student=student_meta, subject=sub, status='Present').count()
        absent_classes = AttendenceRecord.objects.filter(student=student_meta, subject=sub, status='Absent').count()
        
        total_present_overall += present_classes
        total_absent_overall += absent_classes
        
        percentage = round((present_classes / total_classes) * 100, 2) if total_classes > 0 else 0.0
        
        analytics_dataset.append({
            'code': sub.subject_code,
            'name': sub.subject_name,
            'total': total_classes,
            'present': present_classes,
            'percentage': percentage
        })
        
    if total_present_overall == 0 and total_absent_overall == 0:
        total_present_overall = 1 
        
    return render(request, 'student_dashboard.html', {
        'student': student_meta,
        'analytics': analytics_dataset,
        'total_present_overall': total_present_overall,
        'total_absent_overall': total_absent_overall
    })


# 7. LOGOUT SYSTEM VIEW
def user_logout(request):
    logout(request)
    return redirect('welcome')