from django.shortcuts import render,redirect
from .models import Faculty, Certification, ConferencePublication, JournalPublication, BookPublication, Patent, CourseReport, FDP, GuestLecture, Workshop, ConferenceChair
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import pandas as pd
from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpRequest
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from reportlab.lib.styles import getSampleStyleSheet
from typing import List
from cryptography.fernet import Fernet
from urllib.parse import quote, unquote
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from dataManager.settings import EMAIL_HOST_USER
from reportlab.lib.units import inch
import textwrap

# Create your views here.
def compute_summary(department:str, academic_year:(str|None)=None,
                    is_course_needed:bool = True,
                    is_certification_needed:bool = True,
                    is_conferences_needed:bool = True,
                    is_journal_needed:bool = True,
                    is_books_needed:bool = True,
                    is_patents_needed:bool = True,
                    is_guestlectures_needed:bool = True,
                    is_fpd_needed:bool = True,
                    is_workshops_needed:bool = True,
                    is_conferencechairs_needed:bool = True) -> (List[List[str | int]]):
    faculty_data = Faculty.objects.filter(department = department).values()
    required_columns = [is_course_needed, is_certification_needed, is_conferences_needed, is_journal_needed, is_books_needed, is_patents_needed, is_guestlectures_needed, is_fpd_needed, is_workshops_needed, is_conferencechairs_needed]

    summary = []

    for record in faculty_data:
        fid = record["faculty_id"]

        t = []
        t.append([fid, record["name"], academic_year])
        if academic_year:
            if is_course_needed:
                t.append(len(CourseReport.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_certification_needed:
                t.append(len(Certification.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_conferences_needed:
                t.append(len(ConferencePublication.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_journal_needed:
                t.append(len(JournalPublication.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_books_needed:
                t.append(len(BookPublication.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_patents_needed:
                t.append(len(Patent.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_guestlectures_needed:
                t.append(len(GuestLecture.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_fpd_needed:
                t.append(len(FDP.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_workshops_needed:
                t.append(len(Workshop.objects.filter(faculty_id = fid, academic_year = academic_year)))
            if is_conferencechairs_needed:
                t.append(len(ConferenceChair.objects.filter(faculty_id = fid, academic_year = academic_year)))
        else:
            if is_course_needed:
                t.append(len(CourseReport.objects.filter(faculty_id = fid)))
            if is_certification_needed:
                t.append(len(Certification.objects.filter(faculty_id = fid)))
            if is_conferences_needed:
                t.append(len(ConferencePublication.objects.filter(faculty_id = fid)))
            if is_journal_needed:
                t.append(len(JournalPublication.objects.filter(faculty_id = fid)))
            if is_books_needed:
                t.append(len(BookPublication.objects.filter(faculty_id = fid)))
            if is_patents_needed:
                t.append(len(Patent.objects.filter(faculty_id = fid)))
            if is_guestlectures_needed:
                t.append(len(GuestLecture.objects.filter(faculty_id = fid)))
            if is_fpd_needed:
                t.append(len(FDP.objects.filter(faculty_id = fid)))
            if is_workshops_needed:
                t.append(len(Workshop.objects.filter(faculty_id = fid)))
            if is_conferencechairs_needed:
                t.append(len(ConferenceChair.objects.filter(faculty_id = fid)))

        summary.append(t)
    total_list = [["Total", "Total"]]

    for i in range(required_columns.count(True)):
        total_list.append(sum([record[i + 1] for record in summary]))

    summary.append(total_list)
    
    return (summary, required_columns)

def query_data(request:HttpRequest) -> (HttpRequest):
    faculty_data = Faculty.objects.get(faculty_id = request.session["faculty_id"])
    existing_academic_years = []
    existing_academic_years.extend([ i[0] for i in list(CourseReport.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(Certification.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(ConferencePublication.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(JournalPublication.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(BookPublication.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(Patent.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(GuestLecture.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(FDP.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(Workshop.objects.values_list("academic_year"))])
    existing_academic_years.extend([ i[0] for i in list(ConferenceChair.objects.values_list("academic_year"))])
    existing_academic_years = set(existing_academic_years)
    years_summary_data = {}
    required_years, required_columns, required_deaprtments = [], [], []
    existing_columns = ["ALL", "COURSE_DETAILS", "CERTIFICATION_DETAILS", "CONFERENCE_DETAILS", "JOURNAL_DETAILS", "BOOK_DETAILS", "PATENT_DETAILS", "GUEST_LECTURE_DETAILS", "FDP_DETAILS", "WORKSHOP_DETAILS", "CONFERENCE_CHAIR_DETAILS"]
    # existing_departments = ["ALL", "CSE", "CAI", "ECE", "EEE", "CE", "ME", "MBA", "BSH"]
    if request.method == "POST":
        required_years = dict(request.POST)["academic_years_selector"]
        required_columns = dict(request.POST)["column_names_selector"]
        # required_deaprtments = dict(request.POST)["department_names_selector"]
        if "ALL" in required_columns:
            required_columns = existing_columns
        # if "ALL" in required_deaprtments:
        #     required_deaprtments = existing_departments
        for year in required_years:
            years_summary_data[year] = []
            # for department in required_deaprtments:
            years_summary_data[year].append(compute_summary(faculty_data.department,
                                                            year,
                                                            "COURSE_DETAILS" in required_columns,
                                                            "CERTIFICATION_DETAILS" in required_columns, 
                                                            "CONFERENCE_DETAILS" in required_columns, 
                                                            "JOURNAL_DETAILS" in required_columns, 
                                                            "BOOK_DETAILS" in required_columns, 
                                                            "PATENT_DETAILS" in required_columns, 
                                                            "GUEST_LECTURE_DETAILS" in required_columns, 
                                                            "FDP_DETAILS" in required_columns, 
                                                            "WORKSHOP_DETAILS" in required_columns, 
                                                            "CONFERENCE_CHAIR_DETAILS" in required_columns))
    department_summary_data = compute_summary(faculty_data.department)
    return render(request, "query_data_form.html", {"existing_academic_years":existing_academic_years, "academic_years_summary":years_summary_data, "grand_totals":department_summary_data[0][-1]})

def encrypt_text(request:HttpRequest,text:str) -> (bytes):
    key = Fernet.generate_key().decode('utf-8') if "fernet_key" not in request.session else request.session["fernet_key"]
    cipher_suite = Fernet(key)
    # Encrypt the text
    encrypted_text = cipher_suite.encrypt(text.encode('utf-8'))
    request.session["fernet_key"] = key
    return encrypted_text

def decrypt_text(request:HttpRequest, encrypted_text):
    cipher_suite = Fernet(request.session["fernet_key"])
    decrypted_text = cipher_suite.decrypt(encrypted_text).decode('utf-8')
    return decrypted_text

def password_reset_initiator(request:HttpRequest) -> (HttpResponseRedirect | HttpResponsePermanentRedirect):
    cipher = encrypt_text(request, request.session["faculty_id"])
    cipher = quote(cipher)
    obj = Faculty.objects.get(faculty_id = request.session["faculty_id"])
    email_status = send_mail("Password Reset - Faculty Vault",
                         strip_tags(render_to_string("password_reset_email.html",{'id':obj.faculty_id, 'cipher':cipher})),
                         EMAIL_HOST_USER,
                         [obj.email],
                         fail_silently=False)
    if email_status:
        messages.success(request, "Password Rest eMail sent successfully.")
    else:
        messages.error(request, "Something went wrong!. Please try again later or contact administrator.")
    return redirect(dashboard)

def password_reset(request:HttpRequest, cipher:str) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    cipher = unquote(cipher)
    if decrypt_text(request, cipher) != request.session["faculty_id"]:
        messages.error(request, "Session seems to be expired! Try again later or contact administrator.")
        return redirect(dashboard)
    if request.method == "POST":
        obj = User.objects.get(username=request.session["faculty_id"])
        obj.password = make_password(request.POST["pswd"])
        obj.save()
        messages.success(request, "Password changed successfully!")
        return redirect(dashboard)
    return render(request, "password_reset_form.html")

def login_view(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    '''
    Basically it returns the login page as HttpResponse
    On successful login it will redirect the user to the dashboard.
    '''
    if request.user.is_authenticated:   # If the user is already logged in, redirect to the dashboard
        return redirect('dashboard')
    if request.method == 'POST':
        username = str(request.POST['username']).upper()
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session["faculty_id"]=username
            return redirect('dashboard')  # Replace 'dashboard' with your desired URL
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'index.html')

def logout_view(request:HttpRequest) -> (HttpResponseRedirect | HttpResponsePermanentRedirect):
    logout(request)
    return redirect(login_view)  # Replace 'home' with your desired URL

def register_faculty(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    if request.method == 'POST':
        new_faculty_id = str(request.POST["facultyId"]).upper()
        new_user_name = request.POST["name"]
        new_position = request.POST["position"]
        new_department = request.POST["department"]
        new_contact_number = request.POST["contactNumber"]
        new_email = request.POST["email"]
        new_doj = request.POST["dateOfJoining"]

        obj = Faculty()
        obj.faculty_id = new_faculty_id
        obj.name = new_user_name
        obj.position = new_position
        obj.department = new_department
        obj.contactNumber = new_contact_number
        obj.email = new_email
        obj.date_of_joining = datetime.date(new_doj)
        obj.save()

        user = User(username=new_faculty_id, password=make_password("Vasavi@1234"))
        user.save()
        subject = 'Welcome to FacultyVault'
        context = {'user_name': new_user_name}
        message = render_to_string('welcome_email.html', context)
        plain_message = strip_tags(message)
        from_email = EMAIL_HOST_USER,  # Replace with your email
        to_email = new_email
        send_mail(subject, plain_message, from_email, [to_email], html_message=message)
        messages.success(request, f"Accout successfully created for {new_faculty_id}.")

        return redirect(dashboard)

    return render(request, 'register_form.html',{"faculty_data":faculty_data})

@login_required(login_url='home')
def dashboard(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    certifications_data = Certification.objects.filter(faculty_id=f_ID)
    conferences_data = ConferencePublication.objects.filter(faculty_id=f_ID)
    journals_data = JournalPublication.objects.filter(faculty_id=f_ID)
    books_data = BookPublication.objects.filter(faculty_id=f_ID)
    patents_data = Patent.objects.filter(faculty_id=f_ID)
    courses_data = CourseReport.objects.filter(faculty_id=f_ID)
    fdps_data = FDP.objects.filter(faculty_id=f_ID)
    guest_lectures_data = GuestLecture.objects.filter(faculty_id=f_ID)
    workshops_data = Workshop.objects.filter(faculty_id=f_ID)
    conference_chairs_data = ConferenceChair.objects.filter(faculty_id=f_ID)

    if request.method == "POST":
        required_id = str(request.POST["faculty_search"]).upper()
        try:
            obj = Faculty.objects.get(faculty_id = required_id)
            return redirect('profile_viewer', obj.faculty_id)
        except Exception as e:
            messages.warning(request,"The entered ID does not exist.")
            return redirect(dashboard)
    return render(request,"dashboard.html",{"faculty_data":faculty_data,
                                            "certifications_data":certifications_data,
                                            "conferences_data":conferences_data,
                                            "journals_data":journals_data,
                                            "books_data":books_data,
                                            "patents_data":patents_data,
                                            "courses_data":courses_data,
                                            "fdps_data":fdps_data,
                                            "guest_lectures_data":guest_lectures_data,
                                            "workshops_data":workshops_data,
                                            "conference_chairs_data":conference_chairs_data,
                                            "summary_data": compute_summary(faculty_data.department) if faculty_data.is_hod else None})

def profile_viewer(request:HttpRequest, faculty_id:str) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    if not (request.user.is_superuser or request.user.is_staff):
        messages.warning(request, "You are not supposed to use the requested page...")
        return redirect(dashboard)
    faculty_data = Faculty.objects.get(faculty_id=faculty_id)
    certifications_data = Certification.objects.filter(faculty_id=faculty_id)
    conferences_data = ConferencePublication.objects.filter(faculty_id=faculty_id)
    journals_data = JournalPublication.objects.filter(faculty_id=faculty_id)
    books_data = BookPublication.objects.filter(faculty_id=faculty_id)
    patents_data = Patent.objects.filter(faculty_id=faculty_id)
    courses_data = CourseReport.objects.filter(faculty_id=faculty_id)
    fdps_data = FDP.objects.filter(faculty_id=faculty_id)
    guest_lectures_data = GuestLecture.objects.filter(faculty_id=faculty_id)
    workshops_data = Workshop.objects.filter(faculty_id=faculty_id)
    conference_chairs_data = ConferenceChair.objects.filter(faculty_id=faculty_id)
    return render(request,"profile_viewer.html",{"faculty_data":faculty_data,
                                            "certifications_data":certifications_data,
                                            "conferences_data":conferences_data,
                                            "journals_data":journals_data,
                                            "books_data":books_data,
                                            "patents_data":patents_data,
                                            "courses_data":courses_data,
                                            "fdps_data":fdps_data,
                                            "guest_lectures_data":guest_lectures_data,
                                            "workshops_data":workshops_data,
                                            "conference_chairs_data":conference_chairs_data})

@login_required(login_url='home')
def basic_info(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    if request.method == "POST":
        new_name = request.POST["name"]
        new_contact_number = request.POST["contactNumber"]
        new_mail = request.POST["email"]
        faculty_data.name = new_name
        faculty_data.contactNumber = new_contact_number
        faculty_data.email = new_mail
        faculty_data.save()
        return redirect(certifications)
    return render(request,"basic_info_form.html",{"faculty_data":faculty_data})

@login_required(login_url='home')
def course_details(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    courses_data = CourseReport.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = CourseReport(faculty_id = f_ID,
                                   academic_year=request.POST["new_academic_year%d"%(i)],
                                    title_of_course = request.POST["new_title_of_course%d"%(i)],
                                    course_code = request.POST["new_course_code%d"%(i)],
                                    lecture = request.POST["new_lecture%d"%(i)],
                                    tutorial = request.POST["new_tutorial%d"%(i)],
                                    phase_1 = request.POST["new_phase_1%d"%(i)],
                                    phase_2 = request.POST["new_phase_2%d"%(i)],
                                    pass_percentage = request.POST["new_pass_percentage%d"%(i)])
                obj.save()
        else:
            for i in range(len(courses_data)):
                record_id = courses_data[i]["id"]
                obj = CourseReport.objects.get(id=record_id)
                if "title_of_course%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.title_of_course = request.POST["title_of_course%d"%(i)]
                    obj.course_code = request.POST["course_code%d"%(i)]
                    obj.lecture = request.POST["lecture%d"%(i)]
                    obj.tutorial = request.POST["tutorial%d"%(i)]
                    obj.phase_1 = request.POST["phase_1%d"%(i)]
                    obj.phase_2 = request.POST["phase_2%d"%(i)]
                    obj.pass_percentage = request.POST["pass_percentage%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"courses_form.html",{"name":faculty_data.name,"courses_data":courses_data})


@login_required(login_url='home')
def guest_lecture(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    guest_lectures_data = GuestLecture.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = GuestLecture(faculty_id = f_ID,
                                   academic_year=request.POST["new_academic_year%d"%(i)],
                                    name_of_the_guest_lecture = request.POST["new_name_of_the_guest_lecture%d"%(i)],
                                    name_of_the_host_institute = request.POST["new_name_of_the_host_institute%d"%(i)],
                                    from_date = request.POST["new_from_date%d"%(i)],
                                    to_date = request.POST["new_to_date%d"%(i)],
                                    duration = request.POST["new_duration%d"%(i)])
                obj.save()
        else:
            for i in range(len(guest_lectures_data)):
                record_id = guest_lectures_data[i]["id"]
                obj = GuestLecture.objects.get(id=record_id)
                if "name_of_the_guest_lecture%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.name_of_the_guest_lecture = request.POST["name_of_the_guest_lecture%d"%(i)]
                    obj.name_of_the_host_institute = request.POST["name_of_the_host_institute%d"%(i)]
                    obj.from_date = request.POST["from_date%d"%(i)]
                    obj.to_date = request.POST["to_date%d"%(i)]
                    obj.duration = request.POST["duration%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"guest_lecture_form.html",{"name":faculty_data.name,"guestlectures_data":guest_lectures_data})

@login_required(login_url='home')
def fdp_form(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    fdps_data = FDP.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = FDP(faculty_id = f_ID,
                          academic_year=request.POST["academicYear%d"%(i)],
                                    name_of_the_fdp = request.POST["new_name_of_the_fdp%d"%(i)],
                                    name_of_the_institute = request.POST["new_name_of_the_institute%d"%(i)],
                                    from_date = request.POST["new_from_date%d"%(i)],
                                    to_date = request.POST["new_to_date%d"%(i)],
                                    duration = request.POST["new_duration%d"%(i)],
                                    fdp_organized = True if "new_fdp_organized%d"%(i) in request.POST else False)
                obj.save()
        else:
            for i in range(len(fdps_data)):
                record_id = fdps_data[i]["id"]
                obj = FDP.objects.get(id=record_id)
                if "name_of_the_fdp%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.name_of_the_fdp = request.POST["name_of_the_fdp%d"%(i)]
                    obj.name_of_the_institute = request.POST["name_of_the_institute%d"%(i)]
                    obj.from_date = request.POST["from_date%d"%(i)]
                    obj.to_date = request.POST["to_date%d"%(i)]
                    obj.duration = request.POST["duration%d"%(i)]
                    obj.fdp_organized = True if "fdp_organized%d"%(i) in request.POST else False
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"fdp_form.html",{"name":faculty_data.name,"fdps_data":fdps_data})

@login_required(login_url='home')
def workshop_form(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    workshops_data = Workshop.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = Workshop(faculty_id = f_ID,
                               academic_year=request.POST["new_academic_year%d"%(i)],
                                    name_of_the_workshop = request.POST["new_name_of_the_workshop%d"%(i)],
                                    name_of_the_institute = request.POST["new_name_of_the_institute%d"%(i)],
                                    from_date = request.POST["new_from_date%d"%(i)],
                                    to_date = request.POST["new_to_date%d"%(i)],
                                    duration = request.POST["new_duration%d"%(i)],
                                    workshop_organized = True if "new_workshop_organized%d"%(i) in request.POST else False)
                obj.save()
        else:
            for i in range(len(workshops_data)):
                record_id = workshops_data[i]["id"]
                obj = Workshop.objects.get(id=record_id)
                if "name_of_the_workshop%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.name_of_the_workshop = request.POST["name_of_the_workshop%d"%(i)]
                    obj.name_of_the_institute = request.POST["name_of_the_institute%d"%(i)]
                    obj.from_date = request.POST["from_date%d"%(i)]
                    obj.to_date = request.POST["to_date%d"%(i)]
                    obj.duration = request.POST["duration%d"%(i)]
                    obj.workshop_organized = True if "workshop_organized%d"%(i) in request.POST else False
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"workshop_form.html",{"name":faculty_data.name,"workshops_data":workshops_data})

@login_required(login_url='home')
def conference_chair_form(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    conference_chairs_data = ConferenceChair.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = ConferenceChair(faculty_id = f_ID,
                                      academic_year = request.POST["new_academic_year%d"%(i)],
                                    title_of_the_conference = request.POST["new_title_of_the_conference%d"%(i)],
                                    duration = request.POST["new_duration%d"%(i)])
                obj.save()
        else:
            for i in range(len(conference_chairs_data)):
                record_id = conference_chairs_data[i]["id"]
                obj = ConferenceChair.objects.get(id=record_id)
                if "title_of_the_conference%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.title_of_the_conference = request.POST["title_of_the_conference%d"%(i)]
                    obj.duration = request.POST["duration%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"conference_chair_form.html",{"name":faculty_data.name,"conference_chairs_data":conference_chairs_data})

@login_required(login_url='home')
def certifications(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    certifications_data = Certification.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = Certification(faculty_id = f_ID,
                                    academic_year= request.POST["new_academic_year%d"%(i)],
                                    name_of_certification = request.POST["new_certificate_name%d"%(i)],
                                    certification_authority = request.POST["new_certification_authority%d"%(i)],
                                    date = request.POST["new_date%d"%(i)],
                                    url = request.POST["new_url%d"%(i)])
                obj.save()
        else:
            for i in range(len(certifications_data)):
                record_id = certifications_data[i]["id"]
                obj = Certification.objects.get(id=record_id)
                if "certificate_name%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.name_of_certification = request.POST["certificate_name%d"%(i)]
                    obj.certification_authority = request.POST["certification_authority%d"%(i)]
                    obj.date = request.POST["date%d"%(i)]
                    obj.url = request.POST["url%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"certifications_form.html",{"name":faculty_data.name,"certifications_data":certifications_data})

@login_required(login_url='home')
def conferences(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    conference_data = ConferencePublication.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = ConferencePublication(faculty_id = f_ID,
                                            academic_year=request.POST["new_academic_year%d"%(i)],
                                    name_of_conference_attended = request.POST["new_conference_name%d"%(i)],
                                    paper_entitled = request.POST["new_paper_entitled%d"%(i)],
                                    from_date = request.POST["new_from_date%d"%(i)],
                                    to_date = request.POST["new_to_date%d"%(i)],
                                    url = request.POST["new_url%d"%(i)])
                obj.save()
        else:
            for i in range(len(conference_data)):
                record_id = conference_data[i]["id"]
                obj = ConferencePublication.objects.get(id=record_id)
                if "conference_name%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.name_of_conference_attended = request.POST["conference_name%d"%(i)]
                    obj.paper_entitled = request.POST["paper_entitled%d"%(i)]
                    obj.from_date = request.POST["from_date%d"%(i)]
                    obj.to_date = request.POST["to_date%d"%(i)]
                    obj.url = request.POST["url%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"conferences_form.html",{"name":faculty_data.name,"conference_data":conference_data})

@login_required(login_url='home')
def journals(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    journals_data = JournalPublication.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = JournalPublication(faculty_id = f_ID,
                                         academic_year=request.POST["new_academic_year%d"%(i)],
                                         title_of_publication = request.POST["new_publication_name%d"%(i)],
                                    name_of_journal = request.POST["new_journal_name%d"%(i)],
                                    date_published = request.POST["new_date%d"%(i)],
                                    url = request.POST["new_url%d"%(i)])
                obj.save()
        else:
            for i in range(len(journals_data)):
                record_id = journals_data[i]["id"]
                obj = JournalPublication.objects.get(id=record_id)
                if "publication_name%d"%(i) in request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.title_of_publication = request.POST["publication_name%d"%(i)]
                    obj.name_of_journal = request.POST["journal_name%d"%(i)]
                    obj.date_published = request.POST["date%d"%(i)]
                    obj.url = request.POST["url%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"journals_form.html",{"name":faculty_data.name,"journals_data":journals_data})

@login_required(login_url='home')
def books(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    books_data = BookPublication.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = BookPublication(faculty_id = f_ID,
                                      academic_year = request.POST["new_academic_year%d"%(i)],
                                    title_of_book = request.POST["new_book_title%d"%(i)],
                                    issbn = request.POST["new_issbn%d"%(i)],
                                    date_published = request.POST["new_date%d"%(i)],
                                    doi_link = request.POST["new_url%d"%(i)])
                obj.save()
        else:
            for i in range(len(books_data)):
                record_id = books_data[i]["id"]
                obj = BookPublication.objects.get(id=record_id)
                if request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.title_of_book = request.POST["book_title%d"%(i)]
                    obj.issbn = request.POST["issbn%d"%(i)]
                    obj.date_published = request.POST["date%d"%(i)]
                    obj.doi_link = request.POST["url%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"books_form.html",{"name":faculty_data.name,"books_data":books_data})

@login_required(login_url='home')
def patents(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)
    patents_data = Patent.objects.filter(faculty_id=f_ID).values()
    if request.method == "POST":
        no_of_new_records = int(request.POST["newRecordsCounter"])
        if no_of_new_records:
            for i in range(1, no_of_new_records + 1):
                obj = Patent(faculty_id = f_ID,
                             academic_year=request.POST["new_academic_year%d"%(i)],
                                    title_of_innovation = request.POST["new_innovation_title%d"%(i)],
                                    application_no = request.POST["new_application_number%d"%(i)],
                                    date = request.POST["new_date%d"%(i)],
                                    url = request.POST["new_url%d"%(i)])
                obj.save()
        else:
            for i in range(len(patents_data)):
                record_id = patents_data[i]["id"]
                obj = Patent.objects.get(id=record_id)
                if request.POST:
                    obj.academic_year = request.POST["academic_year%d"%(i)]
                    obj.title_of_innovation = request.POST["innovation_title%d"%(i)]
                    obj.application_no = request.POST["application_number%d"%(i)]
                    obj.date = request.POST["date%d"%(i)]
                    obj.url = request.POST["url%d"%(i)]
                    obj.save()
                else:
                    obj.delete()
        return redirect(dashboard)
    return render(request,"patents_form.html",{"name":faculty_data.name,"patents_data":patents_data})

@login_required(login_url='home')
def responsibilities(request:HttpRequest) -> (HttpResponse | HttpResponseRedirect | HttpResponsePermanentRedirect):
    f_ID = request.session["faculty_id"]
    faculty_data = Faculty.objects.get(faculty_id=f_ID)

    if request.method == "POST":
        # Assuming you have added 'dept_res' and 'college_res' fields in the form
        department_responsibilities = request.POST.get('dept_res', '')
        college_responsibilities = request.POST.get('college_res', '')

        # Update the Faculty model with the new responsibilities
        faculty_data.department_level = department_responsibilities
        faculty_data.college_level = college_responsibilities
        faculty_data.save()
        
        return redirect(dashboard)
    return render(request,"responsibilities_form.html", {'record': faculty_data})

def download_excel(request:HttpRequest) -> (HttpResponse):
    faculty_data = list(Faculty.objects.all().values())
    certificates_data = list(Certification.objects.all().values())
    conferences_data = list(ConferencePublication.objects.all().values())
    journals_data = list(JournalPublication.objects.all().values())
    books_data = list(BookPublication.objects.all().values())
    patents_data = list(Patent.objects.all().values())
    
    buffer = BytesIO()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        pd.DataFrame(faculty_data).to_excel(writer, sheet_name="Faculty Basic Information", index=False)
        pd.DataFrame(certificates_data).to_excel(writer, sheet_name="Certifications Data", index=False)
        pd.DataFrame(conferences_data).to_excel(writer, sheet_name="Conferences Data", index=False)
        pd.DataFrame(journals_data).to_excel(writer, sheet_name="Journals Data", index=False)
        pd.DataFrame(books_data).to_excel(writer, sheet_name="Books Data", index=False)
        pd.DataFrame(patents_data).to_excel(writer, sheet_name="Patents Data", index=False)
    
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=report_{timestamp}.xlsx'
    return response


def generate_pdf(response:HttpRequest, faculty_data:Faculty, certifications_data:List[Certification], conferences_data:List[ConferencePublication], journals_data:List[JournalPublication], books_data:List[BookPublication], patents_data:List[Patent], courses_data:List[CourseReport], guest_lectures_data:List[GuestLecture], workshops_data:List[Workshop], conference_chairs_data:List[ConferenceChair], fdps_data:List[FDP]) -> (HttpResponse):
    styles = getSampleStyleSheet()
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    content = []
    
    header_text = f"{faculty_data.name}"
    content.append(Paragraph(header_text, styles['Heading1']))

    # Faculty Information
    faculty_info = [
        f"ID: {faculty_data.faculty_id}",
        f"Position: {faculty_data.position}",
        f"Department: {faculty_data.department}",
        f"Contact Number: {faculty_data.contactNumber}",
        f"Email: {faculty_data.email}",
        f"Date of Joining: {faculty_data.date_of_joining}",
    ]
    content.extend([Paragraph(info, styles['Normal']) for info in faculty_info])

    # Course Details
    content.append(Paragraph("Course Details", styles['Heading2']))
    if courses_data:
        courses_table_data = [["A.Y.", "Course Name", "Course Code", "No.of Lecture Hours", "No.of Tutorial Hours", "Feedback(Phase1)", "Feedback(Phase2)", r"Pass % in SEM Exams"]]
        courses_table_data.extend([
            [course.academic_year, course.title_of_course, course.course_code, course.lecture, course.tutorial, course.phase_1, course.phase_2, course.pass_percentage]
            for course in courses_data
        ])
        col_widths = [max(len(str(row[i])) for row in courses_table_data) * 12 for i in range(len(courses_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1 * inch if width > 1 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        courses_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=10))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in courses_table_data
        ]
        courses_table = Table(courses_table_data_wrapped,colWidths=max_col_widths)
        courses_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(courses_table)
    else:
        content.append(Paragraph("No data available for courses.", styles['Normal']))

    # Certifications
        
    content.append(Paragraph("Certifications", styles['Heading2']))
    if certifications_data:
        certifications_table_data = [["A.Y.", "Name Of The Certification", "Certification Authority", "Date Of Issue", "URL Of The Certificate"]]
        certifications_table_data.extend([
            [certification.academic_year, certification.name_of_certification, certification.certification_authority, certification.date, certification.url]
            for certification in certifications_data
        ])
        col_widths = [max(len(str(row[i])) for row in certifications_table_data) * 12 for i in range(len(certifications_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        certifications_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in certifications_table_data
        ]
        certifications_table = Table(certifications_table_data_wrapped, colWidths=max_col_widths)
        certifications_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(certifications_table)
    else:
        content.append(Paragraph("No data available for certifications.", styles['Normal']))
    
    #Conferences
    content.append(Paragraph("Conference", styles['Heading2']))
    if conferences_data:
        conferences_table_data = [["A.Y.", "Name Of The Conference", "Paper Entitled", "Conference Started On", "Conference Ended On", "URL Of The Certificate"]]
        
        conferences_table_data.extend([[
            conference.academic_year,
            conference.name_of_conference_attended,
            conference.paper_entitled,
            conference.from_date,
            conference.to_date,
            conference.url
        ]
            for conference in conferences_data
        ])

        # Calculate column widths dynamically
        col_widths = [max(len(str(row[i])) for row in conferences_table_data) * 12 for i in range(len(conferences_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        conferences_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in conferences_table_data
        ]

        # Create the table with manual line breaks
        conferences_table = Table(conferences_table_data_wrapped, colWidths=max_col_widths)
        conferences_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        content.append(conferences_table)
    else:
        content.append(Paragraph("No data available for conferences.", styles['Normal']))
    
    #Journals
    content.append(Paragraph("Journal Publications", styles['Heading2']))
    if journals_data:
        journals_table_data = [["A.Y.", "Name Of The Journal", "Title Of The Publication", "Date Of Issue", "URL Of The Certificate"]]
        journals_table_data.extend([
            [journal.academic_year, journal.title_of_publication, journal.title_of_publication, journal.date_published, journal.url]
            for journal in journals_data
        ])
        col_widths = [max(len(str(row[i])) for row in journals_table_data) * 12 for i in range(len(journals_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        journals_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in journals_table_data
        ]
        journals_table = Table(journals_table_data_wrapped, colWidths=max_col_widths)
        journals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(journals_table)
    else:
        content.append(Paragraph("No data available for journals.", styles['Normal']))

    #Books
    content.append(Paragraph("Book Publications", styles['Heading2']))
    if books_data:
        books_table_data = [["A.Y.", "Name Of The Book", "ISSBN", "Published Date", "DOI Link"]]
        books_table_data.extend([
            [book.academic_year, book.title_of_book, book.issbn, book.date_published, book.doi_link]
            for book in books_data
        ])
        col_widths = [max(len(str(row[i])) for row in books_table_data) * 12 for i in range(len(books_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        books_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in books_table_data
        ]
        books_table = Table(books_table_data_wrapped,colWidths=max_col_widths)
        books_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(books_table)
    else:
        content.append(Paragraph("No data available for books.", styles['Normal']))
    
    #Patents
    content.append(Paragraph("Patents", styles['Heading2']))
    if patents_data:
        patents_table_data = [["A.Y.", "Title Of The Innovation", "Application Number", "Date Of Issue", "URL Of The Certificate"]]
        patents_table_data.extend([
            [patent.academic_year, patent.title_of_innovation, patent.application_no, patent.date, patent.url]
            for patent in patents_data
        ])
        col_widths = [max(len(str(row[i])) for row in patents_table_data) * 12 for i in range(len(patents_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        patents_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in patents_table_data
        ]
        patents_table = Table(patents_table_data_wrapped,colWidths=max_col_widths)
        patents_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(patents_table)
    else:
        content.append(Paragraph("No data available for patents.", styles['Normal']))
    
    #Guest Lectures
    content.append(Paragraph("Guest Lectures", styles['Heading2']))
    if guest_lectures_data:
        guest_lectures_table_data = [["A.Y.", "Name Of The Guest Lecture", "Host Institution Name", "Started On", "Ended On", "Duration"]]
        guest_lectures_table_data.extend([
            [guest_lecture.academic_year, guest_lecture.name_of_the_guest_lecture, guest_lecture.name_of_the_host_institute, guest_lecture.from_date, guest_lecture.to_date, guest_lecture.duration]
            for guest_lecture in guest_lectures_data
        ])
        col_widths = [max(len(str(row[i])) for row in guest_lectures_table_data) * 12 for i in range(len( guest_lectures_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        guest_lectures_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in  guest_lectures_table_data
        ]
        guest_lectures_table = Table(guest_lectures_table_data_wrapped, colWidths=max_col_widths)
        guest_lectures_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(guest_lectures_table)
    else:
        content.append(Paragraph("No data available for guest lectures.", styles['Normal']))
    
    #FDP
    content.append(Paragraph("Faculty Development Programmes", styles['Heading2']))
    if fdps_data:
        fdps_table_data = [["A.Y.", "Name Of The FDP", "Host Institution Name", "Started On", "Ended On", "Duration", "Organized/Attended"]]
        fdps_table_data.extend([
            [fdp.academic_year, fdp.name_of_the_fdp, fdp.name_of_the_institute, fdp.from_date, fdp.to_date, fdp.duration, "Organized" if fdp.fdp_organized else "Attended"]
            for fdp in fdps_data
        ])
        col_widths = [max(len(str(row[i])) for row in fdps_table_data) * 12 for i in range(len(fdps_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.1 * inch if width > 1.1 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        fdps_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in fdps_table_data
        ]
        fdps_table = Table(fdps_table_data_wrapped,colWidths=max_col_widths)
        fdps_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(fdps_table)
    else:
        content.append(Paragraph("No data available for Faculty Development Programmes.", styles['Normal']))
    
    #Workshops
    content.append(Paragraph("Workshops", styles['Heading2']))
    if workshops_data:
        workshops_table_data = [["A.Y.", "Name Of The Workshop", "Host Institution Name", "Started On", "Ended On", "Duration", "Organized/Attended"]]
        workshops_table_data.extend([
            [workshop.academic_year, workshop.name_of_the_workshop, workshop.name_of_the_institute, workshop.from_date, workshop.to_date, workshop.duration, "Organized" if workshop.workshop_organized else "Attended"]
            for workshop in workshops_data
        ])
        col_widths = [max(len(str(row[i])) for row in workshops_table_data) * 12 for i in range(len(workshops_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.1 * inch if width > 1.1 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        workshops_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in workshops_table_data
        ]
        workshops_table = Table(workshops_table_data_wrapped,colWidths=max_col_widths)
        workshops_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(workshops_table)
    else:
        content.append(Paragraph("No data available for workshops.", styles['Normal']))
    
    #Conference Chair
    content.append(Paragraph("Conference Chair", styles['Heading2']))
    if conference_chairs_data:
        conference_chairs_table_data = [["A.Y.","Name Of The Conference", "Duration"]]
        conference_chairs_table_data.extend([
            [conference_chair.academic_year, conference_chair.title_of_the_conference, conference_chair.duration]
            for conference_chair in conference_chairs_data
        ])
        col_widths = [max(len(str(row[i])) for row in conference_chairs_table_data) * 12 for i in range(len(conference_chairs_table_data[0]))]

        # Set maximum column widths
        max_col_widths = [1.2 * inch if width > 1.2 * inch else width for width in col_widths]

        # Create a new list to store the modified data with manual line breaks
        conference_chairs_table_data_wrapped = [
            [
                '\n'.join(textwrap.wrap(str(cell), width=15))  # Adjust the width parameter as needed
                for cell in row
            ]
            for row in conference_chairs_table_data
        ]
        conference_chairs_table = Table(conference_chairs_table_data_wrapped,colWidths=max_col_widths)
        conference_chairs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        content.append(conference_chairs_table)
    else:
        content.append(Paragraph("No data available for conference chairs.", styles['Normal']))

    pdf.build(content)
    buffer.seek(0)
    response.write(buffer.getvalue())

    return response


def download_profile(request:HttpRequest, faculty_id:str) -> (HttpResponse):
    try:
        faculty_data = Faculty.objects.get(faculty_id=faculty_id)
    except Exception:
        faculty_data = None

    certificates_data = Certification.objects.filter(faculty_id=faculty_id)
    conferences_data = ConferencePublication.objects.filter(faculty_id=faculty_id)
    books_data = BookPublication.objects.filter(faculty_id=faculty_id)
    patents_data = Patent.objects.filter(faculty_id=faculty_id)
    journals_data = JournalPublication.objects.filter(faculty_id=faculty_id)
    courses_data = CourseReport.objects.filter(faculty_id=faculty_id)
    fdps_data = FDP.objects.filter(faculty_id=faculty_id)
    guest_lectures_data = GuestLecture.objects.filter(faculty_id=faculty_id)
    workshops_data = Workshop.objects.filter(faculty_id=faculty_id)
    conference_chairs_data = ConferenceChair.objects.filter(faculty_id=faculty_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{faculty_data.name}({faculty_id})_faculty_profile.pdf"'

    return generate_pdf(response, faculty_data, certificates_data, conferences_data, journals_data, books_data, patents_data, courses_data, guest_lectures_data, workshops_data, conference_chairs_data, fdps_data)
