from app.app import app, db
from app.forms import RegistrationForm, LoginForm
from app.rest_api import *


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/presentations', methods=['GET', 'POST'])
def presentations():
    return render_template('presentations.html')


# region User authorize
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect('/')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(csrf_enabled=False)
    if request.method == "POST":
        if User.query.filter_by(name=form.username.data).first() is None:
            new_user = User(name=form.username.data, email=form.email.data, role_id=3)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
        else:
            flash('Username is exist')
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


# endregion
