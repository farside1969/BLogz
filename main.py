from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:LaunchCode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f8wv3w2f>v9j4sEuhcNYydAGMzzZJgkGgyHE9gUqaJcCk^f*^o7fQyBT%XtTvcYM'

#store post
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.String(750))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, title_error, body_error, owner ):
        self.title = title
        self.body = body
        self.title_error = title_error
        self.body_error = body_error
        self.owner = owner

    #validate
    def title_valid(self):
        if self.title:
            return True
        else:
            return False

    def body_valid(self):
        if self.body:
            return True
        else:
            return False

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#display entry redirect
@app.route("/")
def index():
    return redirect("/blog")

#display entry handler
@app.route("/blog")
def display_blog_entries():
    #display single entry
    entry_id = request.args.get('id')
    if (entry_id):
        entry = Blog.query.get(entry_id)
        return render_template('single_entry.html', title="Blog Entry", entry=entry)

    else:
        all_entries = Blog.query.all()   
    return render_template('all_entries.html', title="All Entries", all_entries=all_entries)

#new entry
@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        new_entry_title = request.form['title']
        title_error = "Title must be typed here"
        body_error = "Beans must be spilled here"
        new_entry_body = request.form['body']
        owner = request.form['owner']
        new_entry = Blog(new_entry_title, new_entry_body, title_error, body_error, owner)

        if not new_entry.title_valid():
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_entry_title=new_entry_title,
                new_entry_body=new_entry_body,
                title_error=title_error,
                owner=owner)

        if not new_entry.body_valid():
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_entry_title=new_entry_title,
                new_entry_body=new_entry_body,
                body_error=body_error,
                owner=owner)

        if new_entry.body_valid() and new_entry.title_valid():
                db.session.add(new_entry)
                db.session.commit()

                # display recent blog entry
                url = "/blog?id=" + str(new_entry.id)
                return redirect(url)
    #new entry form
    else:
        return render_template('new_entry_form.html', title="Create new blog entry")

if __name__ == '__main__':
    app.run()