from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///small_arms_factory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for complaints
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

# WTForm for complaint submission
class ComplaintForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Please enter your name.")])
    email = StringField('Email', validators=[DataRequired(message="Please enter your email."), Email(message="Invalid email address.")])
    subject = StringField('Subject', validators=[DataRequired(message="Please enter a subject.")])
    description = TextAreaField('Description', validators=[DataRequired(message="Please enter the description of your complaint.")])
    submit = SubmitField('Submit Complaint')

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ComplaintForm()
    if form.validate_on_submit():
        complaint = Complaint(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            description=form.description.data
        )
        db.session.add(complaint)
        db.session.commit()
        flash('Your complaint has been submitted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/complaints')
def complaints():
    all_complaints = Complaint.query.all()
    return render_template('complaints.html', complaints=all_complaints)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Simple authentication (for demonstration purposes)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':  # Change these credentials
            complaints = Complaint.query.all()
            return render_template('admin.html', complaints=complaints)
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin_login.html')

@app.route('/delete/<int:complaint_id>')
def delete_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint has been deleted.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
