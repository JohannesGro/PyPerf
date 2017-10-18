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
    """The class renderer reads the results of one or several benchmarks and
    creates a human readable output for example showing table or diagrams. The renderer provides two
    use cases. Firstly, a comparison between a plurality of benchmarks. Secondly, a analysis and
    determine a trend of a single system.
    A json file created by the benchrunner can be taken as a input. Currently this
    module supports html output only.
    """
    currentDir = os.path.dirname(__file__)
    benchmarkFile = os.path.join(currentDir, "benchmarkResults.json")
    outputFile = 'benchmarkResults_{}.html'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
    loggingFile = 'renderer.log'

    # CLI
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks", "-b", nargs='+', default=benchmarkFile, help="One or more json files which contain the benchmarks. It is also possible to use folders. All json files from a folder will be loaded.")
    parser.add_argument("--outfile", "-o", nargs='?', default=outputFile, help="The results will be stored in this file (html).")
    parser.add_argument("--reference", "-r", nargs='?', help="""A referenced benchmark for the comparision. Uses the reference to mark some benchmarks result
                                                                as positiv or negativ. This option will be ignored if the -trend option is active.""")
    parser.add_argument("--logconfig", "-l", nargs='?', default="", help="Configuration file for the logger.")
    parser.add_argument("--trend", "-t", default=False, action="store_true", help="Using the benchmarks to show a trend of a system.")

    template = """
    <!DOCTYPE html>
    <html>
    <head>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro" rel="stylesheet">
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
        logger.debug("trend: " + str(self.args.trend))
        logger.debug("reference: " + str(self.args.reference))

        data = self.loadBenchmarkData()
        self.organizeData(data)
        self.renderAllData()

    def organizeData(self, data):
        """Takes the read-in data and puts the data in a format for further processing.

        :param data: a dict with the data of benchmark files.
        """

        # three parts
        self.fileList = []
        self.sysInfos = {}
        self.benchmarkData = {}

        # create a list of all files
        firstFile = data.keys()[0]
        for fileName in data.keys():
            self.fileList.append(fileName)

        # create dict of all sysinfos. The values of all files are represented as a list.
        for sysinfo, val in data[firstFile]["Sysinfos"].iteritems():
            attributeValues = []
            for fileName in self.fileList:
                if sysinfo in data[fileName]["Sysinfos"]:
                    attributeValues.append(data[fileName]["Sysinfos"][sysinfo])
                else:
                    attributeValues.append('-')
            self.sysInfos[sysinfo] = attributeValues

        # create dict of all benches->test->results. The values all files are represented as a list.
        for bench, benchContent in data[firstFile]["results"].iteritems():
            self.benchmarkData[bench] = {}
            # argument list of a bench
            self.benchmarkData[bench]['args'] = benchContent['args']

            # iterate over all bench tests
            for test, testContent in benchContent['data'].iteritems():
                resultValues = []
                self.benchmarkData[bench][test] = {}
                self.benchmarkData[bench][test]['unit'] = testContent['unit']
                self.benchmarkData[bench][test]['type'] = testContent['type']
                for fileName in self.fileList:
                    resultValues.append(data[fileName]["results"][bench]['data'][test]['value'])
                self.benchmarkData[bench][test]['values'] = resultValues

    def renderBenchMeasurementsTrend(self, benchName):
        """Produces html code for the data of the given bench name.
        Diagrams are created only if there are more than one file. Otherwise
        a table is created.

        :param benchName: name of the bench
        :returns: html code of the data
        """
        res = ""
        body = ""
        # no diagram for a one entr
        if len(self.fileList) > 1:
            body = self.createTrendDiagramForBenchName(benchName)
        else:
            body += self.renderTablesByTypes(benchName)
        return body

    def createTrendDiagramForBenchName(self, benchName):
        """Produce html/js code to display the data of a benchmark as diagram.
        The javascript function can be find in chart.js.

        :param benchName: name of the benchmark
        :returns: html/js code of the diagram.
        """
        htmlCode = ""
        # iterate over all tests within in a bench
        for benchTestName, benchTestData in sorted(self.benchmarkData[benchName].iteritems()):
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
                    testResult = calcAvg(testResult)
                measurements.append({'value': testResult, 'time': utcTime, 'tooltip': tooltip})
            # creates a base64 id for the element. test names could be invalid.
            eleId = createElementId("{}{}".format(benchName, benchTestName))
            htmlCode += self.createTrendDiagram({'name': benchTestName, 'meas': measurements}, eleId, benchTestName)
        return htmlCode

    def renderSysInfosTrend(self):
        """Produces the html code for the system infos. The infos are separated into 6 different groups.
        This groups are determined by prefix. There are 5 default prefixes ('Memory', 'CPU', 'CADDOK', 'Disk', 'Swap').
        The infos that could not be assigned to a group will be placed under 'Others'.

        :returns: html code for displaying the system infos.
        """
        templ = "<div class='tile'>{}</div>"
        rowTempl = "<tr><td>{}</td><td>{}</td></tr>"
        tableTemp = "<table><tr><th>System Info</th><th>Value</th></tr>{}</table>"
        groupsTemp = "<details><summary>{0}</summary>{1}</details>"

        sysinfosList = self.sysInfos
        groups = ""
        groupsKeywords = ['CADDOK', 'CPU', 'Disk', 'Memory', 'Swap', 'Other']
        for group in groupsKeywords:
            graphs = ""
            if group == 'Other':
                groupElements = sysinfosList
            else:
                # find the element for the current group
                groupElements = {key: val for key, val in sysinfosList.iteritems() if key.find(group) == 0}
            groupRows = ""
            for sysinfoname, values in sorted(groupElements.iteritems()):
                # no diagram for one entry
                if len(self.fileList) > 1:
                    # not the same columns
                    if not values[1:] == values[:-1]:
                        # are the values valid for the chart
                        if not type(values[0]) is list and isFloat(values[0]):
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
        """Some system infos can be shown as a diagram. This method produces the
        html/js for the given system info.

        :returns: html code for displaying system infos"""
        sysinfovalues = self.sysInfos[SysInfoName]
        timeList = self.sysInfos['Current Time (UTC)']

        measurements = []
        for index, value in enumerate(sysinfovalues):
            measurements.append({'value': value, 'time': timeList[index]})

        return self.createTrendDiagram({'name': SysInfoName, 'meas': measurements}, createElementId(SysInfoName), SysInfoName)

    def createTrendDiagram(self, data, elementId, title):
        """Produce html js code to display the data of a benchmark as diagram.
        The javascript function can be find in chart.js.

        :param benchName: name of the benchmark
        :param elementId: if of the dom element of the diagram
        :param title: displayed title for the diagram

        :returns: html/js code of the diagram.
        """
        elementTempl = """
        <div id="{0}" class="diagramContainer">
        <h3>{2}</h3>
        <script>
        var {0} = {1};
        createTrendChart("#{0}",self.{0}, 0);
        </script>
        <select class="selection" onchange='var svg = this.parentNode.getElementsByTagName("svg")[0]; svg.parentNode.removeChild(svg); createTrendChart("#{0}",self.{0}, this.selectedIndex);'>
        <option value="0" selected>All</option>
        <option value="1">24h</option>
        <option value="2">Weekdays</option>
        </select>
        </div>"""
        return elementTempl.format(elementId, json.dumps(data), title)

    def renderSysInfos(self):
        """Produces the html code for the system infos.

        :returns: html code for displaying the system infos.
        """
        numFiles = len(self.fileList)
        templ = "<div class='tile'>{}</div>"
        groupsTemp = "<details><summary>{0}</summary>{1}</details>"

        tableTemp = "<table>{}{}</table>"
        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"
        sysinfosList = self.sysInfos

        groups = ""
        groupsKeywords = ['CADDOK', 'CPU', 'Disk', 'Memory', 'Swap', 'Other']
        for group in groupsKeywords:
            if group == 'Other':
                groupElements = sysinfosList
            else:
                # find the element for the current group
                groupElements = {key: val for key, val in sysinfosList.iteritems() if key.find(group) == 0}
            groupRows = ""
            for sysinfoname, values in sorted(groupElements.iteritems()):
                groupRows += rowTempl.format(sysinfoname, *values)
            groups += groupsTemp.format(group, tableTemp.format(headerTempl.format("System Info", *self.fileList), groupRows))
            # remove the elements from the list
            sysinfosList = {key: val for key, val in sysinfosList.iteritems() if key not in groupElements.keys()}

        return templ.format(groups)

    def loadBenchmarkData(self):
        """Loads the benchmark data. The Format is a dict of the benchmark result
        produced by the benchmark runner. The files are specified in the arguments
        of argparse. If a directory is given it will load all json files from this
        directory.

        :returns: a dict of files which contain the benchmarks"""

        if self.args.reference:
            self.reference = ioservice.loadJSONData(self.args.reference)

        print self.args.benchmarks
        if isinstance(self.args.benchmarks, list):
            # Loads a bunch of benchmarks.
            data = {}
            for fileName in self.args.benchmarks:
                if os.path.isdir(fileName):
                    (_, _, fileNames) = os.walk(fileName).next()
                    for fn in fileNames:
                        # use only json files
                        _, fileExt = os.path.splitext(fn)
                        if fileExt == ".json":
                            data[fn] = ioservice.loadJSONData(os.path.join(fileName, fn))
                    continue
                data[fileName] = ioservice.loadJSONData(fileName)
            self.areBenchmarksComparable(data)
        else:
            # Loads a single benchmark
            data[self.args.benchmarks] = ioservice.loadJSONData(self.args.benchmarks)
        return data

    def areBenchmarksComparable(self, benchmarks):
        """Checks the structure of each benchmark result. The same benchsuite structure is
        necessary for comparison. The benches, the arguments and the test are therefore checked.

        :param benchmarks: dict with all benchmarks
        :raises RuntimeError: if the strucutre of the benchmarks is unequal
        """

        # define compare values from the first file
        firstFile = benchmarks.keys()[0]
        firstFileBenches = benchmarks[firstFile]['results']

        if self.args.reference and firstFileBenches.keys() != self.reference['results'].keys():
            raise RuntimeError("Can not compare given benchmarks ({} - {}) with reference! Different benches.".format(firstFile, self.args.reference))

        for fileName in benchmarks:
            fnBenches = benchmarks[fileName]['results'].keys()
            if firstFileBenches.keys() != fnBenches:
                raise RuntimeError("Can not compare given benchmarks ({} - {})! Different benches.".format(firstFile, fileName))

            for benchName in fnBenches:
                firstFileBenchTest = benchmarks[firstFile]["results"][benchName]["data"].keys()
                firstFileBenchArgs = benchmarks[firstFile]["results"][benchName]["args"]
                # compare args
                benchArgs = benchmarks[fileName]["results"][benchName]["args"]
                if firstFileBenchArgs != benchArgs:
                    raise RuntimeError("Can not compare given benchmarks ({} - {})! Different args in bench: {}".format(firstFile, fileName, benchName))

                # compare bench tests
                benchTests = benchmarks[fileName]["results"][benchName]["data"].keys()
                if firstFileBenchTest != benchTests:
                    raise RuntimeError("Can not compare given benchmarks ({} - {})! Different tests in bench: {}".format(firstFile, fileName, benchName))

        for benchName in firstFileBenches:
            firstFileBenchTest = benchmarks[firstFile]["results"][benchName]["data"].keys()
            firstFileBenchArgs = benchmarks[firstFile]["results"][benchName]["args"]
            if self.args.reference:
                # compare reference bench args
                if firstFileBenchArgs != self.reference['results'][benchName]['args']:
                    raise RuntimeError("Can not compare given benchmarks with reference ({} - {})! Different args in bench: {}".format(self.reference, firstFile, benchName))
                # compare reference bench tests
                referenceBenchTest = self.reference['results'][benchName]['data'].keys()
                if firstFileBenchTest != referenceBenchTest:
                    raise RuntimeError("Can not compare given benchmarks with reference ({} - {})! Different tests ({} - {}) in bench: {}".format(self.reference, firstFile, firstFileBenchTest, referenceBenchTest, benchName))

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
        for benchName in benches:
            logger.info("Render bench: " + benchName)
            body += self.renderBench(benchName)
        ioservice.writeToFile(self.template.format(inlineCss, d3Lib, chartsJS, body), self.args.outfile)

    def renderBench(self, benchName):
        """Generates html code of the given bench name to display its data.
        This function will display a heading, the arguments, table and diagrams.

        :param benchName: the name of the benchmark
        :returns: string with html code
        """
        title = "<h2>{0}</h2>".format(benchName)
        tileTempl = "<div class='tile'>{0}</div>"
        args = self.renderBenchArgs(benchName)
        if self.args.trend:
            measurements = self.renderBenchMeasurementsTrend(benchName)
        else:
            measurements = self.renderBenchMeasurements(benchName)
        return tileTempl.format(title + args + measurements)

    def renderBenchMeasurements(self, benchName):
        """Produces html code for the data of the given bench name.
        A diagram and tables are created.

        :param benchName: name of the bench
        :returns: html code of the data
        """
        res = ""
        # no diagram for one entry
        if len(self.fileList) > 1 or self.args.reference:
            body = self.createDiagramsForBenchName(benchName)
        body += self.renderTablesByTypes(benchName)
        return body

    def createDiagramsForBenchName(self, benchName):
        """Creates a diagramm for every test within the bench.

        :param benchName: name of the bench.
        :returns: html/js code containing all diagrams for the given benchmark."""
        benchTests = self.benchmarkData[benchName]
        # not data available
        if benchTests is None or benchTests == {}:
            return ""

        htmlCode = ""
        for (benchTestName, testData) in sorted(benchTests.iteritems()):
            diagramData = []
            # one entry represents the args for the bench
            if benchTestName == 'args':
                continue

            # reference data
            if self.args.reference:
                val = self.reference['results'][benchName]['data'][benchTestName]['value']
                if testData["type"] == "time_series":
                    val = calcAvg(val)
                diagramData.append({"file": 'reference', "name": benchTestName, "value": val})

            # benchmarks data
            values = testData["values"]
            for index, val in enumerate(values):
                # aggreagte time series and use that value for the diagram
                if testData["type"] == "time_series":
                    val = calcAvg(val)
                diagramData.append({"file": self.fileList[index], "name": benchTestName, "value": val})
                elementId = createElementId(benchName + benchTestName)
            htmlCode += self.createBarDiagram(diagramData, elementId, benchTestName)

        return htmlCode

    def createBarDiagram(self, data, elementId, title):
        """Produce html js code to display the data of a benchmark as diagram.
        The javascript function can be find in chart.js.

        :param benchName: name of the benchmark
        :param elementId: if of the dom element of the diagram
        :param title: displayed title for the diagram

        :returns: html/js code of the diagram.
        """
        elementTempl = """
        <div id="{0}" class="diagramContainer">
        <h3>{2}</h3>
        <script>
        var data = {1};
        createBarChart("#{0}",self.data);
        </script>
        </div>"""
        return elementTempl.format(elementId, json.dumps(data), title)

    def renderTablesByTypes(self, benchName):
        """Creates tables for each type of bench test.

        :param benchName: name of the benchmark
        :return: the html code of all tables
        """
        types = ["time", "time_series"]
        res = ""
        for t in types:
            res += self.renderTableByType(benchName, t)
        return res

    def renderTableByType(self, benchName, dataType):
        """Creates a table of specific type of bench tests.

        :param benchName: name of the benchmark
        :param dataType: type of the benchmark (e.g. 'time', 'time_series')
        :returns: html code of the table.
        """
        header = "<h3>Tabelle {}</h3>".format(dataType)
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
        if self.args.reference:
            numFiles += 1

        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        if self.args.reference:
            htmlCode += headerTempl.format("Test", "reference", *self.fileList)
        else:
            htmlCode += headerTempl.format("Test", *self.fileList)

        for benchTestName, testData in sorted(test.iteritems()):
            if self.args.reference:
                referenceValue = self.reference['results'][benchName]['data'][benchTestName]['value']
                self.markBounds(referenceValue, testData['values'], testData['type'])
                htmlCode += rowTempl.format(benchTestName, referenceValue, *testData['values'])
            else:
                htmlCode += rowTempl.format(benchTestName, *testData['values'])
        return htmlCode

    def renderTimeSeriesRows(self, benchName, tests):
        """Creates the rows for the table. Each row display data of type 'time_series'.
        The values are aggregated and displayed as a single value.

        :param benchName: name of the benchmark
        :param tests: filtered dict which is containing test
        :returns: string containing the html rows
        """
        htmlCode = ""

        numFiles = len(self.fileList)
        if self.args.reference:
            numFiles += 1

        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 2) + "</tr>"
        outerRowTempl = "<tr><td>{}</td><td colspan='{}'><table>{}</table></td></tr>"
        innerRowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        if self.args.reference:
            htmlCode += headerTempl.format("Test", "Aggregation", "reference", *self.fileList)
        else:
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

            # reference data
            if self.args.reference:
                timeList = self.reference['results'][benchName]['data'][benchTestName]['value']
                maxVal = max(timeList)
                minVal = min(timeList)
                sumVal = sum(timeList)
                avgVal = sumVal / len(timeList)

                self.markBounds(maxVal, listMax, testData['type'])
                self.markBounds(minVal, listMin, testData['type'])
                self.markBounds(sumVal, listSum, testData['type'])
                self.markBounds(avgVal, listAvg, testData['type'])

                innerhtmlCode += innerRowTempl.format("Max", maxVal, *listMax)
                innerhtmlCode += innerRowTempl.format("Min", minVal, *listMin)
                innerhtmlCode += innerRowTempl.format("Sum", sumVal, *listSum)
                innerhtmlCode += innerRowTempl.format("Average", avgVal, *listAvg)
            else:
                innerhtmlCode += innerRowTempl.format("Max", *listMax)
                innerhtmlCode += innerRowTempl.format("Min", *listMin)
                innerhtmlCode += innerRowTempl.format("Sum", *listSum)
                innerhtmlCode += innerRowTempl.format("Average", *listAvg)
            htmlCode += outerRowTempl.format(benchTestName, (numFiles + 1), innerhtmlCode)
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

    def markBounds(self, referenceValue, data, testType):
        """Iterate through the data and compare it to the reference value.
        The data will be marked with red or green if several bounds are reached.

        :param referenceValue: reference value for the comparison
        :param data: a list with values
        :param testType: type of the test. important to determine the upper/lower bounds.
            E.g. the smaller time the better but the more operations per minute the better."""
        # there is two upper and lower bounds.
        firstInterval = 0.3
        secondInterval = 0.5

        # the order of the color represents the bounds [1. upper, 2.upper, 1. lower , 2.lower]
        # light-red, red, light-green, green
        colors = ['#e57373', '#D00000', '#d2e175', '#ADC902']

        if testType == 'time' or testType == 'time_series':
            # determine the bounds
            firstLowerBound = referenceValue
            secondLowerBound = referenceValue * (1 - firstInterval)
            firstUpperBound = referenceValue * (1 + firstInterval)
            secondUpperBound = referenceValue * (1 + secondInterval)
        else:
            # light-green, green, light-red, red
            colors = ['#d2e175', '#ADC902', '#e57373', '#D00000']
            # determine the bounds
            firstLowerBound = referenceValue * (1 - firstInterval)
            secondLowerBound = referenceValue * (1 - secondInterval)
            firstUpperBound = referenceValue
            secondUpperBound = referenceValue * (1 + firstInterval)

        # check if the values reached the bounds and setting the color for this section.
        for i, value in enumerate(data):
            colorIndex = -1
            if value > firstUpperBound:
                if value > secondUpperBound:
                    colorIndex = 1
                else:
                    colorIndex = 0
            elif value < firstLowerBound:
                if value < secondLowerBound:
                    colorIndex = 3
                else:
                    colorIndex = 2
            # change the value if a bound is reached
            if not colorIndex == -1:
                data[i] = "<span style='background-color: {};'>{}</span>".format(colors[colorIndex], value)


def isFloat(s):
    """A helper function for determining if a value (string) could be converted to to float.

    :param s: the string to be checked
    :returns: boolean if the string can be cast to float"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def createElementId(name):
    """A helper function for creating a dom element id. This is useful if the
    name contains not allowed characters.

    :param name: name of the element
    :returns: base64 encoded string without newline and '='"""
    return name.encode('Base64').replace('\n', '').replace('=', '')


def calcAvg(values):
    """A helper function for calculating the average of a list of values.

    :param values: a list of floats
    :returns: average of the list"""
    if len(values) == 0:
        return
    sumTime = sum(values)
    avg = sumTime / len(values)
    return avg
