# dndonations api

#Testing
## Create network
docker network create dndapinet
## Stand up database
docker run -d -e MYSQL_ROOT_PASSWORD=devboxen --name mysql --network=dndapinet mysql:latest
## stand up database-web interface
docker run -d --network=dndapinet -p8080:8080 adminer:latest
## Build and run the app's docker image
make && docker run -p5000:5000 -e ADMIN_PASSWORD=admin123 -e STAFF_PASSWORD=staff123 -e DBUSER=root -e DBPASS=devboxen -e DBHOST=mysql -e DBTABLE=dndapi_2017 --network dndapinet dndapi:1

