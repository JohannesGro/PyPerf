# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
"""
"""

import json
import os
import pkg_resources

import ioservice
from pyperf.log import customlogging


KEY_2_GUILABEL = {
    "cpu_cores_logical": "CPU Count (locial CPUs)",
    "cpu_cores_physical": "CPU Count (physical CPUs)",
    "cpu_frequency": "CPU Frenquency",
    "cpu_load_system": "CPU Time Percent (spent by processes executing in kernel mode)",
    "cpu_load_user": "CPU Time Percent (spent by processes in user mode)",
    "cpu_load_idle": "CPU Time Percent (spent doing nothing)",
    "cpu_system": "CPU Time (spent by processes executing in kernel mode)",
    "cpu_user": "CPU Time (spent by processes in user mode)",
    "cpu_idle": "CPU Time (spent doing nothing)",
    "time": "Current Time (UTC)",
    "user": "Current User",
    "io_read_count": "Disk IO read (count)",
    "io_read_mb": "Disk IO read (MB)",
    "io_read_time": "Disk IO read (time)",
    "io_write_count": "Disk IO write (count)",
    "io_write_mb": "Disk IO write (MB)",
    "io_write_time": "Disk IO write (time)",
    "ce_version": "Elements Version",
    "mem_active": "Memory Active (MB)",
    "mem_available": "Memory Available (MB)",
    "mem_buffers": "Memory Buffers (MB)",
    "mem_cached": "Memory Cached (MB)",
    "mem_free": "Memory Free (MB)",
    "mem_inactive": "Memory Inactive (MB)",
    "mem_percent": "Memory Percent",
    "mem_shared": "Memory Shared (MB)",
    "mem_total": "Memory Total (MB)",
    "mem_total_virtual": "Memory Total Virtual (MB)",
    "mem_used": "Memory Used (MB)",
    "mem_wired": "Memory Wired (MB)",
    "os": "OS-Platform",
    "os_version": "OS-Platform Version",
    "cpu": "Processor",
    "swapped_out": "Swaped Out (MB)",
    "swapped_in": "Swap In (MB)",
    "swap_free": "Swap (Free MB)",
    "swap_percent": "Swap Percent",
    "swap_total": "Swap Total (MB)",
    "swap_used": "Swap Used (MB)",
    "mac_adress": "MAC_Adress",
    "hostnames": "Hostnames",
    "vm": "VM running?: (probably) "
}


