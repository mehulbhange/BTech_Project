from flask import Flask,render_template,jsonify,request,url_for,redirect,session
from flask_pymongo import PyMongo #import PyMongo
from flask_mongoengine import MongoEngine
import json
import os
import sys
from pymongo import MongoClient #import Mongo Client
from bson.json_util import dumps #used to convert bson into json
from bson.objectid import ObjectId # used to generate random ids
from werkzeug.security import generate_password_hash,check_password_hash
from bson import json_util
from flask.helpers import flash


from gtts import gTTS
from time import sleep
import os
import pyglet

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')

app = Flask(__name__)
app.secret_key = "secretkey"
#Mongo connectivity
app.config['MONGO_URI'] = "mongodb://localhost:27017/E_Learning_System" 
mongo = PyMongo(app)

mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.E_Learning_System
user_data = db.get_collection('login_details')
admin_data = db.get_collection('admin_login')
pre_k_quiz_score = db.get_collection('pre_k_quiz_score')
contactUser = db.get_collection('user_quries')
grade_k_quiz_score = db.get_collection('grade_k_quiz_score')
teacher_details = db.get_collection('teacher_details')
grade_1_quiz_score = db.get_collection('grade_1_quiz_score')
#Progressbar
progress_bar = db.get_collection('progress_bar')



#This route the page to the home page 
@app.route('/')
def hello_world():
   return render_template('home.html')

##this is success page route
@app.route('/dashboard')
def dashboard():
   username = session['username']
   user_details = user_data.find_one({'userName':username})
   user_progress = progress_bar.find_one({'userName':username})
   user_name = user_details.get('userName')
   email_id = user_details.get('Email')
   city = user_details.get('City')
   name = user_details.get('fullName')
   progress = []

   if user_progress is None:
      pre_k_progress = 0
      grade_k_progress = 0
      grade_1_progress = 0
      grade_2_progress = 0
      progress.append(0)
      progress.append(0)
      progress.append(0)
      progress.append(0)
      #progress[pre_k_progress,grade_1_progress,grade_1_progress,grade_2_progress]
   else:
      pre_k_progress = user_progress.get('pre_k_progress')
      grade_k_progress = user_progress.get('grade_k_progress')
      grade_1_progress = user_progress.get('grade_1_progress')
      grade_2_progress = user_progress.get('grade_2_progress')
      progress.append(int(pre_k_progress))
      progress.append(int(grade_k_progress))
      progress.append(int(grade_1_progress))
      progress.append(int(grade_2_progress))
      #progress[pre_k_progress,grade_1_progress,grade_1_progress,grade_2_progress]  

   # print("Progress retrival :",progress)

   if 'grade' in session:
      pass
   else:
      session["grade"] = user_details.get('class')
   #if session['grade'] is None:
   
   return render_template("dashboard.html",username=user_name,email_id=email_id,name=name,s_class=session['grade'],progress=progress)


#admin login
@app.route('/adlogin',methods=['POST','GET'])
def adlogin():
   if request.method=='POST':
      #get the user input mail id 
      user_name = request.form.get("adminusername")
      # print(user_name)
      #get the user input password
      user_password = request.form.get("adminpassword")
      #get the user object which have Email equal to user input email
      #and password
      userName = admin_data.find_one({'adminusername' : user_name})
      # print(userName)
      user = userName.get('adminusername')
      #check users mail id and password 
      #if correct then redirect to the dashboard
      #else redirect to the loging page with error message
      if user == user_name and userName.get('adminpassword')==user_password:
         #return render_template('index.html',username=user_name,user=user)
         session['adminusername']=user_name
         return redirect(url_for('adDashboard',usernamef=user))
      else:
         #Invalid login credentials
         #redirect again to the login page and show error message
         return render_template('admin/adlogin.html',error_message="Invalid Credentials!")
   return render_template('admin/adlogin.html')

@app.route('/teacherlogin',methods=['POST','GET'])
def teacherlogin():
   if request.method=='POST':
      #get the user input mail id 
      teacher_name = request.form.get("teachername")
      teacher_grade = request.form.get("teachergrade")
      
      # print(user_name)
      #get the user input password
      #get the user object which have Email equal to user input email
      #and password
      userName = teacher_details.find_one({'teachername' : teacher_name})
      if userName is None:
         return render_template('admin/teacherlogin.html',error_message="Invalid Credentials!")      
      # print(userName)
      user = userName.get('teachername')

      #check users mail id and password 
      #if correct then redirect to the dashboard
      #else redirect to the loging page with error message
      if user == teacher_name and teacher_grade=="pre-k":
         #return render_template('index.html',username=user_name,user=user)
         return redirect(url_for('infoPreK'))
      elif user==teacher_name and teacher_grade=="grade-k":
         return redirect(url_for('infoGradeK'))
      elif user==teacher_name and teacher_grade=="grade-1":
         return redirect(url_for('infoGrade1'))
      else:
         #Invalid login credentials
         #redirect again to the login page and show error message
         return render_template('admin/teacherlogin.html',error_message="Invalid Credentials!")
   return render_template('admin/teacherlogin.html')


@app.route('/adDashboard')
def adDashboard():
   username = session['adminusername']
   # print(username)
   # print(username)
   return render_template('admin/adminHomepage.html',userName=username)

@app.route('/addteacher',methods =['POST','GET'])
def addteacher():
   username = session['adminusername']
   if request.method=="POST":
      tusername=request.form.get("name")
      tgrade=request.form.get("grade")
      existing_teacher=teacher_details.find_one({"teachername":tusername})
      if existing_teacher is None:
         teacher_details.insert(
            {
               "teachername":tusername,
               "teachergrade":tgrade
            }
         )
         # return redirect(url_for('addteacher',userName=username,message="Done"))
         print("new teacher added");
         return render_template('admin/addteacherDetails.html',message="Added Successfully!!!")
      else:
         print("existing user");
         return render_template('admin/addteacherDetails.html',message="Teacher Already Present!")
   #return redirect(url_for('addteacher',userName=username,message="Add teacher template"))

   # print(username)
   return render_template('admin/addTeacherDetails.html',userName=username)

@app.route('/remove',methods =['POST','GET'])
def remove():
   username = session['adminusername']
   if request.method=="POST":
      flag=0
      tusername=request.form.get("name")
      tgrade=request.form.get("grade")
      userName = teacher_details.find_one({'teachername' : tusername})
      if userName is None:
         flash("Not found")
         return redirect(url_for('remove',userName=username,message="not found"))
         # return render_template('admin/removeTeacher.html',userName=username,message="not found")
      else:
         userGrade= userName.get('teachergrade')
         if userName.get('teachername')==tusername and userGrade==tgrade:
            teacher_details.delete_one({'teachername' : tusername})
            flag=1
         else:
            flag=0
         if flag==1:
            return render_template('admin/removeTeacher.html',userName=username,message="Deleted!")
         else:
            return render_template('admin/removeTeacher.html',userName=username,message="Not found!")
      # print(userName)
      # print(userName)
      # user = userName.get('teachername')
      # print(user)

   return render_template('admin/removeTeacher.html',userName=username)

   # print(username)
   #return render_template('admin/removeTeacher.html',userName=username)


@app.route('/userquries')
def userquries():
   return render_template('admin/quries.html')

@app.route('/adminLogout')
def adminLogout():
   session.pop('adminusername',None)
   #session.clear()
   return render_template('admin/adlogin.html')
