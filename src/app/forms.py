# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required, URL


class LoginForm(Form):
    user = TextField('user', validators=[Required()])
    password = PasswordField('pass', validators=[Required()])


class AdminURLForm(Form):
    url = TextField('url', validators=[Required(), URL()])
