
/**
 * Draws a bar chart with d3js.
 *
 * @param {String} DOMElement - The element which shell contain the chart.
 * @param {Array.Object} data - The data for chart. It contains a objects with name of the bench test, the file name and the value.
 */
function createBarChart(DOMElement, data) {

  data.sort(function(a, b) {
    if (b.name.localeCompare(a.name, {sensitivity: "case"}) == 0)
      return a.file.localeCompare(b.file, {sensitivity: "case"}) // ascending
    return b.name.localeCompare(a.name, {sensitivity: "case"});
  });

  var files = [];
  for(var i = 0 ; i < data.length; i++) {
    var d = data[i];
    if( -1 ==  files.indexOf(d.file)) {
      files.push(d.file);
    }
  }
  var num_files = files.length;


  // Color scale
  var color = d3.scaleOrdinal(d3.schemeCategory20);
  var gapBetweenGroups = 5;
  var numGroups = data.length / num_files;

  var margin = {top: 20, right: 30, bottom: 40, left: 100},
      width = 960 - margin.left - margin.right,
      height = (500 / 15) * data.length + gapBetweenGroups * numGroups * (num_files - 1);


  var x = d3.scaleLinear().rangeRound([0, width]);
  var y = d3.scaleBand().rangeRound([height, 0]).paddingInner(0.1);;

  // define x and y axis
  var xAxis = d3.axisBottom()
      .scale(x)

  var yAxis = d3.axisLeft()
      .scale(y)
      .tickSize(0)
      .tickPadding(6)
      .tickFormat("");

  // Define the div for the tooltip
  var div = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0);

  // create a svg
  var svg = d3.select(DOMElement).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  x.domain(d3.extent(data, function(d) {return d.value; })).nice();
  y.domain(data.map(function(d) { return d.file; }));
  var barHeight = y.bandwidth();

    // prepare chart
    var bar = svg.selectAll(".bar")
          .data(data)
        .enter().append("g")
          .attr("class", "bar")

    // create the bars
    bar.append("rect")
        .attr("x", 0)
        .attr("y", function(d, i) { return y(d.file);})
        .attr("width", function(d) { return x(d.value);})
        .attr("height", barHeight)
        .attr("fill", function(d,i) { return color(i % num_files); })
        .on("mouseover", function(d) {
                    div.transition()
                        .duration(200)
                        .style("opacity", .9);
                    div	.html(d.file + "<br/>")
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 28) + "px");
                    })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });

    // write text next to the bars
    var formatVal = d3.format(".5f");
    bar.append("text")
        .attr("x", function(d) { return x(d.value) + 1 ; })
        .attr("y", function(d, i) { return y(d.file) + barHeight / 2 ;})
        .attr("dy", ".35em")
        .attr("alignment-baseline", "baseline")
        .text(function(d) { return formatVal(d.value); });

    // x and y axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
          .attr("fill", "#000")
          .attr("y", 0)
          .attr("x", width)
          .attr("font-size", "14px")
          .attr("dy", "2.5em")
          .attr("text-anchor", "end")
          .text("Values");;

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
          .attr("fill", "#000")
          .attr("transform", "rotate(-90)")
          .attr("y", 0)
          .attr("font-size", "14px")
          .attr("dy", "-1.0em")
          .attr("text-anchor", "end")
          .text("Files");;


    var dataAvg = d3.mean(data, function(d) { return d.value; });

    var lineAvg = d3.line()
      .x(function(d) {return x(dataAvg); })
      .y(function(d, i) {if (i > 0) {return y(d.file)} else {return y(d.file) + barHeight;} }) //include the height of bar
      .curve(d3.curveLinear);

    svg.append("path")
        .datum(data)
        .attr("d", lineAvg)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", 5,5);

    var dataMed = d3.median(data, function(d) { return d.value; });

    var lineMed = d3.line()
      .x(function(d) {return x(dataMed); })
      .y(function(d, i) {if (i > 0) {return y(d.file)} else {return y(d.file) + barHeight;} }) //include the height of bar
      .curve(d3.curveStepBefore);

    svg.append("path")
        .datum(data)
        .attr("d", lineMed)
        .attr("fill", "none")
        .attr("stroke", "orange")
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", 5,5);

    // legend showing the different files.
    var legendRectSize = 18,
        legendSpacing  = 4,
        spaceForLabels = 50;

    var legend = svg.selectAll('.legend')
        .data(files)
        .enter()
        .append('g')
        .attr('transform', function (d, i) {
            var height = legendRectSize + legendSpacing;
            var offset = -gapBetweenGroups/2;
            var horz = spaceForLabels + width + 40 - legendRectSize;
            var vert = i * height - offset + 50;
            return 'translate(' + horz + ',' + vert + ')';
        });

    // displayed color of the files
    legend.append('rect')
        .attr('width', legendRectSize)
        .attr('height', legendRectSize)
        .style('fill', function (d, i) { return color(i); })
        .style('stroke', function (d, i) { return color(i); });

    // text of the file names
    legend.append('text')
        .attr('class', 'legend')
        .attr('x', legendRectSize + legendSpacing)
        .attr('y', legendRectSize - legendSpacing)
        .text(function (d) { return d; });

    var legend2 = svg.selectAll('.legend2')
        .data([{'name':"Median", "color":"orange"}, {'name':"Mean", "color":"red"}])
        .enter()
        .append('g')
        .attr('transform', function (d, i) {
            var height = legendRectSize + legendSpacing;
            var offset = -gapBetweenGroups/2;
            var horz = spaceForLabels + width + 40 - legendRectSize;
            var vert = i * height - offset;
            return 'translate(' + horz + ',' + vert + ')';
        });;


    // displayed color of the entries
    legend2.append('line')
        .attr('x1', 0)
        .attr('x2', legendRectSize)
        .attr('y1', '0.5em')
        .attr('y2', '0.5em')
        .attr("stroke-width", 2.5)
        .style("stroke-dasharray","4,2") //dashed array for line
        .style('stroke', function (d, i) { return d.color; });

    // text of the entry names
    legend2.append('text')
        .attr('class', 'legend')
        .attr('x', legendRectSize + legendSpacing)
        .attr('y', legendRectSize - legendSpacing)
        .text(function (d) { return d.name; });

}


