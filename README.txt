Source Code Credits:

./account/templatetags/* contents credited to
http://www.soyoucode.com/2011/set-variable-django-template

Various online documents were referenced (e.g., Django's and Python's
documentation) as well Google for some general program-specific 
commands

********************************************************************
* HOW TO RUN
********************************************************************

Windows:

> env_window/Scripts/activate.bat
> set PYTHONPATH=%PYTHONPATH%;c:\<PATH>\reg_sys\global
(navigate to reg_sys folder)
> python manage.py runserver

Now visit 127.0.0.1:8000

Linux:

You will need to install the proper version of
Python (3.x) and set it up so not recommended 
for testing purposes.

* To create additional superusers:
python manage.py createsuperuser

********************************************************************
* NOTES
********************************************************************

./diagrams/ contains the design diagrams
./documentations/ contains user's & programmer's documentation
./env_windows/
./env_window/ is the python virtual environment that makes running
this software on different systems possible without configuration
./reg_sys/ is the software itself

********************************************************************
* TESTING
********************************************************************

The following information and files discussed are for and exist for
testing purposes only.
 
The system has been set up with dummy accounts/courses.
The user accounts are made as follows:

username (admin): admin
password: admin

username: professor1
password: 123

username: professor2
password: 123

username: student1
password: 123

username: student2
password: 123

To make dummy accounts/courses when the database is 100% empty:

1. Start server (see above; How to run)
2. Visit 127.0.0.1:8000/fill_db

To delete the database and set it back up with fresh dummy account/courses:
(from root directory of this document)
1. Stop the server if running
2. Delete reg_sys/db.sqlite3
3. Delete reg_sys/reg_sys/__phycache__
4. Execute "python reg_sys/manage.py migrate --run-syncdb"
5. Start server
6. Visit 127.0.0.1:8000/fill_db to refill

But note this only makes course/accounts. You will have to sign in
to test the features (add courses, drop courses, and so on).