#
# Developed by David Harris (3276780)
#
#

from django.shortcuts import render
from django.http import HttpResponse
from account import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
from django.shortcuts import redirect
from account import views as account
import json

#
#Displays class list 
#
def class_list(request):
	if not account.verify_professor(request):
		return HttpResponse("Error: Not logged in as professor or your account has been deactivated.")
			
	if request.method == 'GET':
		id=request.GET.get("id")
		#Get all students in the class
		class_list=models.StudentClass.objects.filter(myclass=id)
		return render(
				request,'student_list.html',
				{
					"class":models.Class.objects.get(id=id),
					"class_list":class_list,
				}
			)
	return HttpResponse("Something went wrong. E1.")
	
#
# Add course to student courses
#
def drop_course_prof(request):
	if account.verify_professor(request):
		user=request.user.person
		if request.method == 'POST':
			try:
				#
				# Two things to do: 1) Remove class listing in ProfessorClass object
				# 2) Remove professor reference in Class object
				#
				for id in request.POST.getlist('courses_checkbox'):
					#Get professor object 
					professor=models.Professor.objects.get(registration=user)
					#Get class entry in ProfessorClass
					teach_course=models.ProfessorClass.objects.get(
						professor=professor,
						status='enrolled',
						myclass__id=id
					)
					
					#
					# Get class and remove professor object from it. This
					# returns a list of courses at most 1 (because only abs
					# single professor can have an entry in the Class object).
					# Filter instead of get prevents error if no results for
					# whatever reason
					myclass = models.Class.objects.filter(id=id,professor=professor)
					for result in myclass: 
						result.professor=None
						result.save()
					#Remove the class 
					teach_course.delete()
					account.write_log("professor","add",request.user.id,id)
				return redirect('/professor_courses/')
			except ValueError as error: 
				HttpResponse(error)
	info="Error: You're not signed in as a professor or your account is deactivated."
	return render(request,'info.html',{'info':info})
	
	
#
# Courses professor can teach page
#
#
def can_teach_list_prof(request):
	if account.verify_professor(request):
		#user=request.user.person
		professor=models.Professor.objects.get(registration=request.user.person)
		return redirect('/all_courses?department='+str(professor.department.id))
	info="Error. You're not logged in as a professor or your account is deactivated."
	return render(request,'info.html',{'info':info})
	
#
# Add course to professor courses
#
def add_course_prof(request):
	info=""
	if account.verify_professor(request):
		user=request.user.person
		if request.method == 'POST':
			#For every course selected in web form
			for id in request.POST.getlist('courses_checkbox'):
			
				professor=models.Professor.objects.get(registration=user)
				#Don't add if already teaching
				if (models.ProfessorClass.objects.filter(myclass__id=id,status='enrolled').count() > 0):
					info=" You or another professor is already teaching: "+ models.Class.objects.get(id=id).course.name_id + "."
					continue
					
				#Course taught must be from the same department
				if ( professor.department != models.Class.objects.get(id=id).course.department ):
					info=" You cannot teach "+models.Class.objects.get(id=id).course.name_id+". Wrong department."
					continue
					
				class_to_add=models.Class.objects.get(id=id)
				
				#Don't add if time conflicts with any teaching courses
				conflict=False
				for teaching in models.ProfessorClass.objects.filter(professor__registration__account=request.user):
					if account.check_time_conflict(teaching.myclass,class_to_add):
						info += " " + class_to_add.course.name_id + " conflicts with " +teaching.myclass.course.name_id + ". "
						conflict=True
				if conflict:
					continue
					
				#Get professor object
				professor=models.Professor.objects.get(registration=user)
				myclass=class_to_add
				#Get professor classes object and add to it
				pc = models.ProfessorClass()
				pc.myclass=myclass
				pc.professor=professor
				pc.status='enrolled'
				pc.save()
				#Assign class object to professor object 
				#(e.g., we added class to professor course object, now
				#add professor to the class object)
				#Add class/Teach class
				myclass.professor=professor
				myclass.save()
				account.write_log("professor","add",request.user.id,id)
			if (info == ""):
				return redirect('/professor_courses/')

	return render(request,'info.html',{'info':info})
	
#
# Get professor courses
#
def professor_courses(request):
	if account.verify_professor(request):
		user=request.user.person
		courseList=models.ProfessorClass.objects.filter(professor=models.Professor.objects.get(registration=user),status='enrolled')
		myclasses=[]
		for myclass in courseList:
			myclasses.append(myclass.myclass)
		return render(request,"enrolled_courses_student_professor.html",
			{"classes":
				myclasses
			}
		)
	info="Error. Not logged in as professor or account has been deactivated."
	return render(request,'info.html',{'info':info})