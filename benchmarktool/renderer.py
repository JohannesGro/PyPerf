#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
"""

import argparse
import json
import logging.config
import os
import sqlite3
import sys
import time

import ioservice
from benchmarktool.log import customlogging


class Renderer(object):
    """The module renderer reads the results of one or several benchmarks and
    create a human readable output for example showing table or diagramms.
    A json file created by the benchrunner can be taken as a input. self.currently this
    module supports html output only.
    """
    currentDir = os.path.dirname(__file__)
    benchmarkFile = os.path.join(currentDir, "benchmarkResults.json")
    outputFile = 'benchmarkResults_{}.html'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
    logging_file = 'renderer.log'

    # CLI
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", "-s", nargs='+', default=benchmarkFile, help="One or more json files which contain the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs='?', default=outputFile, help="The results will be stored in this file.")
    parser.add_argument("--logconfig", "-l", nargs='?', default="", help="Configuration file for the logger. (default: %(default)s)")

    template = """
    <html>
    <head>
        <style>
        {}
        </style>
        <script>{}</script>
        <script>{}</script>
    </head>
    <body>
    <h1>Benchmark Results</h1>
    {}

    </body>
    </html>
    """
    data = {}

    def __init__(self, args):
        # Grab the self.args from argv
        if type(args) == argparse.Namespace:
            prev = sys.argv
            sys.argv = []
            self.args = self.parser.parse_args(args=None, namespace=args)
            sys.argv = prev
        else:
            self.args = self.parser.parse_args(args)

    def main(self):
        global logger
        logger = customlogging.init_logging("[Renderer]", configFile=self.args.logconfig, fileName=self.logging_file)
        logger.debug("benchmarks files: {}".format(self.args.benchmarks))
        logger.debug("output file: {}".format(self.args.outfile))
        logger.debug("logger conf file: " + str(self.args.logconfig))

        self.loadBenchmarkData()
        self.createTempSqlDB()
        self.renderTrend()
        return
        self.iterateBenches()

    def createTempSqlDB(self):
        con = sqlite3.connect(':memory:')
        self.cur = con.cursor()
        self.cur.execute("CREATE TABLE Benchmark(B_ID INTEGER PRIMARY KEY unique, Name TEXT)")
        self.cur.execute("CREATE TABLE SysInfo(S_ID INTEGER PRIMARY KEY, Name TEXT)")
        self.cur.execute("CREATE TABLE Benchmark_SysInfo(B_ID INT, S_ID INT, Value TEXT, FOREIGN KEY(B_ID) REFERENCES Benchmark(B_ID), FOREIGN KEY(S_ID) REFERENCES SysInfo(S_ID))")

        self.cur.execute("CREATE TABLE Bench(BE_ID INTEGER PRIMARY KEY, Name TEXT)")
        self.cur.execute("CREATE TABLE Test(T_ID INTEGER PRIMARY KEY, Name TEXT, BE_ID INT, FOREIGN KEY(BE_ID) REFERENCES Bench(BE_ID))")
        self.cur.execute("CREATE TABLE Arg(A_ID INTEGER PRIMARY KEY, Name TEXT, Value TEXT, BE_ID INT, FOREIGN KEY(BE_ID) REFERENCES Bench(BE_ID))")
        self.cur.execute("CREATE TABLE Result(R_ID INTEGER PRIMARY KEY, Type TEXT, Unit TEXT, Value TEXT, T_ID INT, B_ID INT, FOREIGN KEY(B_ID) REFERENCES Benchmark(B_ID), FOREIGN KEY(T_ID) REFERENCES Test(T_ID))")

        for fileName, content in self.data.iteritems():
            print fileName
            self.cur.execute("insert into Benchmark values (?, ?)", (None, fileName))
            B_ID = self.cur.lastrowid
            for sysinfo, val in content["Sysinfos"].iteritems():
                self.cur.execute("insert into SysInfo select :id, :info where not exists(select 1 from SysInfo where SysInfo.Name = :info)", ({'id': None, 'info': sysinfo}))
                self.cur.execute("insert into Benchmark_SysInfo values (?, (select SysInfo.S_ID from SysInfo where SysInfo.Name = ?), ?)", (B_ID, sysinfo, unicode(val)))

            for bench, bench_content in content["results"].iteritems():
                self.cur.execute("insert into Bench select :id, :bench where not exists(select 1 from Bench where Bench.Name = :bench)", ({'id': None, 'bench': bench}))
                for arg, val in bench_content['args'].iteritems():
                    self.cur.execute("insert into Arg select :id, :arg, :val, (select 1 from Bench where Bench.Name = :bench) where not exists(select 1 from Arg where Arg.BE_ID = (select Bench.BE_ID from Bench where Bench.Name = :bench) and Arg.Name = :arg)", ({'id': None, 'arg': arg, 'val': unicode(val), 'bench': bench}))

                for test, test_content in bench_content['data'].iteritems():
                    self.cur.execute("insert into Test select :id, :test, (select 1 from Bench where Bench.Name = :bench) where not exists(select 1 from Test where Test.Name = :test)", ({'id': None, 'test': test, 'bench': bench}))
                    self.cur.execute("insert into Result values (?, ?, ?, ?, (SELECT Test.T_ID from Test where Test.Name = ?), ?)", (None, test_content['type'], test_content['unit'], unicode(test_content['value']), test, B_ID))

            # for line in con.iterdump():
            #     print "{}\n".format(line)

            # self.cur.execute("select SysInfo.Name from Benchmark inner join Benchmark_SysInfo on Benchmark.B_ID = Benchmark_SysInfo.B_ID INNER JOIN SysInfo on SysInfo.S_ID = Benchmark_SysInfo.S_ID;")
            # print self.cur.fetchall()

    def renderTrend(self):
        """Iterates over each bench and calls a render function to display the data.
        The render functions will produce html code. This code will be put together and
        saved as .html file./TODO
        """
        inline_css = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "css", "main.css"))
        d3Lib = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "js", "d3.v4.min.js"))
        chartsJS = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "js", "charts.js"))
        body = self.sysInfoTrend()
        # benches = self.getAllBenches()
        # for benchKey in benches:
        #     logger.info("Render bench: " + benchKey)
        #     body += self.renderBench(benchKey)
        ioservice.writeToFile(self.template.format(inline_css, d3Lib, chartsJS, body), self.args.outfile)

    def sysInfoTrend(self):
        templ = "<div class='tile'><table>{}</table></div>"
        content = ""

        headerTempl = "<tr>" + "<th>{}</th>" * (len(self.data) + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (len(self.data) + 1) + "</tr>"
        self.cur.execute("select Name, GROUP_CONCAT(Benchmark_SysInfo.Value) from SysInfo inner join Benchmark_SysInfo on SysInfo.S_ID = Benchmark_SysInfo.S_ID group by SysInfo.Name;")
        res = self.cur.fetchall()
        for row in res:
            infoname = row[0]
            values = row[1].split(',')
            content += rowTempl.format(infoname, *values)
        result = templ.format(content) + self.createTrendDiagramForSysInfo('Memory free in MB')
        return result

    def createTrendDiagramForSysInfo(self, SysInfoName):
        # self.cur.execute("select Name, GROUP_CONCAT(Benchmark_SysInfo.Value) from SysInfo inner join Benchmark_SysInfo on SysInfo.S_ID = Benchmark_SysInfo.S_ID where Name = ? OR Name = 'Current Time (UTC)' group by Benchmark_SysInfo.B_ID ;", (SysInfoName,))
        self.cur.execute("select max(CASE SysInfo.Name WHEN ? THEN Benchmark_SysInfo.Value END), max(CASE SysInfo.Name WHEN 'Current Time (UTC)' THEN Benchmark_SysInfo.Value END) from SysInfo inner join Benchmark_SysInfo on SysInfo.S_ID = Benchmark_SysInfo.S_ID group by Benchmark_SysInfo.B_ID ;", (SysInfoName,))
        res = self.cur.fetchall()
        print res
        measurements = []
        for ele in res:
            mearurements.append({'value': ele[0], 'time': ele[1]})

        return self.createTrendDiagramm({'name': SysInfoName, 'meas': measurements}, id)

    def createTrendDiagramm(self, data, id):
        """Produce html js code to display the data of a benchmark as diagramm.
        The javascript function can be find in chart.js.
        :param benchName: name of the benchmark

        :returns: html/js code of the diagramm.
        """
        elementTempl = """
        <div id="{0}">
        <script>
        var data = {1};
        createTrendChart("#{0}",self.data);
        </script>
        </div>"""
        print data
        return elementTempl.format(id, data)

    def renderSysInfos(self):
        templ = "<div class='tile'><table>{}</table></div>"
        content = ""

        headerTempl = "<tr>" + "<th>{}</th>" * (len(self.data) + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (len(self.data) + 1) + "</tr>"

        content += headerTempl.format("System Info", *self.data.keys())
        infos = self.data[self.data.keys()[0]]["Sysinfos"]
        for infoName in sorted(infos):
            res = []
            for fileName in sorted(self.data):
                if infoName in self.data[fileName]["Sysinfos"]:
                    res.append(self.data[fileName]["Sysinfos"][infoName])
                else:
                    res.append('-')
                    content += rowTempl.format(infoName, *res)
                    return templ.format(content)

    def loadBenchmarkData(self):
        """Loads the benchmark data. The data can be accessed by self.data.
        The Format is a list of the benchmark result produced by the benchmark runner."""
        if isinstance(self.args.benchmarks, list):
            # Loads a bunch of benchmarks.
            for fileName in self.args.benchmarks:
                self.data[fileName] = ioservice.loadJSONData(fileName)
            self.areBenchmarksComparable(self.data)
        else:
            # Loads a single benchmark
            self.data[self.args.benchmarks] = ioservice.loadJSONData(self.args.benchmarks)

    def areBenchmarksComparable(self, benchmarks):
        """Checks the structure of each benchmark result. The same benchsuite is
        necessary for comparison. The benches and the arguments are therefore checked.

        :param benchmarks: list with all benchmarks
        :raises RuntimeError: if the strucutre of the benchmarks is unequal
        """

        # self.getAllBenches returns the benches of the first element
        f0Benches = self.getAllBenches()
        for fileName in benchmarks:
            fnBenches = self.getAllBenches(fileName).keys()
            if f0Benches.keys() != fnBenches:
                raise RuntimeError("Can not compare given benchmarks! Different benches.")
            for benchKey in fnBenches:
                if self.getBenchArgs(benchKey) != self.getBenchArgs(benchKey, fileName):
                    raise RuntimeError("Can not compare given benchmarks! Different args in bench: %s" % benchKey)

    def iterateBenches(self):
        """Iterates over each bench and calls a render function to display the data.
        The render functions will produce html code. This code will be put together and
        saved as .html file.
        """
        inline_css = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "css", "main.css"))
        d3Lib = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "js", "d3.v4.min.js"))
        chartsJS = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "js", "charts.js"))
        body = self.renderSysInfos()
        benches = self.getAllBenches()
        for benchKey in benches:
            logger.info("Render bench: " + benchKey)
            body += self.renderBench(benchKey)
        ioservice.writeToFile(self.template.format(inline_css, d3Lib, chartsJS, body), self.args.outfile)

    def renderBench(self, benchKey):
        """Generates html code of the given bench name to display its data.
        This function will display a heading, the arguments, table and diagramms.

        :param benchKey: the name of the benchmark
        :returns: string with html code
        """
        title = "<h2>{0}</h2>".format(benchKey)
        tileTempl = "<div class='tile'>{0}</div>"
        args = self.renderBenchArgs(benchKey)
        measurements = self.renderBenchMeasurements(benchKey)
        return tileTempl.format(title + args + measurements)

    def renderBenchMeasurements(self, benchName):
        """Produces html code for the data of the given bench name.
        A diagramm and tables are created.

        :param benchName: name of the bench
        :returns: html code of the data
        """
        res = ""
        body = self.createDiagramm(benchName)
        body += self.renderTablesByTypes(benchName)
        return body

    def getTestResult(self, fileName, benchName, benchTest):
        """Helper function to return the result of a bench test.

        :param fileName: name of the file
        :param benchName: name of the benchmark
        :param benchTest: name of the test
        :returns: the selected data from specified file name
        """
        return self.getAllBenches(fileName)[benchName]["data"][benchTest]

    def getAllBenches(self, fileName=""):
        """Helper function to return all benchmarks. If no file name is applied the
        data is token from the first file.

        :param fileName: file where the information shall be taken from
        :returns: a dict of all benchmarks
        """
        if fileName == "":
            fileName = self.data.keys()[0]
        return self.data[fileName]["results"]

    def getAllBenchTests(self, benchName):
        """Helper function to return all test of a benchmark.

        :param benchName: name of the benchmark
        :returns: a dict of all test of a benchmark
        """
        fileName = self.data.keys()[0]
        return self.getAllBenches(fileName)[benchName]['data']

    def getBenchArgs(self, benchName, fileName=""):
        """Helper function to return the arguments of a benchmark.  If no file name
        is applied the data is token from the first file.

        :param benchName: name of the benchmark
        :param fileName: file where the information shall be taken from
        :returns: a dict of arguments
        """
        return self.getAllBenches(fileName)[benchName]["args"]

    def createDiagramm(self, benchName):
        """Produce html js code to display the data of a benchmark as diagramm.
        The javascript function can be find in chart.js.

        :param benchName: name of the benchmark
        :returns: html/js code of the diagramm.
        """
        elementTempl = """
        <div id="{0}">
            <script>
                var data = {1};
                createBarChart("#{0}",self.data);
            </script>
         </div>"""
        tableContent = []
        allTests = self.getAllBenchTests(benchName)
        # not data available
        if allTests is None or allTests == {}:
            return ""
        for (benchTestName, content) in allTests.iteritems():
            for fileName in self.data:
                val = self.getTestResult(fileName, benchName, benchTestName)["value"]
                if content["type"] == "time_series":
                    timeList = val
                    print "#" * 80
                    if len(timeList) == 0:
                        continue
                    sumTime = sum(timeList)
                    avg = sumTime / len(timeList)
                    val = avg
                    print "avg {0} val {1} sum {2}".format(avg, val, sumTime)
                print "#" * 80
                tableContent.append({"file": fileName, "name": benchTestName.encode('UTF-8'), "value": val})
        return elementTempl.format(benchName, tableContent)

    def renderTablesByTypes(self, benchName):
        """Creates tables for each type of bench test.

        :param benchName: name of the benchmark
        :return: the html code
        """
        types = ["time", "time_series"]
        res = ""
        for t in types:
            res += self.renderTableByType(benchName, t)
        return res

    def renderTableByType(self, benchName, type):
        """Creates a table of specific type of bench tests.

        :param benchName: name of the benchmark
        :param type: type of the benchmark (e.g. 'time', 'time_series')
        :returns: html code of the table.
        """
        header = "<h4>Tabelle {}</h4>".format(type)
        allTests = self.getAllBenchTests(benchName)
        # not data available
        if allTests is None or allTests == {}:
            return ""
        elements = dict((benchTestName, content) for (benchTestName, content) in allTests.iteritems() if content["type"] == type)
        if len(elements) == 0:
            return ""

        content = "<table>"
        if type == "time_series":
            content += self.renderTimeSeriesRows(benchName, elements)
        elif type == "time":
            content += self.renderTimeRows(benchName, elements)

        content += "</table>"
        return header + content

    def renderTimeRows(self, benchName, elements):
        """Creates the rows for the table. Each row display data of type 'time'.
        The elements parameter contains a dict which is already filtered by this type.

        :param benchName: name of the benchmark
        :param elements: filtered dict which is containing test
        :returns: string containing the rows
        """
        content = ""

        headerTempl = "<tr>" + "<th>{}</th>" * (len(self.data) + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (len(self.data) + 1) + "</tr>"

        content += headerTempl.format("Test", *self.data.keys())
        for benchTestName in sorted(elements):
            res = []
            for fileName in sorted(self.data):
                res.append(self.getTestResult(fileName, benchName, benchTestName)["value"])
            content += rowTempl.format(benchTestName, *res)
        return content

    def renderTimeSeriesRows(self, benchName, elements):
        """Creates the rows for the table. Each row display data of type 'time_series'.
        The elements parameter contains a dict which is already filtered by this type.

        :param benchName: name of the benchmark
        :param elements: filtered dict which is containing test
        :returns: string containing the rows
        """
        content = ""

        headerTempl = "<tr>" + "<th>{}</th>" * (len(self.data) + 2) + "</tr>"
        outerRowTempl = "<tr><td>{}</td><td colspan='{}'><table>{}</table></td></tr>"
        innerRowTempl = "<tr>" + "<td>{}</td>" * (len(self.data) + 1) + "</tr>"

        content += headerTempl.format("Test", "Aggregation", *self.data.keys())
        for benchTestName in sorted(elements):
            innerContent = ""
            resMax = []
            resMin = []
            resSum = []
            resAvg = []
            resMidOutl = []
            resExtrOutl = []
            for fileName in sorted(self.data):
                timeList = self.getTestResult(fileName, benchName, benchTestName)["value"]
                if len(timeList) == 0:
                    resMax.append([])
                    resMin.append([])
                    resSum.append([])
                    resAvg.append([])
                    resMidOutl.append([])
                    resExtrOutl.append([])
                    continue
                outlier = self.findOutlier(sorted(timeList))
                maxVal = max(timeList)
                minVal = min(timeList)
                sumVal = sum(timeList)
                avgVal = sumVal / len(timeList)
                resMax.append(maxVal)
                resMin.append(minVal)
                resSum.append(sumVal)
                resAvg.append(avgVal)
                resMidOutl.append(outlier['midOutlier'])
                resExtrOutl.append(outlier['extremeOutlier'])
            if len(resMax) == 0:
                continue
            innerContent += innerRowTempl.format("Max", *resMax)
            innerContent += innerRowTempl.format("Min", *resMin)
            innerContent += innerRowTempl.format("Sum", *resSum)
            innerContent += innerRowTempl.format("Average", *resAvg)
            # if len(outlier['midOutlier']) > 0:
            innerContent += innerRowTempl.format("Mid Outlier", *resMidOutl)
            innerContent += innerRowTempl.format("Extreme Outlier", *resExtrOutl)

            content += outerRowTempl.format(benchTestName, (len(self.data) + 1), innerContent)
        return content

    def renderTextByType(self, content):
        """Produce html code to display the given data as text.

        :param content: data which shall be shown.
        :returns: html code
        """
        res = "<h4>{}</h4>".format(content["type"])
        dlTempl = """
            <dl>
            {0}
           </dl>
        """
        dlInnerTempl = "<dt>{0}</dt><dd>{1}</dd>"
        if content["type"] == "time_series":
            timeList = content["value"]
            lenTimeList = len(timeList)
            if lenTimeList > 0:
                maxVal = max(timeList)
                minVal = min(timeList)
                minVal = sum(timeList)
                avgVal = minVal / len(timeList)
                dlInner = ""
                dlInner += dlInnerTempl.format("Unit:", content["unit"])
                dlInner += dlInnerTempl.format("Max:", maxVal)
                dlInner += dlInnerTempl.format("Min:", minVal)
                dlInner += dlInnerTempl.format("Sum:", minVal)
                if "totalTime" in content:
                    dlInner += dlInnerTempl.format("Total Time:", content["totalTime"])
                dlInner += dlInnerTempl.format("Average:", avgVal)
                res += dlTempl.format(dlInner)
        if content["type"] == "time":
            dlInner = ""
            dlInner += dlInnerTempl.format("Result:", str(content["value"]) + " " + content["unit"])
            res += dlTempl.format(dlInner)
        return res

    def renderBenchArgs(self, benchName):
        """Displays the arguments of a benchmark in a table.

        :param benchName: name of the benchmark
        :returns: html table with arguments of the given bench
        """
        result = """
            <table>
                <tr>
                    <th>Argument</th>
                    <th>Value</th>
                </tr>
                {0}
            </table>
        """
        args = self.getBenchArgs(benchName)
        rows = ""
        for key, val in sorted(args.iteritems()):
            rows = rows + "\n<tr><td>{0}</td><td>{1}</td></tr>".format(key, val)
        result = result.format(rows)
        return result

    def calcMedian(self, data):
        size = len(data)
        if not (size % 2 == 0):
            return (data[(size - 1) / 2] + data[(size + 1) / 2]) / 2
        else:
            return data[size / 2]

    def findOutlier(self, data):
        size = len(data)
        if size < 10:
            return {'midOutlier': [], 'extremeOutlier': []}
        median = self.calcMedian(data)
        q1 = self.calcMedian(data[: size / 2])
        q3 = self.calcMedian(data[size / 2:])
        diffQ = q3 - q1
        lowerInnerLimit = q1 - diffQ * 1.5
        upperInnerLimit = q3 + diffQ * 1.5
        lowerOuterLimit = q1 - diffQ * 3
        upperOuterLimit = q3 + diffQ * 3

        midOutlier = []
        extremeOutlier = []
        for d in data:
            if d < lowerInnerLimit or d > upperInnerLimit:
                if d < lowerOuterLimit or d > upperOuterLimit:
                    extremeOutlier.append(d)
                else:
                    midOutlier.append(d)
        return {'midOutlier': midOutlier, 'extremeOutlier': extremeOutlier}
