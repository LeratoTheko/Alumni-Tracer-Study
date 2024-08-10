from django.db import models
from django.contrib.auth.models import User


class GraduatedStudent(models.Model):
    names = models.CharField(max_length=200, blank=False)
    faculty = models.CharField(max_length=6, blank=False)
    course = models.CharField(max_length=200, blank=False)
    student_number = models.CharField(max_length=9, blank=False, primary_key=True)
    graduation_year = models.CharField(max_length=4, blank=False)

    def __str__(self):
        return self.names


class EmploymentAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    student_number = models.CharField(max_length=9, blank=False, primary_key=True)
    faculty = models.CharField(max_length=50, blank=True)
    course = models.CharField(max_length=200, blank=False)
    graduation_year = models.CharField(max_length=4, blank=False)
    employment_status = models.CharField(max_length=100, blank=False)
    company_name = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    contacts = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.student_number


class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, default=1)
    names = models.CharField(max_length=200)
    student_number = models.CharField(max_length=9, unique=True)
    faculty = models.CharField(max_length=6, )
    course = models.CharField(max_length=100)
    graduation_year = models.CharField(max_length=4)
    password = models.CharField(max_length=128)


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,
                                        null=True)  # Define the profile picture field


class StudentsSurvey(models.Model):
    ARE_SATISFIED_CHOICES = [
        ('Satisfied', 'Satisfied'),
        ('I am not Satisfied', 'I am not Satisfied'),
        ('I am not sure', 'I am not sure'),
    ]

    COURSES_CHOICES = [
        ('DEGREE IN SOFTWARE ENGINEERING & MULTIMEDIA', 'DEGREE IN SOFTWARE ENGINEERING & MULTIMEDIA'),
        ('DEGREE IN BUSINESS INFORMATION TECHNOLOGY', 'DEGREE IN BUSINESS INFORMATION TECHNOLOGY'),
        ('DEGREE IN INFORMATION TECHNOLOGY', 'DEGREE IN INFORMATION TECHNOLOGY'),
        ('DEGREE IN FASHION & APPAREL DESIGN', 'DEGREE IN FASHION & APPAREL DESIGN'),
        ('DEGREE IN CREATIVE ADVERTISING', 'DEGREE IN CREATIVE ADVERTISING'),
        ('DEGREE IN GRAPHIC DESIGN', 'DEGREE IN GRAPHIC DESIGN'),
        ('DEGREE IN HOTEL MANAGEMENT', 'DEGREE IN HOTEL MANAGEMENT'),
        ('DEGREE IN TOURISM MANAGEMENT', 'DEGREE IN TOURISM MANAGEMENT'),
        ('DEGREE IN INTERNATIONAL TOURISM', 'DEGREE IN INTERNATIONAL TOURISM'),

    ]

    REASON = [
        ('Career Advancement', 'Career Advancement'),
        ('Personal Interest', 'Personal Interest'),
        ('To acquire new skills', 'To acquire new skills'),
        ('Others', 'Others'),
    ]

    RATINGS = [
        ('Very Poor', 'Very Poor'),
        ('Poor', 'Poor'),
        ('Average', 'Average'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ]

    DEGREE_LEVEL = [
        ('Bachelor1`s Degree', 'Bachelor1`s Degree'),
        ('Bachelor of Arts', 'Bachelor of Arts'),
        ('Associate Degree', 'Associate Degree'),
        ('TVET', 'TVET'),
    ]

    GENDER = [
        ('Male', 'Male',),
        ('Female', 'Female')
    ]

    FACULTY = [
        ('FDI', 'FDI'),
        ('FICT', 'FICT'),
        ('FCTH', 'FCTH'),
        ('FCMB', 'FCMB'),
    ]

    PROGRAM_SATISFACTION = [
        ('Very satisfied', 'Very satisfied'),
        ('Somewhat satisfied', 'Somewhat satisfied'),
        ('Neutral', 'Neutral'),
        ('Somewhat dissatisfied', 'Somewhat dissatisfied'),
        ('Very dissatisfied', 'Very dissatisfied')
    ]

    FACULTY_KNOWLEDGE = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor')
    ]

    ACADEMIC_ADVISORS = [
        ('Very helpful', 'Very helpful'),
        ('Somewhat helpful', 'Somewhat helpful'),
        ('Neutral', 'Neutral'),
        ('Somewhat unhelpful', 'Somewhat unhelpful'),
        ('Very unhelpful', 'Very unhelpful')
    ]

    CURRICULUM = [
        ('Very satisfied', 'Very satisfied'),
        ('Somewhat satisfied', 'Somewhat satisfied'),
        ('Neutral', 'Neutral'),
        ('Somewhat dissatisfied', 'Somewhat dissatisfied'),
        ('Very dissatisfied', 'Very dissatisfied')
    ]

    CAMPUS_FACILITIES = [
        ('Very satisfied', 'Very satisfied'),
        ('Somewhat satisfied', 'Somewhat satisfied'),
        ('Neutral', 'Neutral'),
        ('Somewhat dissatisfied', 'Somewhat dissatisfied'),
        ('Very dissatisfied', 'Very dissatisfied')
    ]

    PROGRAM_SUPPORT = [
        ('Very well', 'Very well'),
        ('Somewhat well', 'Somewhat well'),
        ('Neutral', 'Neutral'),
        ('Somewhat poorly', 'Somewhat poorly'),
        ('Very poorly', 'Very poorly')
    ]

    faculty = models.CharField(max_length=6, choices=FACULTY)
    degree_level = models.CharField(max_length=100, choices=DEGREE_LEVEL)
    course = models.CharField(max_length=100, choices=COURSES_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER)
    reason = models.CharField(max_length=100, choices=REASON)
    program_satisfaction = models.CharField(max_length=100, choices=PROGRAM_SATISFACTION)
    faculty_knowledge = models.CharField(max_length=100, choices=FACULTY_KNOWLEDGE)
    curriculum_satisfaction = models.CharField(max_length=100, choices=CURRICULUM)
    academic_advisors = models.CharField(max_length=100, choices=ACADEMIC_ADVISORS)
    campus_facilities_satisfaction = models.CharField(max_length=100, choices=CAMPUS_FACILITIES)
    extracurricular = models.CharField(max_length=100, choices=CAMPUS_FACILITIES)
    program_support = models.CharField(max_length=100, choices=PROGRAM_SUPPORT)
    career_goals = models.CharField(max_length=100, choices=PROGRAM_SUPPORT)
    career_services = models.CharField(max_length=100, choices=COURSES_CHOICES)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.faculty} - {self.course} - {self.gender}"


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_description = models.TextField()
    company_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    address = models.TextField()
    is_approved = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='employer_profile_pictures/', blank=True, null=True)
    cover_picture = models.ImageField(upload_to='employer_cover_pictures/', blank=True, null=True)

    def __str__(self):
        return self.company_name