@app.route('/prekAdmin')
def prekAdmin():
   return render_template('admin/prek.html',userName=session['adminusername'])


@app.route('/infoPreK')
def infoPreK():
   # username = session['adminusername']
   innerList=[]
   outerList=[]
   markinner=[]
   marksouter=[]
   keyinner=[]
   keyouter=[]
   prek=user_data.find()
   prekmarks=pre_k_quiz_score.find()
   
   for i in prek:
      className=i.get("class")
      if className=="pre_k":
         innerList=[]
         uname=i.get("userName")
         email=i.get("Email")
         city=i.get("City")
         bd=i.get("birthDate")
         fn=i.get("fullName")
         cn=i.get("class")
         innerList.extend([uname,email,city,bd,fn,cn])
         outerList.append(innerList)
      else:
         pass
   for i in prekmarks:
      # print(i)
      markinner=[]
      keyinner=[]
      for j in i:
         # print(i[j])
         markinner.append(i[j])
         keyinner.append(j)
      # print(markinner)
      marksouter.append(markinner)
      keyouter.append(keyinner)
   
   # print(keyouter)
         # print(markinner)
   # print(markinner)
   # print(marksouter)
   # d1={}
   # d2={}
   # for i in prekmarks:
   #    for j in i:
   #       markinner.append(i[j])
   #       marksnames.append(markinner)
   # print(marksnames)
   # return render_template('admin/prek.html',username=username,preklist=outerList,marklist=markinner,marksnames=marksnames)
   # keyinner=[]
   # keyouter=[]
   # for i in prekmarks:
   # # print(i)
   #    keyinner=[]
   #    for j in i:
   #       # print(i[j])
   #       keyinner.append(j)
   #       print(j)
   #    # print(markinner)
   #    keyouter.append(keyinner)
   # print(keyouter)
   # length=len(outerList)
   print(outerList)
   return render_template('admin/prek.html',preklist=outerList,marksouter=marksouter,keyouter=keyouter)


@app.route('/infoGradeK')
def infoGradeK():
   # username = session['adminusername']
   innerList=[]
   outerList=[]
   gradek=user_data.find()
   gradekmarks=grade_k_quiz_score.find()
   markinner=[]
   marksouter=[]
   keyinner=[]
   keyouter=[]
   
   for i in gradek:
      className=i.get("class")
      if className=="grade_k":
         innerList=[]
         uname=i.get("userName")
         email=i.get("Email")
         city=i.get("City")
         bd=i.get("birthDate")
         fn=i.get("fullName")
         cn=i.get("class")
         innerList.extend([uname,email,city,bd,fn,cn])
         outerList.append(innerList)
      else:
         pass
      # mathMarks=marks.get('maths_counting_quiz1_score')
   # print(outerList) 
   for i in gradekmarks:
      # print(i)
      markinner=[]
      keyinner=[]
      for j in i:
         # print(i[j])
         markinner.append(i[j])
         keyinner.append(j)
      # print(markinner)
      marksouter.append(markinner)
      keyouter.append(keyinner)
   return render_template('admin/gradek.html',gradeklist=outerList,marksouter=marksouter,keyouter=keyouter)

@app.route('/infoGrade1')
def infoGrade1():
   # username = session['adminusername']
   innerList=[]
   outerList=[]
   grade1=user_data.find()
   grade1marks=grade_1_quiz_score.find()
   
   for i in grade1:
      className=i.get("class")
      if className=="grade_1":
         innerList=[]
         uname=i.get("userName")
         email=i.get("Email")
         city=i.get("City")
         bd=i.get("birthDate")
         fn=i.get("fullName")
         cn=i.get("class")
         innerList.extend([uname,email,city,bd,fn,cn])
         outerList.append(innerList)
      else:
         pass
      # mathMarks=marks.get('maths_counting_quiz1_score')
   # print(outerList) 

   marksouter=[]
   keyouter=[]
   for i in grade1marks:
      # print(i)
      markinner=[]
      keyinner=[]
      for j in i:
         # print(i[j])
         markinner.append(i[j])
         keyinner.append(j)
      # print(markinner)
      marksouter.append(markinner)
      keyouter.append(keyinner)
   print(keyouter)
   print(marksouter)
   return render_template('admin/grade1.html',grade1list=outerList,marksouter=marksouter,keyouter=keyouter)


#Route to the login page of the user
@app.route('/login', methods=['POST','GET'])
def login():
   if request.method=='POST':
      #get the user input mail id 
      user_email = request.form.get("inputEmail")
      #get the user input password
      user_password = request.form.get("inputPassword")
      #get the user object which have Email equal to user input email
      #and password
      user = user_data.find_one({'Email' : user_email})
      email = user.get('Email')
      user_name = user.get('userName')
      full_name = user.get('fullName')
      #check users mail id and password 
      #if correct then redirect to the dashboard
      #else redirect to the loging page with error message
      if email == user_email and check_password_hash(user.get('Password'),user_password):
         #return render_template('index.html',username=user_name,user=user)
         session['username']=user_name
         session['name']=full_name
         return redirect(url_for('dashboard',username=user_name))
      else:
         #Invalid login credentials
         #redirect again to the login page and show error message
         return render_template('auth/login.html',error_message="Invalid Credentials!")
   return render_template('auth/login.html')

#this is home page
#when user visit the site this comes first
@app.route('/home')
def home():
      #check  if user already logged in or not
      #if logged in then pass the username and name of user to the home template
      #else render the home template without user with sign in sign up options
      if 'username' in session:
         user_details = user_data.find_one({'userName':session['username']})
         username = user_details.get('userName')
         name = user_details.get('fullName')
         return render_template('home.html',username=username,name=name)
      return render_template('home.html')


@app.route('/index')
def index():
   username = session['username']
   user_details = user_data.find_one({'userName':username})
   user_name = user_details.get('userName')
   email_id = user_details.get('Email')
   city = user_details.get('City')
   name = user_details.get('fullName')
   return render_template('index.html',username=user_name,email_id=email_id,name=name)

@app.route('/contact',methods=['POST','GET'])
def contact():
   if request.method=="POST":
      uname=request.form.get("name")
      email=request.form.get("email")
      phone=request.form.get("phone")
      grade=request.form.get("grade")
      message=request.form.get("message")
      # print("user name:",uname,email,phone,message)
      contactUser.insert(
         {
            'name':uname,
            'email':email,
            'phone':phone,
            'grade':grade,
            'message':message
         }
      )
   return render_template('contact.html',username=session['username'],name=session['name'])

