from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
app = Flask(__name__)
app.secret_key='secrets'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile('^[^0-9]+$')
PASSWORD_REGEX = re.compile('\d.*[A-Z]|[A-Z].*\d')
mysql = MySQLConnector(app,'wall')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    # add user registration
    for i in request.form:
        if len(request.form[i]) < 1:
            flash("All fields are required")
            return redirect('/')
    if len(request.form['password']) < 8:
        flash("Password must be at least 8 characters")
        return redirect('/fail')
    elif len(request.form['first']) < 2:
        flash("First name must be at least two characters")
        return redirect('/fail')
    elif len(request.form['last']) < 2:
        flash("Last name must be at least two characters")
    elif not NAME_REGEX.match(request.form['first']):
        flash("First name must be letters only")
        return redirect('/fail')
    elif not NAME_REGEX.match(request.form['last']):
        flash("Last name must be letters only")
        return redirect ('/fail')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address")
        return redirect('/fail')
    elif request.form['password'] != request.form['confirm']:
        flash("Passwords do not match")
        return redirect('/fail')
    else:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        data = {
            'first_name': request.form['first'],
            'last_name': request.form['last'],
            'email': request.form['email'],
            'password': md5.new(request.form['password']).hexdigest(),
            }
        session['email'] = request.form['email']
        flash("registered!")
        mysql.query_db(query, data)
        return redirect('/wall')

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT first_name, last_name FROM users WHERE email = :email AND password = :password"
    data = { 
        'email': request.form['email'],
        'password':md5.new(request.form['password']).hexdigest()
    }
    user = mysql.query_db(query, data)
    if user:
        flash ("logged in!")
        session['email'] = request.form['email']
        return redirect('/wall')
    else:
        flash ("**Username or Password is Incorrect**")
        return redirect('/fail')

@app.route('/wall')
def success():
    query ="SELECT id, first_name, last_name FROM users WHERE email = :email LIMIT 1"
    data = { 'email' : session['email']}
    user = mysql.query_db(query, data)
    session['id'] = user[0]['id']
    # print session['id']
    # print session['email']
    # print user
    querymess = "SELECT messages.id, users.first_name, users.last_name, messages.message, DATE_FORMAT(messages.created_At, '%M %D %Y') as message_date FROM messages JOIN users ON messages.user_id = users.id"
    messages = mysql.query_db(querymess)
    # print messages
    querycomm = "SELECT comments.message_id, users.first_name, users.last_name, comments.comment, DATE_FORMAT(comments.created_at, '%M %D %Y') as comment_date FROM comments JOIN users ON comments.user_id = users.id"
    comments = mysql.query_db(querycomm)
    # print comments
    return render_template('wall.html', user=user, comments=comments, messages=messages)

@app.route('/fail')
def fail():
    return render_template('fail.html')

@app.route('/logout')
def logout():
    session['email'] = ""
    return redirect ('/')

@app.route('/message', methods=['POST'])
def message():
    query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES (:message, :id, NOW(), NOW())"
    data = {
        "message": request.form['message'],
        "id": session['id']
    }
    mysql.query_db(query, data)
    return redirect('/wall')
@app.route('/comment', methods=['POST'])
def comment():
    print request.form['messageid']
    query = "INSERT INTO comments (comment, message_id, user_id, created_at, updated_at) VALUES (:comment, :message_id, :user_id, NOW(), NOW())"
    data = {
        "comment": request.form['comment'],
        "message_id": request.form['messageid'],
        "user_id": session['id']
    }
    mysql.query_db(query,data)
    return redirect('/wall')

app.run(debug=True)