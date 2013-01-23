$(document).ready(function(){
    console.log('analytics.js');

    Apis = {};

    var keys_issued_chart_monthly_year = Date.today().getFullYear();

    var make_cycle = function (/* arguments */) {
        var values = $.extend(true, [], arguments);
        var ix = values.length - 1;
        return function () {
            ix++;
            if (ix >= values.length)
                ix = 0;
            return values[ix];
        };
    };

    var itemgetter = function (k) {
        return function (o) {
            return o[k];
        };
    };

    var key_by = function (xs, kfn) {
        var keyed = {};
        for (var ix = 0; ix < xs.length; ix++) {
            var x = xs[ix];
            var k = kfn(x);
            keyed[k] = x;
        }
        return keyed;
    };

    var as_list = function (obj) {
        var l = [];
        for (var k in obj) {
            l.push(obj[k]);
        }
        return l;
    };
        
    var fetch_api_list = function(){
        return $.getJSON('/analytics/data/apis/')
               .then(function(apis){
                   Apis['list'] = apis;
                   Apis['by_name'] = key_by(Apis.list, itemgetter('name'));
                   Apis['by_id'] = key_by(Apis.list, itemgetter('id'));
               });
    };

    var fetch_calls_all_time = function(){
        var params = {
            'ignore_deprecated': options.ignore_deprecated_apis.toString()
        };
        return $.getJSON('/analytics/data/apis/calls/', params);
    };

    var fetch_calls_30d = function(){
        var begin_date = new Date();
        begin_date.addDays(-30);
        var params = {
            'begin_date': begin_date.toString('yyyy-MM-dd'),
            'ignore_deprecated': options.ignore_deprecated_apis.toString()
        };
        return $.getJSON('/analytics/data/apis/calls/', params);
    };

    var fetch_keys_issued_all_time = function(){
        return $.getJSON('/analytics/data/keys/issued/');
    };

    var fetch_keys_issued = function (begin_date, end_date) {
        var params = {
            'begin_date': begin_date.toString('yyyy-MM-dd'),
            'end_date': end_date.toString('yyyy-MM-dd')
        };
        return $.getJSON('/analytics/data/keys/issued/', params);
    };

    var display_api_calls_chart = function(){
        if (options.api_calls_display !== 'chart')
            return;

        var apis = $.extend(true, {}, Apis.by_name);
        var totals = {};

        fetch_calls_all_time()
        .then(function(calls){
            calls.by_api.forEach(function(api){
                apis[api.api_name]['calls'] = api.calls;
            })

            var api_list = as_list(apis);
            if (options.ignore_deprecated_apis === true) {
                api_list = api_list.filter(function(api){
                    return api.deprecated === false;
                });
            }

            d3.select("#api-calls-chart")
              .datum(api_list)
              .call(barChart()
                    .width(700)
                    .height(400)
                    .margin({'top': 0, 'right': 0, 'bottom': 20, 'left': 140})
                    .y(function(api){ return api['name']; })
                    .x(function(api){ return api['calls'] || 0; }));

            $("#api-calls-chart rect.bar").click(function(event){
                console.log("TODO: navigate to api page for:", $(this).attr("data-y"));
            });
        });
    };

    var display_api_calls_table = function(){
        if (options.api_calls_display !== 'table')
            return;

        var apis = $.extend(true, {}, Apis.by_name);
        _apis = apis;
        var totals = {};

        fetch_calls_all_time()
        .then(function(calls){
            calls.by_api.forEach(function(api){
                apis[api.api_name]['calls_all_time'] = api.calls;
            });
            totals['calls_all_time'] = calls.calls;
        })
        .then(fetch_calls_30d)
        .then(function(calls){
            calls.by_api.forEach(function(api){
                apis[api.api_name]['calls_30d'] = api.calls;
            });
            totals['calls_30d'] = calls.calls;
        })
        .then(function(){
            $("#calls > table > tbody").empty();
            var api_list = as_list(apis);
            if (options.ignore_deprecated_apis === true) {
                api_list = api_list.filter(function(api){
                    return api.deprecated === false;
                });
            }
            _api_list = api_list;
            var row_class_cycle = make_cycle("even", "odd");
            if (api_list.length % 2 == 1) row_class_cycle();

            api_list.forEach(function(api){
                var $row = $($("#calls-by-api-row-tmpl").html());
                $(".api-name", $row).text(api.name);
                $(".calls-all-time", $row).text(api.calls_all_time);
                $(".calls-30d", $row).text(api.calls_30d);
                $("#calls > table > tbody").append($row);
                $row.addClass(row_class_cycle());
            });

            var $totals_row = $($("#calls-by-api-row-tmpl").html());
            $(".api-name", $totals_row).text("Totals")
            $(".calls-all-time", $totals_row).text(totals['calls_all_time']);
            $(".calls-30d", $totals_row).text(totals['calls_30d']);
            $("#calls > table > tbody").append($totals_row);
            $totals_row.addClass(row_class_cycle());
         });
    };

    var display_keys_issued_table = function(){
        if (options.keys_issued_display !== 'table')
            return;

        fetch_keys_issued_all_time()
        .then(function(keys_issued){
            $("#keys-issued-table #keys-issued-all-time").text(keys_issued['issued'].toString());
        })
        .then(function(){
            var begin_date = new Date();
            begin_date.addDays(-30);
            return fetch_keys_issued(begin_date, Date.today());
        })
        .then(function(keys_issued){
            $("#keys-issued-30d").text(keys_issued['issued'].toString());
            $("#keys-issued-table").show();
        })
        .then(function(){
            var begin_date = Date.today();
            begin_date.setMonth(0); // 0 = Jan
            begin_date.setDate(1);
            return fetch_keys_issued(begin_date, Date.today());
        })
        .then(function(keys_issued){
            $("#keys-issued-ytd").text(keys_issued['issued'].toString());
        });
    };

    var display_keys_issued_chart = function(){
        if (options.keys_issued_display !== 'chart')
            return;

        if (options.keys_issued_interval === 'yearly')
            display_yearly_keys_issued_chart();
        else if (options.keys_issued_interval === 'monthly')
            display_monthly_keys_issued_chart(keys_issued_chart_monthly_year);
        else
            console.log('No such interval for keys issued:', interval);
    };

    var display_monthly_keys_issued_chart = function (year) {
        var url = '/analytics/data/keys/issued/__year__/'.replace('__year__', year);
        d3.json(url, function(error, keys_issued){
            _keys_issued = keys_issued;
            if (error) { console.log(error); return; }

            var month_abbrevs = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
           
            d3.select("#keys-issued-chart")
              .datum(keys_issued['monthly'])
              .call(columnChart()
                    .width(700)
                    .height(400)
                    .yMin(0)
                    .x(itemgetter('month'))
                    .y(itemgetter('issued'))
                    .xTickFormat(function(x){ return month_abbrevs[x - 1];  }));

            set_keys_issued_interval('monthly');
            $("#keys-issued-chart figcaption").text("Number of API Keys Issued by Month in " + year.toString());
            keys_issued_chart_monthly_year = year;
        });
    };

    var display_yearly_keys_issued_chart = function(){
        d3.json('/analytics/data/keys/issued/yearly/', function(error, keys_issued){
            if (error) { console.log(error); return; }

            d3.select("#keys-issued-chart")
              .datum(keys_issued['yearly'])
              .call(columnChart()
                    .width(700)
                    .height(400)
                    .yMin(0)
                    .x(itemgetter('year'))
                    .y(itemgetter('issued')));

            $("#keys-issued-chart rect.bar").click(function(event){
                if (options.keys_issued_interval === 'yearly') {
                    display_monthly_keys_issued_chart($(this).attr("data-x"));
                }
            });

            $("#keys-issued-chart figcaption").text("Number of API Keys Issued by Year");
        });
    };

    var set_ignore_internal_keys = function (flag) {
        if (flag === true) {
            options.ignore_internal_keys = true;
            $('#toggle-internal-keys').addClass('active');
            $('#toggle-internal-keys').text("Ignored");
        } else {
            options.ignore_internal_keys = false;
            $('#toggle-internal-keys').removeClass('active');
            $('#toggle-internal-keys').text("Included");
        }
    };

    var set_ignore_deprecated_apis = function (flag) {
        if (flag === true) {
            options.ignore_deprecated_apis = true;
            $('#toggle-deprecated-apis').addClass('active');
            $('#toggle-deprecated-apis').text("Ignored");
        } else {
            options.ignore_deprecated_apis = false;
            $('#toggle-deprecated-apis').removeClass('active');
            $('#toggle-deprecated-apis').text("Included");
        }
    };

    var set_api_calls_display_mode = function (mode) {
        if ((mode === 'table') || (mode == 'chart')) {
            options.api_calls_display = mode;

            if (mode === 'table') {
                $("#api-calls-display-table").addClass("active");
                $("#api-calls-display-chart").removeClass("active");
                $("#api-calls-chart").hide();
                $("#api-calls-table").show();
            } else {
                $("#api-calls-display-chart").addClass("active");
                $("#api-calls-display-table").removeClass("active");
                $("#api-calls-table").hide();
                $("#api-calls-chart").show();
            }
        } else {
            console.log('No such display mode for keys issued.');
        }
    };

    var set_keys_issued_display_mode = function (mode) {
        if ((mode === 'table') || (mode == 'chart')) {
            options.keys_issued_display = mode;

            $("#keys-issued-display-mode .btn").removeClass("active");
            var $chart_options = $("#keys-issued-chart-interval, #keys-issued-chart-cumulative");
            if (mode === 'table') {
                $("#keys-issued-display-table").addClass("active");
                $("#keys-issued-chart").hide();
                $("#keys-issued-table").show();
                $chart_options.hide();
            } else {
                $("#keys-issued-display-chart").addClass("active");
                $chart_options.show();
                $("#keys-issued-table").hide();
                $("#keys-issued-chart").show();
                if ($("#keys-issued-chart").is(":empty") === true) {
                    display_keys_issued_chart();
                }
            }
        } else {
            console.log('No such display mode for keys issued.');
        }
    };

    var set_keys_issued_interval = function (interval) {
        if ((interval === 'yearly') || (interval === 'monthly')) {
            options.keys_issued_interval = interval;

            $("#keys-issued-chart-interval .btn").removeClass("active");
            if (interval === 'yearly') {
                $("#keys-issued-interval-yearly").addClass("active");
            } else {
                $("#keys-issued-interval-monthly").addClass("active");
            }
        } else {
            console.log('No such interval for keys issued:', interval);
        }
    };

    var toggle_ignore_internal_keys = function () {
        set_ignore_internal_keys(!options.ignore_internal_keys);
        $('#toggle-internal-keys').trigger('setting-changed',
                                           {setting: 'ignore_internal_keys',
                                            value: options.ignore_internal_keys});
    };

    var toggle_ignore_deprecated_apis = function () {
        set_ignore_deprecated_apis(!options.ignore_deprecated_apis);
        $('#toggle-deprecated-apis').trigger('setting-changed',
                                           {setting: 'ignore_deprecated_apis',
                                            value: options.ignore_deprecated_apis});
    };

    $('#toggle-internal-keys').click(toggle_ignore_internal_keys);
    $('#toggle-deprecated-apis').click(toggle_ignore_deprecated_apis);

    $('#toggle-internal-keys').on('setting-changed', function(event, changed){
        display_api_calls_table();
        display_api_calls_chart();
    });
    $('#toggle-deprecated-apis').on('setting-changed', function(event, changed){
        display_api_calls_table();
        display_api_calls_chart();
    });
   
    $("#keys-issued-display-table").on('click', function(event){
        set_keys_issued_display_mode('table');
    });
    $("#keys-issued-display-chart").on('click', function(event){
        set_keys_issued_display_mode('chart');
    });

    $("#keys-issued-interval-yearly").on('click', function(event){
        set_keys_issued_interval('yearly');
        display_keys_issued_chart();
    });
    $("#keys-issued-interval-monthly").on('click', function(event){
        set_keys_issued_interval('monthly');
        display_keys_issued_chart();
    });

    $("#api-calls-display-table").click(function(event){
        set_api_calls_display_mode('table');
        display_api_calls_table();
    });
    $("#api-calls-display-chart").click(function(event){
        set_api_calls_display_mode('chart');
        display_api_calls_chart();
    });

    fetch_api_list()
    .then(function(){
        set_ignore_internal_keys(options.ignore_internal_keys);
        set_ignore_deprecated_apis(options.ignore_deprecated_apis);
        set_api_calls_display_mode(options.api_calls_display);
        set_keys_issued_display_mode(options.keys_issued_display);
        set_keys_issued_interval(options.keys_issued_interval);
    })
    .then(display_api_calls_table)
    .then(display_api_calls_chart)
    .then(display_keys_issued_table)
    .then(display_keys_issued_chart);
});
