from datetime import datetime
from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
# from wtforms import StringField, TextAreaField, SelectField, SubmitField
# from wtforms.validators import DataRequired
from flask_wtf import CSRFProtect
from forms import LoginForm, RegisterForm, PostJobForm
from flask_migrate import Migrate
import os
from config import Config
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object(Config)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jobs = db.relationship('Job', backref='user', lazy=True)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    pay = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    poster_name = db.Column(db.String(100), nullable=False)
    poster_contact = db.Column(db.String(100), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
    db.Integer,
    db.ForeignKey('user.id', name='fk_job_user_id'),
    nullable=True
    )
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 



@app.route('/')
def home():
    selected_category = request.args.get('category')
    if selected_category:
        jobs = Job.query.filter_by(category=selected_category).all()
    else:
        jobs = Job.query.all()
    return render_template('index.html', jobs=jobs, selected_category=selected_category)

@app.route('/post', methods=['GET', 'POST'])
def post_job():
    if 'user' not in session:
        flash('Please, login first.')
        return redirect('/login')
    
    form = PostJobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            pay=form.pay.data,
            category=form.category.data,
            poster_name=form.poster_name.data,
            poster_contact=form.poster_contact.data,
            user_id=session.get('user_id')
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect('/')
    
    return render_template('post.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        fullname = form.fullname.data
        email = form.email.data
        phone = form.phone.data
        username = form.username.data
        password = form.password.data

        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("Username or email already exists. Try another.", "danger")
            return render_template('register.html', form=form), 409

        hashed_password = generate_password_hash(password)

        new_user = User(
            fullname=fullname,
            email=email,
            phone=phone,
            username=username,
            password=hashed_password,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        session['user'] = username
        session['user_id'] = new_user.id
        session['role'] = new_user.role

        flash('User successfully registered!', 'success')
        return redirect('/')

    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if user.role == 'banned':
                flash('Your account has been banned. Contact support.', 'danger')
                return redirect(url_for('login'))

            session['user'] = user.username
            session['user_id'] = user.id
            session['role'] = user.role
            flash('You are successfully logged in!', 'success')
            return redirect('/')
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html', form=form)


# This way, when the admin logs in, session['role'] will be 'admin', and we can use it to gatekeep the /admin route like this:

# Admin route
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        flash('Admin dashboard is strictly for admin!', 'error')
        return redirect(url_for('login'))
    
    jobs = Job.query.all()
    users = User.query.all()
    
    flash('You are logged to the admin dashboard. Be careful, you now have elevated leverage on the site', 'success')
    return render_template('admin.html', jobs=jobs, users=users)

# Delete posted job
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if session.get('role') != 'admin':
        flash('Admin dashboard is strictly for admin!', 'error')
        return redirect(url_for('login'))

    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('admin'))

# Ban a user
@app.route('/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    if session.get('role') != 'admin':
        flash('Admin dashboard is strictly for admin!', 'error')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    user.role = 'banned'
    db.session.commit()
    flash('Ban successfully initiated!', 'success')
    return redirect(url_for('admin'))

# To unban a user
@app.route('/unban_user/<int:user_id>', methods=['POST'])
def unban_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    user.role = 'user'  # or set to previous role if stored elsewhere
    db.session.commit()
    flash('User has been unbanned successfully!', 'success')
    if session.get('role') != 'admin':
        flash('Admin dashboard is strictly for admin!', 'error')
    return redirect(url_for('login'))

@app.route('/promote_user/<int:user_id>', methods=['POST'])
def promote_user(user_id):
    if session.get('role') != 'admin':
        flash('Admin dashboard is strictly for admin!', 'error')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash('You promoted a user to admin!', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if session.get('role') != 'admin':
        flash('Admin dashboard is strictly for admin!', 'error')
        return redirect(url_for('login'))

    job = Job.query.get_or_404(job_id)
    form = PostJobForm(obj=job)

    if form.validate_on_submit():
        form.populate_obj(job)
        db.session.commit()
        flash('Job successfully edited!', 'success')
        return redirect(url_for('admin'))

    return render_template('edit_job.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=False)