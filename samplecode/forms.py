# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 15:50:00 2017

@author: jsalomo1
This script handles the Web Forms for the Project
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    def __init__(self):
        self.username = StringField('Username',validators=[DataRequired()])
        self.password = PasswordField('Password',[
                validators.DataRequired()
                ])

class LoginForm(FlaskForm):
    def __init__(self):
        self.username = StringField('Username',validators=[DataRequired()])
        self.password = PasswordField('Password',[
                validators.DataRequired()
                ])