import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import JobPosting
from .models import InternshipPosting

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