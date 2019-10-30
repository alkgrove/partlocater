#!/usr/bin/bash

# Only run this if you have used partlocater with an older altium database and wish to move it to mariadb 10.x or later. 
# The database can be identified if all the tables are varchar(255)
# This converts most tables to database type text so that it will work with Mariadb 10
# export altium database inside of partlocater (or use mysqldump or equivalent)
# cat altium.sql | upgradeSQL.sh > new_altium.sql
# import new_altium.sql into new database. This can be done by connecting to the new database and import
awk '/`Manufacturer Part Number` +varchar/ {gsub(/varchar\([0-9]+\) DEFAULT NULL/, "varchar(255) NOT NULL PRIMARY KEY");}
     /`Description` +varchar/ {print; next;}
     /varchar\([0-9]+\) DEFAULT NULL/ {gsub(/varchar\(255\) DEFAULT NULL/, "TEXT");}
	1 {print}'