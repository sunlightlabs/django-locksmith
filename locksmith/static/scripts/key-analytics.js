(function($){
    $(document).ready(function(){

        var get_endpoint_calls_data = function (chart, callback) {
            var params = {
            }
            var url = $("link#calls-from-key-by-endpoint").attr("href");
            $.getJSON(url, params)
             .done(function(calls){
                chart.independent_label('Endpoint')
                     .dependent_label('Calls')
                     .title('API Calls by Endpoint')
                     .dependent_format(methodcaller('toLocaleString'))
                     .independent_format(methodcaller('toString'))
                     .height(Math.max(2, calls['by_endpoint'].length) * 30);
                callback(calls['by_endpoint'].map(function(e){
                    return [e['api']['name'] + '.' + e['endpoint'], e['calls']];
                }));
             });
        };

        var get_api_calls_data = function (chart, callback) {
            var params = {
            }
            if (chart.get('chart.interval') === 'yearly') {
                var url = $("link#calls-from-key-yearly").attr("href");
                $.getJSON(url, params)
                 .done(function(calls){
                    chart.independent_label('Year')
                         .dependent_label('Calls')
                         .title('API Calls by Year')
                         .table_row_tmpl('.yearly-table-row-tmpl')
                         .dependent_format(methodcaller('toLocaleString'))
                         .independent_format(methodcaller('toString', 10));
                    callback(calls['yearly'].map(function(yr){
                        return [yr['year'], yr['calls']];
                    }));
                 });
            } else if (chart.get('chart.interval') === 'monthly') {
                var year = chart.get('year');
                params['year'] = year;
                var url = $("link#calls-from-key-monthly").attr("href");
                $.getJSON(url, params)
                 .done(function(calls){
                    chart.independent_label('Month')
                         .dependent_label('Calls')
                         .title('API Calls by Month for ' + year.toString())
                         .table_row_tmpl('.monthly-table-row-tmpl')
                         .independent_format(function(x){ return month_abbrevs[x-1]; })
                         .dependent_format(methodcaller('toLocaleString'));
                    callback(calls['monthly'].map(function(m){
                        return [m['month'], m['calls']];
                    }));
                 });
            }
        };

        var api_calls_chart = new AnalyticsChart({
            'target': '#api-calls-container',
            'data_fn': get_api_calls_data
        })
        .set('chart.type', 'column')
        .set('display.mode', options.api_calls_display)
        .set('chart.interval', options.api_calls_interval)
        .set('year', Date.today().getFullYear())
        .margin({'top': 0, 'bottom': 20, 'left': 90, 'right': 0});

        var endpoint_calls_chart = new AnalyticsChart({
            'target': '#endpoint-calls-container',
            'data_fn': get_endpoint_calls_data
        })
        .set('chart.type', 'bar')
        .set('display.mode', options.endpoint_calls_display || 'chart')
        .set('year', Date.today().getFullYear())
        .margin({'top': 0, 'bottom': 20, 'left': 240, 'right': 0});
        
        var state_anchor_proxy = ReactiveSettingsHistoryIface({
            'compression_vocabulary': ANALYTICS_VOCAB,
            'replace_state': true,
            'settings': {
                'apis': api_calls_chart,
                'endpoints': endpoint_calls_chart
            },
            'post_update': function () {
                api_calls_chart.refresh();
                endpoint_calls_chart.refresh();
            }
        });

        api_calls_chart.show();
        endpoint_calls_chart.show();
    });
})(jQuery);