class Renderer(object):
    """The class renderer reads the results of one or several benchmarks and
    creates a human readable output for example showing table or diagrams. The renderer provides two
    use cases. Firstly, a comparison between a plurality of benchmarks. Secondly, a analysis and
    determine a trend of a single system.
    A json file created by the benchrunner can be taken as a input. Currently this
    module supports html output only.
    """
    currentDir = os.path.dirname(__file__)
    loggingFile = 'renderer.log'

    template = u"""
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
    argsWarning = []

    def __init__(self, benchmarks, outfile, reference, logconfig, trend):
        self.benchmarks = benchmarks
        self.outfile = outfile
        self.reference = reference
        self.logconfig = logconfig
        self.trend = trend

    def main(self):
        global logger
        logger = customlogging.init_logging("[Renderer]", configFile=self.logconfig, fileName=self.loggingFile)
        logger.debug("benchmarks files: {}".format(self.benchmarks))
        logger.debug("output file: {}".format(self.outfile))
        logger.debug("logger conf file: " + str(self.logconfig))
        logger.debug("trend: " + str(self.trend))
        logger.debug("reference: " + str(self.reference))

        data = self.loadBenchmarkData()
        # if a directory contains no json files
        if len(data) == 0:
            logger.info("No benchmarks found.")
            return
        self.organizeData(data)
        self.renderAllData()

    def organizeData(self, data):
        """Takes the read-in data and puts the data in a format for further processing.
        In order to use as much data as possible the renderer iterates over all benches and tests of all files
        and shows the information. Older benchmarks can be compared with newer ones if the bench arguments and the test parameter
        are identical.

        :param data: a dict with the data of benchmark files.
        :raises RuntimeError: the data of the benches or tests is invalid
        """
        if len(data) == 0:
            return

        # three parts
        self.fileList = []
        self.sysInfos = {}
        self.benchmarkData = {}

        # create a list of all files
        for fileName in data.keys():
            self.fileList.append(fileName)

        # collect system infos keys of all files
        allSystemInfosKeys = set([])
        for fileName in self.fileList:
            # union the keys
            allSystemInfosKeys.update(data[fileName]["Sysinfos"].keys())

        # create dict of all sysinfos. The values of all files are represented as a list.
        for sysinfo in allSystemInfosKeys:
            attributeValues = []
            for fileName in self.fileList:
                if sysinfo in data[fileName]["Sysinfos"]:
                    attributeValues.append(data[fileName]["Sysinfos"][sysinfo])
                else:
                    attributeValues.append('-')
            self.sysInfos[sysinfo] = attributeValues

        # collect benches of all files
        allBenchKeys = set([])
        for fileName in self.fileList:
            # union the keys
            allBenchKeys.update(data[fileName]["results"].keys())

        # create dict of all benches->test->results. The values all files are represented as a list.
        for bench in allBenchKeys:
            self.benchmarkData[bench] = {}

            # argument list of a bench
            for fileName in self.fileList:
                # check if the bench exist in the given file
                if bench in data[fileName]["results"]:
                    # is there a entry for this bench?
                    if 'args' in self.benchmarkData[bench]:
                        # raise an error if the arguments for the benchmark are inconsistent
                        if not self.benchmarkData[bench]['args'] == data[fileName]["results"][bench]['args']:
                            # raise RuntimeError("Can not compare given benchmarks. Different bench arguments found in {} - {}!".format(fileName, bench))
                            self.argsWarning.append(bench)
                    else:
                        # create first entry
                        self.benchmarkData[bench]['args'] = data[fileName]["results"][bench]['args']

            # test keys list
            allBenchTestKeys = set([])
            for fileName in self.fileList:
                # union the keys
                allBenchTestKeys.update(data[fileName]["results"][bench]['data'].keys())

            # iterate over all bench tests. if the benchmarks does not contain this bench None is used.
            for test in allBenchTestKeys:
                resultValues = []
                self.benchmarkData[bench][test] = {}

                for fileName in self.fileList:
                    # add None if bench or test does not exist
                    if bench not in data[fileName]["results"] or test not in data[fileName]["results"][bench]['data']:
                        resultValues.append(None)
                    else:
                        # the properties of a test has to be consistent in each file
                        if 'unit' in self.benchmarkData[bench][test]:
                            # raise an error if the tests for the benchmark are inconsistent
                            if not self.benchmarkData[bench][test]['unit'] == data[fileName]["results"][bench]['data'][test]['unit']:
                                raise RuntimeError("Can not compare given benchmarks. Different test units found in {} - {} - {}!".format(fileName, bench, test))
                        else:
                            # create first entry
                            self.benchmarkData[bench][test]['unit'] = data[fileName]["results"][bench]['data'][test]['unit']

                        # the properties of a test has to be consistent in each file
                        if 'type' in self.benchmarkData[bench][test]:
                            # raise an error if the tests for the benchmark are inconsistent
                            if not self.benchmarkData[bench][test]['type'] == data[fileName]["results"][bench]['data'][test]['type']:
                                raise RuntimeError("Can not compare given benchmarks. Different test types found in {} - {} - {}!".format(fileName, bench, test))
                        else:
                            # create first entry
                            self.benchmarkData[bench][test]['type'] = data[fileName]["results"][bench]['data'][test]['type']

                        # everthing is fine. add the value of this file
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
                if testResult is None:
                    continue
                # find infos which will be displayed as tooltip
                tooltip = {}
                tooltipSysInfos = ["cpu_percent", "mem_percent"]
                for tooltipSysInfo in tooltipSysInfos:
                    if tooltipSysInfo in self.sysInfos:
                        tooltip[tooltipSysInfo] = self.sysInfos[tooltipSysInfo][index]

                utcTime = self.sysInfos["time"][index]
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

        groupsKeywords = [
            ("CADDOK", "CADDOK"),
            ("CPU", "cpu"),
            ("Disk", "io"),
            ("Memory", "mem"),
            ("Swap", "swap"),
            ("Other", "")]

        for group, groupkey in groupsKeywords:
            graphs = ""
            if group == 'Other':
                groupElements = sysinfosList
            else:
                # find the element for the current group
                groupElements = {key: val for key, val in sysinfosList.iteritems() if key.startswith(groupkey)}

            groupRows = ""
            for sysinfoname, values in sorted(groupElements.iteritems()):
                sysinfoname = KEY_2_GUILABEL.get(sysinfoname, sysinfoname)
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
        timeList = self.sysInfos["time"]

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
        groupsKeywords = [
            ("CADDOK", "CADDOK"),
            ("CPU", "cpu"),
            ("Disk", "io"),
            ("Memory", "mem"),
            ("Swap", "swap"),
            ("Other", "")]

        for group, groupkey in groupsKeywords:
            if group == 'Other':
                groupElements = sysinfosList
            else:
                # find the element for the current group
                groupElements = {key: val for key, val in sysinfosList.iteritems() if key.startswith(groupkey)}
            groupRows = ""
            for sysinfoname, values in sorted(groupElements.iteritems()):
                groupRows += rowTempl.format(KEY_2_GUILABEL.get(sysinfoname, sysinfoname), *values)

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

        if self.reference:
            self.ref = ioservice.loadJSONData(self.reference)

        if isinstance(self.benchmarks, list):
            # Loads a bunch of benchmarks.
            data = {}
            for fileName in self.benchmarks:
                if os.path.isdir(fileName):
                    (_, _, fileNames) = os.walk(fileName).next()
                    for fn in fileNames:
                        # use only json files
                        _, fileExt = os.path.splitext(fn)
                        if fileExt == ".json":
                            data[fn] = ioservice.loadJSONData(os.path.join(fileName, fn))
                    continue
                data[fileName] = ioservice.loadJSONData(fileName)
        else:
            # Loads a single benchmark
            data[self.benchmarks] = ioservice.loadJSONData(self.benchmarks)
        if(self.reference):
            numLoadedFiles = len(data) + 1
        else:
            numLoadedFiles = len(data)
        logger.info("Number of loaded json files: {}".format(numLoadedFiles))
        return data

    def renderAllData(self):
        """Iterates over each bench and calls a render function to display the data.
        The render functions will produce html code. This code will be put together and
        saved as .html file.
        """
        inlineCss = ioservice.readFile(pkg_resources.resource_filename(__name__, "html/assets/css/main.css"))
        d3Lib = ioservice.readFile(pkg_resources.resource_filename(__name__, "html/assets/js/d3.v4.min.js"))
        chartsJS = ioservice.readFile(pkg_resources.resource_filename(__name__, "html/assets/js/charts.js"))

        if self.trend:
            body = self.renderSysInfosTrend()
        else:
            body = self.renderSysInfos()
        benches = self.benchmarkData
        for benchName in benches:
            logger.info("Render bench: " + benchName)
            body += self.renderBench(benchName)
        ioservice.writeToFile(self.template.format(inlineCss, d3Lib, chartsJS, body), self.outfile)

    def renderBench(self, benchName):
        """Generates html code of the given bench name to display its data.
        This function will display a heading, the arguments, table and diagrams.

        :param benchName: the name of the benchmark
        :returns: string with html code
        """
        title = "<h2>{0}</h2>".format(benchName)
        tileTempl = "<div class='tile'>{0}</div>"
        args = self.renderBenchArgs(benchName)
        if self.trend:
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
        body = ""
        # no diagram for one entry
        if len(self.fileList) > 1 or self.reference:
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
            if self.reference:
                if benchName not in self.ref['results'] or benchTestName not in self.ref['results'][benchName]['data']:
                    val = None
                else:
                    val = self.ref['results'][benchName]['data'][benchTestName]['value']
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
        types = ["time", "time_series", "count", "count_series"]
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
        if dataType in ["time_series", "count_series"]:
            content += self.renderSeriesRows(benchName, tests)
        elif dataType in ["time", "count"]:
            content += self.renderRows(benchName, tests)

        content += "</table>"
        return header + content

    def renderRows(self, benchName, test):
        """Creates the rows for the table. Each row display data of type 'time'.
        The elements parameter contains a dict which is already filtered by this type.

        :param benchName: name of the benchmark
        :param elements: filtered dict which is containing test
        :returns: string containing the rows
        """
        htmlCode = ""

        numFiles = len(self.fileList)
        if self.reference:
            numFiles += 1

        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 1) + "</tr>"
        rowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        if self.reference:
            htmlCode += headerTempl.format("Test", "reference", *self.fileList)
        else:
            htmlCode += headerTempl.format("Test", *self.fileList)

        for benchTestName, testData in sorted(test.iteritems()):
            # replace none with '-'
            values = ['-' if val is None else val for val in testData['values']]
            if self.reference:
                if benchName not in self.ref['results'] or benchTestName not in self.ref['results'][benchName]['data']:
                    referenceValue = '-'
                else:
                    referenceValue = self.ref['results'][benchName]['data'][benchTestName]['value']
                self.markBounds(referenceValue, values, testData['type'])
                htmlCode += rowTempl.format(benchTestName, referenceValue, *values)
            else:
                htmlCode += rowTempl.format(benchTestName, *values)
        return htmlCode

    def renderSeriesRows(self, benchName, tests):
        """Creates the rows for the table. Each row display data of type 'time_series'.
        The values are aggregated and displayed as a single value.

        :param benchName: name of the benchmark
        :param tests: filtered dict which is containing test
        :returns: string containing the html rows
        """
        htmlCode = ""

        numFiles = len(self.fileList)
        if self.reference:
            numFiles += 1

        headerTempl = "<tr>" + "<th>{}</th>" * (numFiles + 2) + "</tr>"
        outerRowTempl = "<tr><td>{}</td><td colspan='{}'><table>{}</table></td></tr>"
        innerRowTempl = "<tr>" + "<td>{}</td>" * (numFiles + 1) + "</tr>"

        if self.reference:
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
                if len(timeList) == 0 or timeList is None:
                    listMax.append('-')
                    listMin.append('-')
                    listSum.append('-')
                    listAvg.append('-')
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
            if self.reference:
                if benchName not in self.ref['results'] or benchTestName not in self.ref['results'][benchName]['data']:
                    listMax.append('-')
                    listMin.append('-')
                    listSum.append('-')
                    listAvg.append('-')
                    continue
                timeList = self.ref['results'][benchName]['data'][benchTestName]['value']
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
        result = ""
        if benchName in self.argsWarning:
            warning = "<p style='color: #F75C03;font-size: 16px;'><span style='font-size: 24px; margin-right:10px;'>⚠</span>The arguments of the benchmarks are different from each other!</p>"
            result += warning

        result += """
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
        # reference could be None or non float
        if referenceValue is None or not isFloat(referenceValue):
            return

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
            if not isFloat(value):
                continue
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