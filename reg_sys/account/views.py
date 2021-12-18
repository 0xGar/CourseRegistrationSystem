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
from django.contrib.auth import logout
from django.db.models import Q
import os
import re
import json

#
# Below import not working? You may need to add the directory
# location to the PYTHONPATH environment varabie:
#
# 	Windows(cmd): 	set PYTHONPATH=%PYTHONPATH%;c:\<...>\reg_sys\global
# 	Linux(bash):	export PYTHONPATH=$PYTHONPATH:/<...>/reg_sys/global
#

import global_settings

#
# Set password for first time login. Changing initial password
# counts as activation

def set_password(request):

	#Validate user
	if (not verify_professor(request)) and (not verify_student(request)) and (not request.user.is_superuser):
		info="You're not logged in, you're pending approval, or some other issue. You can't change your password."
		return render(request,'info.html',{'info':info})
		
	#If there's post data, means set password...
	if request.method == 'POST':
		pw = request.POST.get('pw')
		pw_c = request.POST.get('pw_confirm')
		old_pw=request.POST.get('old_pw')
		
		#Ensure password matches requirements
		if len(pw) < global_settings.MIN_PASSWORD_LENGTH:
			return HttpResponse(global_settings.PW_MATCH_PATTERN_ERROR)
		if not re.match(global_settings.PW_MATCH_PATTERN,pw, flags=0):
			return HttpResponse(global_settings.PW_MATCH_PATTERN_ERROR)
		
		#Make sure old password is correct
		if not request.user.check_password(old_pw):
			info="Incorrect password."
			return render(request,'info.html',{'info':info})
			
		#Change password
		if (pw == pw_c):
		
			user=request.user
			
			#Activate account (if not activated)
			if not request.user.is_superuser:
				if (user.person.account_type=="student"):
					account=models.Student.objects.get(registration=user.person)
				elif (user.person.account_type=="professor"):
					account=models.Professor.objects.get(registration=user.person)
				user.person.needs_activation=False
				user.person.save()
				user.save()
			
			#Set new password
			request.user.set_password(pw);
			request.user.save()
			logout(request)
			info="Your password has been set. Please login again."
			return render(request,'info.html',{'info':info})
		else:
			info="Passwords do not match."
			return render(request,'info.html',{'info':info})
			
	info="Something went wrong with changing the password."
	return render(request,'info.html',{'info':info})

#
# User Profile
#

def user_profile(request):
	if verify_professor(request) or verify_student(request) or request.user.is_superuser:
		return render(request,'profile.html',{'user':request.user})
	info="You're not logged in, your account is deactivated or you're pending approval."
	return render(request,'info.html',{'info':info})
#
# Logout View
#
def logout_view(request):
	logout(request)
	info="Logged out."
	return render(request,'info.html',{'info':info})	
#
# Login a user
#
def login_view(request):
	if not request.user.is_anonymous:
		return redirect('/all_courses/')
	response=""
	error='0'
	if (request.method == 'POST'):
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			
			# If there's no person object associated with the account
			# then by design it means this is a regular, run of the
			# mill super user account for making courses,etc.
			# We already logged the super user in -- we're done.
			if not hasattr(user, 'person'):
				return redirect('/all_courses/')
			
			#Check if user needs activation
			account=user
			if user.person.pending_approval:
				info="Your account is pending approval."
				return render(request,'info.html',{"user":user,"info":info})
			#Needs activation. Render set password page
			if account.person.needs_activation==True:
				return render(request,'set_password.html',{"user":user})
			#Doesn't need activation
			return redirect('/all_courses/')

		else:
			response="Incorrect login details."
			error='1'
	return render(request,'login.html',{'response':response,'error':error})
	
#
# All courses
#	

