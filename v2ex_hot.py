#!/usr/bin/env python3
# coding=utf-8
# Created by sharp.gan at 2017-09-01
# Above automatically generated by github.com/supersu097/EZcode4CLI

import json
import requests
import os
from core import helper


def data_get():
    hot_url = 'https://www.v2ex.com/api/topics/hot.json'
    try:
        data = requests.get(hot_url).text
        return json.loads(data)
    except requests.exceptions.ConnectionError:
        helper.logger_getter().error('network connection error!')
        exit(1)


def id_persistence():
    helper.dir_check(helper.TEMP_DIR)
    with open(helper.TEMP_DIR + '/v2ex_id_data.txt', 'w') as f:
        for _ in data_get():
            f.write(str(_['id']) + '\n')


# It's suitable for hourly check in cron job
def hourly_check():
    # if no txt file existing, first init
    if not os.path.isfile(helper.TEMP_DIR + '/v2ex_id_data.txt'):
        id_persistence()
        helper.logger_getter().debug('First init to store id data,exit!')
        exit(0)

    # read previous v2ex_id_data.txt and compare
    with open(helper.TEMP_DIR + '/v2ex_id_data.txt') as f:
        old_id_list = [_.rstrip() for _ in f.readlines()]
    new_id_list = [str(_['id']) for _ in data_get() if str(_['id']) not in old_id_list]

    # if new_id_list is not 0 which means new hot post occurs
    if len(new_id_list) != 0:
        id_persistence()
        mail_body = []
        for data_collection in data_get():
            for new_id in new_id_list:
                if new_id == str(data_collection['id']):
                    mail_body.append(data_collection['title'] + ': ' +
                                     data_collection['url'])
        helper.mail_send(helper.date_getter() + '  V2exHot Update!', '\n'.join(mail_body))
        helper.logger_getter().info('V2ex has new hot posts.')
    else:
        helper.logger_getter().info('V2ex has no new hot post.')


# It's suitable for hourly check in cron job
def daily_check():
    helper.mail_send('V2EX每日热点', '')


if __name__ == '__main__':
    hourly_check()
