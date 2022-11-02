from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import bcrypt, pyodbc
app = Flask(__name__, template_folder='template',static_folder='template/static')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def connection(query,getResult = True):
    s = 'DESKTOP-7R8HL94\SQLEXPRESS' #Your server name
    d = 'website' # database
    u = 'Ela' #Your login
    p = '123' #Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+s+';DATABASE='+d+';UID='+u+';PWD='+ p
    conn = pyodbc.connect(cstr)
    print('CONNECTED!')
    cursor = conn.cursor()
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
    hashed = bcrypt.hashpw(p, salt)
    return hashed

def check_password(password, email):
    passwd = bytes(password, encoding='UTF-8')
    hashed = connection(f'select password from customer where email = {email}', getResult = True)
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
        feedback_score = 0
        feedback = 'No'
        print(request.form)
        session['email'] = email
    
        if "one" in request.form:
            feedback_score = request.form["one"]
            
        elif "two" in request.form:
            feedback_score = request.form["two"]
        
        elif "three" in request.form:
            feedback_score = request.form["three"]
                
        elif "four" in request.form:
            feedback_score = request.form["four"]
        
        elif "five" in request.form:
            feedback_score = request.form["five"]
        
        if "subject" in request.form:
            feedback = request.form["subject"]
        get_customer_id = connection(f'select id from customer where email = {email}', getResult = True)
        get_acc_id = connection(f'select id from account where customer_id = {get_customer_id}')
        connection(f'insert into feedback values({get_acc_id}, {feedback_score}, {feedback}, null, null)', getResult = False)
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
        encripted_pw = Encrypt(new_password_1)

        if "male" in request.form:
            gender = request.form["male"]

        elif "female" in request.form:
            gender = request.form["female"]

        elif "prefer not to say" in request.form:
            gender = request.form["prefer not to say"]
        email_already_exists = connection(f'select * from customer where email = {email}', getResult=True)
        if not email_already_exists:
            print('create account')
            connection(f'insert into customer values({first_name}, {last_name}, {encripted_pw}, {age}, {email}, {gender})', getResult = False)
            get_id = connection(f'select * from customer', getResult = True)
            connection(f'insert into account values(null, {get_id[-1][0]}, null, null, null, null)', getResult = False)
            return redirect(url_for('login'))
        elif email_already_exists:
            print('email already exists')

    return render_template('createaccount.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":

        user_email = request.form["enter email"]
        password_forgot = request.form["new password"]
        repeat_new_pw = request.form["new password"]
        check_email_exists = connection(f'select email from customer where email = {user_email}', getResult=True)
        if check_email_exists and password_forgot == repeat_new_pw:
            encripted_new_pw = Encrypt(repeat_new_pw)
            connection(f'update customer set password = {encripted_new_pw} where email = {user_email}', getResult=False) #uncomment this when deploying
        elif not check_email_exists:
            print('email does not exist')
        elif password_forgot != repeat_new_pw:
            print('passwords not the same')
        return redirect(url_for('login'))
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
           check_email = connection(f'select email from customer where email = {email}', getResult=True)
           # check_email = [[1]]
           if check_email[0][0]:
               check_pw = check_password(pw, email) # uncomment this when deploying
               # check_pw = 1
               if check_pw:
                   session['email'] = email
                   session['pw'] = pw
                   print('login')
               else:
                   print('go to create_account')
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
        new_password = request.form["repeat new password"]
        if session['email'] == enter_email and check_password(enter_email, current_password):
            encripted_new_pw = Encrypt(new_password)
            connection(f'update customer set password = {encripted_new_pw} where email = {enter_email}', getResult=False)
        elif session['email'] != enter_email:
            print('email entered is not the email for this acount')
        elif not check_password(enter_email, current_password):
            print('inserted current password is not correct')
        return redirect(url_for('index12'))
    return render_template('settings.html')


if __name__ == '__main__':
	app.run('127.0.0.1', port=8080, debug=True)  #
    
    
