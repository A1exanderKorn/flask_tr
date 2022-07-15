from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__) # объект app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app) #В скобках объект класса Flask, в котором мы прописали подключение к базе данных

class Article(db.Model): #класс заголовков, наследуется от db.Model
    id = db.Column(db.Integer, primary_key=True) #pr_key - уникальность, поле
    intro = db.Column(db.String(300), nullable=False) #nullable - наличие хотя бы 1 символа
    title = db.Column(db.String(100), nullable = False)
    text = db.Column(db.Text, nullable=False) #Text - огромный объекм текста
    date = db.Column(db.DateTime, default= datetime.utcnow) #значение по умолчанию - время, в которое была создана статья

    def __repr__(self):
        return '<Article %r>' % self.id #Когда мы будем выбирать объект на основе класса, будет выдаваться сам объект + его id поле self=this



@app.route('/')
@app.route('/home')
def st():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/show_base/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)

@app.route('/show_base')
def show_base():
    articles = Article.query.order_by(Article.date).all()
    return render_template("show_base.html", articles=articles, art_length=len(articles))

@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']
        intro = request.form['intro']

        article = Article(title=title, intro=intro, text=text)
        try:
            db.session.add(article)
            db.session.commit() #сохраняем добавленный объект
            return redirect('/') #на главную страницу
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template('create_article.html')


@app.route('/numbers/api/', methods=['GET', 'POST'])
def numbers():
    act = request.args.get('act')
    if act and act != '':
        numb = request.args.get('number', default=0, type=int)
        return render_template("numbers_finish.html", numb=numb, act=act)
    else:
        return render_template("numbers_start.html")


if __name__ == "__main__":
    app.run(debug=True)
