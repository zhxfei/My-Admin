# -*- coding: utf8 -*-
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
from app.utils.personal_config import aliAccessKeyID, aliAccessKeySecret, region_lst_ali
import json, re
from app.utils.tx_cvm_info_sync import parse_message_dict


# 创建 AcsClient 实例


def get_instance(region):
    client = AcsClient(
        aliAccessKeyID,
        aliAccessKeySecret,
        region
    );
    request = DescribeInstancesRequest.DescribeInstancesRequest()
    request.set_PageSize(10)
    # 发起 API 请求并打印返回
    response = client.do_action_with_exception(request)
    res_info = json.loads(response.decode('utf-8'))
    return res_info['Instances']['Instance']


def parse_info(instance_info):
    res_info = dict()
    res_info['sp_name'] = 'aliyun'
    for k, v in instance_info.items():
        if k == 'ZoneId':
            res_info['zoneName'] = v
        if k == 'Cpu':
            res_info['cpu'] = v
        if k == 'PublicIpAddress':
            res_info['wanIpSet'] = ' '.join(v['IpAddress'])
        if k == 'InternetMaxBandwidthOut':
            res_info['bandwidth'] = v
        if k == 'Memory':
            res_info['mem'] = v / 1024
        if k == 'CreationTime':
            res_info['createTime'] = '-'.join(re.findall('(\d+)-(\d+)-(\d+)', v)[0])
        if k == 'InnerIpAddress':
            res_info['lanIp'] = ' '.join(v['IpAddress'])
        if k == 'VpcAttributes':
            if v['PrivateIpAddress']['IpAddress']:
                res_info['lanIp'] = ' '.join(v['PrivateIpAddress']['IpAddress'])
        if k == 'ExpiredTime':
            res_info['deadlineTime'] = '-'.join(re.findall('(\d+)-(\d+)-(\d+)', v)[0])
        if k == 'Status':
            res_info['status'] = v
        if k == 'OSName':
            res_info['os'] = v
        # else:
        #     res_info[k] = v
    return res_info


def get_ali_vps_data():
    res_lst = []
    for region in region_lst_ali:
        instance_lst = get_instance(region)
        for instance_info in instance_lst:
            instance_info = parse_info(instance_info)
            res_lst.append(instance_info)
    return res_lst

