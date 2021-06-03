import os
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging


from flask_mysqldb import MySQL
# Import wtforms and  Each Type of Field to be used
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
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
            flash('This action is not Authorised, Please login', 'danger')
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

    # uname = session['username']
    # Get Assessments 
    result = cur.execute("SELECT * FROM assessments")

    # result = cur.execute("SELECT * FROM crosssells where name = %s", uname)
    # result = cur.execute("SELECT * FROM assessments where name = %s", session['username'])

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
    branch = StringField('branch', [validators.Length(min=1, max=50)])
    customer_account = StringField('customer_account', [validators.Length(min=1, max=20)])
    product = StringField('product', [validators.Length(min=1, max=20)])
    crosssell_type = StringField('crosssell_type', [validators.Length(min=1, max=20)])
    naration = TextAreaField('naration', [validators.Length(min=10)])

# Do Assessment - Page 1 Route  
@app.route('/do_assessment_page_1', methods=['GET', 'POST'])
@is_logged_in
def do_assessment_page_1():
    form = AssessmentForm(request.form)
    if request.method == 'POST' and form.validate():
        pf_number = form.pf_number.data
        branch = form.branch.data
        customer_account = form.customer_account.data
        product = form.product.data
        crosssell_type = form.crosssell_type.data
        naration = form.naration.data
        # submission_date = form.submission_date.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("INSERT INTO assessments(pf_number, branch, customer_account, product, crosssell_type, naration, name) VALUES(%s, %s, %s, %s, %s, %s, %s)", (pf_number, branch, customer_account, product, crosssell_type, naration, session['username']))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Page 1 was completed successfully', 'success')

        return redirect(url_for('do_assessment_page_2'))

    return render_template('do_assessment_page_1.html', form=form)

# Do Assessment - Page 2 Route  
@app.route('/do_assessment_page_2', methods=['GET', 'POST'])
@is_logged_in
def do_assessment_page_2():
    form = AssessmentForm(request.form)
    if request.method == 'POST' and form.validate():
        pf_number = form.pf_number.data
        branch = form.branch.data
        customer_account = form.customer_account.data
        product = form.product.data
        crosssell_type = form.crosssell_type.data
        naration = form.naration.data
        # submission_date = form.submission_date.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("INSERT INTO assessments(pf_number, branch, customer_account, product, crosssell_type, naration, name) VALUES(%s, %s, %s, %s, %s, %s, %s)", (pf_number, branch, customer_account, product, crosssell_type, naration, session['username']))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Page 1 was completed successfully', 'success')

        return redirect(url_for('do_assessment_page_3'))

    return render_template('do_assessment_page_2.html', form=form)


# Do Assessment - Page 3 Route  
@app.route('/do_assessment_page_3', methods=['GET', 'POST'])
@is_logged_in
def do_assessment_page_3():
    form = AssessmentForm(request.form)
    if request.method == 'POST' and form.validate():
        pf_number = form.pf_number.data
        branch = form.branch.data
        customer_account = form.customer_account.data
        product = form.product.data
        crosssell_type = form.crosssell_type.data
        naration = form.naration.data
        # submission_date = form.submission_date.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("INSERT INTO assessments(pf_number, branch, customer_account, product, crosssell_type, naration, name) VALUES(%s, %s, %s, %s, %s, %s, %s)", (pf_number, branch, customer_account, product, crosssell_type, naration, session['username']))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Your Assessment was captured successfully', 'success')

        return redirect(url_for('dashboard_crosssells'))

    return render_template('do_assessment_page_3.html', form=form)

# Edit Assessment Page 1 Route  
@app.route('/edit_assessment_page_1/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_assessment_page_1(id):

    # Create Cursor
    cur = mysql.connection.cursor()

    # Get Assessment by id
    result = cur.execute("SELECT * FROM assessments WHERE id = %s", [id])

    assessment = cur.fetchone()

    # Get Form
    form = AssessmentForm(request.form)

    # Populate Assessment form fields
    form.pf_number.data = assessment['pf_number']
    form.branch.data = assessment['branch']
    form.customer_account.data = assessment['customer_account']
    form.product.data = assessment['product']
    form.crosssell_type.data = assessment['crosssell_type']
    form.naration.data = assessment['naration']

    if request.method == 'POST' and form.validate():
        pf_number = request.form['pf_number']
        branch = request.form['branch']
        customer_account = request.form['customer_account']
        product = request.form['product']
        crosssell_type = request.form['crosssell_type']
        naration = request.form['naration']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("UPDATE assessments SET pf_number=%s, branch=%s, customer_account=%s, product=%s, crosssell_type=%s, naration=%s WHERE id=%s", (pf_number, branch, customer_account, product, crosssell_type, naration, id))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Your Assessment was updated successfully', 'success')

        return redirect(url_for('assessments'))

    return render_template('edit_assessment_page_1.html', form=form)

# Edit Assessment Page 1 Route  
@app.route('/edit_assessment_page_2/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_assessment_page_1(id):

    # Create Cursor
    cur = mysql.connection.cursor()

    # Get Assessment by id
    result = cur.execute("SELECT * FROM assessments WHERE id = %s", [id])

    assessment = cur.fetchone()

    # Get Form
    form = AssessmentForm(request.form)

    # Populate Assessment form fields
    form.pf_number.data = assessment['pf_number']
    form.branch.data = assessment['branch']
    form.customer_account.data = assessment['customer_account']
    form.product.data = assessment['product']
    form.crosssell_type.data = assessment['crosssell_type']
    form.naration.data = assessment['naration']

    if request.method == 'POST' and form.validate():
        pf_number = request.form['pf_number']
        branch = request.form['branch']
        customer_account = request.form['customer_account']
        product = request.form['product']
        crosssell_type = request.form['crosssell_type']
        naration = request.form['naration']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("UPDATE assessments SET pf_number=%s, branch=%s, customer_account=%s, product=%s, crosssell_type=%s, naration=%s WHERE id=%s", (pf_number, branch, customer_account, product, crosssell_type, naration, id))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Your Assessment was updated successfully', 'success')

        return redirect(url_for('edit_assessment_page_3'))

    return render_template('edit_assessment_page_2.html', form=form)

# Edit Assessment Page 1 Route  
@app.route('/edit_assessment_page_3/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_assessment_page_1(id):

    # Create Cursor
    cur = mysql.connection.cursor()

    # Get Assessment by id
    result = cur.execute("SELECT * FROM assessments WHERE id = %s", [id])

    assessment = cur.fetchone()

    # Get Form
    form = AssessmentForm(request.form)

    # Populate Assessment form fields
    form.pf_number.data = assessment['pf_number']
    form.branch.data = assessment['branch']
    form.customer_account.data = assessment['customer_account']
    form.product.data = assessment['product']
    form.crosssell_type.data = assessment['crosssell_type']
    form.naration.data = assessment['naration']

    if request.method == 'POST' and form.validate():
        pf_number = request.form['pf_number']
        branch = request.form['branch']
        customer_account = request.form['customer_account']
        product = request.form['product']
        crosssell_type = request.form['crosssell_type']
        naration = request.form['naration']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute 
        cur.execute("UPDATE assessments SET pf_number=%s, branch=%s, customer_account=%s, product=%s, crosssell_type=%s, naration=%s WHERE id=%s", (pf_number, branch, customer_account, product, crosssell_type, naration, id))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Your Assessment was updated successfully', 'success')

        return redirect(url_for('assessments'))

    return render_template('edit_assessment_page_3.html', form=form)

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