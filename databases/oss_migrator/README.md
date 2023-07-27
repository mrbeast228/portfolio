# Elasticsearch -> Opensearch data migrator
This shell script fully copies one index from Elasticsearch (up to last version at Aug 2023) to Opensearch using Reindex API

## Requirments
+ curl
+ jq

## Usage
At first, endpoints of Elastic and OSS are specified as global variables inside script:
```
ESS_HOST="localhost:9200"
OSS_HOST="localhost:10200"
ESS_ADDR_FROM_OSS_HOST="quickstart-es-http.elastic-system:9200"
```
where **ESS_HOST** is a **host:port** of Elasticsearch, same for **OSS_HOST**. **ESS_ADDR_FROM_OSS_HOST** is the address of Elasticsearch host visible from OSS machine. If you're running anything script on local machine, specify it same with **ESS_HOST**, but it's usable when ESS/OSS hosts are remote. For example, if they have their own subnet 192.168.14.0/24, and they ports forwarding by router with white IP 1.2.3.4 to 9200 and 10200 for ESS and OSS accordingly, you may have
```
ESS_HOST="1.2.3.4:9200"
OSS_HOST="1.2.3.4:10200"
ESS_ADDR_FROM_OSS_HOST="192.168.14.228:9200"
```
Next, you should specify the password of 'elastic' ESS user in **PWD** variable. By default script is configured to extract it automatically from ECK deployed in Kubernetes, but in any other case you should specify your own
```
PWD=123456
```
After configuration you can run
```
./oss_migrator.sh INDEX_NAME
```
and index INDEX_NAME will be copied to Opensearch with all its properties. On local machine in ECK performance is about 5'000 documents in 2 seconds
After migration you can seamless redirect your software, which working with ESS index, to OSS index, at least it's working with Logstash (Opensearch plugin needed)

## Issues
+ data streams not migrating (TODO)
+ open issue if you found something else
