from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.utils import secure_filename
from PIL import Image
import bcrypt, pyodbc
import os
import glob
import shutil

app = Flask(__name__, template_folder='template', static_folder='template/static')
app.config['SESSION_TYPE'] = 'filesystem'
images_folder_path = "template/static/images"
sounds_folder_path = "template/static/sounds"
app.config['UPLOAD_IMAGE_FOLDER'] = images_folder_path
app.config['UPLOAD_SOUND_FOLDER'] = sounds_folder_path
Session(app)


def connection(query, getResult=True):
    s = 'DESKTOP-7R8HL94\SQLEXPRESS'  # Ela's server name
    s = 'DESKTOP-EGO85AB\SQLEXPRESS' # Jason's server name
    d = 'website'  # database
    u = 'Ege'  # Ela's login
    u = 'jason' # jason's login
    p = '123'  # Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + s + ';DATABASE=' + d + ';UID=' + u + ';PWD=' + p
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
    # Got the bcrypt idea from this youtube video https://www.youtube.com/watch?v=CSHx6eCkmv0
    passwd = bytes(p, encoding='UTF-8')

    salt = bcrypt.gensalt()  # this generates a random string to be appended to the end of password and hashpw will hash both of these strings
    hashed = bcrypt.hashpw(passwd, salt)
    hashed = hashed.decode(encoding='UTF-8')
    return hashed


def check_password(password, email):
    passwd = bytes(password, encoding='UTF-8')
    print(passwd)
    hashed = connection(f"select password from customer where email = '{email}'", getResult=True)
    print(hashed)
    hashed = bytes(hashed[0][0], encoding='UTF-8')
    print(hashed)
    if bcrypt.checkpw(passwd, hashed):  # checkpw will decrypt it and then return
        return True
    else:
        return False


