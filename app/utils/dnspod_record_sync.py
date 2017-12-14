# coding: utf-8
import requests
from app.utils.personal_config import dns_login_token
from app.modles import RecordInfo
from app import db
from datetime import datetime


records_url = 'https://dnsapi.cn/Record.{}'


def records_sync():
    data = {
        'login_token': dns_login_token,
        'format': 'json',
        'domain_id': '28921413'
    }
    res = requests.post(records_url.format('List'), data=data)
    if res.status_code == 200:
        res_data = res.json()
        status_code = res_data.get('status').get('code')
        if status_code == '1':
            # status code = 1 means requests get 'Action completed successful'
            records_data = res_data.get('records')
            record_new_sp_id_lst = set()
            record_old_sp_id_lst = db.session.query(RecordInfo.sp_id).group_by(RecordInfo.sp_id).all()
            record_old_sp_id_lst = set([v[0] for v in record_old_sp_id_lst])
            for record in records_data:
                record_new_sp_id_lst.add(record['id'])
                if not RecordInfo.query.filter_by(sp_id=record['id']).first():
                    if record['enabled'] == '1':
                        records = RecordInfo()
                        records.sp_id = record['id']
                        records.domain_name = res_data['domain']['name']
                        records.name = record['name']
                        records.type = record['type']
                        records.value = record['value']
                        records.updated_time = record['updated_on']
                        records.ttl = record['ttl']
                        records.use_status = True
                        records.monitor_status = 'unknown'
                        db.session.add(records)
            for record_id in record_old_sp_id_lst - record_new_sp_id_lst:
                record = RecordInfo.query.filter_by(sp_id=record_id).first()
                if record:
                    db.session.delete(record)
            db.session.commit()
            return 'sync succeed'
    else:
        return 'sync failed'


def records_add(name, value, record_type, domain_name='zhxfei.com'):
    data = {
        'login_token': dns_login_token,
        'format': 'json',
        'sub_domain': name,
        'record_type': record_type,
        'record_line': '默认',
        'value': value,
        'domain_id': '28921413'
    }
    res = requests.post(records_url.format('Create'), data=data)
    if res.status_code == 200 and res.json()['status']['code'] == '1':
        record = res.json()['record']
        records = RecordInfo()
        records.sp_id = record['id']
        records.name = name
        records.domain_name = domain_name
        records.type = record_type
        records.value = value
        records.updated_time = datetime.now()
        records.ttl = '600'
        records.use_status = True
        records.monitor_status = 'unknown'
        db.session.add(records)
        db.session.commit()
    return res.json()['status']['message']


def record_delete(record_id):
    data = {
        'login_token': dns_login_token,
        'format': 'json',
        'record_id': record_id,
        'domain_id': '28921413'
    }
    res = requests.post(records_url.format('Remove'), data=data)
    return res.json()['status']['message']


def record_modify(record_id):
    pass