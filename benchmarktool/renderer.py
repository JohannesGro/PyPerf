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
    loggingFile = 'renderer.log'

    # CLI
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", "-s", nargs='+', default=benchmarkFile, help="One or more json files which contain the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs='?', default=outputFile, help="The results will be stored in this file.")
    parser.add_argument("--logconfig", "-l", nargs='?', default="", help="Configuration file for the logger. (default: %(default)s)")
    parser.add_argument("--trend", "-t", default=False, action="store_true")

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

        self.loadBenchmarkData()
        self.organizeData()
        self.renderAllData()

    def organizeData(self):
        self.fileList = []
        self.sysInfos = {}
        self.benchmarkData = {}

        firstFile = self.data.keys()[0]
        for fileName in self.data.keys():
            self.fileList.append(fileName)

        for sysinfo, val in self.data[firstFile]["Sysinfos"].iteritems():
            attributeValues = []
            for fileName in self.fileList:
                if sysinfo in self.data[fileName]["Sysinfos"]:
                    attributeValues.append(self.data[fileName]["Sysinfos"][sysinfo])
                else:
                    attributeValues.append('-')
            self.sysInfos[sysinfo] = attributeValues

        for bench, benchContent in self.data[firstFile]["results"].iteritems():
            self.benchmarkData[bench] = {}
            self.benchmarkData[bench]['args'] = benchContent['args']

            for test, testContent in benchContent['data'].iteritems():
                resultValues = []
                self.benchmarkData[bench][test] = {}
                self.benchmarkData[bench][test]['unit'] = testContent['unit']
                self.benchmarkData[bench][test]['type'] = testContent['type']
                for fileName in self.fileList:
                    resultValues.append(self.data[fileName]["results"][bench]['data'][test]['value'])
                self.benchmarkData[bench][test]['values'] = resultValues

    def renderBenchMeasurementsTrend(self, benchName):
        """Produces html code for the data of the given bench name.
        A diagramm and tables are created.

        :param benchName: name of the bench
        :returns: html code of the data
        """
        res = ""
        body = self.createTrendDiagramForBenchName(benchName)
    #    body += self.renderTablesByTypes(benchName)
        return body

    def createTrendDiagramForBenchName(self, benchName):
        """Produce html js code to display the data of a benchmark as diagramm.
        The javascript function can be find in chart.js.

        :param benchName: name of the benchmark
        :returns: html/js code of the diagramm.
        """
        htmlCode = ""
        # iterate over all tests within in a bench
        for benchTestName, benchTestData in self.benchmarkData[benchName].iteritems():
            measurements = []
            if benchTestName == 'args':
                continue
            # iterate over all results
            for index, testResult in enumerate(benchTestData['values']):
                # find infos which will be displayed as tooltip
                tooltip = {}
                tooltipSysInfos = ["CPU Percent", "Memory Percent"]
                for tooltipSysInfo in tooltipSysInfos:
                    tooltip[tooltipSysInfo] = self.sysInfos[tooltipSysInfo][index]

                utcTime = self.sysInfos['Current Time (UTC)'][index]

                # if the result is a time series, it will be aggregated
                if benchTestData['type'] == "time_series":
                    if len(testResult) == 0:
                        continue
                    sumTime = sum(testResult)
                    avg = sumTime / len(testResult)
                    val = avg
                    measurements.append({'value': avg, 'time': utcTime, 'tooltip': tooltip})
                else:
                    measurements.append({'value': testResult, 'time': utcTime, 'tooltip': tooltip})
            # creates a base64 id for the element. test names could be invalid.
            eleId = createElementId("{}{}".format(benchName, benchTestName))
            htmlCode += self.createTrendDiagramm({'name': benchTestName, 'meas': measurements}, eleId, benchTestName)
        return htmlCode

    def renderSysInfosTrend(self):
        templ = "<div class='tile'>{}</div>"
        rowTempl = "<tr><td>{}</td><td>{}</td></tr>"
        tableTemp = "<table><tr><th>System Info</th><th>Value</th></tr>{}</table>"
        groupsTemp = "<details><summary>{0}</summary>{1}</details>"

        sysinfosList = self.sysInfos
        print sysinfosList
        graphs = ""
        groups = ""
        groupsKeywords = ['Memory', 'CPU', 'CADDOK', 'Disk', 'Swap', 'Other']
        for group in groupsKeywords:
            if group == 'Other':
                groupElements = sysinfosList
            else:
                # find the element for the current group
                groupElements = {key: val for key, val in sysinfosList.iteritems() if key.find(group) == 0}
            groupRows = ""
            for sysinfoname, values in groupElements.iteritems():
                # not the same columns
                if not values[1:] == values[:-1]:
                    # are the values valid for the chart
                    if not type(values) is list and isFloat(values[0]):
                        graphs += self.createTrendDiagramForSysInfo(sysinfoname)
                    else:
                        groupRows += rowTempl.format(sysinfoname, values)
                    continue
                groupRows += rowTempl.format(sysinfoname, values[0])
            groups += groupsTemp.format(group, graphs + tableTemp.format(groupRows))
            # remove the elements from the list
            sysinfosList = {key: val for key, val in sysinfosList.iteritems() if key not in groupElements.keys()}

        return templ.format(groups)

    def createTrendDiagramForSysInfo(self, SysInfoName):
        sysinfovalues = self.sysInfos[SysInfoName]
        timeList = self.sysInfos['Current Time (UTC)']

        measurements = []
        for index, value in enumerate(sysinfovalues):
            measurements.append({'value': value, 'time': timeList[index]})

        return self.createTrendDiagramm({'name': SysInfoName, 'meas': measurements}, createElementId(SysInfoName), SysInfoName)

    def createTrendDiagramm(self, data, elementId, title):
        """Produce html js code to display the data of a benchmark as diagramm.
        The javascript function can be find in chart.js.
        :param benchName: name of the benchmark

        :returns: html/js code of the diagramm.
        """
        elementTempl = """
        <div id="{0}" class="trendDiag">
        <h4>{2}</h4>
        <script>
        var data = {1};
        createTrendChart("#{0}",self.data);
        </script>
        </div>"""
        return elementTempl.format(elementId, json.dumps(data), title)

    def renderSysInfos(self):
        templ = "<div class='tile'><table>{}</table></div>"

        numFiles = len(self.fileList)
        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        tableContent = headerTempl.format("System Info", *self.fileList)
        for infoName, values in sorted(self.sysInfos.iteritems()):
            tableContent += rowTempl.format(infoName, *values)
        return templ.format(tableContent)

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

        firstFile = self.data.keys()[0]
        firstFileBenches = self.data[firstFile]['results']
        for fileName in benchmarks:
            fnBenches = self.data[fileName]['results'].keys()
            if firstFileBenches.keys() != fnBenches:
                raise RuntimeError("Can not compare given benchmarks! Different benches.")
            for benchKey in fnBenches:
                print firstFile, benchKey
                if self.getBenchArgs(firstFile, benchKey) != self.getBenchArgs(fileName, benchKey):
                    raise RuntimeError("Can not compare given benchmarks! Different args in bench: %s" % benchKey)

    def renderAllData(self):
        """Iterates over each bench and calls a render function to display the data.
        The render functions will produce html code. This code will be put together and
        saved as .html file.
        """
        inlineCss = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "css", "main.css"))
        d3Lib = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "js", "d3.v4.min.js"))
        chartsJS = ioservice.readFile(os.path.join(self.currentDir, "html", "assets", "js", "charts.js"))
        if self.args.trend:
            body = self.renderSysInfosTrend()
        else:
            body = self.renderSysInfos()
        benches = self.benchmarkData
        for benchKey in benches:
            logger.info("Render bench: " + benchKey)
            body += self.renderBench(benchKey)
        ioservice.writeToFile(self.template.format(inlineCss, d3Lib, chartsJS, body), self.args.outfile)

    def renderBench(self, benchKey):
        """Generates html code of the given bench name to display its data.
        This function will display a heading, the arguments, table and diagramms.

        :param benchKey: the name of the benchmark
        :returns: string with html code
        """
        title = "<h2>{0}</h2>".format(benchKey)
        tileTempl = "<div class='tile'>{0}</div>"
        args = self.renderBenchArgs(benchKey)
        if self.args.trend:
            measurements = self.renderBenchMeasurementsTrend(benchKey)
        else:
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

    def getBenchArgs(self, fileName, benchName):
        """Helper function to return the arguments of a benchmark.  If no file name
        is applied the data is token from the first file.

        :param benchName: name of the benchmark
        :param fileName: file where the information shall be taken from
        :returns: a dict of arguments
        """
        return self.data[fileName]["results"][benchName]["args"]

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
        benchTests = self.benchmarkData[benchName]
        # not data available
        if benchTests is None or benchTests == {}:
            return ""
        for (benchTestName, testData) in benchTests.iteritems():
            if benchTestName == 'args':
                continue

            values = testData["values"]
            for index, val in enumerate(values):
                if testData["type"] == "time_series":
                    testResultList = val
                    if len(testResultList) == 0:
                        continue
                    sumTime = sum(testResultList)
                    avg = sumTime / len(testResultList)
                    val = avg
                tableContent.append({"file": self.fileList[index], "name": benchTestName, "value": val})
        return elementTempl.format(benchName, json.dumps(tableContent))

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

    def renderTableByType(self, benchName, dataType):
        """Creates a table of specific type of bench tests.

        :param benchName: name of the benchmark
        :param type: type of the benchmark (e.g. 'time', 'time_series')
        :returns: html code of the table.
        """
        header = "<h4>Tabelle {}</h4>".format(dataType)
        benchTests = self.benchmarkData[benchName]

        # not data available
        if benchTests is None or benchTests == {}:
            return ""

        # filter tests by type
        tests = {benchTestName: testData for benchTestName, testData in benchTests.iteritems() if not benchTestName == 'args' and testData["type"] == dataType}
        if len(tests) == 0:
            return ""

        content = "<table>"
        if dataType == "time_series":
            content += self.renderTimeSeriesRows(benchName, tests)
        elif dataType == "time":
            content += self.renderTimeRows(benchName, tests)

        content += "</table>"
        return header + content

    def renderTimeRows(self, benchName, test):
        """Creates the rows for the table. Each row display data of type 'time'.
        The elements parameter contains a dict which is already filtered by this type.

        :param benchName: name of the benchmark
        :param elements: filtered dict which is containing test
        :returns: string containing the rows
        """
        htmlCode = ""

        numFiles = len(self.fileList)
        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        htmlCode += headerTempl.format("Test", *self.fileList)
        for benchTestName, testData in sorted(test.iteritems()):
            htmlCode += rowTempl.format(benchTestName, *testData['values'])
        return htmlCode

    def renderTimeSeriesRows(self, benchName, tests):
        """Creates the rows for the table. Each row display data of type 'time_series'.
        The elements parameter contains a dict which is already filtered by this type.

        :param benchName: name of the benchmark
        :param elements: filtered dict which is containing test
        :returns: string containing the rows
        """
        htmlCode = ""

        numFiles = len(self.fileList)
        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 2) + "</tr>"
        outerRowTempl = "<tr><td>{}</td><td colspan='{}'><table>{}</table></td></tr>"
        innerRowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        htmlCode += headerTempl.format("Test", "Aggregation", *self.fileList)
        for benchTestName, testData in sorted(tests.iteritems()):
            innerhtmlCode = ""
            listMax = []
            listMin = []
            listSum = []
            listAvg = []

            for timeList in testData['values']:
                if len(timeList) == 0:
                    listMax.append([])
                    listMin.append([])
                    listSum.append([])
                    listAvg.append([])
                    continue
                maxVal = max(timeList)
                minVal = min(timeList)
                sumVal = sum(timeList)
                avgVal = sumVal / len(timeList)
                listMax.append(maxVal)
                listMin.append(minVal)
                listSum.append(sumVal)
                listAvg.append(avgVal)
            if len(listMax) == 0:
                continue
            innerhtmlCode += innerRowTempl.format("Max", *listMax)
            innerhtmlCode += innerRowTempl.format("Min", *listMin)
            innerhtmlCode += innerRowTempl.format("Sum", *listSum)
            innerhtmlCode += innerRowTempl.format("Average", *listAvg)
            htmlCode += outerRowTempl.format(benchTestName, (len(self.fileList) + 1), innerhtmlCode)
        return htmlCode

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
        args = self.benchmarkData[benchName]['args']
        rows = ""
        for key, val in sorted(args.iteritems()):
            rows = rows + "\n<tr><td>{0}</td><td>{1}</td></tr>".format(key, val)
        result = result.format(rows)
        return result


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def createElementId(name):
    return name.encode('Base64').replace('\n', '').replace('=', '')
