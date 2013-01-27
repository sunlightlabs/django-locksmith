// Based on: http://bl.ocks.org/3766585
function columnChart() {
  var margin = {top: 30, right: 10, bottom: 50, left: 50},
      width = 420,
      height = 420,
      xRoundBands = 0.2,
      xValue = function(d) { return d[0]; },
      yValue = function(d) { return d[1]; },
      xScale = d3.scale.ordinal(),
      yScale = d3.scale.linear(),
      yAxis = d3.svg.axis().scale(yScale).orient("left"),
      xAxis = d3.svg.axis().scale(xScale),
      yMin = undefined,
      yMax = undefined,
      xTickFormat = undefined,
      yTickFormat = undefined;
      

  function chart(selection) {
    selection.each(function(data) {

      // Convert data to standard representation greedily;
      // this is needed for nondeterministic accessors.
      data = data.map(function(d, i) {
        return [xValue.call(data, d, i), yValue.call(data, d, i)];
      });
    
      // Update the x-scale.
      xScale
          .domain(data.map(function(d) { return d[0];} ))
          .rangeRoundBands([0, width - margin.left - margin.right], xRoundBands);
         

      // Update the y-scale.
      var yDomain = d3.extent(data.map(function(d){ return d[1]; }));
      if (yMin !== undefined)
        yDomain[0] = yMin;
      if (yMax !== undefined)
        yDomain[1] = yMax;
      yScale
          .domain(yDomain)
          .range([height - margin.top - margin.bottom, 0])
          .nice();

      _yScale = yScale;
      _xScale = xScale;
      _yAxis = yAxis;
      _xAxis = xAxis;
          

      // Select the svg element, if it exists.
      var svg = d3.select(this).selectAll("svg").data([data]);

      // Otherwise, create the skeletal chart.
      var gEnter = svg.enter().append("svg").append("g");
      var yGridLines = gEnter.append("g").attr("class", "y gridlines");
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
      bar .attr("class", function(d, i) { return d[1] < 0 ? "bar negative" : "bar positive"; })
          .attr("x", function(d) { return X(d); })
          .attr("y", function(d, i) { return d[1] < 0 ? Y0() : Y(d); })
          .attr("data-dependent", function(d){ return d[1]; })
          .attr("data-independent", function(d){ return d[0]; })
          .attr("width", xScale.rangeBand())
          .attr("height", function(d, i) { return Math.abs( Y(d) - Y0() ); });

    // x axis at the bottom of the chart
     g.select(".x.axis")
        .attr("transform", "translate(0," + (height - margin.top - margin.bottom) + ")")
        .call(xAxis.orient("bottom").tickFormat(xTickFormat));
    
    // zero line
     g.select(".x.axis.zero")
        .attr("transform", "translate(0," + Y0() + ")")
        .call(xAxis.tickFormat("").tickSize(0));
    
    
      // Update the y-axis.
      g.select(".y.axis")
        .call(yAxis.tickFormat(yTickFormat));

      yGridLines
       .selectAll("line.y.gridline")
       .data(yScale.ticks(10))
       .enter()
       .append("line")
       .attr("class", "y gridline")
       .attr("y1", yScale)
       .attr("y2", yScale)
       .attr("x1", 0)
       .attr("x2", xScale.rangeExtent()[1]);
          
    });
  }


// The x-accessor for the path generator; xScale âˆ˜ xValue.
  function X(d) {
    return xScale(d[0]);
  }

  function Y0() {
    return yScale(0);
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

  chart.yMin = function(_) {
    if (!arguments.length) return yMin;
    yMin = _;
    return chart;
  };

  chart.yMax = function(_) {
    if (!arguments.length) return yMax;
    yMax = _;
    return chart;
  };

  return chart;
}

function AnalyticsColumnChart (options) {
    if (!(this instanceof AnalyticsColumnChart)) {
        return new AnalyticsColumnChart(options);
    }

    var that = this;
    var opts = options || {};
    var require_opt = function (k) {
        if (opts[k] === undefined) throw k.toString() + ' is required.';
    };
    var default_to = function (k, v) { opts[k] = (opts[k] === undefined) ? v : opts[k]; };
    default_to('width', 700);
    default_to('height', 400);
    require_opt('data_fn');
    require_opt('target');
    var $target = $(opts.target);
    var _settings = {};
    var _buttons = {};
    var _quiet = true;
    var _data = null;

    var _data_callback = function(data){
        _data = data;
        if (_setting('display.mode') === 'chart')
            _display_chart();
        else if (_setting('display.mode') === 'table')
            _display_table();
        return that;
    };
    this.data = _data_callback;

    var _display_table = function(){
        var $table = $target.find("table.analytics-table");
        $table.find("tbody").empty();
        _data.forEach(function(pair){
            var $tmpl = null;
            var tmpl_selector = _setting('table.row.tmpl') || '.table-row-tmpl';
            if (Function.prototype.isPrototypeOf(tmpl_selector) === true)
                $tmpl = tmpl_selector.call($target[0], that);
            else
                $tmpl = $(tmpl_selector);

            var $row = $($tmpl.html());

            var independent_label = _setting('independent_format').call(null, pair[0]);
            $row.find(".independent")
            .text(independent_label)
                .attr("data-independent", pair[0])
                .attr("data-dependent", pair[1]);

            var dependent_label = _setting('dependent_format').call(null, pair[1]);
            $row.find(".dependent")
                .text(dependent_label);
            $row.appendTo($target.find("table.analytics-table tbody"));
        });
        $table.find("thead th.independent").text(_setting("independent_label"));
        $table.find("thead th.dependent").text(_setting("dependent_label"));
        $table.find("caption").text(_setting("title"));
        $table.show();
        $target.find(".analytics-chart").hide();

        $target.find(".independent").click(function(event){
            if (_setting('chart.interval') === 'yearly') {
                _setting('chart.interval', 'monthly');
                _setting('year', $(this).attr('data-independent'));
                _refresh();
            }

            $target.trigger('dataClick', this);
        });
    };

    var _display_chart = function(){
        var $chart = $target.find(".analytics-chart");

        var chart = (_setting('chart.type') == 'column')
                  ? columnChart().yMin(0)
                  : barChart().xMin(0);

        chart.width(options['width'])
             .height(options['height'])
             .margin({'top': 0, 'right': 0, 'bottom': 20, 'left': 110});

        chart.xTickFormat((_setting('chart.type') === 'column')
                          ? _setting('independent_format')
                          : _setting('dependent_format'));

        chart.yTickFormat((_setting('chart.type') === 'column')
                          ? _setting('dependent_format')
                          : _setting('independent_format'));
        d3.select($chart[0])
          .datum(_data)
          .call(chart);

        $target.find("rect.bar").click(function(event){
            if (_setting('chart.interval') === 'yearly') {
                _setting('chart.interval', 'monthly');
                _setting('year', $(this).attr('data-independent'));
                _refresh();
            }
            $target.trigger('dataClick', this);
        });

        $target.find("figcaption").text(_setting('title'));
        $target.find("table.analytics-table").hide();
        $target.find(".analytics-chart").show();
    };

    var _refresh = function(){
        opts['data_fn'].call(null, that);
    };

    var _update_buttons = function(k){
        var btns = _buttons[k];
        if (btns !== undefined) {
            var v = _setting(k);
            btns.forEach(function($btn){
                if ($btn.attr('data-value') == v) {
                    $btn.addClass('active');
                } else {
                    $btn.removeClass('active');
                }
            });
        }
    };

    var _setting = function(k, v, update_ui) {
        if (v !== undefined) {
            console.log('For', $target.attr('id'), 'set', k, 'to', v);
            _settings[k] = v;
            if ((update_ui === undefined) || (update_ui === true)) {
                _update_buttons(k);
            }
            if (_quiet === false) {
                $target.trigger('setting-changed', [k, v]);
            }
            return that;
        } else {
            return _settings[k];
        }
    };
    this.setting = function(k, v){ return _setting(k, v, true); };

    var _show = function(){ _refresh(); $target.show(); return that; };
    this.show = _show;
    var _hide = function(){ $target.hide(); return that; };
    this.hide = _hide;
    var _silence = function(/* arguments */){
        if (arguments.length === 1) {
            _quiet = arguments[0];
            return that;
        } else {
            return _quiet;
        }
    };
    this.silence = _silence;

    $target.find("button[data-setting]").click(function(event){
        var k = $(this).attr("data-setting");
        var v = $(this).attr("data-value");
        _setting(k, v);
    });

    $target.find("button[data-setting]").each(function(){
        // Keep a lookup of the buttons for updating the UI later
        var k = $(this).attr("data-setting");
        var lst = _buttons[k] || [];
        lst.push($(this));
        _buttons[k] = lst;

        $(this).click(function(event){
            _refresh();
        });
    });

    _setting('independent_format', function(i){ return i.toString(); });
    _setting('dependent_format', function(d){ return d.toString(); });

    return that;
}

