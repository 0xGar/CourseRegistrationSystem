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
from account import views as account
from django.shortcuts import redirect
from django.db.models import Q
import json
# python manage.py migrate --run-syncdb
#

#
# Minimum length of form input for making new account/course/term
#
NEW_ACCOUNT_MIN_LENGTH=1
NEW_COURSE_MIN_LENGTH=1
NEW_TERM_MIN_LENGTH=1

def user_list_search(request):
	return render(
		request,'user_list_search.html',
		{
			
			}
		)

def user_list_pending(request):
	if request.user.is_superuser:
		account=models.Person.objects.filter(pending_approval=True)
		return render(
			request,'user_list.html',
			{
				"users":account,
				"account_user":User.objects.filter(person=account)
			}
		)
	return HttpResponse("Not logged in as admin or POST content is empty.")
	
def user_list(request):
	if request.user.is_superuser:
		if request.method == "GET":
			first_name=request.GET.get("first_name")
			last_name=request.GET.get("last_name")
			email=request.GET.get("email")
			username=request.GET.get("username")
			account_type=request.GET.get("account_type")
			
			if (not last_name) and (not email) and (not username):
				return HttpResponse("At least one of: user, email, last name must be entered.")
				
			if email or username:
				#Get match for username OR email
				result2=User.objects.filter(Q(email__iexact=email) | Q(username__iexact=username))
				result=[]
				for r in result2:
					result.append(r.person)
			elif first_name or last_name:
				result=models.Person.objects.filter(first_name__icontains=first_name,last_name__iexact=last_name)
			if account_type:
				result=result.filter(account_type=account_type)
				
			return render(
				request,'user_list.html',
				{
					"users":result
				}
			)
	return HttpResponse("Not logged in as admin or POST content is empty.")
			
def request_to_modify_account(request):
	user=request.user
	if not request.user.is_superuser:
		return HttpResponse("You're not an admin.")
	if request.method == 'GET':
		try :
			# GET having id variable means modify account. 
			if (request.GET.get("id")):
				id = request.GET.get("id")
				person = models.Person.objects.filter(id=id)
				if person.count() < 1:
					return HttpResponse("This account has no profile. Editing non-profile accounts (e.g.,"+
						" superusers) is not available.")
				#Will always just be 1 element
				person = person.first()
				department=""
				
				#Edit 99
				#if person.account_type=="student":
				#	department = models.Student.objects.get(registration=person).department.id
				student_department=""
				if person.account_type=="student":
					student_department = models.Student.objects.get(registration=person).department
				
				return render(request,'modify_account.html',
				{
					"user":user,
					"account":person,
					"account_user":User.objects.get(person=person),
					"departments":account.get_departments(),
					"student_department":student_department,
					"modify":True
					}
				)
		except ValueError as error:
			return HttpResponse(error)
	return HttpResponse("Account ID not specified.")

#
# Check form validity for modifying/creating account
# Output > 1 = error message
# Output < 1 = no error
#

def check_account_form(request):
    #Msg for when something goes wrong
	output=""
	post = request.POST
			
	# Check that command input is properly set
	if not post.get("command") == "new_account" and not post.get("command") == "modify_account":
		output="Command input not set"
				
	#
	# Test to make sure proper format/length for required fields.
	# Middle name, phone number optional
	#

	username=post.get("username")
	if not username:
		output="Username is too short."
	username=User.objects.filter(username=username)
	if post.get("command")=="new_account" and username.count() > 0:
		output="Username exists."
    
	email=post.get("email")
	if not email:
		output="Email is too short."
	email=User.objects.filter(email=email)
	if post.get("command")=="new_account" and email.count() > 0:
		output="Email exists."
				
	first_name=post.get("first_name")
	if not first_name:
		output="First name too short."
				
	last_name=post.get("last_name")
	if not last_name:
		output="Last name too short."
				
	date_of_birth=post.get("date_of_birth")
	if not date_of_birth:
				output="Date of birth too short."
	try:
		date = datetime.strptime(date_of_birth,"%Y-%m-%d")
	except ValueError:
		output="Date of birth has invalid dates."
				
	street_name=post.get("street_name")
	if not street_name:
		output="Street name too short."
				
	postal_code=post.get("postal_code")
	if not postal_code:
		output="Postal code too short."
				
	province=post.get("province")
	if not province:
		output="Province too short."
				
	country=post.get("country")
	if not country:
		output="Country too short."
		
	return output
	
	
	
