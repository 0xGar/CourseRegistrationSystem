###################################################
# GLOBAL VARIABLES FOR ENTIRE PROGRAM             #
###################################################
#
# Edit these values to change how the software 
# operates for some features
#

import os

#Subjects offered
#Leave commented; not used
#SUBJECTS=[
#	"Computer Science",
#	"Psychology",
#	"Biology",
#	"Classics",
#	"Mathematics",
#	"Statistics",
#]

#Departments available by default
DEPARTMENTS=[
	"N/A",
	"Computer Science",
	"Arts",
	"Science",
	"Engineering",
	"Statistics",
]

#Course options available by default
COURSE_OPTIONS=[
	"CS2043",
	"CS3123",
	"PSYC1001",
	"PSYC1002",
]

MAX_STUDENT_ENROLLMENT=10 #Max class size
MIN_STUDENT_ENROLLMENT=6 #Min student enrollment

MAX_STUDENT_REG=4 #Max of X courses per student
MIN_PASSWORD_LENGTH=3
PW_MATCH_PATTERN="([A-Z]*[1-9]*)*" #Regex password pattern
PW_MATCH_PATTERN_ERROR="Passwords must be of length "+str(MIN_PASSWORD_LENGTH)

#Leave below code unaltered
#SUBJECTS.sort()
DEPARTMENTS.sort()
COURSE_OPTIONS.sort()
#Leave unaltered
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))