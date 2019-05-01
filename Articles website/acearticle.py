from flask import Flask, render_template, flash, url_for, redirect, request
import secrets
import os
from PIL import Image
from forms import RegisterForm, LoginForm, PostForm, SearchBar, UpdateAccount
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'fd7bc5c1e79754cd01beee7ca22d3d93'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///article.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(25), nullable = False)
	email = db.Column(db.String(), unique = True, nullable = False)
	password = db.Column(db.String(60), nullable = False)
	birthdate = db.Column(db.DateTime, nullable = False)
	city = db.Column(db.String(25), nullable = False)
	country = db.Column(db.String(25), nullable = False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	articles = db.relationship('Articles', backref='author', lazy=True)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

class Articles(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(100), nullable = False)
	date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
	content = db.Column(db.Text, nullable = False)
	popularity = db.Column(db.Integer, default = 0)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

@app.route('/')
@app.route('/home')
def home():
	form = SearchBar()
	posts = Articles.query.all()
	articles_list = Articles.query.order_by(Articles.popularity.desc()).limit(5)
	articles_list1 = Articles.query.order_by(Articles.date_posted.desc()).limit(5)
	return render_template('home.html', title = 'home', posts = posts, form = form, articles = articles_list, art = articles_list1)

@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegisterForm()
	if form.validate_on_submit():
		exists = db.session.query(User.id).filter_by(email=form.email.data).scalar() is not None
		if exists:
			flash('Email Id already exists!', 'danger')
			return redirect(url_for('register'))
		else:
			pw = hashlib.sha256((form.password.data).encode('utf-8')).hexdigest()
			user = User(username = form.username.data, email = form.email.data, password = pw, birthdate = form.birthdate.data, city = form.city.data, country = form.country.data)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('login'))
	return render_template('register.html', title = 'registration form', form = form)

@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))		
	form = LoginForm()
	if form.validate_on_submit():
		authenticate_user = User.query.filter_by(email = form.email.data).first()
		if authenticate_user and authenticate_user.password == hashlib.sha256((form.password.data).encode('utf-8')).hexdigest():
			login_user(authenticate_user)
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccessful! Check Email ID and Password', 'danger')
			return redirect(url_for('login'))
	return render_template('login.html', title = 'login form', form = form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route('/new/post', methods = ['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		article = Articles(title = form.title.data, content = form.content.data, user_id = current_user.id)
		db.session.add(article)
		db.session.commit()
		flash('Added new post successfully!', 'success')
		return redirect(url_for('home'))
	return render_template('new_post.html', title = 'add post', form = form)

@app.route('/update/post/<int:post_id>', methods = ['GET','POST'])
@login_required
def update_post(post_id):
	form = PostForm()
	post = Articles.query.get_or_404(post_id)
	if post.user_id == current_user.id:
		if form.validate_on_submit():
			post.title = form.title.data
			post.content = form.content.data
			db.session.commit()
			return redirect(url_for('home'))
	else:
		flash('You are not authorized person!', 'danger')
		return redirect(url_for('home'))

	if request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('update_post.html', title = 'update post', form = form)

@app.route("/post/<int:post_id>/like", methods=['POST'])
@login_required
def like_post(post_id):
    post = Articles.query.get_or_404(post_id)
    val = post.popularity
    post.popularity = val + 1
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Articles.query.get_or_404(post_id)
    if post.user_id == current_user.id:
    	db.session.delete(post)
    	db.session.commit()
    else:
    	flash('You are not authorized user!', 'danger')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/read")
def read_post(post_id):
    post = Articles.query.get_or_404(post_id)
    return render_template('read_article.html', title='articles', post=post)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account/<int:user_id>")
def account(user_id):
	form = UpdateAccount()
	user = User.query.get_or_404(user_id)
	print(user.image_file)
	articles = user.articles

	if request.method == 'GET':
		form.username.data = user.username
		form.email.data = user.email
		form.city.data = user.city
		form.country.data = user.country
	image_file = url_for('static', filename='profile_pics/' + user.image_file)
	return render_template('account.html', title='account page', user = user, articles = articles, form = form, image_file = image_file)

@app.route('/update/account/<int:user_id>', methods = ['GET','POST'])
@login_required
def update_account(user_id):
	form = UpdateAccount()
	user = User.query.get_or_404(user_id)
	exists = db.session.query(User.id).filter_by(email=form.email.data).scalar() is not None
	if user.id == current_user.id:
		if form.validate_on_submit():
			if current_user.email == form.email.data or not exists:
				if form.picture.data:
					picture_file = save_picture(form.picture.data)
					user.image_file = picture_file
				user.username = form.username.data
				user.email = form.email.data
				user.city = form.city.data
				user.country = form.country.data
				db.session.commit()
				return redirect(url_for('account', user_id=current_user.id))
			else:
				flash('Email ID alread taken!', 'danger')
				return redirect(url_for('account', user_id=current_user.id))

	else:
		flash('You are not authorized person!', 'danger')
		return redirect(url_for('account', user_id=current_user.id))
	return render_template('account.html', title = 'account', form = form)





if __name__ == '__main__':
	app.run(debug = True)