from app.admin import admin
from flask import render_template, redirect, session, url_for, request, flash
from werkzeug.security import generate_password_hash
from app import db
from app.admin.form import UserLoginForm, PwdForm
from app.modles import User, Email, SyncLog
import datetime


@admin.context_processor
def admin_extra():
    email = SyncLog.query.filter_by(has_view=False).order_by(SyncLog.ptr.desc()).first()
    email_1 = SyncLog.query.filter_by(has_view=True).order_by(SyncLog.ptr.desc()).first()
    if email and email_1:
        new_email = email.ptr - email_1.ptr if email.ptr - email_1.ptr > 0 else None
    else:
        new_email = None
    return {
        'online_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'new_email': new_email
    }


@admin.route('/')
def index():
    return render_template('admin/index.html')


@admin.route('/email/list/<int:page>')
def email_list(page):
    if page is None:
        page = 1
    latest_email = Email.query.order_by(Email.time.desc()).first()
    if latest_email:
        sync_log = SyncLog.query.filter_by(ptr=latest_email.id+1).first()
        if sync_log:
            sync_log.has_view = True
            db.session.add(sync_log)
            db.session.commit()
    page_data = Email.query.order_by(Email.time.desc()).paginate(page, 30)
    num_count = latest_email.id if latest_email else 0
    return render_template('admin/mail_list.html', page_data=page_data, num_count=num_count)


@admin.route('/email/sync/')
def email_sync():
    from app.utils.neteasy_email_sync import email_sync
    info = email_sync()
    flash(info, 'succeed')
    return redirect(url_for('admin.email_list', page=1))


@admin.route('/pwd/', methods=['GET', 'POST'])
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        new_pass = form.data['new_pwd']
        print(new_pass)
        admin = User.query.filter_by(name=session['admin']).first()
        admin.pwd = generate_password_hash(new_pass)
        db.session.commit()
        flash('修改密码成功, 请重新登录!', 'succeed')
        return redirect(url_for('admin.logout'))
    return render_template('admin/pwd.html', form=form)


@admin.route('/logout/')
def logout():
    session.pop('admin', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('admin.login'))


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        account = form.data.get('account')
        password = form.data.get('password')
        admin = User.query.filter_by(name=account).first()
        if not admin.check_pwd(password):
            flash('密码错误！')
        elif admin.state == 'off':
            flash('账户已经被冻结，请联系管理员')
        else:
            session['admin'] = account
            session['user_id'] = admin.id
            if admin.is_admin:
                session['is_admin'] = True
            return redirect(request.args.get('next')) if request.args.get('next') else redirect(url_for('admin.index'))
    return render_template('admin/login.html', form=form)
