$(document).ready(function(){
    console.log('analytics.js');

    Apis = {};

    var fetch_api_list = function(){
        return $.getJSON('/analytics/data/apis/')
               .then(function(apis){
                   Apis['list'] = apis;
                   Apis['by_name'] = key_by(Apis.list, itemgetter('name'));
                   Apis['by_id'] = key_by(Apis.list, itemgetter('id'));
               });
    };

    var get_keys_issued = function (chart) {
        var chart_interval = chart.setting('chart.interval');
        if (chart_interval === 'yearly') {
            $.getJSON('/analytics/data/keys/issued/yearly/')
            .then(function(keys_issued){
                chart.setting('title', 'Keys Issued By Year')
                     .setting('independent_format', function(year){ return year.toString(); });
                chart.data(keys_issued['yearly'].map(function(yr){
                    return [yr['year'], yr['issued']];
                }));
            });
        } else if (chart_interval === 'monthly') {
            var url = '/analytics/data/keys/issued/' + chart.setting('year') + '/';
            $.getJSON(url)
            .then(function(keys_issued){
                chart.setting('title', 'Keys Issued by Month for ' + chart.setting('year'))
                     .setting('independent_format', function(x){ return month_abbrevs[x-1]; });
                chart.data(keys_issued['monthly'].map(function(m){
                    return [m['month'], m['issued']];
                }));
            });
        }
    };

    var keys_issued_row_tmpl = function (chart) {
        if (chart.setting('chart.interval') === 'yearly')
            return $(this).find('.yearly-table-row-tmpl');
        else
            return $(this).find('.monthly-table-row-tmpl');
    };

    var get_apis_by_call = function (chart) {
        var params = {
            'ignore_deprecated': options.ignore_deprecated_apis.toString()
        };
        params['ignore_deprecated'] = false;
        var time_period = chart.setting('time.period');
        var title = 'API Calls All Time';
        if (time_period === 'past-30-days') {
            var dt = Date.today().addDays(-30).toString('yyyy-MM-dd');
            params['begin_date'] = dt;
            title = 'API Calls Since ' + dt;
        } else if (time_period === 'year-to-date') {
            var dt = Date.today();
            dt.setMonth(0);
            dt.setDate(1);
            params['begin_date'] = dt.toString('yyyy-MM-dd');
            title = 'API Calls Year to Date: ' + dt.getFullYear();
        }

        $.getJSON('/analytics/data/apis/calls/', params)
        .then(function(calls){
            var apis = $.extend(true, {}, Apis.by_name);

            calls['by_api'].forEach(function(api){
                var name = api['api_name'];
                apis[name]['calls'] = api['calls'];
            });

            var pairs = as_list(apis).map(function(api){
                return [api['name'], api['calls'] || 0];
            });
            pairs.sort(itemcomparer(0, methodcaller('localeCompare')));
            chart.setting('title', title)
                 .data(pairs);
        });
    };

    var localeString = methodcaller('toLocaleString');

    fetch_api_list()
    .then(function(){
        var calls_chart = new AnalyticsColumnChart({
            'target': '#calls',
            'data_fn': get_apis_by_call
        })
        .setting('chart.type', 'bar')
        .setting('display.mode', options.apis_by_call_display || 'chart')
        .setting('time.period', options.apis_by_call_period || 'all-time')
        .setting('dependent_format', localeString)
        .silence(false)
        .show();


        var keys_issued_chart = new AnalyticsColumnChart({
            'target': '#keys',
            'data_fn': get_keys_issued
        })
        .setting('chart.type', 'column')
        .setting('display.mode', options.keys_issued_display || 'chart')
        .setting('chart.interval', options.keys_issued_interval || 'yearly')
        .setting('dependent_format', localeString)
        .setting('table.row.tmpl', keys_issued_row_tmpl)
        .setting('year', Date.today().getFullYear())
        .silence(false)
        .show();

        $('#calls').on('dataClick', function (event, dataElement) {
            var url = '/analytics/new/api/' + $(dataElement).attr('data-independent') + '/';
            window.location.href = url;
        });
    });
});
