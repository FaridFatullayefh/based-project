from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'PvaqqdTuvlvly71'  
db = SQLAlchemy(app)

USERNAME = 'admin'
PASSWORD = 'admin'

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False) 
    user_codes = db.relationship('UserCode', backref='account', lazy=True)
    
class UserCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(4), nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and password == PASSWORD:
            session['username'] = username  
            return redirect(url_for('dashboard'))
        else:
            return 'Səhv var', 401
    return render_template('login.html')

categories = ["Netflix", "Spotify", "Youtube Premium", "Canva", "Duolingo", "Exxen", "İpTV",
    "Prime Video", "ChatGPT", "Freepik", "Envato", "ADOBE Creative Cloud", "CapCut PRO",
    "Gain", "Deezer", "Yandex Music", "Storytel", "Udemy", "Adobe Stock", "iStock",
    "Shutterstock", "Semrush", "Picsart", "Brandpack", "Figma", "JetBrains", "Flaticon",
    "Lovepik", "Pikbest", "PNGtree", "Motion Array", "AutoDesk", "AutoCAD", "3DMax",
    "Ofis Proqramları", "Windows 10-11", "Tinder Premium", "VPN", "Canlı TV kanallar", "Sports"]  

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:  
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_category = request.form.get('new_category')  
        if new_category and new_category not in categories:  
            categories.append(new_category)  
        
        category = request.form.get('existing_category') 
        if category:
            return redirect(url_for('accounts_by_category', category=category)) 

        return redirect(url_for('dashboard'))  
    
    return render_template('dashboard.html', categories=categories)


@app.route('/accounts/<category>', methods=['GET', 'POST'])
def accounts_by_category(category):
    if 'username' not in session:  
        return redirect(url_for('login'))

    if category not in categories:
        return 'Kategoriya tapılmadı', 404

    accounts = Account.query.filter_by(category=category).all()
    
    if request.method == 'POST':
        account = request.form['account']
        user_code = request.form['user_code']
        end_date = request.form['end_date']
        
        email, password = account.split(':') 
        
        new_account = Account(email=email, password=password, category=category)
        db.session.add(new_account)
        db.session.commit()
        
        if user_code:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            new_user_code = UserCode(user_code=user_code, end_date=end_date_obj, account_id=new_account.id)
            db.session.add(new_user_code)
            db.session.commit()
        
        return redirect(url_for('accounts_by_category', category=category))
    
    return render_template('accounts_by_category.html', accounts=accounts, category=category)

@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    if 'username' not in session:  
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        account = request.form['account']
        user_code = request.form['user_code']
        end_date = request.form['end_date']
        
        email, password = account.split(':')  
        
        new_account = Account(email=email, password=password)
        db.session.add(new_account)
        db.session.commit()
        
        if user_code:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            new_user_code = UserCode(user_code=user_code, end_date=end_date_obj, account_id=new_account.id)
            db.session.add(new_user_code)
            db.session.commit()
        
        return redirect(url_for('accounts_by_category'))
    
    accounts = Account.query.all()
    return render_template('accounts_by_category.html', accounts=accounts)
@app.route('/add_user_code/<account_id>', methods=['POST'])
def add_user_code(account_id):
    if 'username' not in session:  
        return redirect(url_for('login'))
    
    user_code = request.form['user_code']
    end_date = request.form['end_date']
    
    if len(user_code) == 4 and user_code.isdigit():
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        new_user_code = UserCode(user_code=user_code, end_date=end_date_obj, account_id=account_id)
        db.session.add(new_user_code)
        db.session.commit()
        
        account = Account.query.get(account_id)
        if account:
            category = account.category
            return redirect(url_for('accounts_by_category', category=category))
    
    return redirect(url_for('dashboard')) 


@app.route('/delete_user_code/<int:account_id>/<int:user_code_id>', methods=['POST'])
def delete_user_code(account_id, user_code_id):
    account = Account.query.get(account_id)
    if account:
        user_code = UserCode.query.get(user_code_id)
        if user_code:
            db.session.delete(user_code)
            db.session.commit()
    return redirect(url_for('accounts_by_category', category=account.category))  

@app.route('/logout')
def logout():
    session.pop('username', None)  
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(debug=True)
