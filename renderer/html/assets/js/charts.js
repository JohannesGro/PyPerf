function createBarChart(DOMElement, data) {

  var margin = {top: 20, right: 30, bottom: 40, left: 200},
      width = 960 - margin.left - margin.right,
      height = (500 /8*data.length) - margin.top - margin.bottom;

  var x = d3.scaleLinear().rangeRound([0, width]);

  var y = d3.scaleBand().rangeRound([height, 0]).paddingInner(0.15);;

  var xAxis = d3.axisBottom()
      .scale(x)

  var yAxis = d3.axisLeft()
      .scale(y)
      .tickSize(0)
      .tickPadding(6);

  var barHeight = 40;
  var svg = d3.select(DOMElement).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    x.domain(d3.extent(data, function(d) { return d.value; })).nice();
    y.domain(data.map(function(d) { return d.name; }));

    var bar = svg.selectAll(".bar")
          .data(data)
        .enter().append("g")
          .attr("class", "bar")

    bar.append("rect")
        .attr("x", 0)
        .attr("y", function(d) { return y(d.name) })
        .attr("width", function(d) { return x(d.value) - x(0); })
        .attr("height", y.bandwidth());


    var formatVal = d3.format(".5f");
    bar.append("text")
        .attr("x", function(d) { return x(d.value) + 1 ; })
        .attr("y", function(d) { return y(d.name) + y.bandwidth()/2;})
        .attr("dy", ".35em")
      //  .attr("text-anchor", "middle")
        .attr("alignment-baseline", "baseline")
        .text(function(d) { return formatVal(d.value); });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);


    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

/*

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", function(d) { return y(d.name); } )
        .attr("x", function(d) { return x(d.value); }  )
        .text(function(d) { return formatVal(d.value); });
*/


}
