# Slack check if guest account has joined a specific channel

## Description

特定WSの特定チャンネルにゲストアカウントが参加していないかをチェックする。  
Check whether a guest account is participating in a specific channel of a specific WS.  

### use case

* 社員がゲストアカウントの招待申請をする
* 誤って、社員用の社内向けアナウンスチャンネルへ招待してしまう
* ゲストアカウントが社内向けアナウンスチャンネルへ参加してしまう

上記のケースを検出する

## How To Use

### Prapare

set your slack API token, target channel ID and e-mail domain to `settings.ini`  
```
[slack]
token=xoxp-111111111111-222222222222-3333333333333-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
channel=XXXXXXXXX
domain=@example.com
```

### Run Script

```
# ./main.py
or
# python main.py
```
※ python 実行環境にあわせて実行してください

# Ref

## Slack APIs

* https://api.slack.com/methods/users.list  
WSに参加しているユーザの一覧取得  

* https://api.slack.com/methods/conversations.members  
チャンネル(conversations)に参加しているメンバーの一覧取得  

* https://api.slack.com/methods/users.info  
WSに参加している各ユーザの情報  

# Requirements

python => 3.0  
Slack API Scopes: `users:read`, `channels:read`, `groups:read`, `im:read`, `mpim:read`, 

# Todo

* ゲストアカウント判定は、ドメインではなくてユーザ情報から取得できるしそっちのほうが良い
