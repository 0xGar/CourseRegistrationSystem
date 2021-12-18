#
# Developed by David Harris (3276780)
#
#
#
# 

from django.db import models
from django.contrib.auth.models import User

#
# Profile information per account. Must link to Django's User 
# table so that this information can be accessed upon login
#
class Person(models.Model):
	first_name = models.CharField(max_length=50,blank=False)
	middle_name = models.CharField(max_length=50,blank=True)
	last_name = models.CharField(max_length=50,blank=False)
	date_of_birth = models.DateField(blank=False)
	email = models.CharField(max_length=50,blank=False)
	#Admin might not know offhand; that's ok at creation time
	phone_number = models.CharField(max_length=20,blank=True)
	street_name = models.CharField(max_length=50,blank=False)
	postal_code = models.CharField(max_length=50,blank=False)
	province = models.CharField(max_length=50,blank=False)
	country = models.CharField(max_length=50,blank=False)
	#"Professor","Student","Other". All lowercase. 
	account_type=models.CharField(max_length=10,blank=False)
	# Can be blank, but if account_type is student or professor
	# one of them must be set. Unfortunately there's no way to
	# ensure "one or the other must be set" within the definition of
	# the database itself.
	student = models.ForeignKey('Student',related_name='+',null=True)
	professor = models.ForeignKey('Professor',related_name='+',null=True)
	#Links to the User object that Django creates when a new account is made
	account=models.OneToOneField(User,null=False)
  #Is the account accepted/rejected (active/inactive)
	is_active=models.BooleanField(default=True)
  #For when user made his or her own account; needs to be approved
	pending_approval=models.BooleanField(default=False)
	# Need activation -> Does the user need to
	# 	do something to change initial default password?
	needs_activation=models.BooleanField(default=True)
#
# Information about students. Must link to Person 
#
class Student (models.Model):
	#is_active=models.BooleanField(default=True)
	department=models.ForeignKey('Department',related_name='+',null=False)
	#Links to Person class, which links to User class
	registration=models.ForeignKey('Person',related_name='+',null=False)

#
# Information about professors. Must link to Person 
#
class Professor (models.Model):
	#is_active=models.BooleanField(default=False)
	#Links to Person class, which links to User class
	registration=models.ForeignKey('Person',related_name='+',null=False)
	department=models.ForeignKey('Department',related_name='+',null=False)
	
#
# Indicates what courses the student is/has took. Links to student table.
#
class StudentClass(models.Model):
    #Must be linked to student and course
	student=models.ForeignKey('Student',related_name='+',null=False)
	myclass=models.ForeignKey('Class',related_name='+',null=False)
	#Options: "Enrolled","Withdrawn","Finished". All lowercase.
	status=models.CharField(max_length=10,blank=False)
	
#
# Indicates what courses professors is/has taught
#
class ProfessorClass(models.Model):
    #Must be linked to a professor & course
	professor=models.ForeignKey('Professor',related_name='+',null=False)
	myclass=models.ForeignKey('Class',related_name='+',null=False)
	#Options: "Teaching","Finished". All lowercase.
	status=models.CharField(max_length=10,blank=False)
	

#
# Contains ALL class times.
# All can be blank if dates unknown 
class ClassTime(models.Model):
	day=models.CharField(max_length=100,blank=True)
	start=models.CharField(max_length=10,blank=True)
	end=models.CharField(max_length=10,blank=True)
	#Must be linked to a course
	myclass = models.ForeignKey('Class',related_name='+',null=False)

#
# Contains prerequisite courses for all courses
# Linked to specific class as opposed to courses in general
# because prerequisites may change in time (e.g., setting
# up a class a year from now knowing prerequisites will be
# different than a class you're making this year)
class CoursePrerequisite(models.Model):
	course=models.ForeignKey('Course',related_name='+',null=False)
	prerequisite=models.CharField(max_length=50,blank=False)
	
#
# Contains ALL departments
#
class Department(models.Model):
	name=models.CharField(max_length=100,unique=True)

#
# Contains ALL courses. Class time specified in time table.
#
class Term(models.Model):
    #Fall, Winter,Summer
	name=models.CharField(max_length=10,blank=False)
	year=models.CharField(max_length=4,blank=False)
	reg_start_date=models.DateField(blank=True)
	reg_end_date=models.DateField(blank=True)
	withdrawal_date=models.DateField(blank=True)
	class Meta:
		unique_together = ('name', 'year',)

#
# Contains ALL Classes
#
class Class(models.Model):
	building=models.CharField(max_length=50,blank=True)
	class_start_date=models.DateField(blank=True)
	class_end_date=models.DateField(blank=True)
	#Values: "Active","Cancelled","Finished". All lowercase
	status=models.CharField(max_length=10,blank=False)
	#A course must be taught, but it can be decided later, so null=True
	professor=models.ForeignKey('Professor',related_name='+',null=True)
	term=models.ForeignKey('Term',related_name='+',null=False)
	course=models.ForeignKey('Course',related_name='+',null=False)
	
	#Set ordering for when iterated
	class Meta:
		ordering = ('term__name','course__department__name','course__name_id')

#
# Contains ALL courses.
#
class Course(models.Model):
	description=models.TextField(blank=True)
	#name_id, e.g, 2043
	name_id=models.CharField(max_length=50,blank=False)
	name=models.CharField(max_length=50,blank=False)
	#Subject,e.g., Psychology
	subject=models.CharField(max_length=50,blank=False)	
	# A department should be specified
	department=models.ForeignKey('Department',related_name='+',null=False)
	#Year--