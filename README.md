# Ashley
Chatbot with soul

## Requirements
- redis
- imagemagick
- python3.8

## Data
- All images stored in `res` folder
- Markov's chains stored in `/var/lib/redis/dump.rdb` (don't forget to `chown redis:redis /var/lib/redis/dump.rdb`)
- Other data stored in `database/db.sqlite` (`database` folder should be writable for tmp sqlite files)
- To run this bot as systemd service, copy `systemctl-example.toml` to `/etc/systemd/system/ashleybot.service`, edit it and run `service ashleybot start && systemctl enable ashleybot.service`

## Install using venv
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade wheel setuptools
pip install -r requirements.txt
```

## Run using venv
```bash
venv/bin/python -m ashlee
```
