from collections import Counter
import logging
import requests
import plotly.graph_objects as go
import plotly.io as pio
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from django.contrib import messages
from django.db import IntegrityError
import plotly.express as px
from django.db.models import Count
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_backends
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from matplotlib import pyplot as plt
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as auth_logout
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.contrib.auth import login as auth_login

import seaborn as sns
import pandas as pd
import io
import base64
import random

from .email import send_job_application_email
from .forms import JobPostingForm, UserLoginForm
from .forms import ProfileUpdateForm
from .forms import EmployerProfileForm
from .forms import InternshipApplicationForm
from .forms import CustomLoginForm
from .forms import StudentsSurveyForm
from .forms import AlumniSearchForm
from .forms import AlumniEmploymentStatus
from .forms import EmployerRegistrationForm
from .forms import InternshipForm
from .forms import AlumniUserCreationForm
from .forms import AlumniVerificationForm
from .forms import AlumniLoginForm
from .forms import ProfessionalDetailsForm
from .forms import ApplyJobForm
from .forms import StudentVerificationForm
from .forms import StudentUserCreationForm

from .models import JobPosting, Student
from .models import GraduatedStudent
from .models import EmploymentAnalysis
from .models import UserProfile
from .models import StudentsSurvey
from .models import Employer
from .models import Survey, Question
from .models import InternshipPosting
from .models import ProfessionalDetails

from django.db.models import Q

User = get_user_model()

logger = logging.getLogger(__name__)


def my_view(request):
    logger.debug('Attempting to reverse URL "name"')
    try:
        url = reverse('name')
        logger.debug(f'Reversed URL: {url}')
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.error(f'Error reversing URL: {e}')


def base(request):
    job_postings = JobPosting.objects.all().order_by('-created_at')[:3]
    internship = InternshipPosting.objects.all().order_by('-created_at')[:3]

    context = {
        'job_postings': job_postings,
        'internship_posting': internship
    }
    return render(request, "alumni/basetemplates/base.html", context)


def welcome(request):
    return render(request, "alumni/basetemplates/intro.html", {})


# user accounts authentication
def signUp(request):
    return render(request, "alumni/authent/account_info.html", {})


def signIn(request):
    return render(request, "alumni/authent/signIn.html", {})


def homepage(request):
    return render(request, "alumni/basetemplates/home.html", {})


def about_us(request):
    return render(request, "alumni/basetemplates/about_us.html", {})


# faculties analysis
def architecture_and_build_environment(request):
    return render(request, "alumni/faculties/AaBE.html", {})


def communication_media_and_broadcasting(request):
    return render(request, "alumni/faculties/CMB.html", {})


def business_and_globalization(request):
    return render(request, "alumni/faculties/BaG.html", {})


def information_communication_and_technology(request):
    return render(request, "alumni/faculties/ICT.html", {})


def creativity_in_tourism_and_hospitality(request):
    return render(request, "alumni/faculties/CTH.html", {})


def innova(request):
    return render(request, "alumni/faculties/IaD.html")


# students page
def prospective_students(request):
    return render(request, "alumni/students/prospective_students.html", {})


def show_ict_analysis(request):
    return render(request, "alumni/basetemplates/about_analysis.html", {})


