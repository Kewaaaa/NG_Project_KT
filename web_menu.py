from flask import Flask, request, redirect, render_template, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask("NGFood")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_BINDS'] = {
        'db2': 'sqlite:///receipte.db',
        'db3': 'sqlite:///users-creditcard.db'
}
db = SQLAlchemy(app)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    picture_path = db.Column(db.String(255), unique = True)
    food_name = db.Column(db.String(255))
    price = db.Column(db.Integer)
    ingredients = db.Column(db.String(255))

    def __repr__(self):
        return self.food_name

class Receipte(db.Model):
    __bind_key__ = 'db2'
    id = db.Column(db.Integer, primary_key = True)
    receipte_food_name = db.Column(db.String(255))
    receipt_price = db.Column(db.Integer)
    receipt_total_price = db.Column(db.Integer)
 

class Creditcards(db.Model):
    __bind_key__ = 'db3'
    id = db.Column(db.Integer, primary_key = True)
    card_number = db.Column(db.String(255))
    cvv = db.Column(db.Integer)
    validity = db.Column(db.String(255))
    money = db.Column(db.Integer, nullable=False)


@app.route("/")
def index():    
    content = Food.query.all()
    return render_template("menu.html", content = content)



@app.route("/about/<food_title>")
def about(food_title):
    about_food_content = db.session.query(Food).filter(Food.food_name == food_title).all()
    return render_template("about_page.html", about = about_food_content)



@app.route('/getdata', methods=['GET', 'POST'])
def getData():
    lst = []
    jsn_obj = request.get_json()
    buffer = jsn_obj['price']
    price = int(buffer)
    with open('static/total_price/full_price.txt', mode='a') as f:
        file = f.write(str(buffer) + '\n')
    with open('static/total_price/full_price.txt', 'r') as f:
        fl = f.read()
        line = fl.split('\n')  
    for row in line:
        if row == '':
            continue
        else:
            lst.append(int(row))    
    summa = sum(lst)    
    return jsonify(summa)


@app.route('/pay-page', methods=['GET', 'POST'])
def pay():
    receipte_content = Receipte.query.all()
    full_price = Receipte.query.first()
    price = full_price.receipt_total_price
    return render_template('pay-page.html', rec_content = receipte_content, price=price)

@app.route('/pay-page-handler', methods=['GET', 'POST'])
def payhandler():
    data = request.get_json()
    for key, value in data.items():
        if value.startswith('{') and value.endswith('}'):
            json_value = json.loads(value)
            name = json_value['name']
            food_price = json_value['price']
            element = Receipte(receipte_food_name = name, receipt_price = food_price)
            db.session.add(element)
            db.session.commit()
        elif key == 'total_price':
            print(key, value)
            full_price = Receipte(receipt_total_price = value)
            db.session.add(full_price)
            db.session.commit()
    return jsonify(data)



@app.route('/paycarts',  methods=['GET', 'POST'])
def paycart():
    cardnum = request.form.get('nums')
    req_cvv = request.form.get('cvv')
    req_valid = request.form.get('valid')

    check = db.session.query(Creditcards).filter(Creditcards.card_number == cardnum, Creditcards.cvv == req_cvv, Creditcards.validity == req_valid).all()

    if check:
        full_price = Receipte.query.first()
        price = full_price.receipt_total_price
        cash = Creditcards.query.filter(Creditcards.card_number == cardnum).first()
        my_card = Creditcards.query.filter(Creditcards.card_number == "1234567812345678").first()
        money_int = int(cash.money)
        if money_int > price:
            transaction = money_int - price
            cash.money = transaction
            my_card.money = my_card.money+price
            db.session.commit()
            flash('access')
        return redirect(url_for('pay'))
    return redirect(url_for('pay'))



    # res.headers['Access-Control-Allow-Origin'] = "*"
 

# with app.app_context():
#     db.create_all()
app.run(host="0.0.0.0", port="8081")