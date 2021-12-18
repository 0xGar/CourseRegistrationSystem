#
# Developed by David Harris (3276780)
#
#
# Responsible for 
#	1, cancelling class once registration deadline is reached,
# 	2, Marking classes as finished
#	3, Sending info to billing system
#
# This needs to be ran once a day using a job scheduler of some sort
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
import global_settings

#
# Run every day at midnight
#
billing_info=""
#Current time
current_time=datetime.now().date()
#Get all active classes after registration date deadline
classes = models.Class.objects.filter(status='active',term__reg_end_date__lt=current_time)
#
# Now see if any class needs to be cancelled or to label it as done
#
for myclass in classes:
	#1. Check if class should be cancelled
	if models.StudentClass.filter(myclass=myclass).count() < global_settings.MIN_CLASS_ENROLLMENT:
		myclass.status='cancelled'
		myclass.save()
		#Update status of course for each student taking it
		for student_class in models.StudentClass.filter(myclass=myclass,status='enrolled'):
			student_class.status='cancelled'
			student_class.save()
			continue #Continue here since cancelled courses don't get labeled as finished
	#Class is finished, update class to specify so
	#end_d=datetime.strptime(myclass.class_end_date, "%Y-%M-%D").time()
	if (current_time > myclass.class_end_date):
		myclass.status='finished'
		myclass.save()
		# For every student taking the class,indicate its finished
		for student_class in models.StudentClass.filter(myclass=myclass,status='active'):
			student_class.status='finished'
			student_class.save()
		continue
		# For every professor teaching the class,indicate its finished
		for prof_class in models.ProfessorClass.filter(myclass=myclass,status='active'):
			prof_class.status='finished'
			prof_class.save()
		continue
	#
	# Only reach here if 1, class is active, reached registration deadline, but
	# course is not yet complete. This means it's time to send student to billing
	# for this class
	# For every student taking the class
	for student_class in models.StudentClass.filter(myclass=myclass,status='enrolled'):
		student_class.status='billing'
		student_class.save()
		# Add to billing file
		billing_info += "Profile ID: "+student_class.student.registration.id+"Course ID: "+student_class.myclass.id

if not billing_info == "":
	print ("hi")
	with open(os.path.join(BASE_DIR, "logs/billing_"+current_time.isoformat()+".txt"),'w') as file:
		file.write(billing_info)