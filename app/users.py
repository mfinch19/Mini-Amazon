from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.user import User


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField(_l('First Name'), validators=[DataRequired()])
    lastname = StringField(_l('Last Name'), validators=[DataRequired()])
    mailingaddress = StringField(_l('Mailing Address'), validators=[DataRequired()])
    zipcode = StringField(_l('ZIP Code'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    balance = 0
    submit = SubmitField(_l('Register'))

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('There is already an account associated with this email address.'))

class UpdatePasswordForm(FlaskForm):
    oldpassword = PasswordField(_l('Confirm Current Password'), validators=[DataRequired()])
    password = PasswordField(_l('New Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat New Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Confirm Password Change'))

    def validate_oldpassword(self, oldpassword):
        if User.password_match(current_user.email, oldpassword.data) == False:
            raise ValidationError(_('This does not match the password associated with your account.'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.mailingaddress.data,
                         form.zipcode.data,
                         form.balance)          
        flash('Congratulations, you are now a registered user! Login to begin shopping.')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/account_balance', methods=['GET', 'POST'])
def view_balance():
    return render_template('account_balance.html')

@bp.route('/withdraw_balance', methods=['GET', 'POST'])
def withdraw_balance():
    User.withdraw_balance(request)
    return redirect(url_for('users.view_balance'))

@bp.route('/add_balance', methods=['GET', 'POST'])
def add_balance():
    User.add_balance(request)
    return redirect(url_for('users.view_balance'))

@bp.route('/view_account_info', methods=['GET', 'POST'])
def view_account_info():
    return render_template('edit_account.html')

@bp.route('/edit_account_info', methods=['GET', 'POST'])
def edit_account_info():
    User.update_account_info(request)
    return redirect(url_for('index.profile'))

@bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = UpdatePasswordForm()

    if form.validate_on_submit():
        User.update_password(form.password2.data)        
        logout_user()  
        flash('Your password has been updated. Please login.')
        return redirect(url_for('users.login'))
    return render_template('change_password.html', title='Change Password', form=form)