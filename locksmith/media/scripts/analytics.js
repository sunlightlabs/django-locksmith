$(document).ready(function(){
    console.log('analytics.js');

    Apis = {};

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

    var display_calls_table = function(){
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
        console.log(changed.setting, 'changed to', changed.value);
        display_calls_table();
    });
    $('#toggle-deprecated-apis').on('setting-changed', function(event, changed){
        console.log(changed.setting, 'changed to', changed.value);
        display_calls_table();
    });

    fetch_api_list()
    .then(function(){
        set_ignore_internal_keys(options.ignore_internal_keys);
        set_ignore_deprecated_apis(options.ignore_deprecated_apis);
    })
    .then(display_calls_table);
});