function createTrendChart(DOMElement, data, option) {
    console.log(option);



    data.meas.sort(function(a, b) {
      return a.time.localeCompare(b.time, {sensitivity: "case"});
    });

   var parseTime = d3.utcParse("%Y-%m-%dT%H:%M:%S.%L%L");
    if(option == 1) {
      var formatTime = d3.timeFormat("0000-00-00T%H:%M:%S.%L%L");
      var copy = data.meas;
      for (var x of data.meas) {
        // Shows only the explicitly set index of "5", and ignores 0-4

        console.log((x.time))
        console.log(parseTime(x.time))
        console.log(formatTime(x.time))

        console.log(x);
      }
    }

    var margin = {top: 20, right: 100, bottom: 40, left: 100},
      width = 560 - margin.left - margin.right,
      height = 300 - margin.top - margin.bottom;

      // Define the div for the tooltip
      var div = d3.select("body").append("div")
          .attr("class", "tooltip")
          .style("opacity", 0);

    var svg = d3.select(DOMElement).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom),
      g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    //2017-09-23T08:16:03.777000


    var x = d3.scaleTime()
      .rangeRound([0, width]);

    var y = d3.scaleLinear()
      .rangeRound([height, 0]);

    var area = d3.area()
    .x(function(d) { return x(parseTime(d.time)); })
    .y0(height)
    .y1(function(d) { return y(d.value); });

    x.domain(d3.extent(data.meas, function(d) { return parseTime(d.time); }));
    y.domain(d3.extent(data.meas, function(d) { return d.value; }));

    g.append("path")
    .datum(data.meas)
    .attr("class", "area")
    .attr("d", area);


    var dataAvg = d3.mean(data.meas, function(d) { return d.value; });

      // displayed avg
      g.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', y(dataAvg))
      .attr('y2', y(dataAvg))
      .attr("stroke-width", 1.5)
      .style("stroke-dasharray", "5,5") //dashed array for line
      .style('fill', 'red')
      .style('stroke', 'red');

    var dataMed = d3.median(data.meas, function(d) { return d.value; });

      // displayed median
      g.append('line')
          .attr('x1', 0)
          .attr('x2', width)
          .attr('y1', y(dataMed))
          .attr('y2', y(dataMed))
          .attr("stroke-width", 1.5)
          .style("stroke-dasharray", "5,5") //dashed array for line
          .style('fill', 'orange')
          .style('stroke', 'orange');


    g.append("g")
        .call(d3.axisLeft(y))
      .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("font-size", "14px")
        .attr("dy", "-4.71em")
        .attr("text-anchor", "end")
        .text("Measurements");

    g.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x).ticks(10).tickFormat(d3.timeFormat("%Hh")))
    .append("text")
    .attr("fill", "#000")
    .attr("y", 0)
    .attr("x", width)
    .attr("font-size", "14px")
    .attr("dy", "2.5em")
    .attr("text-anchor", "end")
    .text("Time");


    // Add the scatterplot
    svg.selectAll("dot")
        .data(data.meas)
      .enter().append("circle")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("r", 5)
        .attr("cx", function(d) { return x(parseTime(d.time)); })
        .attr("cy", function(d) { if (isNaN(d.value)){console.log(d.value, d.time, data.name)} ;return y(d.value); })
        .on("mouseover", function(d) {
                    div.transition()
                        .duration(200)
                        .style("opacity", .9);
                    div	.html("Time: " + d.time + "<br/>Value: " + d.value +  extractToolTip(d.tooltip))
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY + 28) + "px");
                    })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });

    // legend showing the different files.
    var legendLineSize = 18,
        legendSpacing  = 4,
        spaceForLabels = 25,
        leftSpacing = 10;
  var gapBetweenGroups = 5;

    var legend = svg.selectAll('.legend')
        .data([{'name':"Median", "color":"orange"}, {'name':"Mean", "color":"red"}])
        .enter()
        .append('g')
        .attr('transform', function (d, i) {
            var height = legendLineSize + legendSpacing;
            var offset = -gapBetweenGroups/2;
            var horz = spaceForLabels + width + margin.left - legendLineSize;
            var vert = i * height - offset;
            return 'translate(' + horz + ',' + vert + ')';
        });

    // displayed color of the entries
    legend.append('line')
        .attr('x1', 0)
        .attr('x2', legendLineSize)
        .attr('y1', '0.5em')
        .attr('y2', '0.5em')
        .attr("stroke-width", 2.5)
        .style("stroke-dasharray","4,2") //dashed array for line
        .style('fill', function (d, i) { return d.color; })
        .style('stroke', function (d, i) { return d.color; });

    // text of the entry names
    legend.append('text')
        .attr('class', 'legend')
        .attr('x', legendLineSize + legendSpacing)
        .attr('y', legendLineSize - legendSpacing)
        .text(function (d) { return d.name; });


    // extracts tooltip from json object and return a html string for the div
    function extractToolTip(tooltip) {
      res = ""
      for (tip in tooltip) {
        res += "<br/>" + tip + ": "+ tooltip[tip];
      }
      return res;
    }
}
