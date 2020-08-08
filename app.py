from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from flask_mail import Message
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///db.db'
app.config['SECRET_KEY']='619619'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['MAIL_DEFAULT_SENDER'] = ""
db = SQLAlchemy(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))

@login_manager.user_loader
def get(id):
    return User.query.get(id)

@app.route('/',methods=['GET','POST'])
def get_login(): 

    if request.method == 'POST':  
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('user does not exist signup or try again')
            return redirect('/')

        if not check_password_hash(user.password, password):
            flash('password is incorrect')
            return redirect('/')
        
        login_user(user)
        return redirect('/home')

    else:
        return render_template('open.html')

@app.route('/home')
@login_required
def home():
    all_users = User.query.order_by(User.id).all()
    return render_template('home.html',all_users= all_users)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_id = current_user.id
    user_to_delete = User.query.get_or_404(id)

    if current_user == user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash ('you deleted yourself')
        return redirect('/')

    else:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash ('user was deleted')
        return redirect('/home')

@app.route('/logout', methods=['GET','POST'])
def logout():
    if request.method == 'POST':
        return redirect ('/')

# @app.route('/verify', methods=['GET','POST'])
# def verify():
#     if request.method == 'POST':
#         otp = 

@app.route('/signup', methods=['GET','POST'])
def signup_post():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        user = User.query.filter_by(email=email).first()
        if user:
            flash( 'Email address already exists.')
            time.sleep(2)
            return redirect('/signup')
        
        new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))
        flash('signup succesfull')
        time.sleep(2)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    
    else: 
        return render_template('signup.html')
 
if __name__ == "__main__":
    app.run(debug=True) 