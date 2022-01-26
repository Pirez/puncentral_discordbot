
build:
	docker build -t puncentralbot .

run:
	docker run -d --restart always puncentralbot