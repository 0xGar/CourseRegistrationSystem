"""reg_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from account import views as account
from student import views as student
from professor import views as professor
#from scheduler import views
from administrator import views as administrator
import fill_database

urlpatterns = [
	url(r'^$',account.login_view),
	url(r'^profile',account.user_profile),
	url(r'^teach_list', professor.can_teach_list_prof ),
	url(r'^fill_db/', fill_database.fill ),
    url(r'^admin/', admin.site.urls),
	url(r'^new_account',administrator.create_or_modify_account),
	url(r'^modify_account',administrator.request_to_modify_account),
	url(r'^new_class',administrator.create_or_modify_class),
	url(r'^modify_class',administrator.request_to_modify_class),
	url(r'^new_term',administrator.new_term),
	url(r'^new_course',administrator.new_course),
	url(r'^user_list_pending',administrator.user_list_pending),
	url(r'^user_list_search',administrator.user_list_search),
	url(r'^user_list',administrator.user_list),
	url(r'^login',account.login_view),
	url(r'^logout',account.logout_view),
	url(r'^show_course',account.show_course),
	url(r'^all_courses',account.all_courses),
	url(r'^set_password',account.set_password),
	url(r'^filter_courses', account.filter_courses ),
	url(r'^add_course/?$',student.add_course),	
	url(r'^student_courses',student.student_courses),
	url(r'^recommended_courses',student.recommended_courses),
	url(r'^drop_course/?$',student.drop_course),
	url(r'^professor_courses',professor.professor_courses),
	url(r'^add_course_prof',professor.add_course_prof),	
	url(r'^drop_course_prof',professor.drop_course_prof),
	url(r'^class_list/?$',professor.class_list),	
]

handler404 = 'account.views.page_not_found'


