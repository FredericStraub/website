from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import bcrypt, pyodbc
app = Flask(__name__, template_folder='template',static_folder='template/static')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def connection(query,getResult = True):
    s = 'DESKTOP-7R8HL94\SQLEXPRESS' #Your server name
    d = 'website' # database
    u = 'Ege' #Your login
    p = '123' #Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+s+';DATABASE='+d+';UID='+u+';PWD='+ p
    conn = pyodbc.connect(cstr)
    print('CONNECTED!')
    cursor = conn.cursor()
    print(query)
    cursor.execute(query)
    if getResult:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

def Encrypt(p):

    #Got the bcrypt idea from this youtube video https://www.youtube.com/watch?v=CSHx6eCkmv0
    passwd = bytes(p,encoding='UTF-8')

    salt = bcrypt.gensalt() # this generates a random string to be appended to the end of password and hashpw will hash both of these strings
    hashed = bcrypt.hashpw(passwd, salt)
    hashed = hashed.decode(encoding = 'UTF-8')
    return hashed

def check_password(password, email):
    passwd = bytes(password, encoding='UTF-8')
    print(passwd)
    hashed = connection(f"select password from customer where email = '{email}'", getResult = True)
    print(hashed)
    hashed = bytes(hashed[0][0], encoding ='UTF-8')
    print(hashed)
    if bcrypt.checkpw(passwd, hashed): # checkpw will decrypt it and then return
        return True
    else:
        return False


@app.route('/testing', methods=['GET', 'POST'])
def index():
	if request.method =='POST':
		print(request.form.get('first_name'))
	return render_template('index.html')