@app.route('/sessionUpdate', methods=['POST','GET'])
def sessionUpdate():
   username = session['username']
   user_details = user_data.find_one({'userName':username})
   user_progress = progress_bar.find_one({'userName':username})
   user_name = user_details.get('userName')
   email_id = user_details.get('Email')
   city = user_details.get('City')
   name = user_details.get('fullName')

   progress = []
   if user_progress is None:
      pre_k_progress = 0
      grade_k_progress = 0
      grade_1_progress = 0
      grade_2_progress = 0
      progress.append(0)
      progress.append(0)
      progress.append(0)
      progress.append(0)
      #progress[pre_k_progress,grade_1_progress,grade_1_progress,grade_2_progress]
   else:
      pre_k_progress = user_progress.get('pre_k_progress')
      grade_k_progress = user_progress.get('grade_k_progress')
      grade_1_progress = user_progress.get('grade_1_progress')
      grade_2_progress = user_progress.get('grade_2_progress')
      progress.append(int(pre_k_progress))
      progress.append(int(grade_k_progress))
      progress.append(int(grade_1_progress))
      progress.append(int(grade_2_progress))
      #progress[pre_k_progress,grade_1_progress,grade_1_progress,grade_2_progress]  

   print("Progress retrival :",progress)

   if request.method == "POST":
      req_data = request.get_json()
      stud_class = req_data['class']
      session.modified = True
      session['grade'] = stud_class
      print("session updated",session['grade'])
      return render_template("dashboard.html",username=user_name,email_id=email_id,name=name,s_class=session["grade"],progress=progress)
      #return redirect(url_for('dashboard',username=user_name))
      #return "working"

   return render_template("dashboard.html",username=user_name,email_id=email_id,name=name,s_class=session['grade'],progress=progress)


@app.route('/register', methods=['POST','GET'])
def register():
   if request.method == 'POST':
      user_name = request.form.get("username")
      email_id = request.form.get("inputEmail")
      password = request.form.get("inputPassword")
      retyped_password = request.form.get("retypedPassword")
      city = request.form.get("inputCity")
      dob = request.form.get("inputDOB")
      fname = request.form.get("fname")
      mname = request.form.get("mname")
      lname = request.form.get("lname")
      class_name = request.form.get("class_name")
      if class_name is None:
         class_name = "pre_k"
      checkbox = request.form.get("checkbox")
      name = fname+" "+mname +" "+lname

      #generate a password hash to securely store the password in database
      p_hash = generate_password_hash(password)
      #get username and email from existing database
      #and check if it already exists
      #if yes give error message
      #else proceed
      existing_username = user_data.find_one({'userName':user_name})
      if existing_username is None:
         existing_usermail = user_data.find_one({'Email':email_id})
         if existing_usermail is None:
            if password == retyped_password:
               user_data.insert(
                  {
                     'userName':user_name,
                     'Email':email_id,
                     'Password':p_hash,
                     'City':city,
                     'birthDate':dob,
                     'fullName': name,
                     'class': class_name
                  }
               )
            else:
               return render_template('auth/register.html',message="Password not matched!")
            if checkbox == "on":
               #if sign in is checked
               #then redirect to the index page
               session['username']=user_name
               session['name']=name
               # session['grade']=class_name
               session['grade']=class_name
               progress=[0,0,0,0]
               # print(user_name)
               # print(name)
               # print(dob)
               # print(email_id)
               # print(class_name)
               return render_template("dashboard.html",username=user_name,email_id=email_id,name=name,s_class=session['grade'],progress=progress)
            else:
               #if the sign in not checked 
               #then redirect to the login page and show success message
               return render_template('auth/login.html',message="Registered successfully! Please login")
         else:
            return render_template('auth/register.html',message="Email alredy exists!")
      else:
         return render_template('auth/register.html',message="Username alredy exists!")
      #return user_name+"<br>"+email_id+"<br>"+password+"<br>"+retypedPassword+"<br>"+city+"<br>"+dob
   return render_template('auth/register.html')


@app.route('/profile')
def profile():
   if 'username' in session:
      user_details = user_data.find_one({'userName':session['username']})
      username = user_details.get('userName')
      name = user_details.get('fullName')
      email = user_details.get('Email')
      city = user_details.get('City')
      dob = user_details.get('birthDate')
      className=user_details.get('class')
      
      d={}
      d2={}
      d3={}
      # mathMarks=marks.get('maths_counting_quiz1_score')
      if className== "grade_k":
         d={}
         d2={}
         d3={}
         marks=grade_1_quiz_score.find_one({'userName':session['username']})
         marks2=grade_k_quiz_score.find_one({'userName':session['username']})
         marks3=pre_k_quiz_score.find_one({'userName':session['username']})
         if marks==None and marks2==None and marks3==None:
            d={}
            d2={}
            d3={}
            return render_template('profile.html',username=username,name=name,email=email,city=city,dob=dob,s_class=session["grade"],d=d,d2=d2,d3=d3)      
         else:
            if marks!=None:
               for key in marks:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks[key],int):
                     d.update({key:marks[key]})
                     # print(key,marks[key])
                  else:
                     pass
            if marks2!=None:
               for key in marks2:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks2[key],int):
                     d2.update({key:marks2[key]})
                     # print(key,marks[key])
                  else:
                     pass
            if marks3!=None:
               for key in marks3:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks3[key],int):
                     d3.update({key:marks3[key]})
                     # print(key,marks[key])
                  else:
                     pass
      elif className== "pre_k":
         d={}
         d2={}
         d3={}
         marks=grade_1_quiz_score.find_one({'userName':session['username']})
         marks2=grade_k_quiz_score.find_one({'userName':session['username']})
         marks3=pre_k_quiz_score.find_one({'userName':session['username']})
         if marks==None and marks2==None and marks3==None:
            d={}
            d2={}
            d3={}
            return render_template('profile.html',username=username,name=name,email=email,city=city,dob=dob,s_class=session["grade"],d=d,d2=d2,d3=d3) 
         
         else:
            if marks!=None:
               for key in marks:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks[key],int):
                     d.update({key:marks[key]})
                     # print(key,marks[key])
                  else:
                     pass
            if marks2!=None:
               for key in marks2:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks2[key],int):
                     d2.update({key:marks2[key]})
                     # print(key,marks[key])
                  else:
                     pass
            if marks3!=None:
               for key in marks3:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks3[key],int):
                     d3.update({key:marks3[key]})
                     # print(key,marks[key])
                  else:
                     pass
      elif className== "grade_1":
         d={}
         d2={}
         d3={}
         marks=grade_1_quiz_score.find_one({'userName':session['username']})
         marks2=grade_k_quiz_score.find_one({'userName':session['username']})
         marks3=pre_k_quiz_score.find_one({'userName':session['username']})
         if marks==None and marks2==None and marks3==None:
            d={}
            d2={}
            d3={}
            return render_template('profile.html',username=username,name=name,email=email,city=city,dob=dob,s_class=session["grade"],d=d,d2=d2,d3=d3) 
         
         else:
            if marks!=None:
               for key in marks:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks[key],int):
                     d.update({key:marks[key]})
                     # print(key,marks[key])
                  else:
                     pass
            if marks2!=None:
               for key in marks2:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks2[key],int):
                     d2.update({key:marks2[key]})
                     # print(key,marks[key])
                  else:
                     pass
            if marks3!=None:
               for key in marks3:
                  # print(key)
                  # print(marks[key])
                  if isinstance(marks3[key],int):
                     d3.update({key:marks3[key]})
                     # print(key,marks[key])
                  else:
                     pass
      # print(d)
   return render_template('profile.html',username=username,name=name,email=email,city=city,dob=dob,s_class=session["grade"],d=d,d2=d2,d3=d3)

@app.route('/updateProfile')
def updateProfile():
   return render_template('profile.html')
   
@app.route('/about')
def about():
   return render_template('about.html',username=session['username'],name=session['name'])

@app.route('/aboutforAll')
def aboutforAll():
   return render_template('aboutforall.html')


@app.route('/index_2')
def index_2():
   return render_template('index_2.html')

