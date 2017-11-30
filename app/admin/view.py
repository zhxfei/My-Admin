from app.admin import admin
from flask import render_template, redirect, session, url_for, request, flash
from werkzeug.security import generate_password_hash
from app import db
from app.utils.dnspod_record_sync import record_delete, records_sync, records_add
from app.admin.form import UserLoginForm, PwdForm, RecordAddForm, record_type
from app.modles import User, Email, SyncLog, RecordInfo
import datetime
from functools import wraps


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


def login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@admin.route('/pwd/', methods=['GET', 'POST'])
@login_req
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


@admin.route('/')
@login_req
def index():
    return render_template('admin/index.html')


@admin.route('/email/list/<int:page>')
@login_req
def email_list(page):
    if page is None:
        page = 1
    latest_email = Email.query.order_by(Email.time.desc()).first()
    if latest_email:
        sync_log = SyncLog.query.filter_by(ptr=latest_email.id + 1).first()
        if sync_log:
            sync_log.has_view = True
            db.session.add(sync_log)
            db.session.commit()
    page_data = Email.query.order_by(Email.time.desc()).paginate(page, 10)
    num_count = latest_email.id if latest_email else 0
    return render_template('admin/mail_list.html', page_data=page_data, num_count=num_count)


@admin.route('/email/sync/')
@login_req
def email_sync():
    from app.utils.neteasy_email_sync import email_sync
    info = email_sync()
    flash(info, 'succeed')
    return redirect(url_for('admin.email_list', page=1))


@admin.route('/record/sync/')
@login_req
def record_sync():
    info = records_sync()
    flash(info, 'succeed')
    return redirect(url_for('admin.record_list', page=1))


@admin.route('/record/list/<int:page>', methods=['GET', 'POST'])
@login_req
def record_list(page=None):
    if page is None:
        page = 1
    page_data = RecordInfo.query.paginate(page, 20)
    form = RecordAddForm()
    if form.validate_on_submit():
        name = form.data.get('name')
        value = form.data.get('value')
        record_ty = [v[1] for v in record_type if v[0] == form.data.get('type')][0]
        info = records_add(name, value, record_ty)
        flash(info, 'succeed')
        return redirect(url_for('admin.record_list', page=1))
    return render_template('admin/records_list.html', page_data=page_data, form=form)


@admin.route('/record/del/<int:record_id>')
@login_req
def record_del(record_id):
    info = record_delete(record_id)
    if info == 'Action completed successful':
        record = RecordInfo.query.filter_by(sp_id=record_id).first()
        db.session.delete(record)
        db.session.commit()
    flash(info, 'succeed')
    return redirect(url_for('admin.record_list', page=1))

