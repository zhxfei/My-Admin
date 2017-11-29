# coding: utf-8
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from datetime import datetime
from app.utils.email_config import pop3_server, email, password
from app import db
from app.modles import Email, SyncLog
email_info_lst = ['From', 'To', 'Subject', 'Date']


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def get_header_value(msg, header):
    value = msg.get(header, '')
    if value:
        if header == 'Subject':
            value = decode_str(value)
            print(value, '\n')
        elif header == 'Date':
            try:
                date_time = datetime.strptime(msg.get('Date'), "%a, %d %b %Y %H:%M:%S %z (%Z)")
            except ValueError as e:
                date_time = datetime.strptime(msg.get('Date'), "%a, %d %b %Y %H:%M:%S %z")
            value = date_time.strftime('%Y-%m-%d %H:%M')
        else:
            hdr, addr = parseaddr(value)
            name = decode_str(hdr)
            value = u'%s %s' % (name, addr)
    return value


def save_info(msg):
    email = Email()
    for header in email_info_lst:
        value = get_header_value(msg, header)
        if header is email_info_lst[0]:
            email.mail_sender = value
        elif header is email_info_lst[1]:
            email.mail_receiver = value
        elif header is email_info_lst[2]:
            email.subject = value
        else:
            email.time = value
    db.session.add(email)


def email_sync():
    try:
        server = poplib.POP3(pop3_server)
        server.user(email)
        server.pass_(password)
        resp, mails, octets = server.list()
        index = len(mails)

        sync = SyncLog.query.order_by(SyncLog.ptr.desc()).first()
        if sync:
            start = sync.ptr
        else:
            start = 1
        if start < index+1:
            for i in range(start, index + 1):
                resp, lines, octets = server.retr(i)
                msg_content = b'\r\n'.join(lines).decode('utf-8', 'ignore')
                msg = Parser().parsestr(msg_content)
                save_info(msg)
            new_sync = SyncLog(
                ptr=index+1,
                has_view=False
            )
            db.session.add(new_sync)
            db.session.commit()
            info = '更新完成'
        else:
            info = '没有需要更新的邮件'
    except Exception as e:
        info = '更新失败: %s' % e
    return info

