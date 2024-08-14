from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
from flask_app import bcrypt
from datetime import datetime, timedelta

class User:
    db = 'login_reg_schema'

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.birthday = data['birthday']
        self.gender = data['gender']
        self.password = data['password']

    @staticmethod
    def create(form_data):
        query = """
            INSERT INTO users
            (first_name, last_name, email, password, birthday, gender)
            VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(birthday)s, %(gender)s);
        """

        secure_user_data = {
            'first_name': form_data['first_name'],
            'last_name': form_data['last_name'],
            'email': form_data['email'],
            'birthday': form_data['birthday'],
            'gender': form_data['gender'],
            'password': bcrypt.generate_password_hash(form_data['password'])
        }

        user_id = connectToMySQL('login_reg_schema').query_db(query, secure_user_data)

        return user_id
    
    @classmethod
    def get_one_by_email(cls, email):
        query = """
                SELECT * FROM users
                WHERE email = %(email)s;
            """
        results = connectToMySQL(cls.db).query_db(query, email)
        
        this_user = cls(results[0])
    
        return this_user
    
    @classmethod
    def validate_user(cls, form_data):
        is_valid = True
        print("Validating form data...")

        # Validate first name
        if not form_data['first_name']:
            flash('First name is required', 'registration')
            is_valid = False
        elif len(form_data['first_name']) < 2:
            flash('First name must be at least 2 characters.', 'registration')
            is_valid = False

        # Validate last name
        if not form_data['last_name']:
            flash('Last name is required', 'registration')
            is_valid = False
        elif len(form_data['last_name']) < 2:
            flash('Last name must be at least 2 characters', 'registration')
            is_valid = False

        # Validate that email was entered
        if not form_data['email']:
            flash('Email is required', 'registration')
            is_valid = False
        # If email entered, continue with other email validation checks
        else: 
            # Validate that email does not yet exist in DB
            query = """
                SELECT * FROM users
                WHERE email = %(email)s;
            """
            results = connectToMySQL(cls.db).query_db(query, form_data)

            if len(results) > 0:
                flash('User with this email already exists', 'registration')
                is_valid = False

            # Validate email format
            EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
            if not EMAIL_REGEX.match(form_data['email']):
                flash('Invalid email format', 'registration')
                is_valid = False

        # Validate birthday
        if not form_data['birthday']:
            flash('Birthday is required', 'registration')
            is_valid = False
        # If birthday entered, contintue with other birthday validation checks
        else:
            # User must be between 10 and 130 years old
            birth_date = datetime.strptime(form_data['birthday'], '%Y-%m-%d').date()
            today = datetime.today().date()
            ten_years_ago = today - timedelta(days=365*10)
            one_hundred_thirty_years_ago = today - timedelta(days=365*130)
            if birth_date > ten_years_ago:
                flash('You must be at least 10 years old to register', 'registration')
                is_valid = False
            elif birth_date < one_hundred_thirty_years_ago:
                flash('Please enter an accurate birthday', 'registration')

        # Validate gender
        if 'gender' not in form_data:
            flash('Gender is required', 'registration')
            is_valid = False

        # Validate newsletter selections
        if 'newsletters' not in form_data:
            flash('Please select at least one newsletter', 'registration')
            is_valid = False

        # Validate that password was entered:
        if not form_data['password']:
            flash('Password is required', 'registration')
            is_valid = False
        # If password was entered, continue with other password validation checks:
        else: 
            # Validate password confirmation
            if form_data['password'] != form_data['confirm-password']:
                flash('Passwords must match', 'registration')
                is_valid = False
            # Password must contain at least 8 characters, at least one uppercase letter, one lowercase letter, one number, and one special character
            PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
            if not PASSWORD_REGEX.match(form_data['password']):
                flash('Password must contain minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character', 'registration')
                is_valid = False

        return is_valid

    @classmethod
    def validate_login(cls, form_data):
        is_valid = True

        if not form_data['email']:
            flash('Email is required', 'login')
            is_valid = False

        if not form_data['password']:
            flash('Password is required', 'login')
            is_valid = False

        return is_valid

    @classmethod
    def login(cls, form_data):

        if not cls.validate_login(form_data):
            return False

        # Determine whether the email exists in the DB
        query = """
                SELECT * FROM users
                WHERE email = %(email)s;
            """
        results = connectToMySQL(cls.db).query_db(query, form_data)

        if len(results) < 1:
            flash('Invalid email/password', 'login')
            print('Email does not exist in db')
            return False
        
        # Determine whether the password provided matches the password in the DB
        if not bcrypt.check_password_hash(results[0]['password'], form_data['password']):
            flash('Invalid email/password', 'login')
            print('Password incorrect')
            return False
        
        # If login form passes validation checks, return a User object
        return cls(results[0])