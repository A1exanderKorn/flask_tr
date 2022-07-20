import json,os
import logging
import sys
from flask import Flask, render_template, url_for, request, redirect, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from datetime import datetime

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields



app = Flask(__name__) # объект app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app) #В скобках объект класса Flask, в котором мы прописали подключение к базе данных


template = {
    "swagger":"2.0",
    "info":{
        "title":"Numbers(head, title)",
        "description":"info about numbers",
        "contact":{
            "url":"http://numbersapi.com/#42"
        },
        "version":"0.0.1"
    },
    "host":"me",
    "basePath":"api",
    "schemes":["http", "https"],
    "operationId":"numb"
}


swagger = Swagger(app, template = template)

@app.route('/numbers/api')
def numbers():
    """
    post endpoint
    ---
    tags:
        - info about numbers
    parameters:
        - name: number
          in: query
          type: integer
          required: true
          description: number
        - name: act
          in: query
          type: string
          required: true
          description: type of info

    """
    act = request.args.get('act', default="year", type=str)
    numb = request.args.get('number', default=0, type=int)
    return{
        "number": numb,
        "type": act,
        "fact": "http://numbersapi.com/" + str(numb) + "/" + act
    }
#!!! Нормально ли все с этой функцией? Я просто практически скопировал то, что ты написал, и добавил еще в json ссылку на статью, но нужно ли мне как-то вывести саму статью и как это сделать, я не особо разобрался.
#!!! Есть ощущение, что мне надо прописать возможность ввода пользователем параметров act и numb, это надо организовать в этой функции?

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


if __name__ == "__main__":
    app.run(debug=True)
