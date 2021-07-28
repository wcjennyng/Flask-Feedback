from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """Homepage. Redirects to register page"""
    return redirect ('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""

    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        
        try:
            db.session.commit()
            session['username'] = new_user.username 
        except IntegrityError:
            form.username.errors.append('Username/Email taken. Please choose another username/email.')
            return render_template('register.html', form=form)

        return redirect(f"/users/{new_user.username}")
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Login form"""

    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/login')

@app.route('/users/<username>')
def user_page(username):
    """Page when user is logged in"""

    if 'username' not in session or username != session['username']:
        form.username.errors = ["You are not authorized here."]
        return redirect ('/login')

    user = User.query.get(username)
    form = DeleteForm()

    return render_template('user.html', user=user, form=form)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Deletes user and their feedback from database."""

    if 'username' not in session or username != session['username']:
        form.username.errors = ["You are not authorized here."]
        return redirect ('/login')

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def add_feedback(username):
    """Displays form to add feedback. Adds new piece of feedback."""

    if 'username' not in session or username != session['username']:
        form.username.errors = ["You are not authorized here."]
        return redirect ('/login')

    form = FeedbackForm()

    if form.validate_on_submit():
        
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("add.html", form=form)  
    

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update(feedback_id):
    """Displays a form to edit feedback. Updates piece of feedback."""

    feedback = Feedback.query.get(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        form.username.errors = ["You are not authorized here."]
        return redirect ('/login')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("edit.html", form=form, feedback=feedback)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Deletes a piece of feedback."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        form.username.errors = ["You are not authorized here."]
        return redirect ('/login')

    form = DeleteForm()

    if form.validate_on_submit():

        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")



