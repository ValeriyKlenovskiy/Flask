import sqlite3
import os
import datetime
from flask import Flask, render_template, request, g, flash, abort, make_response, session, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required
from UserLogin import UserLogin

DATABASE = '/tmp/flsite.bd'
DEBUG = True
SECRET_KEY = 'aslfasklf8af8433klsdf'

app = Flask(__name__)
app.config.from_object(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=1)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect((app.config['DATABASE']))
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None

@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/visits')
def visits():
    session.permanent = True
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    return f"<h1> Visits counter</h1><p>Число просмотров: {session['visits']}"

@app.route('/')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnnounce())

#@app.route('/ima')
# def ima():
#     img = None
#     with app.open_resource( app.root_path + "/static/images_html/123.png", mode='rb') as f:
#         img = f.read()
#     if img is None:
#         return "None image"
#     res = make_response(img)
#     res.headers['Content-Type'] = 'image/png'
#     return res

@app.route("/add_post", methods=["POST","GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_post.html', menu= dbase.getMenu(), title="Добавление статьи")

@app.route("/post/<alias>")
#@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль', category='error')
    return render_template('login.html', title='Авторизация', menu=dbase.getMenu())


@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4\
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash('Вы успешно зарегистрированы', category='success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при добавлении в БД', category='error')
        else:
            flash('Неверно заполнены поля', category='error')
    return render_template('register.html', title='Регистрация', menu=dbase.getMenu())

@app.route('/logout')
def logout():
    res = make_response('<p>Вы больше не авторизированы<p>')
    res.set_cookie('logged', '', 0)
    return res

@app.route('/profile/<path:username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.html', title='Обратная связь', menu=dbase.getMenu())

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title='Страница не найдена', menu=dbase.getMenu()), 404

if __name__ == '__main__':
    app.run(debug=True)