def all_courses(request):
	#if request.user.is_authenticated():
	user=request.user
	
	if request.method =="POST":
	
		#Get POST data 
		departments = request.POST.get("filter_departments")
		courses = request.POST.get("filter_courses")
		#Split POST data into arrays
		if len(departments) >0:
			departments=departments.split(",")
		else: departments=[]
		if len(courses)>0:
			courses = courses.split(",")
		else: courses=[]
		
		#
		# Filter condition checking
		#
		
		if (len(courses) > 0) and ("-1" not in departments): #Only get specificed courses in specificed departments
			classes = models.Class.objects.filter(course__name_id__in=courses,course__department__id__in=departments)
		elif (len(courses) > 0) and ("-1" in departments): #Get specific course from any department
			classes = models.Class.objects.filter(course__name_id__in=courses)
			#return HttpResponse("d")
		elif "-1" in departments: # Get every course, every department
			classes = models.Class.objects.all()
		else: #Get every course from specificed departments	
			classes = models.Class.objects.filter(course__department__id__in=departments)
			
	#Not POST data; get every course
	else:
			#This *indicates* we're in the "courses I can teach section"
			if (request.GET.get("department")):
				classes=models.Class.objects.filter(course__department=request.GET.get("department"))
			else:
				classes = models.Class.objects.all()
		#prereq = models.CoursePrerequisite.objects.all()
		#time = models.ClassTime.objects.all()
	
	#
	# Further filtering below, such as 
	# active vs inactive courses
	#
	
	departments=get_departments()
	
	#Get current time and filter classes for all classes that can be
	#registered for currently (e.g., in between reg start/end dates)
	current_time=datetime.now().date()
	classes = classes.filter(term__reg_start_date__lte=current_time,term__reg_end_date__gte=current_time)
	
	#Helps to filter the prerequisites by course name
	mycourses=[]
	for myclass in classes:
		mycourses.append(myclass.course)
		
	prereq = models.CoursePrerequisite.objects.filter(course__in=mycourses)
	time = models.ClassTime.objects.filter(myclass__in=classes)
		
	#
	#
	#
	
	#For displaying teach check box of professor only for department he's in 
	person_department=""
	
	enrolled_classes=[]
	
	#
	# Highlighting for courses currently taken by prof or teacher
	#
	
	#If we don't check an error will be thrown as user.person doesn't exist for everyone
	if not user.is_superuser and not user.is_anonymous:
		if (user.person.account_type=="professor"):
			person_department=models.Professor.objects.get(registration=user.person).department
			#Used to high light courses professor is teaching in course list
			professor=models.Professor.objects.filter(registration=user.person)
			enrolled_classes=models.ProfessorClass.objects.filter(status="active",professor=professor)
		if (user.person.account_type=="student"):
			student=models.Student.objects.filter(registration=user.person)
			#Used to high light courses student is taking in course list
			enrolled_classes=models.StudentClass.objects.filter(student=student)
	my_classes=[]
	
	#Get the classes from 
	for c in enrolled_classes:
		my_classes.append(c.myclass)
	
	return render(request,'all_courses.html',
	{
		#Sorting this list is very important, or else
		#result will be scattered on the webpage
		"classes":sorted(classes,key=lambda x: x.course.department.name),
		"prereq":prereq,
		"times":time,
		"departments":departments,
		"user":user,
		"person_department":person_department,
		"my_classes":my_classes
	})	

#
# View course, given ID
#
def show_course(request):
	user=request.user
	if request.method == 'GET':
		try :
			myclass=models.Class.objects.get(id=request.GET["id"])
			return render(request,'show_course.html',
                				{
					"class":myclass,
					"times":models.ClassTime.objects.filter(myclass=myclass),
					"prereq":models.CoursePrerequisite.objects.filter(course=myclass.course),
					"user":user,
				}
			)
		except ValueError as error: 
			HttpResponse(error)
	return HttpResponse("No Course ID specified")
#
# Get departments
#
def get_departments():
	for d in global_settings.DEPARTMENTS:
		if (models.Department.objects.filter(name=d).count() < 1):
			department=models.Department()
			department.name=d
			department.save()
	return models.Department.objects.order_by("name")
	#return global_settings.DEPARTMENTS
	#return models.Department.objects.values_list("name",flat=True).order_by().distinct()

