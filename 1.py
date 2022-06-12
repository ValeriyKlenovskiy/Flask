from flask import Flask, render_template, url_for, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aslfasklf8af8433klsdf'
menu = [{'name': 'Установка', 'url': 'install-flask'},
        {'name': 'Первое приложение', 'url': 'first-app'},
        {'name': 'Обратная связь', 'url': 'contact'}]
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', menu=menu)
@app.route('/about')
def about():
    return render_template('about.html', title='О сайте', menu=menu)
@app.route('/profile/<path:username>')
def profile(username):
    return f'Пользователь: {username}'
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.html', title='Обратная связь', menu=menu)
if __name__ == '__main__':
    app.run(debug=True)