#when time allows, go back and neatly comment everything
#you won't remember the flow or reasoning if you don't

from flask import Flask, request, redirect, render_template, flash, session
from app import app, db
from models import Blog, User
from hashutils import make_pw_hash, check_pw_hash
import os


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'signup', 
        'index', 'home']
    
    if 'user' not in session and request.endpoint not in allowed_routes:
            return redirect('/login')

@app.route("/")
def index():
    return redirect("/blog")

@app.route("/blog")
def home():
    blogs = Blog.query.all()
    welcome = "Elvis has left the building. Log in or Register"
    
    if 'user' in session:
        welcome = session['user'] + " is in the HOUSE!!!"

    return render_template('home.html', title= "BLoGz", 
        blogs= blogs, welcome= welcome)

@app.route("/newblog", methods= ['POST', 'GET'])
def AddBlog():
    error = {"title_blank": "", "body_blank": ""}
    new_body = ""
    new_title = ""
    welcome = session['user'] + " is in the HOUSE!!!"
    existing_user = User.query.filter_by(username=session['user']).first()

    if request.method == 'POST':
        new_title = request.form["title"]
        new_body = request.form["body"]

        if new_title == "":
            error["title_blank"] = "Title your BLoG"
        if new_body == "":
            error["body_blank"] = "You need to add text for your BLoG"

        if error["title_blank"] == "" and error["body_blank"] == "":
            new_blog = Blog(new_title, new_body, existing_user)
            db.session.add(new_blog)
            db.session.commit()
            author = User.query.filter_by(id= new_blog.owner_id).first()
            return redirect("/individual?blog_title="+new_title)

    return render_template('newblog.html', title= "Add a BLoG post", 
        newblog_body= new_body, newblog_title= new_title,
        title_blank= error["title_blank"], body_blank= error["body_blank"],
        welcome= welcome)

@app.route("/individual")
def blog_def():
    welcome = "Elvis has left the building. Log in or Register"
    
    if 'user' in session:
        welcome = session['user'] + " is in the HOUSE!!!"
        title = request.args.get('blog_title')
    
    if title:
        existing_blog = Blog.query.filter_by(title= title).first()
        author = User.query.filter_by(id= existing_blog.owner_id).first()
        return render_template("individual.html", 
            title= existing_blog.title, body= existing_blog.body,
            author= author.username, welcome= welcome)

@app.route("/singleUser")
def UserPosts():
    welcome = "Elvis has left the building. Log in or Register"
 
    if 'user' in session:
        welcome = session['user'] + " is in the HOUSE!!!"
        user = request.args.get('user_link')
    
    if user:
        existing_user = User.query.filter_by(username= user).first()
        user_posts = existing_user.blogs
        return render_template("singleUser.html", welcome= welcome,
            title= user+"'s posts", blogs= user_posts)

    user_list = User.query.all()

    return render_template("blogs.html", title= "BLoGz",
        welcome= welcome, user_list= user_list)

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    error = {"name_error": "", "pass_error": "", "verify_error": ""}
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "":
            error["name_error"] = "Username Can Not Be Blank"
        
        if password == "":
            error["pass_error"] = "Password Must Be At Least 3 Characters"
        
        elif len(password) < 2:
            error["pass_error"] = "Password Must Be At Least 3 Characters"
        
        else:
            if password != verify:
                error["verify_error"] = "Paswords Do Not Match"

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            error["name_error"] = "You're Late To The Party! Try Another Name"

        if error["name_error"] == "" and error["pass_error"] == "" and error["verify_error"] == "":
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            return redirect("/blog")

    return render_template("signup.html", title= "Register for this BLoG",
        name_error= error["name_error"], pass_error= error["pass_error"],
        verify_error= error["verify_error"])

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = {"name_error": "", "pass_error": ""}
    username = ""
            
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            if password == "":
                error["pass_error"] = "Password Must Be At Least 3 Characters"

            elif existing_user.password == password:
                session['user'] = existing_user.username
                return redirect("/blog")
            
            else:
                error["pass_error"] = "Invalid password"
        
        else:
            error["name_error"] = "Invalid username. Try again or Register."

    return render_template("login.html", title= "Login",
        name_error= error["name_error"], pass_error= error["pass_error"],
        username= username)

@app.route("/logout", methods= ['POST', 'GET'])
def logout():

    if 'user' in session:
        del session['user']
    
    return redirect('/blog')

if __name__ == '__main__':
    app.run()