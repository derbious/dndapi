RELEASE := "3"

all: build

build: clean
	docker build . -t dndapi:$(RELEASE)

clean:
	docker rmi -f dndapi:$(RELEASE) || true

push-image: build
	docker tag dndapi:$(RELEASE) us.gcr.io/dndonations-176523/dndapi:$(RELEASE)
	gcloud docker -- push us.gcr.io/dndonations-176523/dndapi:$(RELEASE)