@app.route('/cards')
def cards():
   return render_template('cards.html')

@app.route('/courses')
def courses():
   return render_template('courses.html',username=session['username'],name=session['name'])

@app.route('/demo_quize')
def demo_quize():
   return render_template('demo_quize.html',username=session['username'],name=session['name'])

@app.route('/quiz1')
def quiz1():
   return render_template('pre_k_english_quize_1.html',username=session['username'],name=session['name'])

@app.route('/quiz2')
def quiz2():
   return render_template('pre_k_english_quiz_2.html',username=session['username'],name=session['name'])  

@app.route('/logout')
def logout():
   session.pop('username',None)
   #session.clear()
   session.pop('grade',None)
   return render_template('home.html')

def changeColor():
   print("function called")

@app.route('/prek')
def prek():
   return render_template('coursesFolderPreK/courseInfoPrek.html',username=session['username'],name=session['name'])

@app.route('/gradek')
def gradek():
   return render_template('coursesFolderGradek/coursesinfoGradeK.html',username=session['username'],name=session['name'])

@app.route('/grade1')
def grade1():
   return render_template('coursesFolderGrade1/coursesInfoGrade1.html',username=session['username'],name=session['name'])

# @app.route('/grade2')
# def grade2():
#    return render_template('coursesFolderPreK/courseInfoGrade2.html',username=session['username'],name=session['name'])

@app.route('/chooseMath')
def chooseMath():
   return render_template('coursesFolderPreK/mathTopicChoose.html',username=session['username'],name=session['name'])

@app.route('/IntroNumbers')
def IntroNumbers():
   return render_template('coursesFolderPreK/subFolder/introNumbers1.html',username=session['username'],name=session['name'])

@app.route('/comparison')
def comparison():
   return render_template('coursesFolderPreK/subFolder/comparison.html',username=session['username'],name=session['name'])

@app.route('/intro2')
def intro2():
   return render_template('coursesFolderPreK/subFolder/introNumber2.html',username=session['username'],name=session['name'])

@app.route('/intro3')
def intro3():
   return render_template('coursesFolderPreK/subFolder/introNumber3.html',username=session['username'],name=session['name'])

@app.route('/intro4')
def intro4():
   return render_template('coursesFolderPreK/subFolder/introNumber4.html',username=session['username'],name=session['name'])

@app.route('/intro5')
def intro5():
   return render_template('coursesFolderPreK/subFolder/introNumber5.html',username=session['username'],name=session['name'])

@app.route('/comp')
def comp():
   return render_template('coursesFolderPreK/subFolder/comparison.html',username=session['username'],name=session['name'])

@app.route('/intro6')
def intro6():
   return render_template('coursesFolderPreK/subFolder/introNumber6.html',username=session['username'],name=session['name'])

@app.route('/intro7')
def intro7():
   return render_template('coursesFolderPreK/subFolder/introNumber7.html',username=session['username'],name=session['name'])

@app.route('/intro8')
def intro8():
   return render_template('coursesFolderPreK/subFolder/introNumber8.html',username=session['username'],name=session['name'])

@app.route('/intro9')
def intro9():
   return render_template('coursesFolderPreK/subFolder/introNumber9.html',username=session['username'],name=session['name'])

@app.route('/intro10')
def intro10():
   return render_template('coursesFolderPreK/subFolder/introNumber10.html',username=session['username'],name=session['name'])

@app.route('/solveQuiz')
def solveQuiz():
   return render_template('coursesFolderPreK/subFolder/solveQuiz.html',username=session['username'],name=session['name'])

@app.route('/femo1')
def femo1():
   return render_template('coursesFolderPreK/comparisionTopic/moreFew1.html',username=session['username'],name=session['name'])

@app.route('/femo2')
def femo2():
   return render_template('coursesFolderPreK/comparisionTopic/moreFew2.html',username=session['username'],name=session['name'])

@app.route('/femo3')
def femo3():
   return render_template('coursesFolderPreK/comparisionTopic/moreFew3.html',username=session['username'],name=session['name'])

@app.route('/sd1')
def sd1():
   return render_template('coursesFolderPreK/comparisionTopic/sameDifferent1.html',username=session['username'],name=session['name'])

@app.route('/sd2')
def sd2():
   return render_template('coursesFolderPreK/comparisionTopic/sameDifferent2.html',username=session['username'],name=session['name'])

@app.route('/bigsmall')
def bigsmall():
   return render_template('coursesFolderPreK/comparisionTopic/bigSmall.html',username=session['username'],name=session['name'])

@app.route('/quizSolve')
def quizSolve():
   return render_template('coursesFolderPreK/comparisionTopic/quizSolve.html',username=session['username'],name=session['name'])

@app.route('/shapename')
def shapename():
   return render_template('coursesFolderPreK/geometry/shapeName.html',username=session['username'],name=session['name'])

@app.route('/circle')
def circle():
   return render_template('coursesFolderPreK/geometry/circle.html',username=session['username'],name=session['name'])

@app.route('/triangle')
def triangle():
   return render_template('coursesFolderPreK/geometry/triangle.html',username=session['username'],name=session['name'])

@app.route('/rectangle')
def rectangle():
   return render_template('coursesFolderPreK/geometry/rectangle.html',username=session['username'],name=session['name'])

@app.route('/solveQuiz1')
def solveQuiz1():
   return render_template('coursesFolderPreK/comparisionTopic/quizSolve.html',username=session['username'],name=session['name'])

@app.route('/square')
def square():
   return render_template('coursesFolderPreK/geometry/square.html',username=session['username'],name=session['name'])

@app.route('/leftright')
def leftright():
   return render_template('coursesFolderPreK/position/leftRight.html',username=session['username'],name=session['name'])
@app.route('/longshort')
def longshort():
   return render_template('coursesFolderPreK/comparisionTopic/longShort.html',username=session['username'],name=session['name'])

@app.route('/solvequiz')
def solvequiz():
   return render_template('coursesFolderPreK/position/solvequiz.html',username=session['username'],name=session['name'])

@app.route('/coins')
def coins():
   return render_template('coursesFolderPreK/coins/coin.html',username=session['username'],name=session['name'])

@app.route('/coinquiz')
def coinquiz():
   return render_template('coursesFolderPreK/coins/coinquiz.html',username=session['username'],name=session['name'])

@app.route('/engtopic')
def engtopic():
   return render_template('coursesFolderPreK/english/engtopselection.html',username=session['username'],name=session['name'])

@app.route('/eng1')
def eng1():
   return render_template('coursesFolderPreK/english/englishtopics/introEnglish1.html',username=session['username'],name=session['name'])

@app.route('/eng2')
def eng2():
   return render_template('coursesFolderPreK/english/englishtopics/introEnglish2.html',username=session['username'],name=session['name'])

@app.route('/equiz')
def equiz():
   return render_template('coursesFolderPreK/english/englishtopics/quiz.html',username=session['username'],name=session['name'])

@app.route('/uppercase')
def uppercase():
   return render_template('coursesFolderPreK/english/englishtopics/uppercase.html',username=session['username'],name=session['name'])

@app.route('/lowercase')
def lowercase():
   return render_template('coursesFolderPreK/english/englishtopics/lowercase.html',username=session['username'],name=session['name'])

@app.route('/difful')
def difful():
   return render_template('coursesFolderPreK/english/englishtopics/diffUL.html',username=session['username'],name=session['name'])

