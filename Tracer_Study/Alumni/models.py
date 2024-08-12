from django.contrib.auth.models import User
from django.db import models


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
