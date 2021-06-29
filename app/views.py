from app.app import app, db
from app.forms import RegistrationForm, LoginForm
from app.rest_api import *


@app.route('/')
def page_home():
    return render_template('home.html')


@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def page_schedule():
    return render_template('schedule.html')


@app.route('/presentations', methods=['GET', 'POST'])
@login_required
def page_presentations():
    return render_template('presentations.html')


@app.route('/presentations/edit/<int:presentation_id>', methods=['GET', 'POST'])
@login_required
def page_edit_presentation(presentation_id):
    return render_template('edit_presentation.html', presentation_id=presentation_id)


@app.route('/schedule/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def page_edit_schedule(schedule_id):
    return render_template('edit_schedule.html', schedule_id=schedule_id)


# region User authorize
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('page_home'))
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
    return redirect(url_for('page_home'))


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