@app.route('/upload_new', methods=['GET', 'POST'])
def upload():
    if request.method =='POST':

        image = request.form["image"]
        sound = request.form["sound"]

        if image and sound:
            print(image, sound)

        elif image and len(sound) == 0:
            print(image)

        elif sound and len(image) == 0:
            print(sound)

        print(request.form)
    return render_template('upload_new.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        # print(request.form)
        feedback_score = request.form['rating']
        feedback = 'No'
        # print(feedback_score)

        if "email" in session:
            email = session['email']
            if "subject" in request.form:
                feedback = request.form["subject"]
            get_customer_id = connection(f"select id from customer where email = '{email}'", getResult = True)
            get_account_id = connection(f"select id from account where customer_id = '{get_customer_id[0][0]}'", getResult = True)
            connection(f"insert into feedback(account_id, feedback_button, feedback_text, issue, solved_by)"
                       f"values('{get_account_id[0][0]}', '{feedback_score}', '{feedback}', null, null)", getResult = False)
        else:
            flash('You are not logged in. Login or create account to give feedback.')
            return redirect(url_for('login'))
        flash('Thank you, your feedback is successfully submitted.')
        return redirect(url_for('index12'))
    return render_template('contact.html')


@app.route('/account', methods=['GET', 'POST'])
def createaccount():
    if request.method =="POST":
        print(request.form)
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        age = request.form["age"]
        email = request.form["email"]
        password = request.form["psw"]
        new_password_1 = request.form["psw-repeat"]
        gender = request.form['gender']

        if new_password_1 == password:
            encripted_pw = Encrypt(new_password_1)
            email_already_exists = connection(f"select * from customer where email = '{email}'", getResult=True)
            print(email_already_exists)
            if not email_already_exists:
                print('create account')
                connection(
                    f"insert into customer(first_name, last_name, password, age, email, gender) values('{first_name}', '{last_name}', '{encripted_pw}', '{age}', '{email}','{gender}')",
                    getResult=False)
                get_id = connection(f'select * from customer', getResult=True)
                connection(
                    f"insert into account(employee_id, customer_id, islogin, lastupdated, lastupdatedreason, lastupdatedby, prediction) values(null, '{get_id[-1][0]}', null, null, null, null, null)",
                    getResult=False)
                flash('Your account is successfully created, you can login!')
                return redirect(url_for('login'))
            elif email_already_exists:
                flash('An account with this email address already exists.')
                return redirect(url_for('login'))
        else:
            flash('The repeated password is not the same as the first one. Try again.')
    return render_template('createaccount.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":
        user_email = request.form["enter email"]
        password_forgot = request.form["new password"]
        repeat_new_pw = request.form["repeat new password"]
        check_email_exists = connection(f"select email from customer where email = '{user_email}'", getResult=True)
        if 'email' in session:
            flash('You are already logged in')
            return redirect(url_for('index12'))
        elif not check_email_exists:
            flash('Email does not exist')
            return redirect(url_for('forgot'))
        elif check_email_exists and password_forgot == repeat_new_pw:
            encripted_new_pw = Encrypt(repeat_new_pw)
            connection(f"update customer set password = '{encripted_new_pw}' where email = '{user_email}'", getResult=False) #uncomment this when deploying
            flash('Password successfully changed, you can login')
            return redirect(url_for('login'))
        elif password_forgot != repeat_new_pw:
            flash('Passwords do not match')
            return redirect(url_for('forgot'))
    return render_template('forgot.html')


@app.route('/library', methods=['GET', 'POST'])
def library():

	return render_template('library.html')


@app.route('/', methods=['GET', 'POST'])
def index12():
    if request.method =="POST":

        if request.form.get("library") == "Library":
            return redirect(url_for('library'))
            
        elif request.form.get("upload") == "Upload":
            return redirect(url_for('upload'))
        
        elif request.form.get("contact") == "Contact Us":
            return redirect(url_for('contact'))
        
        elif request.form.get("settings") == "Settings":
            return redirect(url_for('settings'))
            
        elif request.form.get("loginnew") == "Log out":
            session.clear()
            return redirect(url_for('login'))    
    
    return render_template('index12.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method =="POST":

       email = request.form["email_1"]
       pw = request.form["psw_1"]

       if "sign_in" in request.form:
           check_email = connection(f"select email from customer where email = '{email}'", getResult=True)
           # check_email = [[1]]
           if len(check_email) > 0:
               check_pw = check_password(pw, email) # uncomment this when deploying
               # check_pw = 1
               if check_pw == True:
                   session['email'] = email
                   session['pw'] = pw
                   print(session)
                   return redirect(url_for('index12'))
               else:
                   flash('Inserted wrong password')
                   return redirect(url_for('login'))
           else:
               flash('This email address does not exist')
               return redirect(url_for('login'))
           return redirect(url_for('index12'))

       if "cancel_forgot" in request.form:
           cancel_forgot = request.form["cancel_forgot"]


       if request.form.get("forgot") == "Forgot Password":
           return redirect(url_for('forgot'))

       if request.form.get("create_account") == "Create new Account":
           return redirect(url_for('createaccount'))
   return render_template('loginnew.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method =="POST":

        print(request.form)
        enter_email = request.form["enter email"]
        current_password = request.form["current password"]
        new_pw =request.form["enter new password"]
        repeat = request.form["repeat new password"]

        if 'email' not in session:
            flash('You are not logged in yet. Login to access your settings.')
            return redirect(url_for('login'))
        if session['email'] == enter_email and check_password(current_password, enter_email):
            if new_pw == repeat:
                encripted_new_pw = Encrypt(new_pw)
                connection(f"update customer set password = '{encripted_new_pw}' where email = '{enter_email}'", getResult=False)
                flash('Your password is successfully changed.')
            else:
                flash('Repeated password is not the same as new password.')
        elif session['email'] != enter_email:
            flash('Email entered is not the email for this account.')
        elif not check_password(current_password, enter_email):
            flash('Inserted current password is not correct.')
    return render_template('settings.html')


if __name__ == '__main__':
	app.run('127.0.0.1', port=8080, debug=True)  #
    
    
