// Based on: http://bl.ocks.org/3766585
function barChart () {
  var margin = {top: 30, right: 10, bottom: 50, left: 50},
      width = 420,
      height = 420,
      yRoundBands = 0.2,
      xValue = function(d) { return d[1]; },
      yValue = function(d) { return d[0]; },
      yScale = d3.scale.ordinal(),
      xScale = d3.scale.linear(),
      xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(5),
      yAxis = d3.svg.axis().scale(yScale).orient("left"),
      xTickFormat = undefined,
      yTickFormat = undefined;
    _yScale = yScale;
    _xScale = xScale;
    _xAxis = xAxis;

  function chart(selection) {
    selection.each(function(data) {

      // Convert data to standard representation greedily;
      // this is needed for nondeterministic accessors.
      data = data.map(function(d, i) {
        return [xValue.call(data, d, i), yValue.call(data, d, i)];
      });
    
      // Update the x-scale.
      yScale
          .domain(data.map(function(d) { return d[1];} ))
          .rangeRoundBands([0, height - margin.top - margin.bottom], yRoundBands);
         

      // Update the y-scale.
      xScale
          .domain(d3.extent(data.map(function(d) { return d[0];} )))
          .range([0, width - margin.left - margin.right])
          .nice();
          

      // Select the svg element, if it exists.
      var svg = d3.select(this).selectAll("svg").data([data]);

      // Otherwise, create the skeletal chart.
      var gEnter = svg.enter().append("svg").append("g");
      var xGridLines = gEnter.append("g").attr("class", "x gridlines");
      gEnter.append("g").attr("class", "bars");
      gEnter.append("g").attr("class", "y axis");
      gEnter.append("g").attr("class", "x axis");
      gEnter.append("g").attr("class", "x axis zero");

      // Update the outer dimensions.
      svg .attr("width", width)
          .attr("height", height);

      // Update the inner dimensions.
      var g = svg.select("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

     // Update the bars.
      var bar = svg.select(".bars").selectAll(".bar").data(data);
      bar.enter().append("rect");
      bar.exit().remove();
      bar .attr("class", function(d, i) { return d[0] < 0 ? "bar negative" : "bar positive"; })
          .attr("y", function(d) { return Y(d); })
          .attr("x", function(d, i) { return X0(); })
          .attr("data-dependent", function(d){ return yValue(d); })
          .attr("data-independent", function(d){ return xValue(d); })
          .attr("height", yScale.rangeBand())
          .attr("width", function(d, i) { return Math.abs( X(d) - X0() ); });

    // x axis at the bottom of the chart
     g.select(".y.axis")
        .attr("transform", "translate(0, 0)")
        .call(yAxis);
    
    // zero line
     g.select(".y.axis.zero")
        .attr("transform", "translate(" + X0() + ", 0)")
        .call(yAxis.tickFormat("").tickSize(0));
    
    
      // Update the y-axis.
      yAxisY = Math.max.apply(null, yScale.range()) + margin.top + margin.bottom;
      yAxisY = yScale.rangeExtent()[1];
      g.select(".x.axis")
        .attr("transform", "translate(0, " + yAxisY + ")")
        .call(xAxis);

      xGridLines
       .selectAll("line.x.gridline")
       .data(xScale.ticks(5))
       .enter()
       .append("line")
       .attr("class", "x gridline")
       .attr("x1", xScale)
       .attr("x2", xScale)
       .attr("y1", Y(0))
       .attr("y2", yScale.rangeExtent()[1]);

    });
  }


// The x-accessor for the path generator; xScale âˆ˜ xValue.
  function X(d) {
    return xScale(d[0]);
  }

  function X0() {
    return xScale(0);
  }

  // The x-accessor for the path generator; yScale âˆ˜ yValue.
  function Y(d) {
    return yScale(d[1]);
  }

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.x = function(_) {
    if (!arguments.length) return xValue;
    xValue = _;
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) return yValue;
    yValue = _;
    return chart;
  };

  chart.xTickFormat = function(_) {
    if (!arguments.length) return xTickFormat;
    xTickFormat = _;
    return chart;
  };

  chart.yTickFormat = function(_) {
    if (!arguments.length) return yTickFormat;
    yTickFormat = _;
    return chart;
  };

  chart.xMin = function(_) {
    if (!arguments.length) return xMin;
    xMin = _;
    return chart;
  };

  chart.xMax = function(_) {
    if (!arguments.length) return xMax;
    xMax = _;
    return chart;
  };

  return chart;
}
