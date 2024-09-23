import json

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import JobPosting, Student, StudentMaterial
from .models import GraduatedStudent
from .models import StudentsSurvey
from .models import Employer
from .models import InternshipPosting
from .models import ProfessionalDetails
from .models import InternshipApplication
from .models import Survey
from .models import Question
from .models import Option


class csvImportForm(forms.Form):
    csv_file = forms.FileField()

    def __init__(self, csv_data=None, *args, **kwargs):
        super(csvImportForm, self).__init__(*args, **kwargs)
        if csv_data:
            for i, row in enumerate(csv_data):
                for j, value in enumerate(row):
                    field_name = f'field_{i}_{j}'
                    self.fields[field_name] = forms.CharField(initial=value, label='', required=False)


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'job_title',
            'company',
            'workplace_type',
            'job_location',
            'job_type',
            'description',
            'skills',
            'deadline'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace_type': forms.Select(attrs={'class': 'form-control'}),
            'job_location': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class InternshipForm(forms.ModelForm):
    class Meta:
        model = InternshipPosting
        fields = ['job_title', 'company', 'workplace_type', 'job_location', 'job_type', 'description', 'skills']


class AlumniSearchForm(forms.Form):
    student_number = forms.CharField(label='Student Number', max_length=20)


class AlumniEmploymentStatus(forms.Form):
    student_number = forms.CharField(label='Student Number', max_length=9)
    employment_status = forms.CharField(label='Employment Status', max_length=100)
    company_name = forms.CharField(label='Company Name', max_length=100)


class AlumniVerificationForm(forms.Form):
    PROGRAM_CHOICES = (
        ('BSSM', 'BSSM'),
        ('BSBT', 'BSBT'),
        ('BSBIT', 'BSBIT'),
    )

    FACULTY_CHOICES = (
        ('FICT', 'FICT'),
        ('FABE', 'FABE'),
        ('FCMB', 'FCMB'),
    )

    student_number = forms.CharField(max_length=9, label="Student Number")
    names = forms.CharField(max_length=200, label="Full Name")
    graduation_year = forms.IntegerField(label="Graduation Year")
    course = forms.ChoiceField(choices=PROGRAM_CHOICES, label="Program")
    faculty = forms.ChoiceField(choices=FACULTY_CHOICES, label="Faculty")

    def __init__(self, *args, **kwargs):
        super(AlumniVerificationForm, self).__init__(*args, **kwargs)
        self.fields['student_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['names'].widget.attrs.update({'class': 'form-control'})
        self.fields['graduation_year'].widget.attrs.update({'class': 'form-control'})
        self.fields['course'].widget.attrs.update({'class': 'form-control'})
        self.fields['faculty'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        student_number = cleaned_data.get('student_number')
        names = cleaned_data.get('names')
        graduation_year = cleaned_data.get('graduation_year')
        course = cleaned_data.get('course')
        faculty = cleaned_data.get('faculty')

        if not GraduatedStudent.objects.filter(
                student_number=student_number,
                names=names,
                graduation_year=graduation_year,
                course=course,
                faculty=faculty
        ).exists():
            raise forms.ValidationError("The provided information does not match our records.")

        return cleaned_data


class AlumniLoginForm(forms.Form):
    student_number = forms.CharField(
        max_length=9,
        label="Student Number",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )


class AlumniUserCreationForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    cover_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control password-field'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control password-field'}),
        }


