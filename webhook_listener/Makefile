build:
	cp ../faceit.py .
	docker build -t puncentralbot_webhook_listen .

run:
	docker run -d -p 5001:5001 --name pc_web_listen puncentralbot_webhook_listen:latest