@login_required
def post_job_view(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.employer = request.user.employer  # Assuming 'employer' is a ForeignKey field in JobPosting model
            job_posting.save()
            return redirect('job_success')
    else:
        form = JobPostingForm()

    return render(request, 'alumni/Job/postjob.html', {'form': form})


def search_alumni(request):
    if request.method == 'POST':
        form = AlumniSearchForm(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            alumni = GraduatedStudent.objects.filter(student_number=student_number)
            return render(request, 'alumni/alum_reg/results.html', {'alumni': alumni})
    else:
        form = AlumniSearchForm()
    return render(request, 'alumni/alum_reg/search.html', {'form': form})


def update_alumni_employment_status(request):
    error_message = None
    if request.method == 'POST':
        form = AlumniEmploymentStatus(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            employment_status = form.cleaned_data['employment_status']
            company_name = form.cleaned_data['company_name']

            # Retrieve associated alumni information
            try:
                alumni = GraduatedStudent.objects.get(student_number=student_number)
                course = alumni.course
                faculty = alumni.faculty
                graduation_year = alumni.graduation_year

                # Update AlumniAnalysis model
                alumni_analysis, _ = EmploymentAnalysis.objects.get_or_create(student_number=student_number)
                alumni_analysis.course = course
                alumni_analysis.faculty = faculty
                alumni_analysis.graduation_year = graduation_year
                alumni_analysis.employment_status = employment_status
                alumni_analysis.company_name = company_name
                alumni_analysis.save()

                return redirect('confirmation')
            except GraduatedStudent.DoesNotExist:
                error_message = f"Alumni with student number {student_number} does not exist."
    else:
        form = AlumniEmploymentStatus()
    return render(request, 'alumni/alum_reg/reg.html', {'form': form})


def registry_confirm(request):
    return render(request, 'alumni/alum_reg/confirm.html', {})


def plot_employment_status(request):
    # Retrieve data from EmploymentAnalysis model
    employment_data = EmploymentAnalysis.objects.all().values_list('employment_status', flat=True)

    # Check if there is any data
    if not employment_data:
        # Render template with error message
        return render(request, 'alumni/plots/no_data.html', {'error_message': 'No data available in the database.'})

    # Create a DataFrame from the retrieved data
    df = pd.DataFrame(employment_data, columns=['EmploymentStatus'])

    # Group the DataFrame by EmploymentStatus and calculate the count of each category
    status_counts = df['EmploymentStatus'].value_counts()

    # Plot the data using Seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(x=status_counts.index, y=status_counts.values, color='skyblue')
    plt.title('Employment Status Distribution')
    plt.xlabel('Employment Status')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode plot image as base64 string
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Close plot to prevent memory leaks
    plt.close()

    return render(request, 'alumni/plots/plot_data.html', {'plot_data': plot_data})


@csrf_exempt
def faculty_of_innovation_design(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FDI"
        )

        if not alumni_data:
            message = f"No employment data available for graduates in {graduation_year} from FDI"
            return render(request, 'alumni/faculties/aid_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])

        plt.xlabel('Program', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Student Counts for Different Programs in {} (FDI)'.format(graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/aid_faculty.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/aid_faculty.html', {})


@csrf_exempt
def innovation_and_design(request):
    if request.method == "POST":
        course = request.POST.get('qualification')
        graduation_year = request.POST.get('graduation_year')

        alumni_data = EmploymentAnalysis.objects.filter(course=course, graduation_year=graduation_year)

        if not alumni_data:
            message = f"No employment data available for {course} graduates in {graduation_year}"
            return render(request, 'alumni/faculties/IaD.html', {'message': message})

        employment_status_list = [alumni.employment_status for alumni in alumni_data]
        employment_status_counts = Counter(employment_status_list)

        labels, counts = zip(*employment_status_counts.items())
        plt.figure(figsize=(10, 10))  # Adjust the figure size as needed

        # Define colors for bars
        num_bars = len(labels)
        colors = [plt.cm.viridis(i / num_bars) for i in range(num_bars)]

        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.xlabel('Employment Status', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Employment Status for {} graduates in {}'.format(course, graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='EMPLOYED').count()
        unemployed_graduates = alumni_data.filter(employment_status='UNEMPLOYED').count()
        self_employed_graduates = alumni_data.filter(employment_status='SELF EMPLOYED').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='EMPLOYED').values_list('company_name', flat=True))
        random.shuffle(employed_companies)
        employed_companies = employed_companies[:3]

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/IaD.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, "alumni/faculties/IaD.html", {})


@csrf_exempt
def business(request):
    if request.method == "POST":
        course = request.POST.get('qualification')
        graduation_year = request.POST.get('graduation_year')
        alumni_data = EmploymentAnalysis.objects.filter(course=course, graduation_year=graduation_year)

        if not alumni_data:
            message = f"No employment data available for {course} graduates in {graduation_year}"
            return render(request, 'alumni/faculties/BaG.html', {'message': message})

        employment_status_list = [alumni.employment_status for alumni in alumni_data]
        employment_status_counts = Counter(employment_status_list)

        labels, counts = zip(*employment_status_counts.items())
        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

        # Define colors for bars
        num_bars = len(labels)
        colors = [plt.cm.viridis(i / num_bars) for i in range(num_bars)]

        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.xlabel('Employment Status', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Employment Status for {} graduates in {}'.format(course, graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='EMPLOYED').count()
        unemployed_graduates = alumni_data.filter(employment_status='UNEMPLOYED').count()
        self_employed_graduates = alumni_data.filter(employment_status='SELF EMPLOYED').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='EMPLOYED').values_list('company_name', flat=True))
        random.shuffle(employed_companies)
        employed_companies = employed_companies[:3]

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/BaG.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/BaG.html', {})


@csrf_exempt
def tourism(request):
    if request.method == "POST":
        course = request.POST.get('qualification')
        graduation_year = request.POST.get('graduation_year')

        alumni_data = EmploymentAnalysis.objects.filter(course=course, graduation_year=graduation_year)

        if not alumni_data:
            message = f"No employment data available for {course} graduates in {graduation_year}"
            return render(request, 'alumni/faculties/CTH.html', {'message': message})

        employment_status_list = [alumni.employment_status for alumni in alumni_data]
        employment_status_counts = Counter(employment_status_list)

        labels, counts = zip(*employment_status_counts.items())
        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

        # Define colors for bars
        num_bars = len(labels)
        colors = [plt.cm.viridis(i / num_bars) for i in range(num_bars)]

        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.xlabel('Employment Status', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Employment Status for {} graduates in {}'.format(course, graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='EMPLOYED').count()
        unemployed_graduates = alumni_data.filter(employment_status='UNEMPLOYED').count()
        self_employed_graduates = alumni_data.filter(employment_status='SELF EMPLOYED').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='EMPLOYED').values_list('company_name', flat=True))
        random.shuffle(employed_companies)
        employed_companies = employed_companies[:3]

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/CTH.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/CTH.html', {})


@csrf_exempt
def architecture(request):
    if request.method == "POST":
        course = request.POST.get('qualification')
        graduation_year = request.POST.get('graduation_year')

        alumni_data = EmploymentAnalysis.objects.filter(course=course, graduation_year=graduation_year)

        if not alumni_data:
            message = f"No employment data available for {course} graduates in {graduation_year}"
            return render(request, 'alumni/faculties/AaBE.html', {'message': message})

        employment_status_list = [alumni.employment_status for alumni in alumni_data]
        employment_status_counts = Counter(employment_status_list)

        labels, counts = zip(*employment_status_counts.items())
        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

        # Define colors for bars
        num_bars = len(labels)
        colors = [plt.cm.viridis(i / num_bars) for i in range(num_bars)]

        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.xlabel('Employment Status', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Employment Status for {} graduates in {}'.format(course, graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='EMPLOYED').count()
        unemployed_graduates = alumni_data.filter(employment_status='UNEMPLOYED').count()
        self_employed_graduates = alumni_data.filter(employment_status='SELF EMPLOYED').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='EMPLOYED').values_list('company_name', flat=True))
        random.shuffle(employed_companies)
        employed_companies = employed_companies[:3]

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/AaBE.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/AaBE.html', {})


