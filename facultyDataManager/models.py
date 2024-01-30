from django.db import models

# Create your models here.
class Certification(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    name_of_certification = models.CharField(max_length=255)
    certification_authority = models.CharField(max_length=255)
    date = models.DateField()
    url = models.URLField()

class JournalPublication(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    title_of_publication = models.CharField(max_length=255)
    name_of_journal = models.CharField(max_length=255)
    date_published = models.DateField()
    url = models.URLField()

class ConferencePublication(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    name_of_conference_attended = models.CharField(max_length=255)
    paper_entitled = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    url = models.URLField()

class BookPublication(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    title_of_book = models.CharField(max_length=255)
    issbn = models.CharField(max_length=20)
    date_published = models.DateField()
    doi_link = models.URLField()

class Patent(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    title_of_innovation = models.CharField(max_length=255)
    application_no = models.CharField(max_length=255)
    date = models.DateField()
    url = models.URLField()

class CourseReport(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    title_of_course = models.CharField(max_length=255)
    course_code = models.CharField(max_length=255)
    lecture = models.CharField(max_length=5)
    tutorial = models.CharField(max_length=5)
    phase_1 = models.CharField(max_length=5)
    phase_2 = models.CharField(max_length=5)
    pass_percentage = models.CharField(max_length=10)

class GuestLecture(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    name_of_the_guest_lecture = models.CharField(max_length=255)
    name_of_the_host_institute = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    duration = models.CharField(max_length=20)

class FDP(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    name_of_the_fdp = models.CharField(max_length=255)
    name_of_the_institute = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    duration = models.CharField(max_length=20)
    fdp_organized = models.BooleanField()

class Workshop(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    name_of_the_workshop = models.CharField(max_length=255)
    name_of_the_institute = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    duration = models.CharField(max_length=20)
    workshop_organized = models.BooleanField()

class ConferenceChair(models.Model):
    faculty_id = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=30)
    title_of_the_conference = models.CharField(max_length=255)
    duration = models.CharField(max_length=20)

class Faculty(models.Model):
    faculty_id = models.CharField(max_length=20, primary_key=True)
    academic_year = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    contactNumber = models.CharField(max_length=10)
    email = models.EmailField()
    date_of_joining = models.DateField()
    department_level = models.CharField(max_length=255,default=None)
    college_level = models.CharField(max_length=255,default=None)
    is_hod = models.BooleanField(default=False)


