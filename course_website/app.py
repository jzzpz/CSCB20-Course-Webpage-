# some part are from the lecture code
from flask import Flask, session, redirect, url_for, escape, request, render_template, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from globals import AccountTypes # make code more clean
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'

db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():

    print(request.headers.get('User-Agent')) # what is this for?

    if request.method == 'POST':

        sql = """
			SELECT *
			FROM users WHERE username='{}' AND password='{}'
			""".format(request.form['username'], request.form['password']) # request.form['username'] is from the name ='username' input tag in html

        results = db.engine.execute(text(sql))
  

        # for arow in results:
        #     print(arow) # ('33', 'instructor1', 'instructor1', 'INSTRUCTOR', 'kevin wang')
        #     print(type(arow)) # <class 'sqlalchemy.engine.result.RowProxy'>

        results = [dict(row) for row in results] # a list of dicts, where each dict is each row
        # print(results)

      
        # for result in results:
        # if result['username']==request.form['username']:
        # if result['password']==request.form['password']:
        if len(results) == 1:

            # create the session variables for username and type
            session['username'] = results[0]['username']
            session['type'] = results[0]['type']
            session['logged_in'] = True
            session['IDnumber']=results[0]['IDnumber']
            session['full_name']=results[0]['full_name']
            # sql1 = """
            # -- SELECT *
            # -- FROM marks
            # -- where studentname='{}'""".format(request.form['username'])
            # results = db.engine.execute(text(sql1))
            return redirect('/index')

        # failling case
        return render_template('login.html', works=" Username/Password is incorrect")

    # also initlize the mark
    # elif 'username' in session:
    # 		sql1 = """
    # 				SELECT *
    # 				FROM marks
    # 				where studentname='{}'""".format(session['username'])
    # 		results = db.engine.execute(text(sql1))
    # 		return render_template('Marks.html',data=results)

    # when method = "GET"
    else:
        # when the already loggin redirect them back index homepage
        if ("logged_in" in session) and session["logged_in"]:
            return redirect('/index')

        return render_template("login.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        accnt_type = request.form['account_type']
        IDnumber = request.form['IDnumber']
        full_name = request.form['full_name']
        
        # check if username already exist
        sql = """ 
			SELECT COUNT(*) AS 'count' FROM users WHERE username = '{}'
		""".format(username)

        results = db.engine.execute(sql)
        results = [dict(row) for row in results]

        sql2 = """
        SELECT COUNT(*) AS 'count2' FROM users WHERE IDnumber = '{}'
		""".format(IDnumber)

        results2 =db.engine.execute(sql2)
        results2 = [dict(row) for row in results2] # [{count2:0}]
        # if username doesn't already exist and  if the IDnumber don't already exist in the data, then add it into the database
        if results[0]['count'] == 0 and results2[0]['count2'] == 0:
            
            sql = """
				INSERT INTO users (IDnumber, username, password, type, full_name) VALUES ('{}', '{}', '{}', '{}' , '{}')
			""".format(IDnumber, username, password, accnt_type, full_name)

            results = db.engine.execute(text(sql))
        else:
            return "Username already exists! Go back to sign up page and choose a different Username\n , OR this IDnumber already have an accounts"
            
        return redirect(url_for('login'))

    else:
        return render_template('signup.html')



@app.route('/marks', methods=['GET', 'POST'])
def marks():



    # submit a remarks request from student
    if  session['logged_in'] and session['type'] == AccountTypes.STUDENT and request.method == 'POST':
        reason = request.form['reason']
        assi_type = request.form['a_assignment']

        print(session['IDnumber'])
        print(assi_type)
        sql =  ''' SELECT  COUNT(*) AS count FROM remarks WHERE remarks.IDnumber = '{}' AND remarks.assi_type = '{}'
        '''.format(session['IDnumber'], assi_type)

        results = db.engine.execute(text(sql))
        results = [dict(row) for row in results]

        print(results)
        if results[0]['count'] != 0:
            sql1 = """
            SELECT * 
            FROM users JOIN marks 
            ON users.IDnumber = marks.IDnumber 
            WHERE users.type = 'STUDENT' AND users.username = '{}' 
            """.format(session['username'])
            results5 = db.engine.execute(text(sql1))
            results5 = [dict(row) for row in results]
            # return "YOU HAVE already submitted a remark request for this assisgnment! <a href="/marks">Go back to marks page</a>"
            return render_template('marks.html', username= session['username'],students=results5, cur_type = True, 
            works="YOU HAVE already submitted a remark request for this assisgnment! Click on Marks on the Navbar if you want to submit another remark request")

    
        # insert it into the sql database
        sql2 = '''
        INSERT INTO remarks (IDnumber,assi_type,reason) VALUES ('{}','{}', '{}')
        '''.format(session['IDnumber'],assi_type,reason )
        db.engine.execute(text(sql2))
        return redirect(url_for('marks'))        

    else:
        # student can only see his own mark
        if session['logged_in'] and session['type'] == AccountTypes.STUDENT:
            sql1 = """
            SELECT * 
            FROM users JOIN marks 
            ON users.IDnumber = marks.IDnumber 
            WHERE users.type = 'STUDENT' AND users.username = '{}' 
            """.format(session['username'])
            results = db.engine.execute(text(sql1))
            results = [dict(row) for row in results]


            return render_template('marks.html', username= session['username'],students=results, cur_type = True, works="")
        
        # instructor can see all student's mark and remark request
        elif session['logged_in'] and session['type'] == AccountTypes.INSTRUCTOR:
            sql1 = '''
            SELECT users.IDnumber, full_name,Quiz1,A1,Midterm 
            FROM users JOIN marks where type='STUDENT' AND users.IDnumber=marks.IDnumber
            '''

            results = db.engine.execute(text(sql1))
            results = [dict(row) for row in results]
            # add all the requests
            sql2 = """
            SELECT * from remarks
            """
            list_remarks =  db.engine.execute(text(sql2))
            list_remarks = [dict(row) for row in list_remarks]
            print (list_remarks)
            return render_template('marks.html', username= session['username'], all_students=results, cur_type = False, works='', all_remarks=list_remarks)

        else:
            return 'You are not logged in'


@app.route('/logout')
def logout():

    # pop everything from the user table
    session.pop('username', None)
    session.pop('type', None)
    session.pop('password', None)
    session['logged_in'] = False
    session.pop('IDnumber',None)
    session.pop('full_name',None)

    return redirect(url_for('login'))


@app.route('/feedback', methods=['POST','GET'])
def feedback():
    # if the user wants to submit the form
    if request.method == 'POST':

        # the name of each textarea
        comment1 = request.form['comment1']
        comment2 = request.form['comment2']
        comment3 = request.form['comment3']
        comment4 = request.form['comment4']
        instructor_name = request.form['instructor_name']  # the value from select tag
        IDnumber = session['IDnumber'] # get the current user's IDnumber(student)
   
        
        # check if the current student have already writting a comment to this insturctor
        sql3 =  ''' SELECT  COUNT(*) AS count FROM feedbacks WHERE feedbacks.IDnumber = '{}' AND feedbacks.full_name = '{}'
        '''.format(IDnumber, instructor_name)
        result3 = db.engine.execute(text(sql3))
        result3 = [dict(row) for row in result3]

        if result3[0]['count'] != 0:
            sql = '''
            SELECT full_name from users where type = 'INSTRUCTOR'
            '''
            results = db.engine.execute(text(sql))
            list_instructors =[dict(row) for row in results]
        
            return render_template('Feedback.html', username=session['username'], cur_type = True,all_instructors= list_instructors ,
            works = 'YOU HAVE already submitted a Feedback for this instuctor Before! Click on Feedback  in the Navbar if want to submit another feedback to a different instructor')

        else:

            # add the comments into the batabase for the instructor
            sql1 = '''
            INSERT INTO feedbacks (IDnumber, comment1, comment2, comment3,comment4, full_name) VALUES ('{}', '{}', '{}', '{}' , '{}', '{}')
            '''.format(IDnumber, comment1, comment2, comment3, comment4, instructor_name)

            db.engine.execute(text(sql1))
            return redirect(url_for('feedback'))

    else:
        # current user is student type
        if ("logged_in" in session) and session['logged_in'] and AccountTypes.STUDENT == session['type']:
            # get all the instructor from the data base
            sql = '''
            SELECT full_name from users where type = 'INSTRUCTOR'
            '''
            results = db.engine.execute(text(sql))
            list_instructors =[dict(row) for row in results]
        
            #suppose cur_type is True for STUDENT 
            return render_template('Feedback.html', username=session['username'], all_instructors= list_instructors, cur_type = True, works='')
        
        # current login is instuctor type
        elif ("logged_in" in session) and session['logged_in'] and AccountTypes.INSTRUCTOR == session['type']:
            sql4 ='''
             SELECT comment1,comment2,comment3,comment4 from feedbacks where full_name = '{}'
            '''.format(session['full_name'])

            comments=db.engine.execute(text(sql4))
            comments = [dict(row) for row in comments]
            # print(comments) -> [{'comment1': 'a', 'comment2': 'b', 'comment3': 'c', 'comment4': 'd'}, {'comment1': 'hgood', 'comment2': 'no', 'comment3': 'yes', 'comment4': 'bye'}]

                                #suppose cur_type is False for instructor
                

            return render_template('Feedback.html', username=session['username'],all_comments=comments ,cur_type = False, works='')
        else:
            return redirect(url_for("login"))

#_________________________________________________________________________________________________
@app.route('/index')
def index():
    if "logged_in" in session and session['logged_in']:
        return render_template('index.html', username=session['username'])
    else:
        # return redirect(/'login')
        return redirect(url_for("login"))


@app.route('/announcement')
def announcements():
    if session['logged_in']:
        return render_template('Announcements.html', username=session['username'])
    else:
        return redirect(url_for("login"))

@app.route('/assignment')
def assignments():
    if "logged_in" in session and session['logged_in']:
        return render_template('Assignment.html', username=session['username'])
    else:
        return redirect(url_for("login"))

@app.route('/lecture')
def lecture():
    if "logged_in" in session and session['logged_in']:
        return render_template('Lecture.html', username=session['username'])
    else:
        return redirect(url_for("login"))

@app.route('/tutorial')
def tutorial():
    if "logged_in" in session and session['logged_in']:
        return render_template('Tutorial.html', username=session['username'])
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
