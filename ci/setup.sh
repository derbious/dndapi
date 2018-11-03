#!/bin/bash
echo "Updating docker"
sudo apt update -y
sudo apt install --only-upgrade docker-ce -y
