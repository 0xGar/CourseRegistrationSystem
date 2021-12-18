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
import global_settings
import json

#
#
#

def recommended_courses(request):
	if not account.verify_student(request):	
		return render(request,'info.html',{'info':"Not logged in as student or account has been deactivated."})
		
	s_current_classes=[]
	s_finished_classes=[]
	s_recommended_classes=[]
	
	# Get all courses that student is taking
	# Separate into current classes and finished classes.
	# Current classes will be checked for time conflict.
	# Finished classes checked for meeting prerequisites
	for student_class in models.StudentClass.objects.filter(student__registration__account=request.user):
		if student_class.status=="enrolled":
			s_current_classes.append(student_class)
		elif student_class.status=="finished":
			s_finished_classes.append(student_class)
	
	current_time=datetime.now().date()	
	
	#
	# This splitting method will combine to list courses from the department 
	# the student is enrolled in first (if any), so that when all courses 
	# are iterated below we will be checking courses from student's department 
	# first
	#
	department=models.Student.objects.get(registration__account=request.user).department
	
	##########################################11111111111111
	first_part_of_all_courses=models.Class.objects.filter(course__department=department,term__reg_start_date__lte=current_time,term__reg_end_date__gte=current_time)
	second_part_of_all_courses=models.Class.objects.filter(term__reg_start_date__lte=current_time,term__reg_end_date__gte=current_time).exclude(course__department=department)
	

	#Join together
	all_classes=[]
	for a in first_part_of_all_courses:
		all_classes.append(a)
	for b in second_part_of_all_courses:
		all_classes.append(b)
		
	for new_class in all_classes:
	
		#Only keep searching courses until  max. registration is reached
		if ( len(s_recommended_classes) + len(s_current_classes) >= global_settings.MAX_STUDENT_REG):
			break
		
		# See if current class to recommend conflicts with any
		# current courses the student is taking
		
		is_conflict=False
		for enrolled_class in s_current_classes:
			#Remember,enrolled_class is a StudentClass object
			# So StudentClass.myclass is the actual class object
			is_conflict = account.check_time_conflict(new_class,enrolled_class.myclass)
			#Break for first conflict found
			if is_conflict:
				break
		
		if is_conflict:
			continue
		
		# See if current class to recommend conflicts with
		# courses we recommended in previous iteration
		
		flag=False
		for new_class2 in s_recommended_classes:
			is_conflict = account.check_time_conflict(new_class,new_class2)
			#Break for first conflict found
			if is_conflict:
				flag=True
				break
		if flag:
			continue;
				
		#Get prerequisites
		prereq = models.CoursePrerequisite.objects.filter(course=new_class.course)
		flag=check_prereq(prereq,s_finished_classes)
		# Add to recommended list if prerequisite is met
		if flag:
			s_recommended_classes.append(new_class)
			
	return render(
		request,
		'all_courses.html',
		{
			#Sorting is very important, or else results will be
			#scattered on the webpage
			"classes":sorted(s_recommended_classes,key=lambda x: x.course.department.name),
			"prereq":models.CoursePrerequisite.objects.all(),
			"times":models.ClassTime.objects.all(),
			"departments":account.get_departments(),
			"user":request.user,
			"recommended_courses":True,
		}
	)

	
#
# Check prerequisites
#
def check_prereq(prereq,s_finished_classes):
	# Compare prerequisites with finished(completed) courses 
	flag=True
	for a in prereq:
		flag=False
		#For every completed course...
		for b in s_finished_classes:
			#If course is prerequisite course...
			if a.prerequisite == b.course.name_id:
				#Then flag it being so
				flag=True
				break
		if flag==False:
			break
	if flag:
		return True
	return False

#
# Drop a student course
#
	
