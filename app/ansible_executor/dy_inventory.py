#!/usr/bin/env python
# coding: utf-8


def parse_args():
    import argparse
    description = "this script just for generating Ansible dynamic inventory file"

    parser = argparse.ArgumentParser(description=description)

    help_info = "list the inventory"
    parser.add_argument('--list', dest='list', action='store_true', help=help_info)
    help_info = "list the host"
    parser.add_argument('--host', dest='host', action='store', help=help_info)

    args = parser.parse_args()
    return args


def main():
    import json
    args = parse_args()
    if args.list:
        inventory = {
            "aliyun": {
                'hosts': ["qd.zhxfei.com", "hkweb.zhxfei.com", 'hk.zhxfei.com', 'sh.zhxfei.com'],
                'vars': {
                    'ansible_ssh_private_key_file': '~/.ssh/id_rsa',
                    'ansible_ssh_user': 'root',
                    'ansible_ssh_port': '9988'
                }
            },
            "txyun": {
                'hosts': ["sh.zhxfei.com", "hk.zhxfei.com"],
                'vars': {
                    'ansible_ssh_private_key_file': '~/.ssh/id_rsa',
                    'ansible_ssh_user': 'root',
                    'ansible_ssh_port': '9988'
                }
            }
        }
    else:
        inventory = {
            '_meta': {
                'hostvars': {}
            }
        }
    print(json.dumps(inventory, indent=4))


if __name__ == '__main__':
    main()