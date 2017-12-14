# coding: utf-8
from QcloudApi.qcloudapi import QcloudApi
import requests


def req_url_generate():
    from app.utils.personal_config import tencent_secret_id, tencent_secret_key, region_lst
    module = 'cvm'
    action = 'DescribeInstances'
    config = {
        'secretId': tencent_secret_id,
        'secretKey': tencent_secret_key,
        'method': 'get'
    }
    params = {
        'SignatureMethod': 'HmacSHA1',
    }
    req_url_lst = []
    for region in region_lst:
        config['Region'] = region
        service = QcloudApi(module, config)
        req_url_lst.append(service.generateUrl(action, params))

    return req_url_lst


def parse_message_dict(dct):
    message = []
    for k, v in dct.items():
        message.append(str(k)+': '+str(v))
    return ';'.join(message)


def get_tx_vps_data():
    res_lst = []
    for req_url in req_url_generate():
        res = requests.get(req_url, timeout=3)
        result = res.json()
        if result['code'] == 0:
            info = result['instanceSet']
            for sp in info:     # info is a list
                for k, v in sp.items():
                    if isinstance(v, list):
                        sp[k] = ','.join(v)
                    if isinstance(v, dict):
                        sp[k] = parse_message_dict(v)
                sp['sp_name'] = 'tencent'

            res_lst += info
    return res_lst


def get_tx_vps_data_final():
    res_lst = []
    tx_data = get_tx_vps_data()
    '''
    tx_data_k_type_lst = ['cpu',
                          'wanIpSet',
                          'createTime',
                          'status',
                          'os',
                          'zoneName',
                          'mem',
                          'deadlineTime',
                          'lanIp'
                          'bandwidth',
                          'sp_name',]
    '''
    for info in tx_data:
        # info = {k: _ for k, _ in info.items() if k in tx_data_k_type_lst}
        res_lst.append(info)
    return res_lst