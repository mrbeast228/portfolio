# Zipkin Cassandra -> PostgreSQL spans migrator
This script fully copies data from Zipkin to PostgreSQL

## Motivation
As storage for spans, traces and links (zipkin dependencies) Zipkin supports Elasticsearch, MySQL and Cassandra, and only last of them is open-source. But as was determined in real case, data extraction from Cassandra by infrastructure monitoring software (e.g. Zabbix) is very slow - about 100x slower by comparsion with it's "native" PostgreSQL, but Zipkin doesn't nativelly support it. In my plans there's writing Zipkin PostgreSQL storage plugin, but it's very complicated, so I created this migration script. For realizing scalable monitoring system (tens of thousands traces every minute), it's the only way right now

## Requirments
+ Python 3.5+
+ argparse
+ psycopg2

## Usage
```
python3 zipkin_cassandra_to_postgres_copier.py --source http://HOSTNAME:9411/zipkin/api/v2 [-U USERNAME] [-P PASSWORD] [-H POSTGRES_HOST] [--port POSTGRES_PORT] [-D POSTGRES_DB] [-S POSTGRES_SCHEMA] [-T POSTGRES_TABLE] [-L LOG_FILE] [--housekeeping --days N]
```
+ **--source** - URL of Zipkin API v2 endpoint, from which script will receive data
+ **-U** - username for accessing PostgreSQL data, it should have write access to specified database. Default - 'zipkin'
+ **-P** - password of specified username for authorization. Default - 'zipkin'
+ **-H** - address/hostname of PostgreSQL host, it should be accesible from machine running script (add to whitelist in firewall if needed)
+ **--port** - port of PostgreSQL, default is 5432 (as usual)
+ **-D** - database which should be used by script to write data. It's not created automatically, you should create it manually before running script. Default is 'zipkin'
+ **-S** - schema which should be used for table with data. Can be created automatically. Default - 'zipkin_etl'
+ **-T** - table which should be used for writing data. Default is 'spans_root'
+ **-L** - path to log file, default is 'zipkin_etl.log' in the directory of script. On every running writes info about count of migrated data
+ **--housekeeping** - special flag which enables "cleaner" mode - it will clean data in database which is elder then N days
+ **--days** - specify how old data should be cleaned

For scalable systems, scripts receives from Zipkin only data of last 60 seconds (if specify more there'll be so much data that script may crash), so you need to use cron (for example) to automatically run script exactly every 60 seconds (to not lose the data)
