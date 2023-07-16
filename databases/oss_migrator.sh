#!/bin/bash
set -e

# verbose mode
if [ "$2" != "verbose" ]; then
    exec 2>/dev/null
    alias curl='curl -s'
fi

# define variables
INDEX="$1"
ESS_HOST="localhost:9200"
OSS_HOST="localhost:10200"
ESS_ADDR_FROM_OSS_HOST="quickstart-es-http.elastic-system:9200"

# prepare for index creation
echo "Receiving index $INDEX configuration..." >&2
PWD=$(kubectl get secret quickstart-es-elastic-user -n elastic-system -o go-template='{{.data.elastic | base64decode}}') # password for Elastic
JSON=$(curl --insecure -u elastic:$PWD https://$ESS_HOST/$INDEX) # JSON description of index
JQCMD="del(.\"$INDEX\".settings.index.uuid, .\"$INDEX\".settings.index.creation_date, .\"$INDEX\".settings.index.version, .\"$INDEX\".settings.index.provided_name) | .\"$INDEX\"" # command for JSON editor for preparing to use with OpenSearch API

TOOSS=$(echo $JSON | jq "$JQCMD") # final index configuration
if [ "$TOOSS" = "null" ]; then
    echo "ERROR: index $INDEX is not exist on Elastic!"
    exit 1
fi

# create index
echo "Generating new index..." >&2
if ! curl --insecure -XPUT -H'Content-type: application/json' -u 'admin:admin' "https://$OSS_HOST/$INDEX" "$TOOSS" >/dev/null; then
    echo "WARNING: index $INDEX already exists in Opensearch"
fi

# reindex index =)
echo "Syncing index..." >&2
REINDEX_REQUEST="{\"source\":{\"remote\":{\"host\":\"https://$ESS_ADDR_FROM_OSS_HOST\",\"username\":\"elastic\",\"password\":\"$PWD\"},\"index\":\"$INDEX\"},\"dest\":{\"index\":\"$INDEX\"}}" # command for API for re-indexing
curl --insecure -XPOST -H'Content-type:application/json' -u 'admin:admin' "https://$OSS_HOST/_reindex?wait_for_completion=false" -d "$REINDEX_REQUEST" >/dev/null
echo "Done!"

exit 0
