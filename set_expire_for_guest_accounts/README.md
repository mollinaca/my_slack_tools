# slack_guest_expire

## Description

OrG 配下のWSに参加しているゲストアカウントをチェックし、有効期限が設定されていない場合は `180日` に設定する作業をWS単位で対話的に実行する。  
Check the guest accounts that participate in the WS under OrG and If the expiry date is not set, set the expiry date to `180 days` in each WS interactively.  

## How To Use

### Prapare

set your slack API token to `settings.ini`  

```
[slack]
token=xoxp-111111111111-222222222222-3333333333333-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Run Script

```
# ./main.py
or
# python main.py
```
※ python 実行環境にあわせて実行してください

### std out

for example...
```
 # ./main.py
Get all Workspace info... done
1/3 Workspace :  ['TXXXXXXXX', 'WS-A', 'https://ws-a-xxxxxxxx.slack.com/']
 => Set ExpirationDate to guest users? [Y/n] : n
skip Workspace: ['TXXXXXXXX', 'WS-A', 'https://ws-a-xxxxxxxx.slack.com/']
2/3 Workspace :  ['TYYYYYYYY', 'WS-B', 'https://ws-b-yyyyyyy.slack.com/']
 => Set ExpirationDate to guest users? [Y/n] : n
 => Set to expire after 180 days for guest accounts that have not been set to expire... 100/100 done
3/3 Workspace :  ['TZZZZZZZZ', 'mollinaca-test', 'https://mollinaca-test-zzzzzzzzz.slack.com/']
 => Set ExpirationDate to guest users? [Y/n] : Y
 => Get guest users... done
 => All guest users had an expiration date set.
```

## Ref

### Slack APIs

* admin.teams.list

https://api.slack.com/methods/admin.teams.list  
team（WS）の一覧を取得  

* admin.users.list

https://api.slack.com/methods/admin.users.list  
team（WS）ごとにゲストアカウントの情報（有効期限）を取得  

* admin.users.setExpiration

https://api.slack.com/methods/admin.users.setExpiration  
ゲストユーザの有効期限を設定する  

# Requirements

python => 3.0  
Slack API Scopes: `admin.teams:read, admin.users:read, admin.users:write`  
