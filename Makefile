
run:
	venv/bin/python -m ashlee

install:
	sudo apt update
	sudo apt install redis imagemagick
	sudo apt install python3 python3-venv python-is-python3
	python -m venv venv
	source venv/bin/activate
	pip install --upgrade wheel setuptools
	pip install -r requirements.txt
	deactivate
	echo "Move dump.rdb to /var/lib/redis/dump.rdb and set its owner to redis:redis"
	echo "Move database.db to database/"
	echo "Move systemctl-example.toml to /etc/systemd/system/ashleybot.service, do service ashleybot start and systemctl enable ashleybot.service"

