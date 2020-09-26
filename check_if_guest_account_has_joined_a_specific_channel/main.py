#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import configparser
import urllib.request, urllib.error, urllib.parse
import json
import time

def loadconf ():
    global token, channel, domain

    cfg = configparser.ConfigParser ()
    cfg_file = os.path.dirname(__file__) + '/settings.ini'
    cfg.read (cfg_file)
    token = cfg['slack']['token']
    channel = cfg['slack']['channel']
    domain = cfg['slack']['domain']
    return 0

def print_progress_cycle (message:str, i:int):
    if i%4 == 0:
        x = '|'
    elif i%4 == 1:
        x = '/'
    elif i%4 == 2:
        x = '-'
    elif i%4 == 3:
        x = '\\'
    else:
        x = '|'

    print (message + x, '\r', end='')

class Exec_api:
    def exec (self, req):
        """
        explanation:
            exec Slack API
        Args:
            req: urllib request object
        Return:
            body: Json object (dict)

        正常に完了した場合は Responsbody(json) を返す
        失敗した場合は、エラーjson(dict) を返す
        {"ok": false, "err":{"code": $err.code, "reason": $err.reason}}
        """
        body = {"ok": False}

        try:
            with urllib.request.urlopen(req) as res:
                body = json.loads(res.read().decode('utf-8'))
        except urllib.error.HTTPError as err:
            time.sleep (61)
            try:
                with urllib.request.urlopen(req) as res:
                    body = json.loads(res.read().decode('utf-8'))
            except urllib.error.HTTPError as err:
                err_d = {'reason': str(err.reason), 'code': str(err.code)}
                body = {'ok': False, 'err':err_d}

        except urllib.error.URLError as err:
            time.sleep (11)
            try:
                with urllib.request.urlopen(req) as res:
                    body = json.loads(res.read().decode('utf-8'))
            except urllib.error.URLError as err:
                err_d = {'reason': str(err.reason)}
                body = {'ok': False, 'err':err_d}

        return body

class Api:

    def conv_members (self, channel:str = None, cursor:str = None) -> dict:
        """
        # GET
        https://api.slack.com/methods/conversations.members
        """
        if not channel:
            body = {"ok": False}
            return body

        query = '?token=' + token + '&channel=' + channel + '&limit=1000'
        if cursor:
            query += '&cursor=' + cursor

        url = 'https://slack.com/api/conversations.members' + query

        req = urllib.request.Request (url)
        api = Exec_api ()
        body = api.exec (req)
        return body

    def users_list (self, cursor:str = None) -> dict:
        """
        GET
        https://api.slack.com/methods/users.list
        """
        query = '?token=' + token + '&limit=500'
        if cursor:
            query += '&cursor=' + cursor
        url = 'https://slack.com/api/users.list' + query

        req = urllib.request.Request (url)
        api = Exec_api ()
        body = api.exec (req)
        return body

    def users_info (self, user:str = None) -> dict:
        """
        GET
        https://api.slack.com/methods/users.info
        """
        if not user:
            body = {"ok": False}
            return body
        query = '?token=' + token + '&user=' + user
        url = 'https://slack.com/api/users.info' + query

        req = urllib.request.Request (url)
        api = Exec_api ()
        body = api.exec (req)
        return body


def main ():

    loadconf ()
    users = {} # WSのユーザ一覧、ユーザIDとメールアドレスの突合に使う
    members = [] # 対象チャンネルに参加してるメンバー一覧
    prob_list = [] # 対象チャンネルに参加している 自社ドメイン 以外のメールアドレスのユーザ

    # WS に参加しているユーザ情報の取得
    api = Api ()
    i = 0
    print_progress_cycle ('get all WS users list... ', i%4)
    res = api.users_list ()
    if not res['ok']:
        print ()
        print (res, file=sys.stderr)
        exit (1)

    for member in res['members']:
        if 'email' in member['profile']:
            userid = member['id']
            email = member['profile']['email']
            users[userid] = email
        else:
            pass

    next_cursor = res['response_metadata']['next_cursor']
    while next_cursor:
        i += 1
        print_progress_cycle ('get all WS users list... ', i%4)
        res = api.users_list (next_cursor)
        for member in res['members']:
            if 'email' in member['profile']:
                userid = member['id']
                email = member['profile']['email']
                users[userid] = email
            else:
                pass
        next_cursor = res['response_metadata']['next_cursor']
    print ('get all WS users list... done')

    # 対象チャンネル に参加しているメンバー情報の取得
    api = Api ()
    i = 0
    print_progress_cycle ('get members list... ', i%4)
    res = api.conv_members (channel)
    for member in res['members']:
        members.append(member)

    next_cursor = res['response_metadata']['next_cursor']

    while next_cursor:
        i += 1
        print_progress_cycle ('get members list... ', i%4)
        res = api.conv_members (channel, next_cursor)
        for member in res['members']:
            members.append(member)
        next_cursor = res['response_metadata']['next_cursor']
    print ('get members list...  done')

    # 結果の確認
    i = 0
    i_max = len (members)
    for userid in members:
        i += 1
        print ('checking members... ' + str(i) + '/' + str(i_max), '\r', end='')

        if userid in users:
            email = users[userid]
            if domain in email:
                pass
            else:
                prob_list.append([userid, email])
        else:
            # チャンネルにいるのにユーザ一覧にはいない？
            api = Api ()
            res = api.users_info (userid)
            if res['ok']:
                if res['user']['deleted']:
                    pass # 削除済みのユーザ
                else: # チャンネルに存在するがユーザ一覧には存在せず、アカウントが delete されてもいないユーザ？
                    prob_list.append([userid])

    print ('checking members... ' + str(i) + '/' + str(i_max) + " done")

    if prob_list:
        print ("==== guest members who joind $channel ====")
        for member in prob_list:
            print ("id:", member[0], "email:", member[1])
    else:
        print (" -> no guest account detected :clap:")

if __name__ == '__main__':
    main ()
    exit (0)
