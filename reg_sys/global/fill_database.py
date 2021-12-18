from django.shortcuts import render
from django.http import HttpResponse
from account import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
from account import views as account
from django.shortcuts import redirect
import json
# python manage.py migrate --run-syncdb
#

#
# Minimum length of form input for making new account/course/term
#
NEW_ACCOUNT_MIN_LENGTH=1
NEW_COURSE_MIN_LENGTH=1
NEW_TERM_MIN_LENGTH=1

#
# This is a TEST method for filling the database with dummy data.
# To use it, visit "127.0.0.1:8000/fill_db"
# ONLY use it when the database is empty
# The database may be emptied by deleting db.sqlite3 then deleting
# the cache file directory under /project/reg_sys/reg_sys 
# dir (__pycache__), then running "python manage.py migrate --run-syncdb"
# to recreate the database
#

def fill(request):
	
	term=new_term("Fall","2016","2016-05-09","2016-10-09","2016-11-10")
	term2=new_term("Winter","2017","2016-09-08","2017-01-09","2017-03-01")
	
	#
	# COMPUTER SCIENCE
	#
	
	course=new_course(
		"Computer Science",
		"Introduction to programming in Java.",
		"Java I",
		"CS1001",
		"Computer Science",
		[],)
	new_class("HH101","2016-09-09","2016-12-15",course,term2,
	[
		["14:30:00","15:20:00","Class","Monday"],
		["14:30:00","15:20:00","Class","Wednesday"],
		["14:30:00","15:20:00","Class","Friday"],
	])
	
	course=new_course(
		"Computer Science",
		"Introduction to programming in Java II",
		"Java II",
		"CS1002",
		"Computer Science",
		["CS1001"],)
	new_class("HH101","2016-09-09","2016-12-15",course,term2,
	[
		["14:30:00","12:20:00","Class","Monday"],
		["14:30:00","15:20:00","Class","Monday"],
	])
	
	course=new_course(
		"Computer Science",
		"Parallel programming and matrix stuff",
		"High Speed Computing",
		"CS3123",
		"Computer Science",
		["CS1001","CS1002"],)
	new_class("HH101","2016-09-09","2016-12-15",course,term2,
	[
		["18:30:00","21:20:00","Class","Tuesday"],
	])
	
	# PSYCHOLOGY
	
	course=new_course(
		"Arts",
		"Introduction to Psychology I",
		"Psychology I",
		"PSYC1001",
		"Psychology",
		[],)
	new_class("HH101","2016-09-09","2016-12-15",course,term2,
	[
		["18:30:00","21:20:00","Class","Tuesday"],
	])
	course=new_course(
		"Arts",
		"Introduction to Psychology II",
		"Psychology II",
		"PSYC1002",
		"Psychology",
		["PSYC1001",],)
	new_class("HH101","2016-09-09","2016-12-15",course,term2,
	[
		["18:30:00","21:20:00","Class","Wednesday"],
	])

	course=new_course(
		"Arts",
		"Covers the history of psychology",
		"History of psychology",
		"PSYC4023",
		"Psychology",
		["PSYC1001","PSYC1002"],)
	new_class("HH101","2016-09-09","2016-12-15",course,term2,
	[
		["18:30:00","21:20:00","Class","Tuesday"],
		["18:30:00","21:20:00","Class","Friday"],
	])	
	
	# ACCOUNTS
	#
	
	create_account(
	"student",
	"student1",
	"student1@student.com",
	"Smith","M","Doh","1995-05-5",
	"15068492810",
	"20",
	"Smith",
	"E2L-3MH",
	"New Brunswick",
	"Canada",
	1)
	
	create_account(
	"student",
	"student2",
	"student2@student.com",
	"Jane","M","Doh","1997-04-5",
	"17048492210",
	"10",
	"Creek",
	"LMF-4MZ",
	"New Brunswick",
	"Canada",
	1)

	create_account(
	"student",
	"student3",
	"student3@student.com",
	"Chriss","J","Johnston","1992-04-5",
	"12043492290",
	"223",
	"Bowling",
	"FMB-9MX",
	"New Brunswick",
	"Canada",
	2)

	create_account(
	"professor",
	"professor1",
	"professor1@professor.com",
	"Richard","S","White","1972-04-5",
	"13441492290",
	"310",
	"Sawyer Lane",
	"CSL-M3G",
	"New Brunswick",
	"Canada",
	1)
	
	create_account(
	"professor",
	"professor2",
	"professor2@professor.com",
	"Bradley","S","Neil","1956-09-10",
	"14441692991",
	"15",
	"Tom Lane",
	"DSS-M4V",
	"New Brunswick",
	"Canada",
	2)
	
	return HttpResponse("Done")
	
def new_course(course_department,course_description,course_name,course_name_id,course_subject,prereqs):
	course = models.Course()
	course.description=course_description
	course.name=course_name
	course.name_id=course_name_id
	course.subject=course_subject
	if (models.Department.objects.filter(name=course_department).count() < 1):
		department=models.Department()
		department.name=course_department
		department.save()
	department=models.Department.objects.get(name=course_department)
	course.department=department
	course.save()
	
	for  prereq in prereqs:
		if (models.CoursePrerequisite.objects.filter(prerequisite=prereq,course=course).count() < 1):
			prereq_table=models.CoursePrerequisite()
			prereq_table.prerequisite=prereq
			prereq_table.course=course
			prereq_table.save()
	return course

def new_class(building,class_start_date,class_end_date,course_id,term_id,times):
	myclass = models.Class()
	myclass.building=building
	myclass.class_start_date=class_start_date
	myclass.class_end_date=class_end_date
	myclass.course=course_id
	status="active"
	myclass.term=term_id
	myclass.save()	
	for time in times:
		time_table = models.ClassTime()
		time_table.start = time[0]
		time_table.end= time[1]
		time_table.class_type=time[2]
		time_table.day = time[3]
		time_table.myclass=myclass
		time_table.save()
	return myclass
			
def new_term(term_name,term_year,reg_start_date,reg_end_date,withdrawal_date):
	term=models.Term()
	term.name=term_name
	term.year=term_year
	term.reg_start_date=reg_start_date
	term.reg_end_date=reg_end_date
	term.withdrawal_date=withdrawal_date		
	term.save()
	return term
	
def create_account(account_type,username,email,first_name,middle_name,last_name,date_of_birth,
	phone_number,street_number,street_name,postal_code,province,country,department):
	p = models.Person()
	p.account_type=account_type
	p.email=email
	p.first_name=first_name
	p.middle_name=middle_name
	p.last_name=last_name
	p.date_of_birth=date_of_birth
	p.phone_number=phone_number
	p.street_name=street_name
	p.postal_code=postal_code
	p.province=province
	p.country=country
	
	pw="123"
	username=username
	email=p.email
	user = User.objects.create_user(username,email,pw);
	user.save();
	p.account=user
	p.save()
	
	if (p.account_type == 'student'):
		student=models.Student(department=models.Department.objects.get(id=department),registration=p)
		student.save()
	elif (p.account_type == 'professor'):
		prof=models.Professor(department=models.Department.objects.get(id=department),registration=p)
		prof.save()	
	return True