@app.route('/vowel')
def vowel():
   return render_template('coursesFolderPreK/english/englishtopics/vowels.html',username=session['username'],name=session['name'])

@app.route('/consonent')
def consonent():
   return render_template('coursesFolderPreK/english/englishtopics/consonent.html',username=session['username'],name=session['name'])

@app.route('/birds')
def birds():
   return render_template('coursesFolderPreK/english/englishtopics/bird.html',username=session['username'],name=session['name'])

@app.route('/animals')
def animals():
   return render_template('coursesFolderPreK/english/englishtopics/animal.html',username=session['username'],name=session['name'])

@app.route('/humanparts')
def humanparts():
   return render_template('coursesFolderPreK/gk/humanBody.html',username=session['username'],name=session['name'])

@app.route('/humanparts2')
def humanparts2():
   return render_template('coursesFolderPreK/gk/humanBody2.html',username=session['username'],name=session['name'])

@app.route('/other')
def other():
   return render_template('coursesFolderPreK/gk/other.html',username=session['username'],name=session['name'])


#quizes
@app.route('/grade_1_quiz_list')
def grade_1_quiz_list():
   return render_template('grade_1_quiz_list.html',username=session['username'],name=session['name'])   


@app.route('/pre_k_quiz_list')
def pre_k_quiz_list():
   return render_template('pre_k_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/pre_k_maths_quiz_list')
def pre_k_maths_quiz_list():
   return render_template('PrekQuiz/maths/pre_k_maths_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/pre_k_english_quiz_list')
def pre_k_english_quiz_list():
   return render_template('PrekQuiz/english/pre_k_english_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/pre_k_gk_quiz_list')
def pre_k_gk_quiz_list():
   return render_template('PrekQuiz/GK/pre_k_gk_quiz_list.html',username=session['username'],name=session['name'])


@app.route('/lowercase_quiz')
def lowercase_quiz():
   return render_template('PrekQuiz/english/lowercase_quiz.html',username=session['username'],name=session['name'])

@app.route('/uppercase_quiz')
def uppercase_quiz():
   return render_template('PrekQuiz/english/uppercase_quiz.html',username=session['username'],name=session['name'])


@app.route('/intro_quiz')
def intro_quiz():
   return render_template('PrekQuiz/english/intro_to_alphabets.html',username=session['username'],name=session['name'])

@app.route('/consonants_vowels_quiz')
def consonants_vowels_quiz():
   return render_template('PrekQuiz/english/consonants_vowels_quiz.html',username=session['username'],name=session['name'])

@app.route('/animals_birds_quiz')
def animals_birds_quiz():
   return render_template('PrekQuiz/english/animals_birds_quiz.html',username=session['username'],name=session['name'])



# Maths quizes 
@app.route('/maths_quiz1')
def maths_quiz1():
   return render_template('PrekQuiz/maths/maths_quiz_1.html',username=session['username'],name=session['name'])  

@app.route('/counting_quiz')
def counting_quiz():
   return render_template('PrekQuiz/maths/counting_quiz.html',username=session['username'],name=session['name'])  

@app.route('/shapes_quiz')
def shapes_quiz():
   return render_template('PrekQuiz/maths/shapes_quiz.html',username=session['username'],name=session['name'])  


@app.route('/intro_to_coins_quiz')
def intro_to_coins_quiz():
   return render_template('PrekQuiz/maths/intro_to_coins_quiz.html',username=session['username'],name=session['name'])  

@app.route('/comparison_quiz')
def comparison_quiz():
   return render_template('PrekQuiz/maths/comparison_quiz.html',username=session['username'],name=session['name'])


#GK quizes
@app.route('/human_bodyparts_quiz')
def human_bodyparts_quiz():
   return render_template('PrekQuiz/gk/human_bodyparts_quiz.html',username=session['username'],name=session['name'])


@app.route('/setProgress',methods=['POST','GET'])
def setProgress():
   user_name = session['username']
   #print("username ", user_name)
   if request.method == "POST":
      req_data = request.get_json()
      stud_class = req_data['class']
      progress = req_data['progress']
      visit_id = req_data['_id']
      existing_user = progress_bar.find_one({'userName':user_name})
      if existing_user is None:
         if stud_class == "pre_k":
            progress_bar.insert({
            'userName': user_name,
            'pre_k_progress' : progress,
            'pre_k_visited' : [visit_id],
            'grade_k_progress' : 0,
            'grade_k_visited' : [],
            'grade_1_progress' : 0,
            'grade_1_visited' : [],
            'grade_2_progress' : 0,
            'grade_2_visited' : []  
            })
         elif stud_class == "grade_k":
            progress_bar.insert({
            'userName': user_name,
            'pre_k_progress' : 0,
            'pre_k_visited' : [],
            'grade_k_progress' : progress,
            'grade_k_visited' : [visit_id],
            'grade_1_progress' : 0,
            'grade_1_visited' : [],
            'grade_2_progress' : 0,
            'grade_2_visited' : []
            })
         elif stud_class == "grade_1":
            progress_bar.insert({
            'userName': user_name,
            'pre_k_progress' : 0,
            'pre_k_visited' : [],
            'grade_k_progress' : 0,
            'grade_k_visited' : [],
            'grade_1_progress' : progress,
            'grade_1_visited' : [visit_id],
            'grade_2_progress' : 0,
            'grade_2_visited' : [] 
            })
         else:
            progress_bar.insert({
            'userName': user_name,
            'pre_k_progress' : 0,
            'pre_k_visited' : [],
            'grade_k_progress' : 0,
            'grade_k_visited' : [],
            'grade_1_progress' : 0,
            'grade_1_visited' : [],
            'grade_2_progress' : progress,
            'grade_2_visited' : [visit_id]  
            })
         
      else:
         if stud_class == "pre_k":
            pre_k_progress = existing_user.get('pre_k_progress')
            pre_k_progress = pre_k_progress + progress
            if pre_k_progress > 100:
               pre_k_progress = 100
            pre_k_visited = existing_user.get('pre_k_visited')
      
            if visit_id in pre_k_visited:
               pass
            else:
               print("pre k operations")
               pre_k_visited.append(visit_id)
               print("Executed : else block")
               progress_bar.update_one(
                  {'userName':user_name},
                  {
                     "$set": {
                        'pre_k_progress': pre_k_progress,
                        'pre_k_visited' : pre_k_visited
                     }
               
                  }
               )
            
         elif stud_class == "grade_k":
            grade_k_progress = existing_user.get('grade_k_progress')
            grade_k_progress = grade_k_progress + progress
            if grade_k_progress > 100:
               grade_k_progress = 100
            grade_k_visited = existing_user.get('grade_k_visited')
      
            if visit_id in grade_k_visited:
               pass
            else:
               print("grade k operations")
               grade_k_visited.append(visit_id)
               progress_bar.update_one(
               {'userName':user_name},
               {
                  "$set": {
                     'grade_k_progress': grade_k_progress,
                     'grade_k_visited' : grade_k_visited
                  }
               
               }
            )   
         
         elif stud_class == "grade_1":
            grade_1_progress = existing_user.get('grade_1_progress')
            grade_1_progress = grade_1_progress + progress
            if grade_1_progress > 100:
               grade_1_progress = 100
            grade_1_visited = existing_user.get('grade_1_visited')
      
            if visit_id in grade_1_visited:
               pass
            else:
               print("grade 1 operations")
               print("List before : ",grade_1_visited)
               grade_1_visited.append(visit_id)
               print("List after : ",grade_1_visited)
               progress_bar.update_one(
               {'userName':user_name},
               {
                  "$set": {
                     'grade_1_progress': grade_1_progress,
                     'grade_1_visited' : grade_1_visited
                  }
               
               }
            )


   else:
      "Something went wrong"