@csrf_exempt
def media(request):
    if request.method == "POST":
        course = request.POST.get('qualification')
        graduation_year = request.POST.get('graduation_year')

        if course == "ALL ABOVE":
            alumni_data = EmploymentAnalysis.objects.filter(graduation_year=graduation_year)
        else:
            alumni_data = EmploymentAnalysis.objects.filter(course=course, graduation_year=graduation_year)

        if not alumni_data:
            message = f"No employment data available for {course} graduates in {graduation_year}"
            return render(request, 'alumni/faculties/CMB.html', {'message': message})

        employment_status_list = [alumni.employment_status for alumni in alumni_data]
        employment_status_counts = Counter(employment_status_list)

        labels, counts = zip(*employment_status_counts.items())
        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

        # Define colors for bars
        num_bars = len(labels)
        colors = [plt.cm.viridis(i / num_bars) for i in range(num_bars)]

        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.xlabel('Employment Status', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Employment Status for {} graduates in {}'.format(course, graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Annotate bars with percentages
        total_count = sum(counts)
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            percentage = (count / total_count) * 100
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%', ha='center', va='bottom', size=10)

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='EMPLOYED').count()
        unemployed_graduates = alumni_data.filter(employment_status='UNEMPLOYED').count()
        self_employed_graduates = alumni_data.filter(employment_status='SELF EMPLOYED').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='EMPLOYED').values_list('company_name', flat=True))
        random.shuffle(employed_companies)
        employed_companies = employed_companies[:3]

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/CMB.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/CMB.html', {})


@csrf_exempt
def information(request):
    if request.method == "POST":
        course = request.POST.get('qualification')
        graduation_year = request.POST.get('graduation_year')

        if course == "ALL ABOVE":
            alumni_data = EmploymentAnalysis.objects.filter(graduation_year=graduation_year)
        else:
            alumni_data = EmploymentAnalysis.objects.filter(course=course, graduation_year=graduation_year)

        if not alumni_data:
            message = f"No employment data available for {course} graduates in {graduation_year}"
            return render(request, 'alumni/faculties/ICT.html', {'message': message})

        employment_status_list = [alumni.employment_status for alumni in alumni_data]
        employment_status_counts = Counter(employment_status_list)

        labels, counts = zip(*employment_status_counts.items())
        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed

        # Define colors for bars
        num_bars = len(labels)
        colors = [plt.cm.viridis(i / num_bars) for i in range(num_bars)]

        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.xlabel('Employment Status', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Employment Status for {} graduates in {}'.format(course, graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Annotate bars with percentages
        total_count = sum(counts)
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            percentage = (count / total_count) * 100
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%', ha='center', va='bottom')

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='EMPLOYED').count()
        unemployed_graduates = alumni_data.filter(employment_status='UNEMPLOYED').count()
        self_employed_graduates = alumni_data.filter(employment_status='SELF EMPLOYED').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='EMPLOYED').values_list('company_name', flat=True))
        random.shuffle(employed_companies)
        employed_companies = employed_companies[:3]

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/ICT.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/ICT.html', {})


