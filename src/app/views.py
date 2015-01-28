# -*- coding: utf-8 -*-
from flask import render_template, redirect, session, url_for, request, g, flash
from flask.ext.login import LoginManager, UserMixin, login_required, logout_user, login_user, current_user

from fetch import update
import time

from app import app, settings

from forms import LoginForm, AdminURLForm
from app.fetch import load_urls, save_urls

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    user_database = {"admin": ("admin", "Admin"),
                     "jazz": ("jazz", "Jazz")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls, userid):
        u_data = cls.user_database.get(userid, None)
        if u_data:
            return cls(u_data[0], u_data[1])
        return None


@app.before_request
def before_request():
    g.user = current_user


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = load_user(form.user.data)
        if user and form.password.data == user.password:
            print form.user.data
            login_user(user)
            flash(u"Вы вошли")
            return redirect(request.args.get("next") or url_for("admin"))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/delete_url", methods=["POST"])
@login_required
def delete_url():
    fn = request.form.get("id")
    urls = load_urls()
    for u in urls:
        if u['filename'] == fn:
            flash(u"Адрес %s удален" % (u['url']))
            urls.remove(u)
            break
    save_urls(urls)
    return redirect(url_for("admin"))


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    form = AdminURLForm()
    urls = load_urls()
    if form.validate_on_submit():
        urls.append({"url": form.url.data,
                     "filename": "cache_%0.0f" % (time.time()*1000)})
        save_urls(urls=urls)
        flash(u"Адрес %s добавлен" % (form.url.data))
    return render_template("admin.html", form=form,  urls=urls)


@app.route('/')
@app.route('/index')
def index():
    results = update(urls=load_urls())
    return render_template('index.html', results=results)
