from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random
import time 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///db.db'
app.config['SECRET_KEY']='WDx6XbW1jj6ak63zCF'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'kimomonk213@gmail.com'
app.config['MAIL_PASSWORD'] = 'WDx6XbW1jj6ak63zCF'
app.config['MAIL_DEFAULT_SENDER'] = 'kimomonk213@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False 
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))
    otp = db.Column(db.Integer(), default=0)

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
            flash('*user does not exist signup or try again*')
            return redirect('/')

        if not check_password_hash(user.password, password):
            flash('*password is incorrect*')
            return redirect('/')
        
        login_user(user)
        return redirect('/home')

    else:
        logout_user()
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

    if user_id == user_to_delete.id:
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
        user = current_user
        logout_user()
        return redirect ('/')

@app.route('/verify/<int:id>', methods=['GET','POST'])
def verify (id):
    check_user = User.query.get_or_404(id)
    og_otp = check_user.otp 
    check_otp = request.form.get('OTP')

    if not int(check_otp) == int(og_otp):
        flash('**otp is incorrect**')
        db.session.delete(check_user)
        db.session.commit()
        #return render_template('verify.html', newuser = check_user)
        return redirect('/signup') 

    flash('verification succesful')
    time.sleep(2)
    login_user(check_user)
    return redirect('/home')


@app.route('/signup', methods=['GET','POST'])
def signup_post():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        user = User.query.filter_by(email=email).first()
        if user:
            flash( '**Email address already exists.**')
            time.sleep(2)
            return redirect('/signup')
        
        otp = random.randint(100,999)

        msg = Message("OTP",recipients=[email])
        msg.body =  "hello, %s your OTP is: %d " % (username,otp) 
        mail.send(msg)
        flash ('confirm your otp')
        newuser = User(email=email, username=username, password=generate_password_hash(password, method='sha256'), otp = otp )
        db.session.add(newuser)
        db.session.commit()
        return render_template('verify.html', newuser = newuser)
    
    else: 
        return render_template('signup.html')
 
if __name__ == "__main__":
    app.run(debug=True) 