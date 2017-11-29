import io
import json
import logging
import requests
import time

logging.basicConfig()
logger = logging.getLogger("[" + __name__ + " - WebBenchmark]")
ch = logging.StreamHandler()
logger.addHandler(ch)

from benchmarktool.bench import Bench
from benchmarktool.timer import Timer

from cdb import sqlapi, constants
from cs.platform.web.root import Root
from webtest import TestApp as Client
from cdbwrapc import Operation
from cdb.platform.mom import SimpleArguments
from cdb.platform.mom.entities import CDBClassDef



class WebBenchmark(Bench):
    def setUpClass(self):
        app = Root()
        self.client = Client(app)    

    def abench_get_all(self):
        logger.info("bench_get_all")

        sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'")
        sql_count_after =  sqlapi.SQLget_statistics()['statement_count']    

        self.storeResult(t.elapsed.total_seconds(), name="Get: no_cache")
        self.storeResult(sql_count_after - sql_count_before, name="Get SQL-Count", type="count", unit="statements")

        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'")
        self.storeResult(t.elapsed.total_seconds(),  name="Get: cache")
#        print response.json


    def abench_get_all_astable(self):
        logger.info("bench_get_all_astable")

        sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table")
        sql_count_after =  sqlapi.SQLget_statistics()['statement_count']  

        self.storeResult(t.elapsed.total_seconds(), name="Get as table: no cache")
        self.storeResult(sql_count_after - sql_count_before, name="Get as table SQL-Count", type="count", unit="statements")

        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table")
        self.storeResult(t.elapsed.total_seconds(),  name="Get as table: cache")
#        print response.json


    def bench_get_progesseviley(self):
        logger.info("bench_get_progressively")
        time_series = []
        statements = []
        for i in range(self.args["step"], 2000, self.args["step"]):
            sql_count_before =  sqlapi.SQLget_statistics()['statement_count']  
            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&maxrows={}".format(i))
            sql_count_after =  sqlapi.SQLget_statistics()['statement_count']  

            time_series.append(t.elapsed.total_seconds())
            statements.append(sql_count_after - sql_count_before)

        print time_series
        tmp = list(time_series)
        for i, val in enumerate(tmp):
            if i > 0:
                time_series[i] = val - tmp[i-1]

        self.storeResult(time_series, name="Get Progessive", type="time_series")

        print statements
        tmp = list(statements)
        for i, val in enumerate(tmp):
            if i > 0:
                statements[i] = val - tmp[i-1]

        self.storeResult(statements, name="Get Progressively SQL-Count", type="count_series", unit="statements")

    def bench_search_operation(self):
        logger.info("bench_search_operation")
        op = Operation(constants.kOperationSearch,
                       CDBClassDef("test_benchmark"),
                       SimpleArguments(cdb_module_id="cs.restgenericfixture"))
        op.run()
        self.test_retrieve_table_data_cpp(op, "")
        self.test_retrieve_table_data_elements_ui(op, "")


    def test_retrieve_table_data_cpp(self, op, table_name):
        logger.info("test_retrieve_table_data_cpp")
        with Timer() as t:
            res = op.get_result()[1].as_table(table_name).getData()
        self.storeResult(t.elapsed.total_seconds(), name="Retrieve Table data cpp", type="time")

        
    def test_retrieve_table_data_elements_ui(self, op, table_name):
        logger.info("test_retrieve_table_data_elements_ui")
        payload = {}
        c = Client(Root())
        params = {"object_navigation_id": None,
                  "values": {},
                  "operation_state" : op.getOperationState()}
        with Timer() as t:
            response = c.post_json(u'/internal/uisupport/operation/class/test_benchmark/CDB_Search/run',
                                   payload)
        self.storeResult(t.elapsed.total_seconds(), name="Retrieve Table data elements ui", type="time")




def saveJSONData(fileName, data):
    """This functions dumps json data into a file. The name of the output file
    is determined by parameter.

    :param fileName: name of the destination file
    :param data: json data which will be saved to file
    """
    logger.info("Saving json to file: " + fileName)
    try:
        with io.open(fileName, 'w', encoding="utf-8") as outfile:
            outfile.write(unicode(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)))
    except IOError as err:
        logger.exception("Could not open file to save the data! " + str(err))
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.exception("Could not decode values! " + str(err))
    except TypeError as err:
        logger.exception("Could not serialize object! " + str(err))
    except:
        logger.exception("Unexpected error occurred! ")
    else:
        logger.info("Saving successful")


if __name__ == "__main__":
    step = 100
    webui = WebBenchmark()
    webui.run({'step': step})
    # workaround execute without runner
    benchresult = {"Sysinfos": {},
            "results": {
            "WebBenchmark": {
            "args": {
                "step": step
            },"data": {}
            }
    }}
    benchresult["results"]["WebBenchmark"]["data"] =  webui.results
    print benchresult
    output_file = 'benchmarkResults_{}.json'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
    saveJSONData(output_file, benchresult)



