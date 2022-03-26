from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import sys

app = Flask(__name__)
app.debug = True

app.secret_key = 'mango'


# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'tempuser'
app.config['MYSQL_PASSWORD'] = '123+Temppass'
app.config['MYSQL_DB'] = 'graduation'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def choose_mode():
    if request.form.get("login"):
        return redirect(url_for('login'))
    if request.form.get("signup"):
        return redirect(url_for('signup'))
    else:
        return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password,))
        
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['rollno'] = account['rollno']
            return redirect(url_for('tracker'))
        else:
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'rollno' in request.form:
        rollno = request.form['rollno']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[0-9]+', rollno):
            msg = 'Roll No must contain only numbers!'
        elif not rollno or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (email, password, rollno,))
            mysql.connection.commit()
            msg = 'Registration successsful!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        pass
    return render_template('signup.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('rollno', None)

    return redirect(url_for('login'))


@app.route('/tracker')  
def tracker():
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (session['email'],))
    account = cursor.fetchone()

    data = []
    data.append(account['email'].split('@')[0])
    data.append(account['email'])
    data.append(account['rollno'])

    if account['program'] and account['joinyear']:
        data.append(account['program'] + ', ' + str(account['joinyear']))
    else:
        data.append('')

    if account['major']:
        data.append(account['major'])
    else:
        data.append('')

    if account['minor']:
        data.append(account['minor'])
    else:
        data.append('')

    if account['honors']:
        data.append(account['honors'])
    else:
        data.append('')

    return render_template('tracker.html', data=data)

if __name__ == '__main__':
    app.run()