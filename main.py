from flask import (
    Flask,
    request,
    redirect,
    render_template,
    send_from_directory,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config["DEBUG"] = True
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://blogz:blogz@localhost:3306/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "dccsvxuBiec7"

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    body = db.Column(db.String(2100), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, owner, title, body):
        self.owner = owner
        self.title = title
        self.body = body
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(13), unique=True, nullable=False)
    password = db.Column(db.String(16), nullable=False)
    posts = db.relationship("Post", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)


@app.route("/blog")
def blog():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        posts = Post.query.filter_by(owner=user).all()
        return render_template("singleuser.html", owner=user.username, posts=posts)

    single_post = request.args.get("id")
    if single_post != None:
        post = Post.query.get(single_post)
        return render_template("singlepost.html", post=post)

    posts = Post.query.all()
    return render_template('blog.html', posts=posts, user=session["username"])


@app.route("/blog/newpost", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        

        if title == "" and body == "":
            error = "You must include a title and body!"
            return render_template("newpost.html", error=error)

        elif title == "" and body != "":
            error = "You must include a title!"
            return render_template("newpost.html", body=body, error=error)

        elif body == "" and title != "":
            error = "You must include a body!"
            return render_template("newpost.html", title=title, error=error)

        elif title != "" and body != "":
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Post(owner, title, body)
            db.session.add(new_post)
            db.session.commit()

            return redirect("/blog?id=" + str(new_post.id))

    return render_template("newpost.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if "username" not in session:
            return render_template("login.html")

        return redirect("/blog/newpost")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["username"] = username
            return redirect("/blog/newpost")

        elif not user:
            username_error = "Username does not exist."
            return render_template(
                "login.html",
                username_error=username_error)

        elif user and user.password != password:
            password_error = "Password is incorrect."
            return render_template("login.html", password_error=password_error)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    username_error = None
    password_error = None
    verify_error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        existing_user = User.query.filter_by(username=username).first()

        if not 4 <= len(username) < 14:
            username_error = "Invalid username."

        if not 4 <= len(password) < 16:
            password_error = "Invalid password."

        if password != verify:
            verify_error = "Passwords do not match."

        if existing_user:
            username_error = "Username already exists."
            return render_template(
                "signup.html", 
                username_error=username_error,
                password_error=password_error,
                verify_error=verify_error)

        elif username_error !=None or password_error !=None or verify_error !=None:
            return render_template(
                "signup.html",
                username_error=username_error,
                password_error=password_error,
                verify_error=verify_error)
 
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = username
        return redirect("/blog/newpost")
            

    return render_template("signup.html")


@app.route("/logout")
def logout():
    try:
        del session["username"]
        return redirect("/")
    except KeyError:
        return redirect("/login")


if __name__ == "__main__":
    app.run()