def drop_course(request):
	info=""
	if account.verify_student(request):
		user=request.user.person
		if request.method == 'POST':
			try:
				current_time=datetime.now().date()
				for id in request.POST.getlist('courses_checkbox'):
					enrolled_course=models.StudentClass.objects.get(
						student=models.Student.objects.get(registration=user),
						status='enrolled',
						myclass__id=id
					)
					#Make sure we can withdraw from it by comparing time
					if (current_time <= enrolled_course.myclass.term.withdrawal_date):
						#Drop the course
						enrolled_course.delete()
						account.write_log("student","drop",request.user.id,id)
					else:
						info +=" You cannot drop " + enrolled_course.myclass.course.name + " "
				if info=="":
					return redirect('/student_courses/')
			except ValueError as error: 
				HttpResponse(error)
	return render(request,'info.html',{'info':info})
	
#
# Add course to student courses
#
def add_course(request):
	info=""
	if account.verify_student(request):
		user=request.user.person
		if request.method == 'POST':
			#Get courses the student is already taking
			enrolled_courses=models.StudentClass.objects.filter(student=models.Student.objects.get(registration=user),status='enrolled').count()
			new_courses=len(request.POST.getlist('courses_checkbox'))
			
			# Don't add courses if the number of new courses + current courses
			# is beyond total courses allowed
			if (enrolled_courses+new_courses > global_settings.MAX_STUDENT_REG):
				info= """The number of courses you selected 
						is beyond the maximum number allowed.
						Please select fewer courses and try again."""
				return render(request,'info.html',{'info':info})
				
			#Add each course selected (by id) to enrolled courses
			for id in request.POST.getlist('courses_checkbox'):
	
				#Don't add if already enrolled
				if (models.StudentClass.objects.filter(myclass__id=id,
						status='enrolled',
						student__registration__account=request.user).count() > 0):
					info+=" You're already enrolled in: "+models.Class.objects.get(id=id).course.name_id + ". "
					continue
				
				#Get class to add to student class list
				class_to_add=models.Class.objects.get(id=id)
				
				#Don't add if max students is reached
				student_enrollment=models.StudentClass.objects.filter(myclass=class_to_add,status='enrolled').count()
				if (student_enrollment > global_settings.MAX_STUDENT_ENROLLMENT):
					info= " Course " + class_to_add.course.name_id + " is full. "
					continue
				
				current_time=datetime.now().date()
				#Make sure course is within registration start/end times
				if (current_time <= class_to_add.term.reg_start_date) or (current_time > class_to_add.term.reg_end_date):
					info += " Registration times do not let you register for " + class_to_add.course.name + " "
					continue
					
				#Don't add if time conflicts with any enrolled courses
				conflict=False
				for enrolled in models.StudentClass.objects.filter(student__registration__account=request.user):
					if account.check_time_conflict(enrolled.myclass,class_to_add):
						info += class_to_add.course.name_id + " conflicts with " +enrolled.myclass.course.name_id + ". "
						conflict=True
				if conflict:
					continue
					
				#Make sure student meets the prerequisites
				prereq = models.CoursePrerequisite.objects.filter(course=class_to_add.course)
				finished_courses=models.StudentClass.objects.filter(student__registration=request.user.person,status="finished")
				tmp=[]
				for a in finished_courses:
					tmp.append(a.myclass)
				finished_courses=tmp
				flag=check_prereq(prereq,finished_courses)
				# Add to recommended list if prerequisite is met
				if not flag:
					info +=" You do not meet the prerequisites for "+class_to_add.course.name_id
					continue
			
				#No issues; add course to enrolled courses
				sc = models.StudentClass()
				sc.myclass=class_to_add
				sc.student=models.Student.objects.get(registration=user)
				sc.status='enrolled'
				sc.save()
				#Write it to log
				account.write_log("student","add",request.user.id,id)
				info+=sc.myclass.course.name_id + " added to enrolled courses. "
	
	#if ( len(info) > 1):
	return render(request,'info.html',{'info':info})
	#return redirect('/student_courses/')
#
# Get student courses
#
def student_courses(request):
	if account.verify_student(request):
		user=request.user.person
		classList=models.StudentClass.objects.filter(student=models.Student.objects.get(registration=user),status__in=['enrolled','billing'])
		
		classes=[]
		for myclass in classList:
			classes.append(myclass.myclass)
		return render(request,"enrolled_courses_student_professor.html",
			{"classes":
				classes
			}
		)
	info="Error. Not logged in as student or account has been deactivated."
	return render(request,'info.html',{'info':info})