#
# 1. Adds a new user account, associating it with 1, professor, or 2
# student
# 2. Or modifies an account 
#
# I was going to completely separate new account/modify account sections
# into different methods, but this requires duplicating some code that
# may increase the chances of creating an inconsistency between making 
# a new account and modifying a new account if the database is ever 
# modified. So this method is a little hairy but for a good reason
#

def create_or_modify_account(request):
	if not request.user.is_superuser:
		if not request.user.is_anonymous:
			return HttpResponse("You already have an account.")
	
    # Output for when something goes wrong
	output=""
	user=request.user
	
	# Post data -> make new account or modify account
	# No post data -> show the "make new account"
	
	if request.method == 'POST':
		try :
			user=""
			
			#Check form validity
			validity=check_account_form(request)
			if ( len(validity) > 1):
				return HttpResponse(validity)
				
			post = request.POST
			new_account=True
			
			# New account; create new account object
			if post.get("command") == "new_account":
				p = models.Person()
			#Modified account; get account object & user account
			else: 
				if not request.user.is_superuser:
					return HttpResponse("You're not an admin. You cannot modify accounts.")
				p= models.Person.objects.get(id=post.get("account_db_id"))
				user=User.objects.get(person=p)
				new_account=False
				
			# Set attributes for the Person model (the user profile)
			# If the database changes then this section and check_account_form()
			# must be manually updated

			#Can only be set when making new account (cannot be modified)
			if new_account: 
				p.account_type=post.get("account_type")
        
			email=post.get("email")
			p.email=email
			p.first_name=post.get("first_name")
			p.middle_name=post.get("middle_name")
			p.last_name=post.get("last_name")
			p.date_of_birth=post.get("date_of_birth")
			p.phone_number=post.get("phone_number")
			p.street_name=post.get("street_name")
			p.postal_code=post.get("postal_code")
			p.province=post.get("province")
			p.country=post.get("country")

			#Pw/username only used if creating new account, determined below
			pw=""
			username=post.get("username")
			
			#Make a new account
			if new_account:
				# Random password. The admin makes accounts so the student
				# will be in charge of making his own password after logging in
				pw=User.objects.make_random_password()
			
				#
				# Get username,email,pw, make user account. 
				#
        
				user = User.objects.create_user(username,email,pw);
				user.save();
				
				#
				# Add newly created user reference to profile
				#
				p.account=user
			#Modified account; change email/username if applicable
			else:
				if User.objects.filter(email=email).count() < 1:
					user.email=email
					user.save()
				elif User.objects.get(email=email) == user:
					#Same email as before; do nothing
					{}
				else:
					return HttpResponse("Email is taken by another user.")
				if User.objects.filter(username=username).count()<1:
					user.username=username
					user.save()
				elif User.objects.get(username=username) == user:
					#Do nothing; same user name
					{}
				else:
					return HttpResponse("Username is taken by another user.")
        
			#
			# Save profile
			#
			p.save()
			
			#If superuser, can indicate active/inactive
			if request.user.is_superuser:
				status=post.get("account_status")
				if status=="inactive":
					p.is_active=False
					p.save()
				elif status=="active" and p.is_active==False:
					p.is_active=True
					p.pending_approval=False
					p.save()
					
			# If not superuser then account must wait approval
			# to be activated
			if not request.user.is_superuser:
				p.is_active=False
				p.pending_approval=True
				p.save()
		
			department=post.get("department")
				
			# 
			# Link the Person to either a student or professor model
			# (and make the model instance for either the student or professor)
			# If account exist it will just update the department
			if (p.account_type == 'student'):
				if new_account:
					#Create the student object, specifying department
					student=models.Student(department=models.Department.objects.get(id=department),registration=p)
				else:
					student=models.Student.objects.get(registration=p)
				student.department=models.Department.objects.get(id=department)
				student.save()
			elif (p.account_type == 'professor'):
				if new_account:
					prof=models.Professor(registration=p)
				else:
					prof=models.Professor.objects.get(registration=p)
				prof.department=models.Department.objects.get(id=department)
				prof.save()
					
			if not new_account:
				#Arrive here if course is modified
				info="The account has been modified."
				return render(request,'info.html',{'info':info})
				
			#Arrive here if new account is made
			return render(
				request,'new_account_made.html',
				{
					'password':pw,
					'username':username
				}
			)
		except ValueError as error: 
			output=error
		return HttpResponse(output)
	#No post data (means not modifying/account account); just
	# form to make new account
	return render(request,'new_account.html',
		{
			'user':user,
			"departments":account.get_departments(),
	})
	
