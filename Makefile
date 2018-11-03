test:
	pytest

image:
	docker build . -t dndapi:$(TRAVIS_JOB_ID)

image-push:
	@echo "to be implemented [image-push]"
