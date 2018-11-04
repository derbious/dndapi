test:
	pytest

image:
	docker build . -t dndapi:$(TRAVIS_JOB_ID)

push-image:
	docker tag dndapi:$(TRAVIS_JOB_ID) us.gcr.io/dndonations-176523/dndapi:$(TRAVIS_JOB_ID)
	docker push us.gcr.io/dndonations-176523/dndapi:$(TRAVIS_JOB_ID)
