RELEASE := "1"

all: build

build: clean
	docker build . -t dndapi:$(RELEASE)

clean:
	docker rmi -f dndapi:$(RELEASE) || true