def allowed_image_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_sound_file(filename):
    ALLOWED_EXTENSIONS = {'wav'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_sorted(dir_list): #to find maximum integer in folder
    copy_dir = dir_list[:]
    for i in range(len(copy_dir)):
        for j in range(len(copy_dir[i][::-1])):
            if copy_dir[i][::-1][j] == '.':
                copy_dir[i] = int(copy_dir[i][:-j-1])
                break
    return sorted(copy_dir)

def split_into_dict(dir_list): #store filename with corresponding extension
    dictionary = {}
    for i in range(len(dir_list)):
        for j in range(len(dir_list[i])):
            if dir_list[i][::-1][j] == '.':
                full = dir_list[i]
                filename = dir_list[i][:-j-1]
                extension = full.replace(filename, '')
                key = int(dir_list[i][:-j - 1])
                dictionary[key] = extension
                break
    return dictionary

def get_image(dir_list, index): #to combine found image name (=integer) with corresponding extension
    img_dir_dict = split_into_dict(dir_list)
    integer_list = split_sorted(dir_list)
    image_int = integer_list[index]
    image_extension = img_dir_dict[image_int]
    full_filename = str(image_int) + image_extension
    return full_filename

@app.route('/testing', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form.get('first_name'))
    return render_template('index.html')


@app.route('/upload_new', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        if "Back" in request.form:
            return redirect(url_for('index12'))

        image = request.files["image"]
        sound = request.files["sound"]
        if 'customer_id' in session:
            if image.filename == '' and sound.filename == '':
                flash("You did not select any files")
            if image.filename != '':
                if allowed_image_file(secure_filename(image.filename)):
                    image_folder_path = app.config['UPLOAD_IMAGE_FOLDER'] + '/' + str(session['customer_id'])
                    if not os.path.exists(image_folder_path):
                        os.makedirs(image_folder_path)
                    img_list = os.listdir(image_folder_path)
                    if len(img_list) == 0: # no images at this point
                        img_path = os.path.join(image_folder_path, '4' + '.' + image.filename.rsplit('.')[-1])
                    if len(img_list) > 0:
                        maximum_int = split_sorted(img_list)[-1]
                        new_int_string = str(maximum_int + 1)
                        img_path = os.path.join(image_folder_path, new_int_string + '.' + image.filename.rsplit('.')[-1])
                    image.save(img_path)
                    desired_size = 224
                    im = Image.open(img_path)
                    old_size = im.size
                    ratio = float(desired_size) / max(old_size)
                    new_size = tuple([int(x * ratio) for x in old_size])
                    img = im.resize(new_size, resample=Image.LANCZOS)
                    new_im = Image.new("RGB", (desired_size, desired_size))
                    new_im.paste(img, ((desired_size - new_size[0]) // 2, (desired_size - new_size[1]) // 2))
                    new_im.save(img_path)
                    flash('Your image is successfully uploaded')
                else:
                    flash('Please upload an image with the file extension png, jpg or jpeg')
            if sound.filename != '':
                if allowed_sound_file(secure_filename(sound.filename)):
                    sound_path = app.config['UPLOAD_SOUND_FOLDER'] + '/' + str(session['customer_id'])
                    if not os.path.exists(sound_path):
                        os.makedirs(sound_path)
                    print(secure_filename(sound.filename))
                    changed_sound_path = os.path.join(sound_path, secure_filename(sound.filename))
                    sound.save(changed_sound_path)
                    flash('Your sound file is successfully uploaded')
                else:
                    flash('Please upload a sound file with the file extension wav')
        else:
            flash('You are not logged in yet. Log in or create an account to upload a file for the prediction.')
            return redirect(url_for('login'))
    return render_template('upload_new.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        if "Back" in request.form:
            return redirect(url_for('index12'))
        # print(request.form)
        feedback_score = request.form['rating']
        feedback = 'No'
        # print(feedback_score)

        if "email" in session:
            email = session['email']
            if "subject" in request.form:
                feedback = request.form["subject"]
            get_customer_id = connection(f"select id from customer where email = '{email}'", getResult=True)
            get_account_id = connection(f"select id from account where customer_id = '{get_customer_id[0][0]}'",
                                        getResult=True)
            connection(f"insert into feedback(account_id, feedback_button, feedback_text, issue, solved_by)"
                       f"values('{get_account_id[0][0]}', '{feedback_score}', '{feedback}', null, null)",
                       getResult=False)
        else:
            flash('You are not logged in. Login or create account to give feedback.')
            return redirect(url_for('login'))
        flash('Thank you, your feedback is successfully submitted.')
        return redirect(url_for('index12'))
    return render_template('contact.html')


@app.route('/account', methods=['GET', 'POST'])
def createaccount():
    if request.method == "POST":
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
            connection(f"update customer set password = '{encripted_new_pw}' where email = '{user_email}'",
                       getResult=False)  # uncomment this when deploying
            flash('Password successfully changed, you can login')
            return redirect(url_for('login'))
        elif password_forgot != repeat_new_pw:
            flash('Passwords do not match')
            return redirect(url_for('forgot'))
    return render_template('forgot.html')


@app.route('/library', methods=['GET', 'POST'])
def library():
    if "Back" in request.form:
        return redirect(url_for('index12'))
    if 'customer_id' in session:
        if not os.path.exists(f"template/static/images/{session['customer_id']}"):
            os.makedirs(f"template/static/images/{session['customer_id']}")
        src_dir = "template/static/images/default_images"
        dst_dir = f"template/static/images/{session['customer_id']}" #personal image directory
        img_list = os.listdir(dst_dir)
        if len(img_list) == 0:
            for jpgfile in glob.iglob(os.path.join(src_dir, "*.jpg")):
                shutil.copy(jpgfile, dst_dir)
            img_list = os.listdir(dst_dir)
            image1 = str(f"/images/{session['customer_id']}/" + img_list[0])
            image2 = str(f"/images/{session['customer_id']}/" + img_list[1])
            image3 = str(f"/images/{session['customer_id']}/" + img_list[2])
        elif len(img_list) == 1:
            for jpgfile in glob.iglob(os.path.join(src_dir, "*.jpg")):
                shutil.copy(jpgfile, dst_dir)
            img_list = os.listdir(dst_dir)
            img_list.remove('2.jpg')
            image1 = str(f"/images/{session['customer_id']}/" + img_list[0])
            image2 = str(f"/images/{session['customer_id']}/" + img_list[1])
            image3 = str(f"/images/{session['customer_id']}/" + img_list[2])
        elif len(img_list) == 2:
            for jpgfile in glob.iglob(os.path.join(src_dir, "*.jpg")):
                shutil.copy(jpgfile, dst_dir)
            img_list = os.listdir(dst_dir)
            remove = ['2.jpg', '3.jpg']
            img_list = list(set(img_list) - set(remove))
            image1 = str(f"/images/{session['customer_id']}/" + img_list[0])
            image2 = str(f"/images/{session['customer_id']}/" + img_list[1])
            image3 = str(f"/images/{session['customer_id']}/" + img_list[2])
        elif len(img_list) == 3:
            image1 = str(f"/images/{session['customer_id']}/" + img_list[0])
            image2 = str(f"/images/{session['customer_id']}/" + img_list[1])
            image3 = str(f"/images/{session['customer_id']}/" + img_list[2])
        elif len(img_list) > 3:
            image1 = str(f"/images/{session['customer_id']}/" + get_image(img_list, -1))
            image2 = str(f"/images/{session['customer_id']}/" + get_image(img_list, -2))
            image3 = str(f"/images/{session['customer_id']}/" + get_image(img_list, -3))
    else:
        flash('Login to see your personal library')
        img_dir = app.config['UPLOAD_IMAGE_FOLDER'] + '/default_images'
        img_list = os.listdir(img_dir)
        image1 = str('/images/default_images/' + img_list[0])
        image2 = str('/images/default_images/' + img_list[1])
        image3 = str('/images/default_images/' + img_list[2])
    return render_template('library.html', image1 = image1, image2 = image2, image3 = image3)


@app.route('/', methods=['GET', 'POST'])
def index12():
    if request.method == "POST":

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
    if request.method == "POST":

        email = request.form["email_1"]
        pw = request.form["psw_1"]

        if "sign_in" in request.form:
            check_email = connection(f"select email from customer where email = '{email}'", getResult=True)
            if len(check_email) > 0:
                check_pw = check_password(pw, email)
                if check_pw == True:
                    session['email'] = email
                    customer_id = connection(f"select id from customer where email = '{email}'", getResult=True)
                    session['customer_id'] = customer_id[0][0]
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
    if request.method == "POST":

        print(request.form)
        enter_email = request.form["enter email"]
        current_password = request.form["current password"]
        new_pw = request.form["enter new password"]
        repeat = request.form["repeat new password"]

        if 'email' not in session:
            flash('You are not logged in yet. Login to access your settings.')
            return redirect(url_for('login'))
        if session['email'] == enter_email and check_password(current_password, enter_email):
            if new_pw == repeat:
                encripted_new_pw = Encrypt(new_pw)
                connection(f"update customer set password = '{encripted_new_pw}' where email = '{enter_email}'",
                           getResult=False)
                flash('Your password is successfully changed.')
                return redirect(url_for('index12'))
            else:
                flash('Repeated password is not the same as new password.')
        elif session['email'] != enter_email:
            flash('Email entered is not the email for this account.')
        elif not check_password(current_password, enter_email):
            flash('Inserted current password is not correct.')
    return render_template('settings.html')


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080, debug=True)  #
