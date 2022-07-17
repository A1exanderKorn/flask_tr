from flask import Flask, render_template, url_for, request, redirect, Blueprint, current_app, json
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


SWAGGER_URL = '/docs'
API_URL = '/swagger'
swagger_ui_blueprint = get_swaggerui_blueprint(
   SWAGGER_URL,
   API_URL,
   config={
       'app.py': "my app"
   }
)
blueprint_numbers = Blueprint(name="Numbers", import_name=__name__)

app = Flask(__name__) # объект app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app) #В скобках объект класса Flask, в котором мы прописали подключение к базе данных

app.register_blueprint(swagger_ui_blueprint)

class InputSchema(Schema):
   number = fields.Int(description="Число", required=True, example=5)
   type = fields.Str(description="Тип информации", required=True, example="year")


class OutputSchema(Schema):
   result = fields.Str(description="Статья", required=True, example="http://numbersapi.com/5/year")


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


"""@blueprint_numbers.route('/numbers/api')
def numbers():
    act = request.args.get('act', default="year", type=str)
    numb = request.args.get('number', default=0, type=int)
    return{
        "text": numb,
        "type": act,
        "fact": "http://numbersapi.com/" + str(numb) + "/" + act
    }
"""
#!!!  Не до конца понял, почему в примере они прописали @blueprint_numbers.route, подозреваю, что это для описания методов в /docs, но я попытался как-то это сделать и не получилось Как описать метод в docs? Как добавить метод в какой-то созданный тег? !!!


@app.route('/numbers/api')
def numbers():
    act = request.args.get('act', default="year", type=str)
    numb = request.args.get('number', default=0, type=int)
    return{
        "text": numb,
        "type": act,
        "fact": "http://numbersapi.com/" + str(numb) + "/" + act
    }
#!!!  Нормально ли все с этой функцией? Я просто практически скопировал то, что ты написал, и добавил еще в json ссылку на статью, но нужно ли мне как-то вывести саму статью и как это сделать, я не особо разобрался. !!!

def load_docstrings(spec, app):
   # Загружаем описание API.
   #:spec: объект APISpec, куда загружаем описание функций
   #:app: экземпляр Flask приложения, откуда берем описание функций
   for fn_name in app.view_functions:
       if fn_name == 'static':
           continue
       view_fn = app.view_functions[fn_name]
       spec.path(view=view_fn)

def get_apispec(app):
    spec = APISpec(
        title="my_app",
        version="1.0.0",
        openapi_version = "3.0.3",
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )
    spec.components.schema("Input", schema=InputSchema)
    spec.components.schema("Output", schema=OutputSchema)

    load_docstrings(spec, app)
    return spec


def create_tags(spec):
   #spec: объект APISpec для сохранения тегов
   tags = [{'name': 'numbers', 'description': 'Операции с числами'}]
   for tag in tags:
       spec.tag(tag)


@app.route('/swagger')
def create_swagger():
    return json.dumps(get_apispec(app).to_dict())

#!!! Вот эти 3 функции я скопировал с хабра, переделал немного под себя, вроде все работает, создал описание в docs только для своей функции numbers, нужно ли в них что-то поправить?
# И еще там был компонент Error, помимо output и input, но у меня ошибки вроде не обрабатываются, поэтому добавлять не стал !!!

if __name__ == "__main__":
    app.run(debug=True)
