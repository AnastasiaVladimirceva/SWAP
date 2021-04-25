from flask import Flask, url_for
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_user
from loginform import LoginForm
from data import db_session
from data.users import User
from data.product import Product
from forms.user import RegisterForm
from flask_login import login_required
from flask_login import current_user
from flask_login import logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms.product import ProductForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def start():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        product = db_sess.query(Product).all()
        return render_template('main.html', title='TopSwap', news=product)
    return render_template("main.html", title='TopSwap')


@app.route('/product/<category>', methods=['GET'])
def category(category):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        result = db_sess.query(Product).filter(Product.category == category)
        print(result)
        return render_template('main.html', news=result)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            patronymic=form.patronymic.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        with open('pass.txt', encoding='utf-8', mode='a') as f:
            f.write(
                f'Фамилия - {form.surname.data}; Имя - {form.name.data}; Отчество - {form.patronymic.data}; email - {form.email.data};  password - {form.password.data}\n')
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/help')
def help():
    return render_template('main.html')


@app.route('/product_add', methods=['GET', 'POST'])
@login_required
def product_add():
    form = ProductForm()
    if form.is_submitted():
        db_sess = db_session.create_session()
        product = Product()
        product.title = form.title.data
        product.content = form.content.data
        product.connection = form.connection.data
        product.category = request.form['category']
        current_user.product.append(product)
        db_sess.merge(current_user)
        db_sess.commit()
        f = request.files['file']
        print(f.read())
        return redirect('/')
    return render_template('product.html', title='Добавление записи',
                           form=form)


def data_sum(data):
    duration = datetime.now() - data
    duration_in_s = int(duration.total_seconds())
    if duration_in_s < 60:
        return f'Publicate {duration_in_s} seconds ago'
    duration_in_s //= 60
    if duration_in_s < 60:
        return f'Publicate {duration_in_s} minutes ago'
    duration_in_s //= 60
    if duration_in_s < 24:
        return f'Publicate {duration_in_s} hours ago'
    duration_in_s //= 24
    if duration_in_s < 7:
        return f'Publicate {duration_in_s} days ago'
    duration_in_s //= 7
    if duration_in_s < 12:
        return f'Publicate {duration_in_s} weeks ago'
    duration_in_s //= 12
    if duration_in_s < 52:
        return f'Publicate {duration_in_s} mounths ago'
    duration_in_s //= 52
    return f'Publicate {duration_in_s} years ago'


@app.route('/<idis>', methods=['GET', 'POST'])
def product_info(idis):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        result = db_sess.query(Product).filter(Product.id == idis).first()
        data = data_sum(result.created_date)
        return render_template('news.html', result=result, data=data)
    else:
        return 'Aboba'


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=8080, debug=True)
    # app.run(host='0.0.0.0', port=port)
