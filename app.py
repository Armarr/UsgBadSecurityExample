from flask import *
import hashlib
import sqlite3

app = Flask(__name__)
app.secret_key = b'\x03h\xa7\xbcDLS\xa4l\xb6\xc5U\xf1Qn\xe885_\x90\xcd\xe2\x8d\xbe' #Needed for sessions
app.config['SESSION_COOKIE_HTTPONLY'] = False

conn = sqlite3.connect('data.db')
conn.set_trace_callback(print)
c = conn.cursor()
c.execute("create table if not exists users (username text, passwordHash text, secret text)")
c.execute("create table if not exists messages (username text, message text)")

@app.route('/')
def default():
	if 'username' in session:
		return redirect("/user/" + session['username'])
	else:
		return redirect("/login")

@app.route('/user/<name>')
def user(name=None):
	secret = c.execute('SELECT secret FROM users WHERE username = "%s"' % name).fetchone()[0]
	messages = c.execute('SELECT * FROM messages').fetchall()
	print(messages[0])
	return render_template('user.html', name=session['username'], secret=secret, messages=messages)

@app.route('/login', methods=['POST', 'GET'])
def login():
	error = None
	if request.method == 'POST':
		loggedInUser = perform_login(request.form['username'], request.form['password'])
		if loggedInUser != None:
			session['username'] = loggedInUser
			return redirect("/user/" + loggedInUser)
		else:
			error = 'Invalid username/password'
	return render_template('login.html', error=error)
	
def perform_login(user, password):
	c = conn.cursor()
	passwordHash = hashlib.md5(password.encode('utf-8')).hexdigest()
	username = c.execute("SELECT username FROM users WHERE username = '%s' AND passwordHash = '%s'" % (user, passwordHash)).fetchone()[0]
	return username
	
@app.route('/message', methods=['POST'])
def message():
	c.execute("INSERT INTO messages VALUES ('%s', '%s')" % (session['username'], request.form['message']))
	conn.commit()
	return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
	

	