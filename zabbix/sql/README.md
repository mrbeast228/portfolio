# Zabbix PostgreSQL requests
This directory contains frequently usable SQL requests to Zabbix PostgreSQL database

## List of requests
Currently (Aug 2023) there are next SQL requests:
+ Get list of "not supported" items with all their properties and location in monitoring system
+ Get list of currentlty active triggers (problem state) with same benefits

The list will be updated...

## Usage
```
$ psql -U ZABBIX_USER_NAME ZABBIX_DB_NAME -W -f project-database/zabbix/sql/REQUEST.sql
<type password>
```