@csrf_exempt
def design_faculty(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FDI"
        )

        if not alumni_data:
            message = f"No employment data available for graduates in {graduation_year} from FDI"
            return render(request, 'alumni/faculties/aid_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])

        plt.xlabel('Program', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Student Counts for Different Programs in {} (FDI)'.format(graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Annotate bars with percentages
        total_count = sum(counts)
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            percentage = (count / total_count) * 100
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%', ha='center', va='bottom')

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/aid_faculty.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/aid_faculty.html', {})


@csrf_exempt
def bag_faculty(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FBG"
        )

        if not alumni_data:
            message = f"No employment data available for graduates in {graduation_year} from FBG"
            return render(request, 'alumni/faculties/BaG_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(12, 9))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])

        plt.xlabel('Program', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Student Counts for Different Programs in {} (FBG)'.format(graduation_year), color='black')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Annotate bars with percentages
        total_count = sum(counts)
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            percentage = (count / total_count) * 100
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%', ha='center', va='bottom')

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/BaG_faculty.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/BaG_faculty.html', {})


@csrf_exempt
def faculty_media(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FCMB"
        )

        if not alumni_data.exists():
            message = f"No employment data available for graduates in {graduation_year} from FCMB"
            return render(request, 'alumni/faculties/cbm_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]

        # Calculate total number of graduates
        total_graduates = sum(counts)

        # Calculate percentages
        percentages = [(count / total_graduates) * 100 for count in counts]
        percentage_texts = [f'{percentage:.1f}%' for percentage in percentages]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        # Create a Plotly bar chart with percentages as text on bars
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=counts,
            marker_color=colors[:len(labels)],
            text=percentage_texts,  # Display percentage on top of each bar
            textposition='outside',  # Position text outside the bars
            width=0.5  # Adjust the width of the bars
        )])

        fig.update_layout(
            title=f'Student Counts for Different Programs in {graduation_year} (FCMB)',
            xaxis_title='Program',
            yaxis_title='Count',
            xaxis_tickangle=-45,
            width=1300,  # Adjust width
            height=900,  # Adjust height
            bargap=0.2  # Adjust gap between bars
        )

        # Convert the plot to HTML
        plot_html = pio.to_html(fig, full_html=False)

        # Retrieve additional summary data
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot and summary data as context
        return render(request, 'alumni/faculties/cbm_faculty.html', {
            'plot_html': plot_html,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/cbm_faculty.html', {})


"""@csrf_exempt
def faculty_inct(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FICT"
        )

        if not alumni_data.exists():
            message = f"No employment data available for graduates in {graduation_year} from FICT"
            return render(request, 'alumni/faculties/ict_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        total_graduates = alumni_data.count()
        course_percentages = {item['course']: (item['count'] / total_graduates) * 100 for item in course_counts}

        df = pd.DataFrame({
            'Course': [item['course'] for item in course_counts],
            'Count': [item['count'] for item in course_counts],
            'Percentage': [course_percentages[item['course']] for item in course_counts]
        })

        fig = px.bar(df, x='Course', y='Count', text='Percentage',
                     title=f'Student Counts for Different Programs in {graduation_year} (FICT)',
                     labels={'Course': 'Program', 'Count': 'Count'},
                     color='Percentage')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)

        # Retrieve summary data
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/ict_faculty.html', {
            'plot_html': plot_html,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/ict_faculty.html', {})"""


@csrf_exempt
def faculty_inct(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FICT"
        )

        if not alumni_data.exists():
            message = f"No employment data available for graduates in {graduation_year} from FICT"
            return render(request, 'alumni/faculties/ict_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        total_graduates = alumni_data.count()
        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]
        percentages = [(count / total_graduates) * 100 for count in counts]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        # Create a Plotly bar chart with percentages as text on bars
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=counts,
            marker_color=colors[:len(labels)],
            text=[f'{percentage:.1f}%' for percentage in percentages],  # Display percentage on top of each bar
            textposition='outside',  # Position text outside the bars
            width=0.5  # Adjust the width of the bars
        )])

        fig.update_layout(
            title=f'Student Counts for Different Programs in {graduation_year} (FICT)',
            xaxis_title='Program',
            yaxis_title='Count',
            xaxis_tickangle=-45,
            width=1300,  # Adjust width
            height=900,  # Adjust height
            bargap=0.2  # Adjust gap between bars
        )

        # Convert the plot to HTML
        plot_html = pio.to_html(fig, full_html=False)

        # Retrieve summary data
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot and summary data as context
        return render(request, 'alumni/faculties/ict_faculty.html', {
            'plot_html': plot_html,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/ict_faculty.html', {})


@csrf_exempt
def faculty_architecture(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FABE"
        )

        if not alumni_data.exists():
            message = f"No employment data available for graduates in {graduation_year} from FABE"
            return render(request, 'alumni/faculties/abe_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        total_graduates = alumni_data.count()
        course_percentages = {item['course']: (item['count'] / total_graduates) * 100 for item in course_counts}

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]
        percentages = [course_percentages[label] for label in labels]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(10, 9))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar and add percentage labels
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])
            plt.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height(), f'{percentages[i]:.1f}%', ha='center',
                     va='bottom', color='black')

        plt.xlabel('Program', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Student Counts for Different Programs in {} (FABE)'.format(graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self_employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as context for the template
        return render(request, 'alumni/faculties/abe_faculty.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/abe_faculty.html', {})


@csrf_exempt
def faculty_aid(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FDI"
        )

        if not alumni_data:
            message = f"No employment data available for graduates in {graduation_year} from FDI"
            return render(request, 'alumni/faculties/aid_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(10, 15))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])

        plt.xlabel('Program', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Student Counts for Different Programs in {} (FDI)'.format(graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/aid_faculty.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/aid_faculty.html', {})


@csrf_exempt
def faculty_FCTH(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and faculty
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty="FCTH"
        )

        if not alumni_data:
            message = f"No employment data available for graduates in {graduation_year} from FCTH"
            return render(request, 'alumni/faculties/cth_faculty.html', {'message': message})

        # Count the number of students for each program
        course_counts = alumni_data.values('course').annotate(count=Count('course')).order_by('course')

        labels = [item['course'] for item in course_counts]
        counts = [item['count'] for item in course_counts]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(10, 9))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])

        plt.xlabel('Program', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title('Student Counts for Different Programs in {} (FCTH)'.format(graduation_year), color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        total_graduates = alumni_data.count()
        employed_graduates = alumni_data.filter(employment_status='employed').count()
        unemployed_graduates = alumni_data.filter(employment_status='unemployed').count()
        self_employed_graduates = alumni_data.filter(employment_status='self-employed').count()

        # Get three random companies for employed graduates
        employed_companies = list(
            alumni_data.filter(employment_status='employed').values_list('company_name', flat=True))
        employed_companies = random.sample(employed_companies, min(3, len(employed_companies)))

        # Return plot image and summary data as JSON response
        return render(request, 'alumni/faculties/cth_faculty.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'employed_graduates': employed_graduates,
            'unemployed_graduates': unemployed_graduates,
            'self_employed_graduates': self_employed_graduates,
            'employed_companies': employed_companies
        })

    return render(request, 'alumni/faculties/cth_faculty.html', {})


@login_required
def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'alumni/profiles/profile.html', {'user_profile': user_profile})


def employers_menu(request):
    employer_group = Group.objects.get(name='Employer')
    if request.user.is_authenticated and employer_group in request.user.groups.all():
        return redirect('employers_dashboard')
    else:
        return redirect(reverse('employers_login'))


@login_required
def employers_dashboard(request):
    return render(request, 'alumni/Job/main.html')


def faculty_cmb(request):
    return render(request, 'alumni/faculties/cbm_faculty.html', {})


def faculty_ict(request):
    return render(request, 'alumni/faculties/ict_faculty.html')


def faculty_cth(request):
    return render(request, 'alumni/faculties/cth_faculty.html')


def faculty_fabe(request):
    return render(request, 'alumni/faculties/abe_faculty.html')


def faculty_fdi(request):
    return render(request, 'alumni/faculties/aid_faculty.html')


