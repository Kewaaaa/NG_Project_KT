from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask("NGFood")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
db = SQLAlchemy(app)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    picture_path = db.Column(db.String(255), unique = True)
    food_name = db.Column(db.String(255))
    price = db.Column(db.Integer)
    ingredients = db.Column(db.String(255))

    def __repr__(self):
        return self.food_name

@app.route("/")
def index():
    content = Food.query.all()
    return render_template("menu.html", content = content)

@app.route("/about/<food_title>")
def about(food_title):
    about_food_content = db.session.query(Food).filter(Food.food_name == food_title).all()
    return render_template("about_page.html", about = about_food_content)


app.run(host="0.0.0.0", port="8081")