def new_course(request):

	if not request.user.is_superuser:
		return HttpResponse("You're not an admin.")
		
	output={}
	output["success"]=True
	output["id"]=""
	output["error"]=""
	
	if request.method == 'POST':
		try :
			post=request.POST
			#Check form validity
			#validity=check_course_form(request)
			#if ( len(validity) > 1):
			#	return HttpResponse(validity)
				
			post = request.POST
	
			course = models.Course()
			course.description=post.get("course_description")
			course.name=post.get("course_name")
			course.name_id=post.get("course_name_id")
			course.subject=post.get("course_subject")
		
			# 1. If the department does not exist in the database create an entry for it.
			# 2. Add a reference to the department inside of the course table.

			#output["id"]=post.get("course_department")
			#return HttpResponse( json.dumps(output) )
			
			#if (models.Department.objects.filter(name=post.get("course_department")).count() < 1):
			#	department=models.Department()
			#	department.name=post.get("course_department")
			#	department.save()
			department=models.Department.objects.get(id=post.get("course_department"))
			course.department=department
			course.save()
			output["id"]=course.id
	
			#Check if there are prerequisite in the form data; 
			#add to prerequisite table for each one found
			#and ignore ones that already exist in there
	
			prereqs = post.get("course_prerequisites")
			if prereqs and len(prereqs) > 1:
				prereqs = prereqs.split(";")
				for  prereq in prereqs:
					#make sure entry doesn't already exist in the case of modifying<<modification removed
					#kept incase reimplementing
					if (models.CoursePrerequisite.objects.filter(prerequisite=prereq,course=course).count() < 1):
						prereq_table=models.CoursePrerequisite()
						prereq_table.prerequisite=prereq
						prereq_table.course=course
						prereq_table.save()
						
		except ValueError as error: 
			output["success"]=False
			output["error"]=error
			
	return HttpResponse( json.dumps(output) )
	
def check_class_form(request):
    #Msg for when something goes wrong
	output=""
	post = request.POST
	
	# Check that command input is properly set
	if not post.get("command") == "new_class" and not post.get("command") == "modify_class":
		output="Command input not set: "
				
	#
	# Test to make sure proper format/length for required fields.
	# Middle name, phone number optional
	#
	
	course_id=post.get("course_id")
	if not course_id:
		output="Course not found."
		
	#name=post.get("class_name")
	#if not name:
	#	output="Course name too short."
	
	#department=post.get("course_department")
	#if not department:
	#	output="Department not specified."
		
	start=post.get("class_start_date")
	if not start:
		output="Course start date too short."
	
	end=post.get("class_end_date")
	if not end:
		output="Course end date too short."
	
	return output
		
#
# Adds a new class to the database
# Works the same as making a new account. See comments there.
#

def create_or_modify_class(request):
	if not request.user.is_superuser:
		return HttpResponse("You're not an admin.")
	output=""
	user=request.user
	if request.method == 'POST':
		try :

			#Check form validity
			validity=check_class_form(request)
			if ( len(validity) > 1):
				return HttpResponse(validity)
				
			post = request.POST
			
			#New course. Make new class object for database
			if (post.get("command") == "new_class"):
				myclass = models.Class()
			#Modified course. Get class object from database
			else:
				myclass = models.Class.objects.get(id=post.get("class_db_id"))
			
			#
			# Set class information into database
			# Changes to the database will need to be 
			# reflected here and also check_course_form()
			#
			myclass.building=post.get("class_building")
			myclass.class_start_date=post.get("class_start_date")
			myclass.class_end_date=post.get("class_end_date")
			myclass.course=models.Course.objects.get(id=post.get("course_id"))

			status="active"
			myclass.term=models.Term.objects.get(id=post.get("term_id"))

			myclass.save()
			
			#For each class time add it to the table containing class times.
			#If modifying the course then delete all entries and add back the ones
			#contained in the form (if time is not modified then the
			#form contains the original times). This way is quicker than
			#comparing the form times with the times in the database one
			#by one
			
			if (post.get("command") == "modify_class"):
				time_table=models.ClassTime.objects.filter(myclass=myclass).delete()
			
			#if class_times (json) is more than 2 ( could just be {} )
			#better ways to check, but this is a quick solution
			if post.get("class_times") and len(post.get("class_times")) > 3:
				class_times=json.loads(post.get("class_times"))
				for day in class_times:
					for time in class_times[day]:
						if (len(time) >1):
							time_table = models.ClassTime()
							time_table.day = day
							time_table.start = time[0]
							time_table.end= time[1]
							time_table.class_type=time[2]
							time_table.myclass=myclass
							time_table.save()
			
		except ValueError as error: 
			return HttpResponse(error)
		
		#
		#Error encountered above (but not caught by exception)
		#Indicate here to user
		#
		if ( len(output) > 1):
			return HttpResponse(output)
			
		# Else, if new course, display new course made page
		if (post.get("command") == "new_class"):
			return render(
				request,'new_class_made.html',
				{
				'class':myclass,
				'user':user
				}
			)
			
		#Arrive here if course is modified
		info="The class has been modified."
		return render(request,'info.html',{'info':info})
		
	#Arrive here if no POST data; display make new class form
	return render(request,'new_class.html',{
		"departments":account.get_departments(),
		"course_options":account.new_course_options(),
		"terms":models.Term.objects.filter(year__gte=datetime.now().year),
		"user":user
		}
	)

