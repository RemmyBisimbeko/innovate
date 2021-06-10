import os
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging


from flask_mysqldb import MySQL
# Import wtforms and  Each Type of Field to be used
from wtforms import Form, StringField, SelectField, TextAreaField, PasswordField, validators
# Import passlib hash
from passlib.hash import sha256_crypt
# Bring wraps in
from functools import wraps

# Init App
app = Flask(__name__)
app.secret_key = 'secret123'
app.config['SESSION_TYPE'] = 'filesystem'

# Config MySQL
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = os.environ.get("MYSQL_CURSORCLASS")
# Init MySQL
mysql = MySQL(app)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# About Route
@app.route('/about')
def about():
    return render_template('about.html')

# Single Assessment Route
@app.route('/assessment/<string:id>')
def assessment(id):
    # Create  Cursor
    cur = mysql.connection.cursor()

    # Get Assessment
    result = cur.execute("SELECT * FROM assessments WHERE id=%s", [id ])

    # Set Assessment Variable and set it to all in Dictionary form
    assessment = cur.fetchone()

    return render_template('assessment.html', assessment=assessment)

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    # Check if GET or POST request, and make sure everything is validated
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        # Encryt password before sending it, submiting it
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor, used to execute commands(mysql)
        cur = mysql.connection.cursor()

        # Execute Query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close the Connection
        cur.close()

        # Set flash message once user is registered  - 'message', 'category'
        flash('You have been registered Successfully, please log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check method
    if request.method == 'POST':
        # If form is submited, GET username and password from the form
        # GET form fields, no need for using wtf forms
        username = request.form['username']
        # Candidate-user input, bse we want to compare with password which is in the db
        passsword_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute Query, GET user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        # Check result, >0 - any rows found
        if result > 0:
            # Get Stored hash
            data = cur.fetchone()
            # Get password from that fetch
            password = data['password']

            # Compare the passwords
            if sha256_crypt.verify(passsword_candidate, password):
                # Passes password check
                # app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return  redirect(url_for('home'))
            else:
                error='Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            # app.logger.info('NO USER FOUND')
            error='Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # Check Logic
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('This action is not Authorised, Please login first', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout Route
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Assessments Route
@app.route('/assessments')
@is_logged_in
def assessments():
    # Create  Cursor
    cur = mysql.connection.cursor()

    # Get Assessments 
    # result = cur.execute("SELECT * FROM assessments")

    result = cur.execute("SELECT * FROM assessments")

    # Set Assessment Variable and set it to all in Dictionary form
    assessments = cur.fetchall()

    if result > 0:
        return render_template('assessments.html', assessments=assessments)
    else:
        msg = 'No Assessments Yet'
        return render_template('assessments.html', msg=msg)

    # Close Connection
    cur.close()

# Add Assessment Form Class
class AssessmentForm(Form):
    pf_number = StringField('pf_number', [validators.Length(min=1, max=6)])
    unit_branch = SelectField('branch', choices=[('--Select Branch/Unit--','--Select Branch/Unit--'),
        ('Adjumani','Adjumani'),
        ('Apac','Apac'),
        ('Arua','Arua'),
        ('Audit','Audit'),
        ('Bugiri','Bugiri'),
        ('Bundibugyo','Bundibugyo'),
        ('Busia','Busia'),
        ('Business Development','Business Development'),
        ('Business Technology','Business Technology'),
        ('Bwaise','Bwaise'),
        ('Bwera','Bwera'),
        ('Bweyale','Bweyale'),
        ('Centralized Back Office','Centralized Back Office'),
        ('Commercial Banking','Commercial Banking'),
        ('Commercial Credit','Commercial Credit'),
        ('Compliance','Compliance'),
        ('Core Banking System','Core Banking System'),
        ('Corporate Communications And Marketing','Corporate Communications And Marketing'),
        ('Corporate Services','Corporate Services'),
        ('Credit Management','Credit Management'),
        ('Directors','Directors'),
        ('E-Banking','E-Banking'),
        ('Ebanking','Ebanking'),
        ('Entebbe Road Corporate','Entebbe Road Corporate'),
        ('Entebbe Road Standard','Entebbe Road Standard'),
        ('Executive Office','Executive Office'),
        ('Finance','Finance'),
        ('Financial Inclusion','Financial Inclusion'),
        ('Financial Markets','Financial Markets'),
        ('Fort Portal','Fort Portal'),
        ('Gulu','Gulu'),
        ('Gulu Market','Gulu Market'),
        ('Head Office','Head Office'),
        ('Hoima','Hoima'),
        ('Human Resource','Human Resource'),
        ('Ibanda','Ibanda'),
        ('Iganga','Iganga'),
        ('International','International'),
        ('Ishaka','Ishaka'),
        ('Isingiro','Isingiro'),
        ('Jinja','Jinja'),
        ('Kabalagala','Kabalagala'),
        ('Kabale','Kabale'),
        ('Kagadi','Kagadi'),
        ('Kampala Cash Centre','Kampala Cash Centre'),
        ('Kamuli','Kamuli'),
        ('Kamwenge','Kamwenge'),
        ('Kanungu','Kanungu'),
        ('Kapchorwa','Kapchorwa'),
        ('Kasese','Kasese'),
        ('Kawempe','Kawempe'),
        ('Kawuku','Kawuku'),
        ('Kayabwe','Kayabwe'),
        ('Kayunga','Kayunga'),
        ('Kiboga','Kiboga'),
        ('Kikuubo','Kikuubo'),
        ('Kikuubo B','Kikuubo B'),
        ('Kireka','Kireka'),
        ('Kisoro','Kisoro'),
        ('Kitgum','Kitgum'),
        ('Koboko','Koboko'),
        ('Kotido','Kotido'),
        ('Kumi Service','Kumi Service'),
        ('Kyenjojo','Kyenjojo'),
        ('Kyotera','Kyotera'),
        ('Legal','Legal'),
        ('Lira','Lira'),
        ('Lugogo','Lugogo'),
        ('Lyantonde','Lyantonde'),
        ('Makerere','Makerere'),
        ('Mapeera','Mapeera'),
        ('Mapeera Platinum','Mapeera Platinum'),
        ('Masaka','Masaka'),
        ('Masindi','Masindi'),
        ('Mbale','Mbale'),
        ('Mbarara','Mbarara'),
        ('Mbarara Corporate','Mbarara Corporate'),
        ('Mityana','Mityana'),
        ('Mobile','Mobile'),
        ('Moroto','Moroto'),
        ('Mpigi','Mpigi'),
        ('Mubende','Mubende'),
        ('Mukono','Mukono'),
        ('Najjanankumbi','Najjanankumbi'),
        ('Nakivubo Road','Nakivubo Road'),
        ('Namirembe Road','Namirembe Road'),
        ('Nansana','Nansana'),
        ('Natete','Natete'),
        ('Nebbi','Nebbi'),
        ('Ntinda','Ntinda'),
        ('Ntungamo','Ntungamo'),
        ('Operations','Operations'),
        ('Paidha','Paidha'),
        ('Pallisa','Pallisa'),
        ('Retail And Microfinance','Retail And Microfinance'),
        ('Risk','Risk'),
        ('Rubaga','Rubaga'),
        ('Rukungiri','Rukungiri'),
        ('Security','Security'),
        ('Sembabule','Sembabule'),
        ('Soroti','Soroti'),
        ('Strategy And Research','Strategy And Research'),
        ('Tororo','Tororo'),
        ('Wakiso','Wakiso'),
        ('Wobulenzi','Wobulenzi')
    ])
    designation = StringField('designation', [validators.Length(min=1, max=30)])
    weaknesses = TextAreaField('weaknesses', [validators.Length(min=1, max=255)])
    self_score = SelectField('self_score', choices=[('--Select Score--','--Select Score--'),('01','01'),('02','02'),('03','03'),('04','04'),('05','05'),('06','06'),('07','07'),('08','08'),('09','09'),('10','10')])
    innovation_idea = TextAreaField('innovation_idea', [validators.Length(min=1, max=255)])
    team_members = TextAreaField('team_members', [validators.Length(min=1, max=255)])
    estimated_cost = StringField('estimated_cost', [validators.Length(min=1, max=30)])
    suggestions = TextAreaField('suggestions', [validators.Length(min=1, max=255)])

# Do Assessment - Page 1 Route  
@app.route('/do_assessment', methods=['GET', 'POST'])
@is_logged_in
def do_assessment():
    form = AssessmentForm(request.form)
    if request.method == 'POST' and form.validate():
        pf_number = form.pf_number.data
        unit_branch = form.unit_branch.data
        designation = form.designation.data
        weaknesses = form.weaknesses.data
        self_score = form.self_score.data
        innovation_idea = form.innovation_idea.data
        team_members = form.team_members.data
        estimated_cost = form.estimated_cost.data
        suggestions = form.suggestions.data
        # submission_date = form.submission_date.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("INSERT INTO assessments(pf_number, unit_branch, designation, weaknesses, self_score, innovation_idea, team_members, estimated_cost, suggestions, name) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (pf_number, unit_branch, designation, weaknesses, self_score, innovation_idea, team_members, estimated_cost, suggestions, session['username']))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Assessment was completed successfully', 'success')

        return redirect(url_for('assessments'))

    return render_template('do_assessment.html', form=form)

# Edit Assessment Route  
@app.route('/edit_assessment/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_assessment(id):

    # Create Cursor
    cur = mysql.connection.cursor()

    # Get Assessment by id
    result = cur.execute("SELECT * FROM assessments WHERE id = %s", [id])

    assessment = cur.fetchone()

    # Get Form
    form = AssessmentForm(request.form)

    # Populate Assessment form fields
    form.pf_number.data = assessment['pf_number']
    form.unit_branch.data = assessment['unit_branch']
    form.designation.data = assessment['designation']
    form.weaknesses.data = assessment['weaknesses']
    form.self_score.data = assessment['self_score']
    form.innovation_idea.data = assessment['innovation_idea']
    form.team_members.data = assessment['team_members']
    form.estimated_cost.data = assessment['estimated_cost']
    form.suggestions.data = assessment['suggestions']

    if request.method == 'POST' and form.validate():
        pf_number = request.form['pf_number']
        unit_branch = request.form['unit_branch']
        designation = request.form['designation']
        weaknesses = request.form['weaknesses']
        self_score = request.form['self_score']
        innovation_idea = request.form['innovation_idea']
        team_members = request.form['team_members']
        estimated_cost = request.form['estimated_cost']
        suggestions = request.form['suggestions']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("UPDATE assessments SET pf_number=%s, unit_branch=%s, designation=%s, weaknesses=%s, self_score=%s, innovation_idea=%s, team_members=%s, estimated_cost=%s, suggestions=%s WHERE id=%s", (pf_number, unit_branch, designation, weaknesses, self_score, innovation_idea, team_members, estimated_cost, suggestions, id))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Your Assessment was updated successfully', 'success')

        return redirect(url_for('assessments'))

    return render_template('edit_assessment.html', form=form)

# Delete Assessment
@app.route('/delete_assessment/<string:id>', methods=['POST'])
@is_logged_in 
def delete_assessment(id):
    # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("DELETE FROM assessments WHERE id=%s", [id])

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Your Assessment was deleted successfully', 'success')

        return redirect(url_for('assessments'))

# Run Server
if __name__ == '__main__':
    
    app.run(debug=True)