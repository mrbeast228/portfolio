import requests
import time
import sys
import json
from argparse import ArgumentParser
import psycopg2
from datetime import datetime, timedelta
from os import path


class Storer:
    connection = False
    initSuccess = False
    logfile = None
    orig_stdout = None

    def logger(self, *args, **kwargs):
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), *args, **kwargs, end="")

    def __init__(self):
        # parse data from command line
        parser = ArgumentParser()

        parser.add_argument("--source", required=True)
        parser.add_argument("-U", "--username", default="zipkin", required=True)
        parser.add_argument("-P", "--password", default="zipkin", required=True)
        parser.add_argument("-H", "--host", default="192.168.140.33", required=True)
        parser.add_argument("--port", default="5432", required=False)
        parser.add_argument("-D", "--database", default="zipkin", required=True)
        parser.add_argument("-S", "--schema", default="zipkin_etl", required=False)
        parser.add_argument("-T", "--table", default="spans_root", required=False)
        parser.add_argument(
            "-L",
            "--log",
            default=path.dirname(path.abspath(__file__)) + "/zipkin_etl.log",
            required=False,
        )
        parser.add_argument("--housekeeping", action="store_true", required=False)
        parser.add_argument("--days", required=False)
        self.args = parser.parse_args()

        # housekeeper mode
        if self.args.housekeeping and not self.args.days:
            parser.error("--housekeeping requires --days N")

        # open log file
        try:
            self.logfile = open(self.args.log, "a+")
            self.orig_stdout = sys.stdout
            sys.stdout = self.logfile
        except Exception as e:
            self.logger("Cannot open log file %s:" % self.args.log, e)

        # connect to PostgreSQL with given credentials
        try:
            self.connection = psycopg2.connect(
                user=self.args.username,
                password=self.args.password,
                host=self.args.host,
                port=self.args.port,
                database=self.args.database,
            )
            self.cursor = self.connection.cursor()
        except (Exception, psycopg2.Error) as error:
            self.logger("Cannot connect to database %s:" % self.args.database, error)
            return None

        # prepare global variables
        self.inserter = (
            "INSERT INTO %s.%s (data, span_timestamp, update_ts, trace_duration) VALUES "
            % (self.args.schema, self.args.table)
        )
        self.request_former = "(%s, TIMESTAMP %s, timezone('utc', now()), %s)"

        # create empty schema and table for our data
        tableReturn = self.initSchemaAndTable()
        if tableReturn == 255:
            self.initSuccess = True
        else:
            self.logger(
                "Cannot init table %s.%s:" % (self.args.schema, self.args.table),
                tableReturn,
            )
            return None

    def initSchemaAndTable(self):
        # create needed table in database if it doesn't exists
        create_schema = "CREATE SCHEMA IF NOT EXISTS %s" % self.args.schema
        create_table = (
            "CREATE TABLE IF NOT EXISTS %s.%s (id serial primary key, data jsonb, span_timestamp timestamp, update_ts timestamp, trace_duration int)"
            % (self.args.schema, self.args.table)
        )
        # create unique complex ID for traces
        create_unique = (
            "CREATE UNIQUE INDEX IF NOT EXISTS complexId ON %s.%s USING btree((data->>'traceId'), (data->>'id'))"
            % (self.args.schema, self.args.table)
        )

        try:
            self.cursor.execute(create_schema)
            self.cursor.execute(create_table)
            self.cursor.execute(create_unique)
            self.connection.commit()
        except (Exception, psycopg2.Error) as error:
            return error
        return 255

    def calcTraceDuration(self, trace):
        # Сортировка спанов, где первый элемент
        traceSortedByTs = sorted(trace, key=lambda x: x["timestamp"], reverse=True)
        # self.logger("[DBG] traceSortedByTs: '{}'\n".format(trace))

        traceDuration = traceSortedByTs[0]["timestamp"] - traceSortedByTs[-1]["timestamp"]
        if "duration" in traceSortedByTs[0]:
            traceDuration += traceSortedByTs[0]["duration"]
        # self.logger("[DBG] traceDuration: '{}'\n".format(traceDuration))

        # Кейс когда трассировка началась рутспаном и им же закончилась
        for span in trace:
            if "duration" in span:
                if span["duration"] > traceDuration:
                    traceDuration = span["duration"]

        return traceDuration

    def microsecondsToTimestamp(self, microseconds):
        epoch = datetime(1970, 1, 1)
        raw_datetime = epoch + timedelta(microseconds=microseconds)
        return str(raw_datetime).split(".")[0]

    def getJsonData(self):
        self.spandata = []
        end_ts = int(time.time()) * 1000 + 60 * 1000
        lookback = 120 * 1000
        limit = 4000
        full_url = "{}/traces?endTs={}&lookback={}&limit={}".format(
            self.args.source, end_ts, lookback, limit
        )
        try:
            resp = requests.get(full_url)
            traces = resp.json()
        except Exception as e:
            self.logger("Cannot download traces:", e)
            return False

        # self.logger("[DBG] traces: '{}'\n".format(traces))
        self.logger("[DBG] Extracted {} traces\n".format(len(traces)))
        for trace in traces:
            traceDuration = 0
            try:
                traceDuration = self.calcTraceDuration(trace)
            except (Exception) as e:
                self.logger(
                    "[DBG] cannot parse trace duration for trace: '{}'\n".format(trace)
                )
            for span in trace:
                if "parentId" not in span:
                    span["traceDuration"] = traceDuration
                    self.spandata.append(json.dumps(span, separators=(",", ":")))
        return True

    def saveJsonData(self):
        # prepare request variables for postgres
        baseRequestData = ()
        dataCount = 0
        baseRequestString = ""

        # convert every span to data tuples and count it
        for span in self.spandata:
            spanJson = json.loads(span)
            if "timestamp" in spanJson:
                span_time = self.microsecondsToTimestamp(spanJson["timestamp"])
            else:
                span_time = str(datetime.now()).split(".")[0]

            trace_duration = spanJson["traceDuration"]

            baseRequestData += (span, span_time, trace_duration)
            dataCount += 1

        # exit if no data
        if dataCount == 0:
            return True

        # create request string
        for i in range(dataCount):
            baseRequestString += self.request_former
            if i != dataCount - 1:
                baseRequestString += ", "

        # make a request
        try:
            request = self.inserter + baseRequestString + " ON CONFLICT DO NOTHING"
            # self.logger("[DBG] request: '{}'\n".format(request))
            # self.logger("[DBG] baseRequestData: '{}'\n".format(baseRequestData))
            self.logger(
                "[DBG] Wrote {} lines to DB\n".format(int(len(baseRequestData) / 3))
            )
            self.cursor.execute(request, baseRequestData)
            self.connection.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            self.logger("Error adding data to database:", error)
            return False

    def houseKeeper(self):
        try:
            self.cursor.execute(
                "DELETE FROM %s.%s WHERE span_timestamp < now() - interval '%d days'"
                % (self.args.schema, self.args.table, int(self.args.days))
            )
            self.connection.commit()
        except (Exception, psycopg2.Error) as error:
            self.logger("Error housekeeping old data:", error)
            return False
        return True

    def __del__(self):
        # close connection in destructor
        if self.connection:
            self.cursor.close()
            self.connection.close()
        if self.logfile:
            sys.stdout = self.orig_stdout
            self.logfile.close()


storer = Storer()
if storer.initSuccess:
    if storer.args.housekeeping:
        storer.houseKeeper()
    else:
        if storer.getJsonData():
            storer.saveJsonData()