#
# Modify, given ID.
#
# User visits modify_course page by clicking a link with GET data specifying the
# course id. Information is retreived from the database for the course and displayed
# to the user. The user changes the information and hits submit. The submit button
# takes the user to the new_course page, the POST data specifying that the course 
# needs to be modified; it's not really new. So the course is updated.
#

def request_to_modify_class(request):
	if not request.user.is_superuser:
		return HttpResponse("You're not an admin.")
	user=request.user
	if request.method == 'GET':
		try :
		
			# GET with id variable present means modify course. The following code
			# will retreive the course from the database, and related
			# tables (course time table, prerequisite table, etc)
			# and display the information to the user for editing.
			
			if (request.GET.get("id")):
				id = request.GET.get("id")
				myclass = models.Class.objects.get(id=id)

				#
				# Get time for the course from the database. Store in array.
				#
			
				timeArray={}
				times = models.ClassTime.objects.filter(myclass=myclass)
				for time in times:
					if not hasattr(timeArray,time.day):
						timeArray[time.day]=[]
					timeArray[time.day].append([time.start,time.end,"blank"])
				
				#
				# Get prerequisites
				#
			
			#	req_result=""
			#	prereq = models.CoursePrerequisite.objects.filter(course=myclass.course)
			#	for req in prereq:
			#		req_result +=req.prerequisite+";"
			#	if ";" in req_result:
			#		req_result = req_result[:-1]
					
				return render(request,'modify_class.html',
				{
					'departments':account.get_departments(),
					'class':myclass,
					'class_times':	json.dumps(timeArray),
					#'prereq':req_result,
					"course_options":account.new_course_options(),
					"terms":models.Term.objects.all(),
					"user":user
					}
				)
				
		except ValueError as error: 
			output=error
			return HttpResponse(output)
	
	# No post data specified (no course ID provided). So,
	# just redirect the user to the new course page with no
	# POST data, meaning a new course will be made.
	return render(request,'new_course.html',{user:'user'})
	
#
# Creates a new term
#

def new_term(request):
	if not request.user.is_superuser:
		return HttpResponse("You're not an admin.")
	output={}
	output["success"]=True
	output["name"]=""
	output["year"]=""
	output["id"]=""
	output["error"]=""
	
	user=request.user
	flag=False
	
	if request.method == 'POST':
		try :
			post=request.POST
			term=models.Term()
			
			term.name=post.get("term_name")
			if not post.get("term_name"):
				output["success"]=False
				output["error"]="Term name too short."
				flag=True
				
			term.year=post.get("term_year")
			if not post.get("term_year"):
				output["Success"]=False
				output["error"]="Term year too short"
				flag=True
				
			#Only do if no errors occured
			if not flag:
				#Registration start/end, withdrawal dates optional
				term.reg_start_date=post.get("reg_start_date")
				term.reg_end_date=post.get("reg_end_date")
				term.withdrawal_date=post.get("withdrawal_date")
			
				term.save()
				
				output["name"]=post.get("term_name")
				output["year"]=post.get("term_year")
				output["id"]=term.id
				
		except ValueError as error: 
			output["success"]=False
			output["error"]=error
			
	return HttpResponse( json.dumps(output) )