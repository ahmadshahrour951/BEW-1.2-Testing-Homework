import os
from unittest import TestCase

from datetime import date

from books_app import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################


def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()


def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################


class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        # TODO: Write a test for the signup route. It should:
        # - Make a POST request to /signup, sending a username & password
        # - Check that the user now exists in the database
        data = {
            'username': 'test',
            'password': 'test',
        }
        self.app.post('/signup', data=data)
        user = User.query.filter_by(username='test').one()
        self.assertIsNotNone(user)
        self.assertEqual('test', user.username)

    def test_signup_existing_user(self):
        # TODO: Write a test for the signup route. It should:
        # - Create a user
        # - Make a POST request to /signup, sending the same username & password
        # - Check that the form is displayed again with an error message
        data = {
            'username': 'test',
            'password': 'test',
        }
        # perform the first signup
        self.app.post('/signup', data=data)

        #perform the second signup with the same user data
        res = self.app.post('/signup', data=data)
        res_text = res.get_data(as_text=True)
        self.assertIn('That username is taken.', res_text)

    def test_login_correct_password(self):
        # TODO: Write a test for the login route. It should:
        # - Create a user
        # - Make a POST request to /login, sending the created username & password
        # - Check that the "login" button is not displayed on the homepage
        data = {
            'username': 'test',
            'password': 'test',
        }
        self.app.post('/signup', data=data)
        res = self.app.post('/login', data=data,  follow_redirects=True)
        res_text = res.get_data(as_text=True)
        self.assertNotIn('Log In', res_text)
        self.assertIn('You are logged in as test', res_text)

    def test_login_nonexistent_user(self):
        # TODO: Write a test for the login route. It should:
        # - Make a POST request to /login, sending a username & password
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        data = {
            'username': 'test_2',
            'password': 'test_2',
        }
        res = self.app.post(
            '/login', data=data,  follow_redirects=True)
        res_text = res.get_data(as_text=True)
        self.assertNotIn('Log Out', res_text)
        self.assertIn(
            'No user with that username. Please try again.', res_text)

    def test_login_incorrect_password(self):
        # TODO: Write a test for the login route. It should:
        # - Create a user
        # - Make a POST request to /login, sending the created username &
        #   an incorrect password
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        data = {
            'username': 'test',
            'password': 'test',
        }
        self.app.post('/signup', data=data)
        data['password'] = 'test_2'
        res = self.app.post(
            '/login', data=data,  follow_redirects=True)
        res_text = res.get_data(as_text=True)
        self.assertNotIn('Log Out', res_text)
        self.assertIn(
            "Password doesn&#39;t match. Please try again.", res_text)

    def test_logout(self):
        # TODO: Write a test for the logout route. It should:
        # - Create a user
        # - Log the user in (make a POST request to /login)
        # - Make a GET request to /logout
        # - Check that the "login" button appears on the homepage
        data = {
            'username': 'test',
            'password': 'test',
        }
        self.app.post('/signup', data=data)
        self.app.post('/login', data=data)
        res = self.app.get('/logout', follow_redirects=True)
        res_text = res.get_data(as_text=True)
        self.assertIn('Log In', res_text)