def comparison(request):
    if request.method == "POST":
        graduation_year = request.POST.get('graduation_year')

        # Filter alumni data by graduation year and specified faculties
        alumni_data = EmploymentAnalysis.objects.filter(
            graduation_year=graduation_year,
            faculty__in=["FDI", "FICT", "FCMB", "FCTH", "FABE", "FBG"]
        )

        if not alumni_data.exists():
            message = f"No employment data available for graduates in {graduation_year} from the specified faculties"
            return render(request, 'alumni/faculties/comparison.html', {'message': message})

        # Count the number of students for each faculty
        faculty_counts = alumni_data.values('faculty').annotate(count=Count('faculty')).order_by('faculty')

        total_graduates = alumni_data.count()
        faculty_percentages = {item['faculty']: (item['count'] / total_graduates) * 100 for item in faculty_counts}

        labels = [item['faculty'] for item in faculty_counts]
        counts = [item['count'] for item in faculty_counts]
        percentages = [faculty_percentages[label] for label in labels]

        # Define colors for bars
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow']

        plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
        bars = plt.bar(labels, counts, width=0.5, edgecolor='black')  # Adjust the width of the bars

        # Assign different colors to each bar
        for i, bar in enumerate(bars):
            bar.set_color(colors[i % len(colors)])
            plt.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height(), f'{percentages[i]:.1f}%', ha='center',
                     va='bottom', color='black')

        plt.xlabel('Faculty', color='blue')
        plt.ylabel('Count', color='blue')
        plt.title(f'Student Counts for Different Faculties in {graduation_year}', color='blue')
        plt.xticks(rotation=45)  # Rotate x-axis labels if needed
        plt.tight_layout()

        # Convert plot to image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        # Retrieve summary data
        faculty_graduates = {item['faculty']: item['count'] for item in faculty_counts}

        faculty_full_names = {
            'FABE': 'Faculty of Architecture and Building Environment',
            'FDI': 'Faculty of Innovation and Design',
            'FICT': 'Faculty of Information, Communication and Technology',
            'FCMB': 'Faculty of Communication Media and Broadcasting',
            'FCTH': 'Faculty of Creative Tourism and Hospitality',
            'FBG': 'Faculty of Business and Globalization'
        }

        faculty_summary = " ".join(
            [f"{faculty} ({faculty_full_names[faculty]}): {count} graduates ({percentages[labels.index(faculty)]:.1f}%)"
             for faculty, count in
             faculty_graduates.items()])

        # Return plot image and summary data as context for the template
        return render(request, 'alumni/faculties/comparison.html', {
            'plot_image': plot_image,
            'graduation_year': graduation_year,
            'total_graduates': total_graduates,
            'faculty_summary': faculty_summary
        })

    return render(request, 'alumni/faculties/comparison.html', {})


def make_compare(request):
    return render(request, 'alumni/faculties/comparison.html')


def survey_view(request):
    # Check if the device has already submitted the form
    if request.COOKIES.get('has_submitted_survey'):
        return HttpResponseForbidden("You have already submitted the survey.")

    if request.method == 'POST':
        form = StudentsSurveyForm(request.POST)
        if form.is_valid():
            form.save()

            # Set a cookie to track the submission
            response = redirect('survey_thanks')  # Redirect to a thank you page
            response.set_cookie('has_submitted_survey', 'true', max_age=60 * 60 * 24 * 365)  # Cookie expires in 1 year
            return response
    else:
        form = StudentsSurveyForm()

    return render(request, 'alumni/students/survey.html', {'form': form})


def survey_thanks_view(request):
    return render(request, 'alumni/students/survey_thanks.html')


def current_students_form(request):
    # Aggregation by faculty, gender, and satisfaction
    faculty_stats = StudentsSurvey.objects.values('faculty').annotate(
        total=Count('id'),
        #avg_satisfaction=Avg('satisfaction')
    )

    gender_stats = StudentsSurvey.objects.values('gender').annotate(
        total=Count('id'),
        #avg_satisfaction=Avg('satisfaction')
    )

    """satisfaction_stats = StudentsSurvey.objects.values('satisfaction').annotate(
        total=Count('id')
    )"""

    faculty_names = [stat['faculty'] for stat in faculty_stats]
    total_responses = [stat['total'] for stat in faculty_stats]

    # Calculate the overall total responses
    overall_total_responses = sum(total_responses)

    # Create the bar graph
    fig, ax = plt.subplots()
    ax.bar(faculty_names, total_responses, color="skyblue")
    ax.set_xlabel('Faculty')
    ax.set_ylabel('Total Responses')
    ax.set_title('Total Survey Responses by Faculty')

    # Convert the graph to a PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode the image to base64
    graph = base64.b64encode(image_png).decode('utf-8')
    plt.close()

    context = {
        'graph': graph,

        'faculty_stats': faculty_stats,
        'gender_stats': gender_stats,
        #'satisfaction_stats': satisfaction_stats,
        #'overall_total_responses': overall_total_responses,
    }

    return render(request, 'alumni/students/student_analysis.html', context)


def available_job(request):
    if request.user.is_authenticated:
        try:
            employer = Employer.objects.get(user=request.user)
        except Employer.DoesNotExist:
            employer = None

        jobs_by_logged_in_employer = JobPosting.objects.filter(employer=employer).order_by(
            '-created_at') if employer else JobPosting.objects.none()
        jobs_by_other_employers = JobPosting.objects.exclude(employer=employer).order_by(
            '-created_at') if employer else JobPosting.objects.all().order_by('-created_at')
    else:
        jobs_by_logged_in_employer = JobPosting.objects.none()
        jobs_by_other_employers = JobPosting.objects.all().order_by('-created_at')

    context = {
        'jobs_by_logged_in_employer': jobs_by_logged_in_employer,
        'jobs_by_other_employers': jobs_by_other_employers,
    }

    return render(request, "alumni/Job/avaibale_jobs.html", context)


