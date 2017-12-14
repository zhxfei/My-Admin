# coding: utf-8
from os import system
import time


def refresh():
    try:
        t1 = time.time()
        system('ansible -m setup --tree out/ all')
        t2 = time.time()
        system('ansible-cmdb out/ > ./templates/admin/overview.html')
        t3 = time.time()
        print(t2-t1)
        print(t3 - t2)
    except Exception as e:
        pass