@app.route('/getScore',methods=['POST','GET'])
def getScore():
   if request.method == "POST":
      req_data = request.get_json()
      stud_class = None

      user_name = session['username']
      quiz_name = req_data['quiz_name']
      stud_class = req_data['class']
      user_score = req_data['score']

      if stud_class == "pre_k": 
         existing_user = pre_k_quiz_score.find_one({'userName':user_name})
         if existing_user is None:
            pre_k_quiz_score.insert(
                        {
                           'userName': user_name,
                           quiz_name : quiz_name,
                           quiz_name+'_score' : user_score
                        })
         else:
            pre_k_quiz_score.update({
                           'userName': user_name},
                           {
                              "$set":{
                                    quiz_name:quiz_name,
                                    quiz_name+'_score' : user_score
                                 }
                              })
      elif stud_class == "grade_k": 
         existing_user = grade_k_quiz_score.find_one({'userName':user_name})
         if existing_user is None:
            grade_k_quiz_score.insert(
                        {
                           'userName': user_name,
                           quiz_name : quiz_name,
                           quiz_name+'_score' : user_score
                        })
         else:
            grade_k_quiz_score.update({
                           'userName': user_name},
                           {
                              "$set":{
                                    quiz_name:quiz_name,
                                    quiz_name+'_score' : user_score
                                 }
                              })
      elif stud_class == "grade_1":
         existing_user = grade_1_quiz_score.find_one({'userName':user_name})
         if existing_user is None:
            grade_1_quiz_score.insert(
                        {
                           'userName': user_name,
                           quiz_name : quiz_name,
                           quiz_name+'_score' : user_score
                        })
         else:
            grade_1_quiz_score.update({
                           'userName': user_name},
                           {
                              "$set":{
                                    quiz_name:quiz_name,
                                    quiz_name+'_score' : user_score
                                 }
                              })
            
   else:
      return "something went wrong!"
   


@app.route('/readQuestion',methods=['POST','GET'])
def readQuestion():
   if request.method == "POST":
      req_data = request.get_json()     
      question = req_data['question']
      tts = gTTS(text=question, lang='en')
      filename = 'temp.mp3'
      tts.save(filename)
      music = pyglet.media.load(filename, streaming=False)
      music.play()
      sleep(music.duration) #prevent from killing
      os.remove(filename) #remove temperory file

#grade K starts here
@app.route('/quizGradek')
def quizGradek():
   return render_template('coursesFolderGradek/maths/counting/howToSolveQuiz.html',username=session['username'],name=session['name'])
@app.route('/engtopselection')
def engtopselection():
   return render_template('coursesFolderGradek/english/englishTopicSelection.html',username=session['username'],name=session['name'])

@app.route('/alpharev')
def alpharev():
   return render_template('coursesFolderGradek/english/alphaRev.html',username=session['username'],name=session['name'])

@app.route('/quizgk')
def quizgk():
   return render_template('coursesFolderGradek/english/quizgk.html',username=session['username'],name=session['name'])

@app.route('/vocorev')
def vocorev():
   return render_template('coursesFolderGradek/english/vocorev.html',username=session['username'],name=session['name'])

@app.route('/shortword1')
def shortword1():
   return render_template('coursesFolderGradek/english/shortWord1.html',username=session['username'],name=session['name'])

@app.route('/shortword2')
def shortword2():
   return render_template('coursesFolderGradek/english/shortWord2.html',username=session['username'],name=session['name'])

@app.route('/shortword3')
def shortword3():
   return render_template('coursesFolderGradek/english/shortWord3.html',username=session['username'],name=session['name'])

@app.route('/shortword4')
def shortword4():
   return render_template('coursesFolderGradek/english/shortWord4.html',username=session['username'],name=session['name'])

@app.route('/eachwordalpha')
def eachwordalpha():
   return render_template('coursesFolderGradek/english/eachalphaword.html',username=session['username'],name=session['name'])

@app.route('/shortsen1')
def shortsen1():
   return render_template('coursesFolderGradek/english/shortSen1.html',username=session['username'],name=session['name'])

@app.route('/shortsen2')
def shortsen2():
   return render_template('coursesFolderGradek/english/shortsen2.html',username=session['username'],name=session['name'])

@app.route('/opposites')
def opposites():
   return render_template('coursesFolderGradek/english/opposite.html',username=session['username'],name=session['name'])
@app.route('/opposites2')
def opposites2():
   return render_template('coursesFolderGradek/english/opposites2.html',username=session['username'],name=session['name'])
@app.route('/jumbled')
def jumbled():
   return render_template('coursesFolderGradek/english/jumbled.html',username=session['username'],name=session['name'])
@app.route('/mathTopicSelection')
def mathTopicSelection():
   return render_template('coursesFolderGradek/maths/mathTopicSelection.html',username=session['username'],name=session['name'])
@app.route('/numbers1to10')
def numbers1to10():
   return render_template('coursesFolderGradek/maths/counting/numbers1to10.html',username=session['username'],name=session['name'])
@app.route('/numbers11to20')
def numbers11to20():
   return render_template('coursesFolderGradek/maths/counting/numbers11to20.html',username=session['username'],name=session['name'])
@app.route('/numbers21to30')
def numbers21to30():
   return render_template('coursesFolderGradek/maths/counting/numbers21to30.html',username=session['username'],name=session['name'])
@app.route('/numbers31to40')
def numbers31to40():
   return render_template('coursesFolderGradek/maths/counting/numbers31to40.html',username=session['username'],name=session['name'])
@app.route('/numbers41to50')
def numbers41to50():
   return render_template('coursesFolderGradek/maths/counting/numbers41to50.html',username=session['username'],name=session['name'])

@app.route('/basicshapes')
def basicshapes():
   return render_template('coursesFolderGradek/maths/shapes/basicShapes.html',username=session['username'],name=session['name'])

@app.route('/sphere')
def sphere():
   return render_template('coursesFolderGradek/maths/shapes/sphere.html',username=session['username'],name=session['name'])

@app.route('/cylinder')
def cylinder():
   return render_template('coursesFolderGradek/maths/shapes/cylinder.html',username=session['username'],name=session['name'])
@app.route('/cone')
def cone():
   return render_template('coursesFolderGradek/maths/shapes/cone.html',username=session['username'],name=session['name'])
@app.route('/cube')
def cube():
   return render_template('coursesFolderGradek/maths/shapes/cube.html',username=session['username'],name=session['name'])
@app.route('/comp1')
def comp1():
   return render_template('coursesFolderGradek/maths/comparision/comp1.html',username=session['username'],name=session['name'])
@app.route('/comp2')
def comp2():
   return render_template('coursesFolderGradek/maths/comparision/comp2.html',username=session['username'],name=session['name'])
@app.route('/comp3')
def comp3():
   return render_template('coursesFolderGradek/maths/comparision/comp3.html',username=session['username'],name=session['name'])
