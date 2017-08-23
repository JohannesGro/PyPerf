#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
import argparse
import json
import logging
import sys


logger = logging.getLogger("[" + __name__ + " - Renderer]")

benchmark_file = "benchmarkResults.json"
output_file = "benchmarkResults.html"

template = """
<html>
<head>
    <link rel="stylesheet" href="main.css">
</head>
<body>
<h1>Benchmark Results</h1>
{0}

</body>
</html>
"""


def main():
    data = loadJSONData()
    iterateBenches(data)


def iterateBenches(data):
    body = ""
    for bench_key, bench_val in data["results"].iteritems():
        logger.info("Render bench: " + bench_key)
        body += render_bench(bench_key, bench_val)

        # result = start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
        # results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
    writeHTML(template.format(body))


def render_bench(name, content):
    title = "<h2>{0}</h2>".format(name)
    tile_templ = "<div class='tile'>{0}</div>"
    args = render_args(content["args"])
    data = render_data(content["data"])
    return tile_templ.format(title + args + data)
    # print args


def render_data(data):
    title_templ = "<h3>{0}</h3>"
    content_templ = "<div class='content'>{0}</div>"
    res = ""
    for (name, content) in data.iteritems():
        title = title_templ.format(name)
        # body = render_types(data)
        body = render_tables_for_all_types(data)
        # res = res + tile_templ.format(title + body)
    # return content_templ.format(res)
    return body


def render_table_by_type(data, type):
    res = "<h4>Tabelle {}</h4>".format(type)
    elements = dict((name, content) for (name, content) in data.iteritems() if content["type"] == type)
    time_series_table_header_templ = """<tr>
                    <th>{}</th>
                    <th>{}</th>
                    <th>{}</th>
                    <th>{}</th>
                    <th>{}</th>
                  </tr>"""
    time_series_row_templ = """<tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                  </tr>"""
    time_header_templ = """  <tr>
                    <th>{}</th>
                    <th>{}</th>
                  </tr>"""
    time_row_templ = """  <tr>
                    <td>{}</td>
                    <td>{}</td>
                  </tr>"""
    content = "<table>"
    if type == "time_series":
        content += time_series_table_header_templ.format("Test", "Max", "Min", "Sum", "Average")
    elif type == "time":
        content += time_header_templ.format("Test", "Time")
    for (name, data) in elements.iteritems():
        if type == "time_series":
            time_list = data["value"]
            max_val = max(time_list)
            min_val = min(time_list)
            sum_val = sum(time_list)
            avg_val = sum_val / len(time_list)
            content += time_series_row_templ.format(name, max_val, min_val, sum_val, avg_val)
        elif type == "time":
            content += time_row_templ.format(name, data["value"])
    content += "</table>"
    return res + content


def render_tables_for_all_types(data):
    types = ["time", "time_series"]
    res = ""
    for t in types:
        res += render_table_by_type(data, t)
    return res


def render_types(content):
    res = "<h4>{}</h4>".format(content["type"])
    dl_temp = """
        <dl>
        {0}
       </dl>
    """
    dl_inner_temp = "<dt>{0}</dt><dd>{1}</dd>"
    if content["type"] == "time_series":
        time_list = content["value"]
        len_time_list = len(time_list)
        if len_time_list > 0:
            max_val = max(time_list)
            min_val = min(time_list)
            sum_val = sum(time_list)
            avg_val = sum_val / len(time_list)
            dl_inner = ""
            dl_inner += dl_inner_temp.format("Unit:", content["unit"])
            dl_inner += dl_inner_temp.format("Max:", max_val)
            dl_inner += dl_inner_temp.format("Min:", min_val)
            dl_inner += dl_inner_temp.format("Sum:", sum_val)
            if "totalTime" in content:
                dl_inner += dl_inner_temp.format("Total Time:", content["totalTime"])
            dl_inner += dl_inner_temp.format("Average:", avg_val)
            res += dl_temp.format(dl_inner)
    if content["type"] == "time":
        dl_inner = ""
        dl_inner += dl_inner_temp.format("Result:", str(content["value"]) + " " + content["unit"])
        res += dl_temp.format(dl_inner)
    return res


def render_args(args):
    result = """
        <table>
            <tr>
                <th>Argument</th>
                <th>Value</th>
            </tr>
            {0}
        </table>
    """
    rows = ""
    for key, val in args.iteritems():
        rows = rows + "\n<tr><td>{0}</td><td>{1}</td></tr>".format(key, val)
    result = result.format(rows)
    return result


def loadJSONData():
    """
    This functions load the json-data.
    """
    try:
        with open(benchmark_file) as data_file:
            data = json.load(data_file)
    except IOError as err:
        logger.error("Could not open benchmark data file! " + str(err))
        sys.exit(1)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode benchmark data file! " + str(err))
        sys.exit(1)
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[:]))
        sys.exit(1)
    else:
        logger.info("Reading successful")
    return data


def writeHTML(data):
    """
    This functions dumps json data into a file.
    """
    logger.info("Saving Results to file: " + output_file)
    try:
        with open(output_file, 'w') as out:
            out.write(data)
    except IOError as err:
        logger.error("Could not open file to save the data! " + str(err))
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode values! " + str(err))
    except TypeError as err:
        logger.error("Could not serialize object! " + str(err))
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
    else:
        logger.info("Saving successful")

if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="""reads data of benchmarks from a json file.
                                    Each benchmakrs will be called rendered. Produces a html file with the results.""")
    parser.add_argument("--benchmarks", "-s", nargs=1, default=benchmark_file, help="A json file which contains the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs=1, default=output_file, help="The results will be stored in this file.")

    # Grab the opts from argv
    opts = parser.parse_args()
    main()
