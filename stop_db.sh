#!/bin/bash

mongoexport --db interns --collection logs --out dbfiles/logs.json
mongoexport --db interns --collection faq --out dbfiles/faq.json
mongoexport --db interns --collection users --out dbfiles/users.json
mongoexport --db interns --collection convs --out dbfiles/convs.json

mongo < mongostop.js

rm -rf ~/data

