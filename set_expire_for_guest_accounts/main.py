#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import configparser
import urllib.request, urllib.error, urllib.parse
import json
import time, datetime

def loadconf ():
    global token

    cfg = configparser.ConfigParser ()
    cfg_file = os.path.dirname(__file__) + '/settings.ini'
    cfg.read (cfg_file)
    token = cfg['slack']['token']
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
        x = '?'

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

    def admin_teams_list (self, cursor:str = None) -> dict:
        """
        # GET
        https://api.slack.com/methods/admin.teams.list
        """
        query = '?token=' + token + '&limit=' + '100'
        if cursor is not None:
            query += '&cursor=' + cursor
        url = "https://slack.com/api/admin.teams.list" + query

        req = urllib.request.Request (url)
        api = Exec_api ()
        body = api.exec (req)
        return body

    def admin_users_list (self, team:str = None, cursor:str = None) -> dict:
        """
        # GET
        https://api.slack.com/methods/admin.users.list
        """
        if team is None:
            body = {'ok': False}
            return body
        query = '?token=' + token + '&team_id=' + team + '&limit=100'
        if cursor:
            query += '&cursor=' + cursor
        url = 'https://slack.com/api/admin.users.list' + query

        req = urllib.request.Request (url)
        api = Exec_api ()
        body = api.exec (req)
        return body

    def admin_users_set_expiration (self, team:str = None, user:str = None, ex_ts:float = None) -> dict:
        """
        # POST
        https://api.slack.com/methods/admin.users.setExpiration
        """
        if (team is None) or (user is None) or (ex_ts is None):
            body = {'ok': False}
            return body

        url = 'https://slack.com/api/admin.users.setExpiration'
        params = {
            'token': token,
            'expiration_ts': ex_ts,
            'team_id': team,
            'user_id': user
        }

        req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)))
        api = Exec_api ()
        body = api.exec (req)
        return body


#####################
# main() 用関数
#####################

def after180_ut (t:float) -> float:
    """
    unix time を与えると、 180日後（15,552,000 秒後) を返す
    """
    ret = int(t + 15552000)
    return ret

def get_teams () -> list:
    """
    OrG 配下の WS id 一覧を取得する
    """
    teams = []
    i = 0
    print_progress_cycle ('Get all Workspace info... ', i)
    api = Api ()
    res = api.admin_teams_list ()
    for team in res['teams']:
        teams.append ([team['id'],team['name'],team['team_url']])

    if 'response_metadata' in res:
        next_cursor = res['response_metadata']['next_cursor']
    else:
        next_cursor = None

    while next_cursor:
        i += 1
        print_progress_cycle ('Get all WS id... ', i)
        res = api.admin_teams_list (next_cursor)
        for team in res['teams']:
            teams.append ([team['id'],team['name'],team['team_url']])

        if 'response_metadata' in res:
            next_cursor = res['response_metadata']['next_cursor']
        else:
            next_cursor = None

    print ('Get all Workspace info... done')
    return teams

def get_guest_users (team:str = None) -> dict:
    """
    WS に参加しているゲストユーザのうち、有効期限が未設定のゲストユーザ一覧を取得する
    """
    if team is None:
        res = {'ok': False}
        return res
    guest_users = []
    i = 0
    print_progress_cycle (' => Get guest users... ', i)

    api = Api ()
    res = api.admin_users_list (team)
    for user in res['users']:
        if user['is_restricted'] or user['is_ultra_restricted']:
            if 'expiration_ts' in user:
                if not user['expiration_ts']: # 0 なら
                    guest_users.append (user['id'])

    if 'response_metadata' in res:
        next_cursor = res['response_metadata']['next_cursor']
    else:
        next_cursor = None

    while next_cursor:
        i += 1
        print_progress_cycle (' => Get guest users... ', i)
        res = api.admin_users_list (team, next_cursor)
        for user in res['users']:
            if user['is_restricted'] or user['is_ultra_restricted']:
                if 'expiration_ts' in user:
                    if not user['expiration_ts']: # 0 なら
                        guest_users.append (user['id'])

        if 'response_metadata' in res:
            next_cursor = res['response_metadata']['next_cursor']
        else:
            next_cursor = None

    print (' => Get guest users... done')
    res = {'ok': True, 'guest_users': guest_users}
    return res

def main ():
    loadconf ()

    # 現在時刻の unixtime と 180日後の unixtime を取得
    now = datetime.datetime.now().timestamp()
    t = after180_ut (now)

    # WS 一覧を取得
    teams = get_teams ()

    # ゲストユーザの一覧を有効期限込で取得
    i = 0
    for ws_info in teams:
        i += 1
        team = ws_info[0]
        print (str(i) + '/' + str(len(teams)), 'Workspace : ', ws_info)
        print (' => Set ExpirationDate to guest users? [Y/n] : ', end='')
        ans = input()
        if ans == 'Y':
            guest_users = get_guest_users (team)['guest_users']

            # 有効期限が設定されていないゲストユーザに対して有効期限を設定する
            if guest_users:
                j = 0
                for guest_user in guest_users:
                    j += 1
                    print (' => Set to expire after 180 days for guest accounts that have not been set to expire... ' + str(j) + '/' + str(len(guest_users)) + ' : ' + guest_user, '\r', end='')
                    # 有効期限を設定する処理
                    api = Api ()
                    res = api.admin_users_set_expiration (team, guest_user, t)
                    if not res['ok']:
                        # もし処理に失敗したなら、10秒 sleep して1回だけリトライ。それでもダメなら失敗のまま次の処理へ進む。
                        time.sleep (10)
                        res = api.admin_users_set_expiration (team, guest_user, t)

                print (' => Set to expire after 180 days for guest accounts that have not been set to expire... ' + str(j) + '/' + str(len(guest_users)) + ' : ' + guest_user + " done")
            else:
                print (' => All guest users had an expiration date set.')
        else:
            print ('skip Workspace:', ws_info)

if __name__ == '__main__':
    main ()
    exit (0)
