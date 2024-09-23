from django.shortcuts import render

from .models import JobPosting
from .models import InternshipPosting


def welcome(request):
    return render(request, "alumni/basetemplates/intro.html", {})


def base(request):
    job_postings = JobPosting.objects.all().order_by('-created_at')[:3]
    internship = InternshipPosting.objects.all().order_by('-created_at')[:3]

    context = {
        'job_postings': job_postings,
        'internship_posting': internship
    }
    return render(request, "alumni/basetemplates/base.html", context)
