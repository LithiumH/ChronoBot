#!/bin/bash

mkdir -p ~/data/db
mongod --dbpath ~/data/db &
mongoimport --db interns --collection logs --file dbfiles/logs.json
mongoimport --db interns --collection faq --file dbfiles/faq.json
mongoimport --db interns --collection users --file dbfiles/users.json
mongoimport --db interns --collection convs --file dbfiles/convs.json

exit;