class StudentsSurveyForm(forms.ModelForm):
    class Meta:
        model = StudentsSurvey
        fields = ['faculty', 'degree_level', 'course', 'gender', 'reason', 'program_satisfaction', 'faculty_knowledge',
                  'curriculum_satisfaction', 'academic_advisors', 'campus_facilities_satisfaction', 'extracurricular',
                  'program_support', 'career_goals', 'career_services', 'comments']
        widgets = {
            'faculty': forms.Select(attrs={'class': 'form-control', 'maxlength': '50'}),
            'degree_level': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'program_satisfaction': forms.Select(attrs={'class': 'form-control'}),
            'faculty_knowledge': forms.Select(attrs={'class': 'form-control'}),
            'curriculum_satisfaction': forms.Select(attrs={'class': 'form-control'}),
            'academic_advisors': forms.Select(attrs={'class': 'form-control'}),
            'campus_facilities_satisfaction': forms.Select(attrs={'class': 'form-control'}),
            'extracurricular': forms.Select(attrs={'class': 'form-control'}),
            'program_support': forms.Select(attrs={'class': 'form-control'}),
            'career_goals': forms.Select(attrs={'class': 'form-control'}),
            'career_services': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(label='Company Profile Picture', required=False)

    class Meta:
        model = Employer
        fields = ['profile_picture', 'company_description', 'contact_phone', 'address']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Remove company email and website fields from the form
            self.fields.pop('company_email')
            self.fields.pop('website')


class EmployerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    company_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    contact_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    profile_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    cover_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'profile_picture']

    def clean_contact_email(self):
        contact_email = self.cleaned_data.get('contact_email')
        allowed_domains = ['ac.ls', 'co.ls', 'com']
        domain = contact_email.split('@')[1]
        if domain not in allowed_domains:
            raise forms.ValidationError("Please use a company email address.")
        return contact_email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        employer = Employer(
            user=user,
            company_name=self.cleaned_data['company_name'],
            company_description=self.cleaned_data['company_description'],
            company_email=self.cleaned_data['company_email'],
            contact_phone=self.cleaned_data['contact_phone'],
            website=self.cleaned_data['website'],
            address=self.cleaned_data['address'],
            is_approved=False,
            profile_picture=self.cleaned_data.get('profile_picture'),
            cover_picture=self.cleaned_data.get('cover_picture')
        )
        if commit:
            employer.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProfessionalDetailsForm(forms.ModelForm):
    EMPLOYMENT_STATUS_CHOICES = [
        ('', 'Select Employment Status'),
        ('unemployed', 'Unemployed'),
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('studying', 'Studying'),
        ('self_employed_and_employed', 'Self Employed and Employed'),
        ('employed_and_studying', 'Employed and Studying'),
        ('self_employed_and_studying', 'Self Employed and Studying'),
    ]

    employment_status = forms.ChoiceField(choices=EMPLOYMENT_STATUS_CHOICES,
                                          widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ProfessionalDetails
        fields = [
            'employment_status', 'company_name', 'country', 'job_position',
            'duration_in_company', 'is_related_to_profession', 'started_length',
            'email', 'contacts', 'skills'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'job_position': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_in_company': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_related_to_profession': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'started_length': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacts': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InternshipApplicationForm(forms.ModelForm):
    class Meta:
        model = InternshipApplication
        fields = ['full_name', 'email', 'phone_number', 'major', 'gpa', 'previous_internships', 'skills',
                  'cover_letter', 'resume']
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'major': 'Major/Field of Study',
            'gpa': 'GPA',
            'previous_internships': 'Previous Internships',
            'skills': 'Skills and Qualifications',
            'cover_letter': 'Cover Letter',
            'resume': 'Resume/CV Upload',
        }
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }


class ApplyJobForm(forms.Form):
    job_id = forms.IntegerField(widget=forms.HiddenInput())
    full_name = forms.CharField(max_length=255, label='Full Name')
    email = forms.EmailField(label='Email')
    resume = forms.FileField(label='Upload Resume')
    cover_letter = forms.CharField(widget=forms.Textarea, label='Cover Letter')


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = ['company_name', 'company_description', 'company_email', 'contact_phone', 'website', 'address',
                  'profile_picture', 'cover_picture']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
            'cover_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            if self.instance.question_type == 'dropdown' or self.instance.question_type == 'checkboxes':
                # Override the default inline formset to use a custom formset
                self.fields['option_set'] = forms.inlineformset_factory(
                    Question,
                    Option,
                    form=OptionForm,
                    extra=1,
                    min_num=1,
                    validate_min=True,
                    max_num=None,
                    validate_max=False,
                    can_delete=True,
                )


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'deadline', 'target_audience']

    question_set = forms.inlineformset_factory(Survey, Question, form=QuestionForm, extra=1)


class StudentVerificationForm(forms.Form):
    student_number = forms.CharField(max_length=9, widget=forms.TextInput(attrs={'class': 'form-control'}))
    names = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    faculty = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control'}))
    course = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=100, required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=22, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class StudentUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        # Exclude the password fields from Meta to handle them separately

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text='Enter the same password as above, for verification.'
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class StudentMaterialForm(forms.ModelForm):
    class Meta:
        model = StudentMaterial
        fields = ['title', 'description', 'file']