def register_employer(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            employers_group = Group.objects.get(name='Employer')
            user.groups.add(employers_group)

            # Get the backend and log the user in
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user, backend=user.backend)

            return redirect('employers_login')  # Change to your dashboard URL
    else:
        form = EmployerRegistrationForm()
    return render(request, 'alumni/Job/emp_reg.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if the user is in the 'employers' group
                if user.groups.filter(name='Employer').exists():
                    login(request, user)
                    return redirect('employers')  # Change to your dashboard URL
                else:
                    # User is not in the 'employers' group
                    form.add_error(None, "You do not have the required permissions to log in.")
            else:
                # Invalid login credentials
                form.add_error(None, "Invalid username or password")
    else:
        form = CustomLoginForm()
    return render(request, 'alumni/Job/emp_log.html', {'form': form})


# @login_required
def approve_employer(request, employer_id):
    if not request.user.is_staff:  # Ensure only staff can approve
        return redirect('home')  # Change to your home URL

    employer = Employer.objects.get(id=employer_id)
    employer.is_approved = True
    employer.save()
    return redirect('unapproved_employers')  # Change to your list of unapproved employers URL


# @login_required
def unapproved_employers(request):
    if not request.user.is_staff:  # Ensure only staff can view
        return redirect('home')  # Change to your home URL

    unapproved_employers = Employer.objects.filter(is_approved=False)
    return render(request, 'alumni/Job/unapproved.html', {'unapproved_employers': unapproved_employers})


def profile_update(request):
    employer_instance = request.user.employer
    form = ProfileUpdateForm(request.POST, request.FILES, instance=employer_instance,
                             initial={'company_description': employer_instance.company_description,
                                      'contact_phone': employer_instance.contact_phone,
                                      'address': employer_instance.address})
    if form.is_valid():
        form.save()
        return redirect('profile_update_success')
    else:
        employer_instance = request.user.employer
        form = ProfileUpdateForm(initial={'company_description': employer_instance.company_description,
                                          'contact_phone': employer_instance.contact_phone,
                                          'address': employer_instance.address})
    return render(request, 'alumni/Job/profile_update.html', {'form': form})


def profile_update_success(request):
    return render(request, 'alumni/Job/profile_success.html', {})


def employer_list(request):
    employers = Employer.objects.all()
    return render(request, 'alumni/Job/employer_list.html', {'employers': employers})


def view_job(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id)
    return render(request, 'alumni/Job/job_detail.html', {'job_posting': job_posting})


def internship_posting(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('internship_success')
    else:
        form = InternshipForm()

    return render(request, 'alumni/Job/internship_post.html', {'internship_posting': form})


def internship_list(request):
    internship = InternshipPosting.objects.all()

    return render(request, 'alumni/Job/internship_list.html', {'internship_posting': internship})


def internship_success(request):
    return render(request, 'alumni/Job/intern_success.html', )


def make_good(request):
    return render(request, 'career/make_good_first.html', )


def interviews(request):
    return render(request, 'alumni/services/tech.html', )


def verify_alumni(request):
    if request.method == 'POST':
        form = AlumniVerificationForm(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            try:
                graduated_student = GraduatedStudent.objects.get(student_number=student_number)
                request.session['verified_alumni'] = {
                    'student_number': graduated_student.student_number,
                    'first_name': graduated_student.names.split()[0],
                    'last_name': graduated_student.names.split()[-1]
                }
                return redirect('create_user')
            except GraduatedStudent.DoesNotExist:
                form.add_error('student_number', 'Student number not found.')
    else:
        form = AlumniVerificationForm()

    return render(request, 'alumni/alum_reg/verify_alumni.html', {'form': form})


def verify_student(request):
    if request.method == 'POST':
        form = AlumniVerificationForm(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            try:
                current_student = Student.objects.get(student_number=student_number)
                request.session['verified_Student'] = {
                    'student_number': current_student.student_number,
                    'first_name': current_student.names.split()[0],
                    'last_name': current_student.names.split()[-1]
                }
                return redirect('register')  # Ensure 'register' is a valid URL name
            except Student.DoesNotExist:  # Corrected the exception from GraduatedStudent to Student
                form.add_error('student_number', 'Student number not found.')
    else:
        form = AlumniVerificationForm()

    return render(request, 'alumni/students/student_verify.html', {'form': form})


def create_user(request):
    if 'verified_alumni' not in request.session:
        return redirect('verify_alumni')

    initial_data = {
        'first_name': request.session['verified_alumni']['first_name'],
        'last_name': request.session['verified_alumni']['last_name'],
        'username': request.session['verified_alumni']['student_number']
    }

    if request.method == 'POST':
        form = AlumniUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Add user to Alumni group
            group = Group.objects.get(name='Alumni')
            user.groups.add(group)

            # Create ProfessionalDetails instance
            profile_picture = form.cleaned_data.get('profile_picture')
            cover_picture = form.cleaned_data.get('cover_picture')
            ProfessionalDetails.objects.create(
                user=user,
                profile_picture=profile_picture,
                cover_picture=cover_picture
            )

            del request.session['verified_alumni']
            return redirect('success')
    else:
        form = AlumniUserCreationForm(initial=initial_data)

    return render(request, 'alumni/alum_reg/create_user.html', {'form': form})


def success(request):
    return render(request, 'alumni/alum_reg/success.html')


def user_login(request):
    if request.method == 'POST':
        form = AlumniLoginForm(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            password = form.cleaned_data['password']
            user = authenticate(request, username=student_number, password=password)
            if user is not None:
                login(request, user)
                try:
                    # Check if the user has professional details
                    professional_details = ProfessionalDetails.objects.get(user=user)
                    if professional_details.employment_status:
                        # Redirect to alumni portal if employment status exists
                        return redirect('alumni_portal')
                    else:
                        # Redirect to professional details form if employment status is null
                        return redirect('professional_details_update')
                except ProfessionalDetails.DoesNotExist:
                    # Redirect to professional details form if professional details not found
                    return redirect('professional_details_update')
            else:
                error_message = "Invalid student number or password."
                return render(request, 'alumni/alum_reg/login.html', {'form': form, 'error_message': error_message})
    else:
        form = AlumniLoginForm()
    return render(request, 'alumni/alum_reg/login.html', {'form': form})


def professional_details_view(request):
    user = request.user
    try:
        # Check if the user already has professional details
        professional_details = user.professionaldetails
        # If professional details exist, handle the update
        if request.method == 'POST':
            form = ProfessionalDetailsForm(request.POST, instance=professional_details)
            if form.is_valid():
                # Update the existing ProfessionalDetails instance
                form.save()
                # Redirect to a success page or any other page
                return redirect('professional_details_submitted')
        else:
            # Populate the form with existing professional details for editing
            form = ProfessionalDetailsForm(instance=professional_details)
    except ProfessionalDetails.DoesNotExist:
        # If the user does not have professional details, handle the creation
        if request.method == 'POST':
            form = ProfessionalDetailsForm(request.POST)
            if form.is_valid():
                # Create a new ProfessionalDetails instance
                professional_details_instance = form.save(commit=False)
                professional_details_instance.user = user
                professional_details_instance.save()
                # Redirect to a success page or any other page
                return redirect('professional_details_submitted')
        else:
            # Display an empty form for creating professional details
            form = ProfessionalDetailsForm()

    return render(request, 'alumni/alum_reg/professional_details.html', {'form': form})


def prof_success(request):
    return render(request, 'alumni/alum_reg/suc.html')


@login_required
def alumni_portal(request):
    return render(request, 'alumni/alum_reg/main.html')


def alumni_menu(request):
    alumni_group = Group.objects.get(name='Alumni')
    if request.user.is_authenticated and alumni_group in request.user.groups.all():
        return redirect('alumni_portal')
    else:
        return redirect(reverse('alumni_login'))


def alumni_available(request):
    job_listings = JobPosting.objects.all().order_by('-created_at')
    return render(request, 'alumni/alum_reg/available_jobs.html', {'available_jobs': job_listings})


def alumni_internship(request):
    internship = InternshipPosting.objects.all()
    return render(request, 'alumni/alum_reg/available_internship.html', {'internship_posting': internship})


def alumni_interviews(request):
    return render(request, 'alumni/alum_reg/interviews.html')


def employers_list_on_alumni(request):
    employers = Employer.objects.all()
    return render(request, 'alumni/alum_reg/employer_profiles.html', {'employers_profile': employers})


def alumni_profiles_in_alumni(request):
    alumni_profiles = ProfessionalDetails.objects.all()
    return render(request, 'alumni/alum_reg/alumni_profiles.html', {'alumni_profiles': alumni_profiles})


def alumni_profiles_in_employers(request):
    alumni_profiles = ProfessionalDetails.objects.all()
    return render(request, 'alumni/Job/alumni_profiles.html', {'alumni_profiles': alumni_profiles})


def alumni_profile(request, username):
    alumni_profile_selected = get_object_or_404(ProfessionalDetails, user__username=username)
    return render(request, 'alumni/Job/selected.html', {'alumni_profile': alumni_profile_selected})


def job_success(request):
    return render(request, 'alumni/Job/job_success.html')


def job_internship_list(request):
    query = request.GET.get('query', '')
    trying = request.GET.get('try', '')

    if query:
        job_postings = JobPosting.objects.filter(
            Q(job_title__icontains=query) |
            Q(company__icontains=query)
        )
        internship_postings = InternshipPosting.objects.filter(
            Q(job_title__icontains=query) |
            Q(company__icontains=query)
        )
    else:
        job_postings = JobPosting.objects.all()
        internship_postings = InternshipPosting.objects.all()

    context = {
        'job_postings': job_postings,
        'internship_postings': internship_postings,
    }

    return render(request, 'alumni/services/search_results.html', context)


def search_skills_view(request):
    query = request.GET.get('skills', '')
    if query:
        results = ProfessionalDetails.objects.filter(skills__icontains=query, employment_status='unemployed')
    else:
        results = ProfessionalDetails.objects.none()

    return render(request, 'alumni/employers/search_alumni.html', {'results': results, 'query': query})


@require_http_methods(["GET"])
def custom_logout(request):
    auth_logout(request)
    return redirect(reverse_lazy('employers_login'))


@require_http_methods(["GET"])
def alumni_logout(request):
    auth_logout(request)
    return redirect(reverse_lazy('alumni_login'))


def internship_detail_in_alumni_portal(request, internship_id):
    internship = get_object_or_404(InternshipPosting, id=internship_id)
    return render(request, 'alumni/alum_reg/internship_detail.html', {'internship': internship})


def apply_for_internship(request, internship_id):
    internship = get_object_or_404(InternshipPosting, id=internship_id)
    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.applicant = request.user
            application.save()

            messages.success(request, 'Application submitted successfully.')
            return redirect('application_success')  # Redirect to success page
    else:
        form = InternshipApplicationForm()
    return render(request, 'alumni/alum_reg/apply_internship.html', {'form': form})


def application_success(request):
    return render(request, 'alumni/alum_reg/apply_success.html')


def apply_job(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id)

    if request.method == 'POST':
        form = ApplyJobForm(request.POST, request.FILES)
        if form.is_valid():
            application_data = form.cleaned_data

            # Prepare data for sending to the employer's website
            employer_url = job_posting.company_website  # Ensure this field exists and is correctly populated
            payload = {
                'full_name': application_data['full_name'],
                'email': application_data['email'],
                'cover_letter': application_data['cover_letter'],
                'job_title': job_posting.job_title
            }

            try:
                response = requests.post(employer_url, data=payload, files={'resume': application_data['resume']})

                if response.status_code == 200:
                    # Application successful
                    return render(request, 'alumni/Job/apply_success.html', {'job_posting': job_posting})
                else:
                    # Application failed
                    return render(request, 'alumni/Job/apply_failure.html',
                                  {'message': 'Application failed. Please try again.'})
            except requests.RequestException as e:
                # Handle request errors (e.g., network issues)
                return render(request, 'alumni/Job/apply_failure.html', {'message': f'An error occurred: {e}'})
        else:
            # If form is not valid, render the form with errors
            return render(request, 'alumni/Job/apply_job.html', {'form': form, 'job_posting': job_posting})

    else:
        form = ApplyJobForm(initial={'job_id': job_id})

    return render(request, 'alumni/Job/apply_job.html', {'form': form, 'job_posting': job_posting})


def job_application_success(request):
    return render(request, 'alumni/Job/job_application.html')


def search_alumni_profiles(request):
    query = request.GET.get('query')
    alumni_profiles = ProfessionalDetails.objects.all()  # Get all alumni profiles by default

    if query:  # If a search query is provided
        alumni_profiles = ProfessionalDetails.objects.filter(
            skills__icontains=query)  # Filter alumni profiles by skills
        print(f"Query: {query}, Profiles Count: {alumni_profiles.count()}")  # Debugging output

    return render(request, 'alumni/Job/skill_search.html', {'alumni_profiles': alumni_profiles})


def search_available_jobs_in_employers(request):
    s_job = request.GET.get('s_job', '')
    available_jobs = JobPosting.objects.all()

    if s_job:
        available_jobs = available_jobs.filter(
            Q(job_title__icontains=s_job) |
            Q(job_location__icontains=s_job) |
            Q(company__icontains=s_job) |
            Q(skills__icontains=s_job) |
            Q(deadline__icontains=s_job)
        )

    return render(request, 'alumni/Job/job_search.html', {'available_jobs': available_jobs})


def employment_update(request):
    user = request.user
    try:
        professional_details = user.professionaldetails
    except ProfessionalDetails.DoesNotExist:
        professional_details = None

    if request.method == 'POST':
        form = ProfessionalDetailsForm(request.POST, instance=professional_details)
        if form.is_valid():
            professional_details_instance = form.save(commit=False)
            professional_details_instance.user = user
            professional_details_instance.save()
    else:
        form = ProfessionalDetailsForm(instance=professional_details)

    return render(request, 'alumni/alum_reg/professional_details.html', {'form': form, 'user': user})


def about_us_LUCT(request):
    return render(request, 'alumni/basetemplates/about_us_LUCT.html')


def edit_employer_profile(request):
    try:
        employer_instance = request.user.employer
    except Employer.DoesNotExist:
        employer_instance = None

    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=employer_instance)
        if form.is_valid():
            form.save()
            return redirect('employers')
    else:
        form = EmployerProfileForm(instance=employer_instance)

    return render(request, 'alumni/Job/edit_profile.html', {'form': form})


def current_students(request):
    return render(request, 'alumni/students/nau.html')


def survey_list(request, target_audience):
    surveys = Survey.objects.filter(target_audience__in=[target_audience, Survey.BOTH])
    return render(request, 'survey/survey/survey_list.html', {'surveys': surveys, 'target_audience': target_audience})


def student_internships(request):
    internship = InternshipPosting.objects.all()
    return render(request, 'alumni/students/available_internship.html', {'internship_posting': internship})


def make_apply(request):
    return render(request, 'alumni/students/making_application_student.html')


def student_portal(request):
    return render(request, 'alumni/students/student_home.html',)


def students_interviews(request):
    return render(request, 'alumni/students/interviews_student.html')


@login_required
def edit_job(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            return redirect('available-jobs')
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'alumni/Job/edit_job.html', {'form': form})


@login_required
def delete_job(request, job_id):
    job_posting = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer)
    if request.method == 'POST':
        job_posting.delete()
        return redirect('available-jobs')
    return render(request, 'alumni/Job/confirm_delete.html', {'job_posting': job_posting})


def verify_current_student(request):
    if request.method == 'POST':
        form = StudentVerificationForm(request.POST)
        if form.is_valid():
            student_number = form.cleaned_data['student_number']
            names = form.cleaned_data['names']
            email = form.cleaned_data['email']

            try:
                # Verify student details
                student = Student.objects.get(student_number=student_number, names=names, email=email)

                # Split names into first name and last name
                name_parts = names.split(' ', 1)
                if len(name_parts) == 2:
                    first_name, last_name = name_parts
                else:
                    first_name = name_parts[0]
                    last_name = ''  # Handle cases where there's only one name

                # Store verified student details in session
                request.session['verified_student'] = {
                    'student_number': student_number,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                }

                # Redirect to user creation view
                return redirect('create_student_user')

            except Student.DoesNotExist:
                form.add_error(None, "Student details do not match our records.")

    else:
        form = StudentVerificationForm()

    return render(request, 'alumni/students/verify_student.html', {'form': form})


from django.contrib.auth import get_backends


def create_current_student_user(request):
    if 'verified_student' not in request.session:
        return redirect('verify_student')

    initial_data = {
        'username': request.session['verified_student']['student_number'],
        'first_name': request.session['verified_student']['first_name'],
        'last_name': request.session['verified_student']['last_name'],
        'email': request.session['verified_student']['email']
    }

    if request.method == 'POST':
        form = StudentUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Assign the first authentication backend to the user
            user.backend = get_backends()[0].path

            # Add user to Students group
            group = Group.objects.get(name='Students')
            user.groups.add(group)

            # Log in the user
            login(request, user)

            # Clear session data
            del request.session['verified_student']
            return redirect('students-login')
        else:
            print("Form errors:", form.errors)
    else:
        form = StudentUserCreationForm(initial=initial_data)

    return render(request, 'alumni/students/create_user.html', {'form': form})


def students_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.groups.filter(name='Students').exists():
                    login(request, user)
                    return redirect('student-portal')  # Redirect to student-specific page
                else:
                    form.add_error(None, "You are not authorized to access the student portal.")
            else:
                form.add_error(None, "Invalid username or password.")
        else:
            form.add_error(None, "Form is invalid.")
    else:
        form = UserLoginForm()

    return render(request, 'alumni/students/students_login.html', {'form': form})