class JobPosting(models.Model):
    WORKPLACE_TYPE_CHOICES = [
        ('On-site', 'On-site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]

    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary'),
        ('Internship', 'Internship'),
    ]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='job_postings')
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    workplace_type = models.CharField(max_length=50, choices=WORKPLACE_TYPE_CHOICES)
    job_location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    description = models.TextField()
    skills = models.TextField()
    deadline = models.DateField(null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_title


class InternshipPosting(models.Model):
    WORKPLACE_TYPE_CHOICES = [
        ('On-site', 'On-site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]

    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary'),
        ('Internship', 'Internship'),
    ]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, null=True)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    workplace_type = models.CharField(max_length=50, choices=WORKPLACE_TYPE_CHOICES)
    job_location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    description = models.TextField()
    skills = models.TextField()
    deadline = models.DateField(null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_title


class ProfessionalDetails(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('unemployed', 'Unemployed'),
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('studying', 'Studying'),
        ('self_employed_employed', 'Self Employed and Employed'),
        ('employed_studying', 'Employed and Studying'),
        ('self_employed_studying', 'Self Employed and Studying'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employment_status = models.CharField(max_length=100, choices=EMPLOYMENT_STATUS_CHOICES)
    skills = models.CharField(max_length=100, blank=False, null=False)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    job_position = models.CharField(max_length=100, blank=True, null=True)
    duration_in_company = models.CharField(max_length=100, blank=True, null=True)
    is_related_to_profession = models.BooleanField(default=False)
    started_length = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    contacts = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    cover_picture = models.ImageField(upload_to='cover_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class InternshipApplication(models.Model):
    internship = models.ForeignKey(InternshipPosting, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    major = models.CharField(max_length=255)
    gpa = models.FloatField()
    previous_internships = models.TextField()
    skills = models.TextField()
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')

    def __str__(self):
        return self.full_name + ' - ' + self.email


class Student(models.Model):
    names = models.CharField(max_length=100, blank=False, null=False)
    student_number = models.CharField(max_length=9, unique=True, primary_key=True, blank=False, null=False)
    faculty = models.CharField(max_length=6, blank=False, null=False)
    course = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=22, blank=True)

    def __str__(self):
        return self.username


class Survey(models.Model):
    TARGET_AUDIENCE_CHOICES = [
        ('students', 'Students'),
        ('alumni', 'Alumni'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE_CHOICES)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('short-answer', 'Short answer'),
        ('paragraph', 'Paragraph'),
        ('multiple-choice', 'Multiple choice'),
        ('checkboxes', 'Checkboxes'),
        ('dropdown', 'Dropdown'),
    ]

    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