@app.route('/add1')
def add1():
   return render_template('coursesFolderGradek/maths/addition/add1.html',username=session['username'],name=session['name'])
@app.route('/add2')
def add2():
   return render_template('coursesFolderGradek/maths/addition/add2.html',username=session['username'],name=session['name'])
@app.route('/add3')
def add3():
   return render_template('coursesFolderGradek/maths/addition/add3.html',username=session['username'],name=session['name'])

@app.route('/sub1')
def sub1():
   return render_template('coursesFolderGradek/maths/subtraction/sub1.html',username=session['username'],name=session['name'])
@app.route('/sub2')
def sub2():
   return render_template('coursesFolderGradek/maths/subtraction/sub2.html',username=session['username'],name=session['name'])
@app.route('/sub3')
def sub3():
   return render_template('coursesFolderGradek/maths/subtraction/sub3.html',username=session['username'],name=session['name'])





@app.route('/anm1')
def anm1():
   return render_template('coursesFolderGradek/gk/animal1.html',username=session['username'],name=session['name'])

@app.route('/anm2')
def anm2():
   return render_template('coursesFolderGradek/gk/animal2.html',username=session['username'],name=session['name'])
@app.route('/fish')
def fish():
   return render_template('coursesFolderGradek/gk/fish.html',username=session['username'],name=session['name'])
@app.route('/plants')
def plants():
   return render_template('coursesFolderGradek/gk/plants.html',username=session['username'],name=session['name'])

@app.route('/country')
def country():
   return render_template('coursesFolderGradek/gk/mycountry.html',username=session['username'],name=session['name'])

@app.route('/drawingBoard')
def drawingBoard():
   return render_template('drawingBoard.html',username=session['username'],name=session['name'])

@app.route('/memorygame')
def memorygame():
   return render_template('games/memorygame.html')
@app.route('/memorygameadvance')
def memorygameadvance():
   return render_template('games/memorygameadvance.html')

@app.route('/additiongame')
def additiongame():
   return render_template('games/additiongame.html')


@app.route('/subtractiongame')
def subtractiongame():
   return render_template('games/subtractiongame.html')

@app.route('/tictactoe')
def tictactoe():
   return render_template('games/tictactoe.html')

@app.route('/puzzle')
def puzzle():
   return render_template('games/puzzle.html')

@app.route('/choosegame')
def choosegame():
   return render_template('games/chooseGame.html',username=session['username'],name=session['name'])

# Grade k quiz routes
# for all subjects
@app.route('/grade_k_quiz_list')
def grade_k_quiz_list():
   return render_template('grade_k_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/grade_k_maths_quiz_list')
def grade_k_maths_quiz_list():
   return render_template('gradekQuiz/Maths/grade_k_maths_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/grade_k_english_quiz_list')
def grade_k_english_quiz_list():
   return render_template('gradekQuiz/English/grade_k_english_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/grade_k_gk_quiz_list')
def grade_k_gk_quiz_list():
   return render_template('gradekQuiz/GK/grade_k_gk_quiz_list.html',username=session['username'],name=session['name'])

# Grade k Maths quizes
@app.route('/grade_k_shapes_quiz1')
def grade_k_shapes_quiz1():
   return render_template('gradekQuiz/Maths/grade_k_shapes_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_counting_quiz1')
def grade_k_counting_quiz1():
   return render_template('gradekQuiz/Maths/grade_k_counting_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_addition_quiz1')
def grade_k_addition_quiz1():
   return render_template('gradekQuiz/Maths/grade_k_addition_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_subtraction_quiz1')
def grade_k_subtraction_quiz1():
   return render_template('gradekQuiz/Maths/grade_k_subtraction_quiz1.html',username=session['username'],name=session['name'])

#Grade K English Quizes
@app.route('/grade_k_alphabets_quiz1')
def grade_k_alphabets_quiz1():
   return render_template('gradekQuiz/English/grade_k_alphabets_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_consonants_vowels_revision_quiz1')
def grade_k_consonants_vowels_revision_quiz1():
   return render_template('gradekQuiz/English/grade_k_consonants_vowels_revision_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_shortwords_quiz1')
def grade_k_shortwords_quiz1():
   return render_template('gradekQuiz/English/grade_k_shortwords_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_short_sentence_quiz1')
def grade_k_short_sentence_quiz1():
   return render_template('gradekQuiz/English/grade_k_short_sentence_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_oppositewords_quiz1')
def grade_k_oppositewords_quiz1():
   return render_template('gradekQuiz/English/grade_k_oppositewords_quiz1.html',username=session['username'],name=session['name'])

# Grade K GK quizes
@app.route('/grade_k_animals_birds_quiz1')
def grade_k_animals_birds_quiz1():
   return render_template('gradekQuiz/GK/grade_k_animals_birds_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_plants_quiz1')
def grade_k_plants_quiz1():
   return render_template('gradekQuiz/GK/grade_k_plants_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_k_fish_quiz1')
def grade_k_fish_quiz1():
   return render_template('gradekQuiz/GK/grade_k_fish_quiz1.html',username=session['username'],name=session['name'])


#Grade 1 Quiz Lists
@app.route('/grade_1_maths_quiz_list')
def grade_1_maths_quiz_list():
   return render_template('grade1Quiz/Maths/grade_1_maths_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/grade_1_english_quiz_list')
def grade_1_english_quiz_list():
   return render_template('grade1Quiz/English/grade_1_english_quiz_list.html',username=session['username'],name=session['name'])

@app.route('/grade_1_gk_quiz_list')
def grade_1_gk_quiz_list():
   return render_template('grade1Quiz/GK/grade_1_gk_quiz_list.html',username=session['username'],name=session['name'])



#Grade 1 Maths Quizes
@app.route('/grade_1_counting_quiz1')
def grade_1_counting_quiz1():
   return render_template('grade1Quiz/Maths/grade_1_counting_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_addition_quiz1')
def grade_1_addition_quiz1():
   return render_template('grade1Quiz/Maths/grade_1_addition_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_subtraction_quiz1')
def grade_1_subtraction_quiz1():
   return render_template('grade1Quiz/Maths/grade_1_subtraction_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_multiplication_quiz1')
def grade_1_multiplication_quiz1():
   return render_template('grade1Quiz/Maths/grade_1_multiplication_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_division_quiz1')
def grade_1_division_quiz1():
   return render_template('grade1Quiz/Maths/grade_1_division_quiz1.html',username=session['username'],name=session['name'])


# Grade 1 English Quizes

@app.route('/grade_1_wordsandsentences_quiz1')
def grade_1_wordsandsentences_quiz1():
   return render_template('grade1Quiz/English/grade_1_wordsandsentences_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_partsofspeech_quiz1')
def grade_1_partsofspeech_quiz1():
   return render_template('grade1Quiz/English/grade_1_partsofspeech_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_alphabeticalorder_quiz1')
def grade_1_alphabeticalorder_quiz1():
   return render_template('grade1Quiz/English/grade_1_alphabeticalorder_quiz1.html',username=session['username'],name=session['name'])


# Grade 1 GK Quizes

@app.route('/grade_1_coloursandshapes_quiz1')
def grade_1_coloursandshapes_quiz1():
   return render_template('grade1Quiz/GK/grade_1_coloursandshapes_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_signals_quiz1')
