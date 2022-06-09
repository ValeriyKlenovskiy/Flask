from flask import Flask, render_template, url_for

app = Flask(__name__)
menu = ['Установка', 'Первое приложение','Обратная связь']
@app.route('/')
@app.route('/index')
def index():
    print(url_for('index'))
    return render_template('index.html', menu=menu)
@app.route('/about')
def about():
    print(url_for('about'))
    return render_template('about.html', title='О сайте', menu=menu)
@app.route('/profile/<path:username>')
def profile(username):
    return f'Пользователь: {username}'
if __name__ == '__main__':
    app.run(debug=True)