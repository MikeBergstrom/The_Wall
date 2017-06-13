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
        flash ("username or password incorrect")
        return redirect('/fail')

@app.route('/wall')
def success():
    query ="SELECT id, first_name, last_name FROM users WHERE email = :email LIMIT 1"
    data = { 'email' : session['email']}
    user = mysql.query_db(query, data)
    print session['email']
    print user
    return render_template('success.html', user=user)

@app.route('/fail')
def fail():
    return render_template('fail.html')

app.run(debug=True)