def new_course_options():
	return models.Course.objects.all()
	#return global_settings.COURSE_OPTIONS

#def get_terms():
	#return COURSE_TERMS
	
# Verifies student
def verify_student(request):
	if request.user.is_authenticated():
		if not hasattr(request.user, 'person'): #Indicates superuser
			return False
		if not request.user.person.is_active:
			return False
		if request.user.person.pending_approval:
			return False
		return (request.user.person.account_type=='student')
	return False
		
# Verifies professor
def verify_professor(request):
	if request.user.is_authenticated():
		if not hasattr(request.user, 'person'): #Indicates superuser
			return False
		if not request.user.person.is_active:
			return False
		if request.user.person.pending_approval:
			return False
		return (request.user.person.account_type=='professor')
	return (False)
	
#
# Writes log when action occured for student/professor
# account_type -> account type (professor/student)
# (could exclude account_type since we have id, but
# keeping it for some level of user readability in the log)
# action -> add/drop
# id -> the user id 
# info -> what to append to file (course id). date not included
#

def write_log(account_type,action,id,info):

	#Format: 2016-12-01 (YYYY-MM-DD)
	current_date = datetime.now().date().isoformat()
	
	#Output log string
	output_log=account_type+":"+str(id)+":"+action+":"+str(info)+":"+datetime.now().ctime()+"\n"
	
	with open(os.path.join(global_settings.BASE_DIR, "logs/actions-"+current_date+".txt"),'a') as file:
		file.write(output_log)
	return True
#
# Check if class conflicts with another class
#

def check_time_conflict(class1,class2):

	#Get times
	times = models.ClassTime.objects.filter(myclass=class1)
	times2 = models.ClassTime.objects.filter(myclass=class2)
	
	#They must be from the same term to cause a conflict
	if (class1.term!=class2.term):
		return  False
		
	#If times are set for both classes
	if times.count() >= 1 and times.count() >= 1:
		#For every time associated with class1
		for time in times:
			#Start comparison with class2
			for time2 in times2:
				#Can only conflict if times are on the same day
				if (time2.day == time.day):
					#
					# Confliction check algorithm
					#-------------------------------------
					# Formula: 	start -> hour+minute 
					#			end	-> start+hour+minute
					#
					# This gives an interval
					#
					# Confliction example using intervals:
					# 
					# |----time1--------| 
					#    |----time2------|
					# 1pm             4pm
					#
					# This confliction is caught by:
					# start2 => start1 and start2 < end1
					# 
							
					#Convert date string in database to datetime
					start1=datetime.strptime(time.start, "%H:%M:%S").time()
					start2=datetime.strptime(time2.start, "%H:%M:%S").time()
					end1=datetime.strptime(time.end, "%H:%M:%S").time()
					end2=datetime.strptime(time2.end, "%H:%M:%S").time()
					
					#Do the formula interval mentioned above
					start1=start1.hour + start1.minute
					start2=start2.hour + start2.minute
					end1=start1 + end1.hour + end1.minute
					end2=start2 + end2.hour + end2.minute
					
					if (start1 >= start2 and start1 < end1) or (end1 > start2 and end1 <= end2):
						#Conflict
						return True
						
	#No conflict
	return False
	
#Only works in non-debugging mode
def page_not_found(request):
	return HttpResponse("Page not found")
	
#
# Return filter results from filter suggestion in
# all course page

def filter_courses(request):
	output={}
	output["success"]=True
	output["list"]=[]
	flag=False
	
	if request.method == 'GET':
		try :
			get=request.GET
			myfilter=get.get("filter")
			if not get.get("filter"):
				output["success"]=False
				output["error"]="No filter"
				flag=True
				
			#Only do if no errors occured
			if not flag:
				#Filter by contains, case insensitive
				results=models.Class.objects.filter( Q(course__name_id__icontains=myfilter)) # | Q(course__name__icontains=myfilter) 
				for a in results:
					output["list"].append(a.course.name_id)
					
		except ValueError as error: 
			output["success"]=False
			output["error"]=error
			
	return HttpResponse( json.dumps(output) )