
# Info

This is the PunCentral Discord Bot, which supports the CS Go team.

## How-To

Please provide a `.env`  file with these following parameters:
```
DISCORD_TOKEN=".."
FACEIT_TOKEN=".."
USERNAMES='["DrWho", "KingKong", "Godzilla"]'
PLAYERIDS='["5f243f5d-5581", "f3a026b0-9781-4312",  "c3337570-16fb-462e"]'
GAMERIDS='["11743", "8068939", "7431"]'
CHANNEL_ID=786
WEBHOOK_SECRET_TOKEN=".."
QUERY_TOKEN=".."
DEBUG=True
```

For the ngrok service you need to provide these environment variables:
```
export NGROK_HOSTNAME="....ngork.io"
export NGROK_AUTH_TOKEN="<TOKEN>"
```

## Services

* Discord Bot server
* Flask WebHook Listener
* Ngork tunnel