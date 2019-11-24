#!/bin/bash
docker build . -t dndonations
docker tag dndonations derbious/dndonations
docker push derbious/dndonations

echo "Check it out: https://hub.docker.com/r/derbious/dndonations"
