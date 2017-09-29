
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
      .tickPadding(6);

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


    x.domain(d3.extent(data, function(d) { return d.value; })).nice();
    y.domain(data.map(function(d) { return d.name; }));
  var barHeight = (y.bandwidth() - (gapBetweenGroups * (num_files - 1))) / num_files;

    // prepare chart
    var bar = svg.selectAll(".bar")
          .data(data)
        .enter().append("g")
          .attr("class", "bar")

    // create the bars
    bar.append("rect")
        .attr("x", 0)
        .attr("y", function(d, i) { return y(d.name) + ((i%num_files)  * (barHeight + gapBetweenGroups))})
        .attr("width", function(d) { return x(d.value) - x(0); })
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
        .attr("y", function(d, i) { return y(d.name) + ((i%num_files)  * (barHeight + gapBetweenGroups)) + barHeight / 2 ;})
        .attr("dy", ".35em")
        .attr("alignment-baseline", "baseline")
        .text(function(d) { return formatVal(d.value); });

    // x and y axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);


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
            var vert = i * height - offset;
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
}


function createTrendChart(DOMElement, data) {

    console.log(data)
    console.log(data.meas)

    data.meas.sort(function(a, b) {
      return a.time.localeCompare(b.time, {sensitivity: "case"});
    });

    var margin = {top: 20, right: 30, bottom: 40, left: 100},
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
    var parseTime = d3.utcParse("%Y-%m-%dT%H:%M:%S.%L%L");

    var x = d3.scaleTime()
      .rangeRound([0, width]);

    var y = d3.scaleLinear()
      .rangeRound([height, 0]);

    var line = d3.line()
      .x(function(d) {return x(parseTime(d.time)); })
      .y(function(d) {return y(d.value); });

    var area = d3.area()
    .x(function(d) { return x(parseTime(d.time)); })
    .y0(height)
    .y1(function(d) { return y(d.value); });

    x.domain(d3.extent(data.meas, function(d) { return parseTime(d.time); }));
    y.domain(d3.extent(data.meas, function(d) { return d.value; }));
    //area.y0(y(0));
    console.log(y(0));

    g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).ticks(10))
      .select(".domain")
        .remove();

        g.append("path")
        .datum(data.meas)
        .attr("class", "area")
        .attr("d", area);
        // g.append("path")
        //     .datum(data.meas)
        //     .attr("fill", "none")
        //     .attr("stroke", "steelblue")
        //     .attr("stroke-linejoin", "round")
        //     .attr("stroke-linecap", "round")
        //     .attr("stroke-width", 1.5)
        //     .attr("d", line);

    g.append("g")
        .call(d3.axisLeft(y))
      .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("font-size", "14px")
        .attr("dy", "-4.71em")
        .attr("text-anchor", "end")
        .text(data.name);


    // Add the scatterplot
    svg.selectAll("dot")
        .data(data.meas)
      .enter().append("circle")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("r", 5)
        .attr("cx", function(d) { return x(parseTime(d.time)); })
        .attr("cy", function(d) { return y(d.value); })
        .on("mouseover", function(d) {
                    div.transition()
                        .duration(200)
                        .style("opacity", .9);
                    div	.html("Time: " + d.time + " Value: " + d.value + "<br/>")
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 28) + "px");
                    })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });



}
