from flask import Flask, flash, request, redirect, render_template, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import html, os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "dccsvxuBiec7"

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    body = db.Column(db.String(2100), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, body):
        self.title = title
        self.body = body

# class User(db.Model):
    

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def fIndex():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return redirect("/blog")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")

@app.route('/blog')
def fBlog():
    try:
        post_id = request.args.get('id')
        entry = Post.query.filter_by(id=post_id).first()
        if post_id != None:
            return render_template("entry.html", entry=entry)
        else:
            lPosts = Post.query.order_by(Post.pub_date.desc()).all()
            return render_template("blog.html", posts=lPosts)
    except KeyError:
        return redirect("/newpost")

@app.route('/blog/newpost', methods=["GET", "POST"])
def fNewPost():
    if request.method == "GET":
        return render_template("newpost.html")

    elif request.method == "POST":
        title = html.escape(request.form["title"])
        body = html.escape(request.form["body"])
        goto = request.form["goto"]

        if title == "" and body == "":
            flash("You must include a title and body!")
            return render_template("newpost.html")

        elif title == "" and body != "":
            flash("You must include a title!")
            return render_template("newpost.html", body=body)
        
        elif body == "" and title != "":
            flash("You must include a body!")
            return render_template("newpost.html", title=title)
        
        elif title != "" and body != "":
            entry = Post(title, body)
            db.session.add(entry)
            db.session.commit()
            if goto == "blog":
                return redirect("/blog")
            else:
                entry = Post.query.order_by(Post.id.desc()).first()
                return redirect("/blog?id=" + str(entry.id))


if __name__ == '__main__':
    app.run()