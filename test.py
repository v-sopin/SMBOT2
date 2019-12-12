from InstagramAPI import InstagramAPI

if __name__ == '__main__':
    api = InstagramAPI('v.sopin', 'XXXXXXX')
    api.login()


[Unit]
Description=Service-MarketBot
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/src/Python-3.7.3/python /root/SMBOT/bot.py
Restart=always

[Install] WantedBy=multi-user.target
