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
import sys
import time

import ioservice
from benchmarktool.log import customlogging


class Renderer(object):
    """The module renderer reads the results of one or several benchmarks and
    create a human readable output for example showing table or diagramms.
    A json file created by the benchrunner can be taken as a input. Currently this
    module supports html output only.
    """
    currentDir = os.path.dirname(__file__)
    benchmarkFile = os.path.join(currentDir, "benchmarkResults.json")
    outputFile = 'benchmarkResults_{}.html'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
    loggingFile = 'renderer.log'

    # CLI
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", "-s", nargs='+', default=benchmarkFile, help="One or more json files which contain the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs='?', default=outputFile, help="The results will be stored in this file.")
    parser.add_argument("--logconfig", "-l", nargs='?', default=loggingFile, help="Configuration file for the logger. (default: %(default)s)")

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
        logger = customlogging.init_logging("[Renderer]", configFile=self.args.logconfig, fileName=self.loggingFile)
        logger.debug("benchmarks files: {}".format(self.args.benchmarks))
        logger.debug("output file: {}".format(self.args.outfile))
        logger.debug("logger conf file: " + str(self.args.logconfig))
        if isinstance(self.args.benchmarks, list):
            self.loadDataForMultipleBenchmarks()
        else:
            self.loadDataForSingleBenchmark()
        self.iterateBenches()

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

    def loadDataForSingleBenchmark(self):
        """Loads a single benchmark"""
        self.data[self.args.benchmarks] = ioservice.loadJSONData(self.args.benchmarks)

    def loadDataForMultipleBenchmarks(self):
        """Loads a bunch of benchmarks."""
        for fileName in self.args.benchmarks:
            self.data[fileName] = ioservice.loadJSONData(fileName)
        self.areBenchmarksComparable(self.data)

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

    def iterateBenches(self, ):
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
