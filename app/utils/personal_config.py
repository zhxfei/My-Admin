# coding: utf-8
import os
'''
163 网易邮箱设置
'''

email = '15852937839@163.com'
password = os.environ.get('netease_mail_password')
pop3_server = 'pop.163.com'


'''
dnspod api token 设置
'''

dns_login_token = os.environ.get('dns_login_token')

'''
tencent cloud API key
'''
tencent_secret_id = os.environ.get('tencent_secret_id')
tencent_secret_key = os.environ.get('tencent_secret_key')
region_lst = ['ap-hongkong', 'ap-shanghai']


'''
aliyun api key
'''
aliAccessKeyID = os.environ.get('aliAccessKeyID')
aliAccessKeySecret = os.environ.get('aliAccessKeySecret')
region_lst_ali = ['cn-hongkong', 'cn-qingdao']


'''
Ansibel inventory hosts file path
'''

ansible_inventory_path = '/etc/ansible/hosts'