def grade_1_signals_quiz1():
   return render_template('grade1Quiz/GK/grade_1_signals_quiz1.html',username=session['username'],name=session['name'])

@app.route('/grade_1_community_quiz1')
def grade_1_community_quiz1():
   return render_template('grade1Quiz/GK/grade_1_community_quiz1.html',username=session['username'],name=session['name'])


# Drawing Board 
@app.route('/drawing_board')
def drawing_board():
   return render_template('drawing_board.html')

#grade1
@app.route('/coursesGrade1')
def coursesGrade1():
   return render_template('coursesFolderGrade1/coursesInfoGrade1.html',username=session['username'],name=session['name'])

@app.route('/englishtopics')
def englishtopics():
   return render_template('coursesFolderGrade1/english/englishTopics.html',username=session['username'],name=session['name'])
@app.route('/mathtopics')
def mathtopics():
   return render_template('coursesFolderGrade1/maths/mathtopics.html',username=session['username'],name=session['name'])
@app.route('/gktopic')
def gktopic():
   return render_template('coursesFolderGrade1/gk/gktopics.html',username=session['username'],name=session['name'])
@app.route('/colorsGrdae1')
def colorsGrdae1():
   return render_template('coursesFolderGrade1/gk/topics/colors.html',username=session['username'],name=session['name'])
@app.route('/shapesgrade1')
def shapesgrade1():
   return render_template('coursesFolderGrade1/gk/topics/shapes.html',username=session['username'],name=session['name'])
@app.route('/quizgrade1')
def quizgrade1():
   return render_template('coursesFolderGrade1/gk/topics/quiz.html',username=session['username'],name=session['name'])
@app.route('/traffic')
def traffic():
   return render_template('coursesFolderGrade1/gk/topics/traffic.html',username=session['username'],name=session['name'])
@app.route('/saftey')
def saftey():
   return render_template('coursesFolderGrade1/gk/topics/saftey.html',username=session['username'],name=session['name'])

@app.route('/community')
def community():
   return render_template('coursesFolderGrade1/gk/topics/community.html',username=session['username'],name=session['name'])
@app.route('/habits')
def habits():
   return render_template('coursesFolderGrade1/gk/topics/habits.html',username=session['username'],name=session['name'])
@app.route('/clean')
def clean():
   return render_template('coursesFolderGrade1/gk/topics/clean.html',username=session['username'],name=session['name'])
@app.route('/counting100')
def counting100():
   return render_template('coursesFolderGrade1/maths/topics/counting/counting100.html',username=session['username'],name=session['name'])
@app.route('/counting10s')
def counting10s():
   return render_template('coursesFolderGrade1/maths/topics/counting/counting10s.html',username=session['username'],name=session['name'])
@app.route('/counting23s')
def counting23s():
   return render_template('coursesFolderGrade1/maths/topics/counting/counting23.html',username=session['username'],name=session['name'])
@app.route('/countingfb')
def countingfb():
   return render_template('coursesFolderGrade1/maths/topics/counting/countingfb.html',username=session['username'],name=session['name'])
@app.route('/additionnl')
def additionnl():
   return render_template('coursesFolderGrade1/maths/topics/additionSub/addition1.html',username=session['username'],name=session['name'])
@app.route('/additionwp')
def additionwp():
   return render_template('coursesFolderGrade1/maths/topics/additionSub/additionwp.html',username=session['username'],name=session['name'])
@app.route('/additionn')
def additionn():
   return render_template('coursesFolderGrade1/maths/topics/additionSub/additionn.html',username=session['username'],name=session['name'])
@app.route('/addition12')
def addition12():
   return render_template('coursesFolderGrade1/maths/topics/additionSub/addition12.html',username=session['username'],name=session['name'])
@app.route('/addition22')
def addition22():
   return render_template('coursesFolderGrade1/maths/topics/additionSub/addition22.html',username=session['username'],name=session['name'])
@app.route('/subnl')
def subnl():
   return render_template('coursesFolderGrade1/maths/topics/sub/subnl.html',username=session['username'],name=session['name'])
@app.route('/subwp')
def subwp():
   return render_template('coursesFolderGrade1/maths/topics/sub/subwp.html',username=session['username'],name=session['name'])
@app.route('/subswp')
def subswp():
   return render_template('coursesFolderGrade1/maths/topics/sub/subswp.html',username=session['username'],name=session['name'])
@app.route('/sub12')
def sub12():
   return render_template('coursesFolderGrade1/maths/topics/sub/sub12.html',username=session['username'],name=session['name'])
@app.route('/sub22')
def sub22():
   return render_template('coursesFolderGrade1/maths/topics/sub/sub22.html',username=session['username'],name=session['name'])
@app.route('/table1to10')
def table1to10():
   return render_template('coursesFolderGrade1/maths/topics/mathtable/table1to10.html',username=session['username'],name=session['name'])
@app.route('/cts')
def cts():
   return render_template('coursesFolderGrade1/maths/topics/mathtable/cts.html',username=session['username'],name=session['name'])
@app.route('/mult')
def mult():
   return render_template('coursesFolderGrade1/maths/topics/multiDiv/mult.html',username=session['username'],name=session['name'])
@app.route('/div')
def div():
   return render_template('coursesFolderGrade1/maths/topics/multiDiv/div.html',username=session['username'],name=session['name'])
@app.route('/words')
def words():
   return render_template('coursesFolderGrade1/english/topics/wordsen/words.html',username=session['username'],name=session['name'])
@app.route('/sentences')
def sentences():
   return render_template('coursesFolderGrade1/english/topics/wordsen/sentences.html',username=session['username'],name=session['name'])

@app.route('/noun')
def noun():
   return render_template('coursesFolderGrade1/english/topics/partsOfSpeech/noun.html',username=session['username'],name=session['name'])
@app.route('/pronoun')
def pronoun():
   return render_template('coursesFolderGrade1/english/topics/partsOfSpeech/pronoun.html',username=session['username'],name=session['name'])
@app.route('/adjective')
def adjective():
   return render_template('coursesFolderGrade1/english/topics/partsOfSpeech/adjective.html',username=session['username'],name=session['name'])
@app.route('/verb')
def verb():
   return render_template('coursesFolderGrade1/english/topics/partsOfSpeech/verb.html',username=session['username'],name=session['name'])
@app.route('/alphaletters')
def alphaletters():
   return render_template('coursesFolderGrade1/english/topics/alphabeticalOrder/letterAlpha.html',username=session['username'],name=session['name'])
@app.route('/alphawords')
def alphawords():
   return render_template('coursesFolderGrade1/english/topics/alphabeticalOrder/alphawords.html',username=session['username'],name=session['name'])
@app.route('/writingwords')
def writingwords():
   return render_template('coursesFolderGrade1/english/topics/writingExcercise/hearing.html',username=session['username'],name=session['name'])
@app.route('/writingsen')
def writingsen():
   return render_template('coursesFolderGrade1/english/topics/writingExcercise/writingsen.html',username=session['username'],name=session['name'])
@app.route('/writingpara')
def writingpara():
   return render_template('coursesFolderGrade1/english/topics/writingExcercise/writingpara.html',username=session['username'],name=session['name'])
@app.route('/literacyskills')
def literacyskills():
   return render_template('coursesFolderGrade1/english/topics/literacy/literacyskill.html',username=session['username'],name=session['name'])








if __name__ == '__main__':
   app.run()
