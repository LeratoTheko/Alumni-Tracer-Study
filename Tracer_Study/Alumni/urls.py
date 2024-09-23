from django.urls import path
from . import views

urlpatterns = [

    path('', views.welcome, name='welcome'),
    path('home', views.base, name='home'),

    path('fabe', views.architecture_and_build_environment, name='fabe'),

    path('ict', views.information_communication_and_technology, name='ict'),
    path('business-and-globalization', views.business_and_globalization, name='business-and-globalization'),
    path('communication-media-and-broadcasting', views.communication_media_and_broadcasting,
         name='communication-media-and-broadcasting'),
    path('creativity-in-tourism-and-hospitality', views.creativity_in_tourism_and_hospitality,
         name='creativity-in-tourism-and-hospitality'),
    path('Innovation_Design', views.innova, name='Innovation_Design'),

    path('communication-media', views.faculty_cmb, name='communication-media'),
    path('information-technology', views.faculty_ict, name='information-technology'),
    path('creative-tourism', views.faculty_cth, name= 'creative-tourism'),
    path('Architecture-technology', views.faculty_fabe, name='Architecture-technology'),
    path('faculty-Aid', views.faculty_aid, name='faculty-Aid'),

    path('prospective_students', views.prospective_students, name='prospective_students'),
    path('ict_analysis', views.show_ict_analysis, name='ict_analysis'),
    path('post_job', views.post_job_view, name='post_job'),

    path('search-yourself', views.search_alumni, name="search-yourself"),
    path('register-employment-status', views.update_alumni_employment_status, name="register-employment-status"),
    path('confirmation',  views.registry_confirm, name="confirmation"),

    path('tourism', views.tourism, name="tourism"),
    path('innovation-and-design', views.innovation_and_design, name='innovation-and-design'),
    path('media', views.media, name="media"),
    path('Architecture', views.architecture, name="Architecture"),
    path('Information', views.information, name="Information"),
    path('business-employment-status', views.business, name="business-employment-status"),

    path('business-and-globalization-faculty', views.bag_faculty, name="business-and-globalization-faculty"),
    path('media-casting', views.faculty_media, name='media-casting'),
    path('faculty-of-ICT', views.faculty_inct, name='faculty-of-ICT'),
    path('fac-Architecture', views.faculty_architecture, name='fac-Architecture'),
    path('Innovation-and-design', views.faculty_of_innovation_design, name='Innovation-and-design'),
    path('tourism-faculty', views.faculty_FCTH, name='tourism-faculty'),


    path('profile_view', views.profile_view, name='profile_view'),

    path('faculty_of_innovation_design', views.faculty_of_innovation_design, name='faculty_of_innovation_design'),
    path('faculty_of_innovation_design_programs', views.innovation_and_design,
         name="faculty_of_innovation_design_programs"),

    path('employers', views.employers_menu, name='employers'),
    path('employers_dashboard', views.employers_dashboard, name='employers_dashboard'),

    path('compare', views.comparison, name='compare'),
    path('perform-compare', views.make_compare, name='perform-compare'),
    path('survey', views.survey_view, name='survey'),
    path('survey_thanks', views.survey_thanks_view, name='survey_thanks'),

    path('current_students_analysis', views.current_students_form, name='current_students_analysis'),

    path('available-jobs', views.available_job, name='available-jobs'),

    path('register_employer', views.register_employer, name="register_employer"),
    path('employers_login', views.login_view, name='employers_login'),
    path('profile_update', views.profile_update, name='profile_update'),
    path('employer_list', views.employer_list, name='employer_list'),
    path('profile_update_success', views.profile_update_success, name='profile_update_success'),
    path('approve_employer/<int:employer_id>/', views.approve_employer, name='approve_employer'),
    path('unapproved_employers', views.unapproved_employers, name='unapproved_employers'),

    path('jobs/<int:job_id>/', views.view_job, name='view_job'),

    path('internship_posting', views.internship_posting, name="internship_posting"),
    path('internship_list', views.internship_list, name="internship_list"),
    path('internship_success', views.internship_success, name="internship_success"),

    path('interviews', views.interviews, name='interviews'),

    path('verify_alumni', views.verify_alumni, name='verify_alumni'),
    path('create-user', views.create_user, name='create_user'),
    path('success', views.success, name='success'),
    path('alumni_login', views.user_login, name='alumni_login'),

    path('professional_details_update', views.professional_details_view, name='professional_details_update'),
    path('professional_details_submitted', views.prof_success, name='professional_details_submitted'),

    path('alumni_portal', views.alumni_portal, name='alumni_portal'),
    path('pass_through', views.alumni_menu, name="pass_through"),

    path('look_available', views.alumni_available, name="look_available"),
    path('look_internships', views.alumni_internship, name="look_internships"),
    path('alumni_interviews', views.alumni_interviews, name="alumni_interviews"),
    path('employers_profiles', views.employers_list_on_alumni, name="employers_profiles"),
    path('alumni_profiles', views.alumni_profiles_in_alumni, name="alumni_profiles"),

    path('alumni_profiles_list', views.alumni_profiles_in_employers, name="alumni_profiles_list"),

    path('alumni_profile/<str:username>/', views.alumni_profile, name='alumni_profile'),
    path('job_success', views.job_success, name="job_success"),
    path('search/', views.job_internship_list, name='job_internship_list'),
    path('search-skills', views.search_skills_view, name='search_skills'),

    path('accounts/logout/', views.custom_logout, name='logout'),
    path('accounts/logout/', views.alumni_logout, name='logout'),

    path('internship/<int:internship_id>/', views.internship_detail_in_alumni_portal, name='internship_detail'),
    path('apply/<int:internship_id>/', views.apply_for_internship, name='apply_for_internship'),
    path('application_success/', views.application_success, name='application_success'),
    path('apply_job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('application_success', views.job_application_success, name='job_application_success'),
    path('search-alumni', views.search_alumni_profiles, name='search_alumni_profiles'),
    path('search-available-jobs', views.search_available_jobs_in_employers, name='search-available-jobs'),
    path('professional_update', views.employment_update, name='professional_update'),
    path('about', views.about_us_LUCT, name='about'),

    path('edit_profile', views.edit_employer_profile, name='edit_profile'),

    path('surveys/<str:target_audience>/', views.survey_list, name='survey_list'),
    path('available-internships', views.student_internships, name='available_internships'),
    path('student-applications', views.make_apply, name='student-applications'),
    path('students_interviews', views.students_interviews, name='students_interviews'),

    path('edit-job/<int:job_id>/', views.edit_job, name='edit-job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete-job'),

    path('verify_current_student', views.verify_current_student, name='verify_current_student'),
    path('create_student_user', views.create_current_student_user, name='create_student_user'),
    path('student-portal', views.student_portal, name='student-portal'),

    path('students-login', views.students_login, name='students-login'),




]
