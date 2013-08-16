function barChart () {
  var margin = {top: 50, right: 50, bottom: 50, left: 50},
      width = 420,
      height = 420,
      yRoundBands = 0.2,
      yScale = d3.scale.ordinal(),
      xScale = d3.scale.linear(),
      xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(5),
      yAxis = d3.svg.axis().scale(yScale).orient("left"),
      xMin = undefined,
      xMax = undefined,
      xTickFormat = undefined,
      yTickFormat = undefined;

  function chart(selection) {
    selection.each(function(data) {
      // Update the x-scale.
      yScale
          .domain(data.map(function(d) { return d[0];} ))
          .rangeRoundBands([0, height - margin.top - margin.bottom], yRoundBands);
         

      // Update the x-scale.
      var xDomain = d3.extent(data.map(function(d){ return d[1]; }));
      if (xMin !== undefined)
          xDomain[0] = xMin;
      if (xMax !== undefined)
          xDomain[1] = xMax;
      xScale
          .domain(xDomain)
          .range([0, width - margin.left - margin.right])
          .nice();

      d3.select(this).select('div.tooltip').remove();
      var tooltip = d3.select(this)
                      .append('div')
                      .attr('class', 'tooltip')
                      .style('position', 'absolute');

      var show_tooltip = function(d){
          var mouse = d3.mouse(selection.node());
          tooltip.style('visibility', 'visible')
                 .style('opacity', '1.0')
                 .style('top', mouse[1] + 10 + 'px')
                 .style('left', mouse[0] + 10 + 'px')
                 .text(yTickFormat(d[0]) + ': ' + xTickFormat(d[1]));
      };
      var hide_tooltip = function(d){
          tooltip.style('visibility', 'hidden');
      };

          
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
      bar.attr("class", function(d, i) { return d[0] < 0 ? "bar negative" : "bar positive"; })
         .attr("y", function(d) { return Y(d); })
         .attr("x", function(d, i) { return X0(); })
         .attr("data-dependent", function(d){ return d[1]; })
         .attr("data-independent", function(d){ return d[0]; })
         .attr("height", yScale.rangeBand())
         .attr("width", function(d, i) { return Math.abs( X(d) - X0() ); })
         .on('mouseover', show_tooltip)
         .on('mousemove', show_tooltip)
         .on('mouseout', hide_tooltip)
         .on('click', hide_tooltip)
        // .on('dblclick', toggle_stats);
         
      
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

  function X(d) {
    return xScale(d[1]);
  }

  function X0() {
    return xScale(0);
  }

  function Y(d) {
    return yScale(d[0]);
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

// Based on: http://bl.ocks.org/3766585
function columnChart() {
  var margin = {top: 50, right: 50, bottom: 50, left: 50},
      width = 420,
      height = 420,
      xRoundBands = 0.2,
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
          
      d3.select(this).select('div.tooltip').remove();
      var tooltip = d3.select(this)
                      .append('div')
                      .attr('class', 'tooltip')
                      .style('position', 'absolute');

      var show_tooltip = function(d){
          var mouse = d3.mouse(selection.node());
          tooltip.style('visibility', 'visible')
                 .style('opacity', '1.0')
                 .style('top', mouse[1] + 10 + 'px')
                 .style('left', mouse[0] + 10 + 'px')
                 .text(xTickFormat(d[0]) + ': ' + yTickFormat(d[1]));
      };
      var hide_tooltip = function(d){
          tooltip.style('visibility', 'hidden');
      };
      
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
      bar.enter().append("rect").append("text").attr("x", function(d) {return X(d);}).attr("y", function(d, i){ return d[1] < 0 ? Y0() : Y(d); }).text(function(d){ return d;});

      bar.exit().remove();
      bar.attr("class", function(d, i) { return d[1] < 0 ? "bar negative" : "bar positive"; })
         .attr("x", function(d) { return X(d); })
         .attr("y", function(d, i) { return d[1] < 0 ? Y0() : Y(d); })
         .attr("data-dependent", function(d){ return d[1]; })
         .attr("data-independent", function(d){ return d[0]; })
         .attr("width", xScale.rangeBand())
         .attr("height", function(d, i) { return Math.abs( Y(d) - Y0() ); })
         .on('mouseover', show_tooltip)
         .on('mousemove', show_tooltip)
         .on('mouseout', hide_tooltip)
         .on('click', hide_tooltip)
       //  .on('dblclick', toggle_stats);

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

  function X(d) {
    return xScale(d[0]);
  }

  function Y0() {
    return yScale(0);
  }

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

function ReactiveSettingsIface (target) {
    if (this === top) {
        return new ReactiveSettingsIface(target);
    }

    var that = this;
    var $target = $(target);
    var _settings = {};
    var _buttons = {};

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
            _settings[k] = v;
            if ((update_ui === undefined) || (update_ui === true)) {
                _update_buttons(k);
            }
            return that;
        } else {
            return _settings[k];
        }
    };
    this.get = function (k) { return _setting(k); };
    this.set = function (k, v) { return _setting(k, v, true); };
    this.update = function (obj) {
        jQuery('#' + $target.attr('id')).find('.value').remove();
        for (var k in obj) {
            _setting(k, obj[k]);
        }
        $target.trigger('settings-changed', obj);
        return that;
    };
    this.settings = function(){ return $.extend(true, {}, _settings); };

    this.target = function(){ return $target; };

    $target.find("button[data-setting]").click(function(event){
        var k = $(this).attr("data-setting");
        var v = $(this).attr("data-value");
        var obj = {};
        obj[k] = v;
        that.update(obj);

    });

    $target.find('button.values').click(function(event){
        jQuery(this).siblings('figure').find('rect.bar').each(function(index) { 
          var d = jQuery(this);
          if ($target.find('.bar_value_' + d.attr('data-independent')).length == 0){
            var group = d.parents('figure')[0];
            var offset = d.position();
            var width = d.attr('width');
           if (_settings['chart.type'] === 'bar'){
              var top = parseInt(offset.top) + 5 + 'px'
              var left = parseInt(offset.left) + parseInt(width) + 5 + 'px'
           } else if (_settings['chart.type'] === 'column'){
              var top = offset.top - 25 +  'px';
              var left = offset.left + 10 + 'px';
           }
            if (d.attr('data-dependent') != 0) {
              d3.select(group)
                .append('div')
                .attr('class', 'value bar_value_' + d.attr('data-independent'))
                .style('visibility', 'visible')
                .style('opacity', '1.0')
                .style('position', 'absolute')
                .style('top',  top)
                .style('left', left)
                .text(d.attr('data-dependent'));
            }
          } else {
            $target.find('.bar_value_' + d.attr('data-independent')).remove();
          }
      })
    })

    $target.find("button[data-setting]").each(function(){
        // Keep a lookup of the buttons for updating the UI later
        var k = $(this).attr("data-setting");
        var lst = _buttons[k] || [];
        lst.push($(this));
        _buttons[k] = lst;
        $(this).click(function(event){
            that.buttons.trigger('click', this);

        });
    });
    this.buttons = $(_buttons);

    $target.addClass('reactive-settings');

    return that;
}

function ReactiveSettingsHistoryIface (options) {
    if ((window.history === undefined)
        || (window.history.pushState === undefined)
        || (window.history.replaceState === undefined)) return;

    if (this === top) {
        return new ReactiveSettingsHistoryIface(options);
    }

    var that = this;

    var _decode_state_anchor = function (anchor) {
        var decoded = JSON.parse(base64_to_unicode(anchor));
        if (options.compression_vocabulary) {
            decoded = vocab_translate_object(decoded, ANALYTICS_VOCAB);
        }
        return decoded;
    };

    var _update_settings_ifaces = function (decoded) {
        for (var decoded_key in decoded) {
            var settings_iface = options.settings[decoded_key];
            if (settings_iface != null) {
                if (! _.isEqual(settings_iface.settings(),
                                decoded[decoded_key])) {
                    settings_iface.update(decoded[decoded_key]);
                }
            }
        }

        if (options.post_update) {
            options.post_update.call(that, decoded);
        }
    };

    var _collect_settings = function () {
        var merged = {};
        for (var settings_key in options.settings) {
            var settings_iface = options.settings[settings_key].settings();
            merged[settings_key] = $.extend(true, {}, settings_iface);
        }
        return merged;
    };

    var _encode_state_anchor = function (obj) {
        var encoded = obj;
        if (options.compression_vocabulary) {
            encoded = vocab_translate_object(obj, ANALYTICS_VOCAB);
        }
        encoded = unicode_to_base64(JSON.stringify(encoded));
        return encoded;
    };

    var _update_history = function(event){
        var merged = _collect_settings();
        var encoded = _encode_state_anchor(merged);
        var url = window.location.protocol + '//' + window.location.host + window.location.pathname +  window.location.search + '#' + encoded;
        if (history.state != encoded) {
            // We need to guard against duplicating state because
            // the popstate event will also cause _update_history
            // to be called.
            if (options.replace_state === true) {
                history.replaceState(encoded, null, url);
            } else {
                history.pushState(encoded, null, url);
            }
        }
    };

    pairs(options.settings).forEach(function(pair){
        var key = pair[0];
        var settings = pair[1];
        settings.target().on('settings-changed', _update_history);
    });

    var _initial_popstate = true;
    var _initial_url = window.location.href;
    $(window).bind('popstate', function(event){
        if ((_initial_popstate === true) && (window.location.href == _initial_popstate)) {
            _initial_popstate = false;
            return;
        }

        var state = event.originalEvent.state;
        if (state !== null) {
            var decoded = _decode_state_anchor(state);
            _update_settings_ifaces(decoded);
        }
    });

    if (window.location.hash.length > 0) {
        var decoded = _decode_state_anchor(window.location.hash.slice(1));
        _update_settings_ifaces(decoded);
        history.replaceState(window.location.hash.slice(1), null, window.location.href);
    } else {
        var merged = _collect_settings();
        var encoded = _encode_state_anchor(merged);
        history.replaceState(encoded, null, window.location.href);
    }

    return that;
};

function AnalyticsChart (options) {
    if (this === top) {
        return new AnalyticsChart(options);
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
    var _data_deferred = $.Deferred();
    var _data = null;

    var _properties = {};
    var _create_property = function (key, default_value) {
        _properties[key] = default_value;
        that[key] = function (value) {
            if (arguments.length === 0) {
                return _properties[key];
            }
            _properties[key] = value;
            return that;
        };
    };
    _create_property('independent_format', function(i){ return i.toString(); });
    _create_property('dependent_format', function(d){ return d.toString(); });
    _create_property('independent_label', null);
    _create_property('dependent_label', null);
    _create_property('title', null);
    _create_property('table_row_tmpl', '.table-row-tmpl');

    var _chart_methods = [];
    var _chart_passthru_method = function (method_name) {
        return function (method_args) {
            _chart_methods.push(methodcaller(method_name, method_args));
            return that;
        };
    };
    this.margin = _chart_passthru_method('margin');
    this.width = _chart_passthru_method('width');
    this.height = _chart_passthru_method('height');

    ReactiveSettingsIface.call(this, options['target']);

    var _data_callback = function(data){
        _data = data;
        if (data.length === 0)
            _display_message('No data')
        else if (that.get('display.mode') === 'chart')
            _display_chart();
        else if (that.get('display.mode') === 'table')
            _display_table();
        return that;
    };

    var _display_message = function (msg) {
        $target.find(".message").show().find(".message-text").text(msg);
        $target.find(".analytics-chart").hide();
        $target.find(".loading-container").hide();
    };

    var _display_table = function(){

        var $table = $target.find("table.analytics-table");
        $table.find("tbody").empty();
        _data.forEach(function(pair){
            var $tmpl = null;
            var tmpl_selector = that.table_row_tmpl();
            if (Function.prototype.isPrototypeOf(tmpl_selector) === true)
                $tmpl = tmpl_selector.call($target[0], that);
            else
                $tmpl = $target.find(tmpl_selector);

            var $row = $($tmpl.html());

            var independent_label = that.independent_format().call(null, pair[0]);
            $row.find(".independent")
                .text(independent_label)
                .attr("data-independent", pair[0])
                .attr("data-dependent", pair[1]);

            var dependent_label = that.dependent_format().call(null, pair[1]);
            $row.find(".dependent")
                .text(dependent_label);
            $row.appendTo($target.find("table.analytics-table tbody"));
        });

        var total_row_tmpl = $target.find('.table-total-row-tmpl').html();
        var $total_row = $(total_row_tmpl);
        if ($total_row.length > 0) {
            var total = _data.reduce(function(prev,curr){ return prev + curr[1]; }, 0);
            $total_row.find(".dependent").text(that.dependent_format().call(null, total));
            $total_row.appendTo($target.find("table.analytics-table tbody"));
        }

        $table.find("thead th.independent").text(that.independent_label());
        $table.find("thead th.dependent").text(that.dependent_label());
        $table.find("caption").text(that.title());
        $table.show();
        $target.find(".analytics-chart").hide();
        $target.find(".loading-container").hide();

        $target.find(".independent").click(function(event){
            if (that.get('chart.interval') === 'yearly') {
                that.update({
                    'chart.interval': 'monthly',
                    'year': $(this).attr('data-independent')
                });
                _refresh();
            }
            $target.trigger('dataClick', this);
        });
    };

    var _display_chart = function(){
        var $chart = $target.find(".analytics-chart");

        var chart = (that.get('chart.type') == 'column')
                  ? columnChart().yMin(0)
                  : barChart().xMin(0);

        chart.width(options['width'])
             .height(options['height']);

        chart.xTickFormat((that.get('chart.type') === 'column')
                          ? that.independent_format()
                          : that.dependent_format());

        chart.yTickFormat((that.get('chart.type') === 'column')
                          ? that.dependent_format()
                          : that.independent_format());
        _chart_methods.forEach(function(fn){
            fn.call(null, chart);
        });
        d3.select($chart[0])
          .datum(_data)
          .call(chart);

        $target.find("rect.bar").click(function(event){
            if (that.get('chart.interval') === 'yearly') {
                that.update({
                    'chart.interval': 'monthly',
                    'year': $(this).attr('data-independent')
                });
                _refresh();
            }
            $target.trigger('dataClick', this);
        });

        $target.find("figcaption").text(that.title());
        $target.find("table.analytics-table").hide();
        $target.find(".loading-container").hide();
        $target.find(".analytics-chart").show();
    };

    var _display_loading = function(){
        $target.find(".analytics-table").hide();
        $target.find(".analytics-chart").hide();
        $target.find(".loading-container").show();
    };

    var _refresh = function(){
        _display_loading();

        if (_data_deferred.state() == "pending") {
            _data_deferred.reject();
        }

        _data_deferred = $.Deferred();
        _data_deferred.promise().then(_data_callback);

        opts['data_fn'].call(null, that, function(data){ _data_deferred.resolve(data); });
    };
    this.refresh = _refresh;

    var _show = function(){ _refresh(); $target.show(); return that; };
    this.show = _show;
    var _hide = function(){ $target.hide(); return that; };
    this.hide = _hide;

    this.buttons.click(function(event){
        _refresh();
    });

    return that;
}

