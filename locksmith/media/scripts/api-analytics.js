$(document).ready(function(){
    var display_api_callers_table = function(){
        var params = {
            'ignore_internal_keys': options.ignore_internal_keys,
            'top': 100,
        }

        var deferred = 
        $.getJSON('/api/analytics/data/api/' + options.api.name + '/callers/', params)
        .then(function(response){
            $("#users table").dataTable({
                'bLengthChange': false,
                'bSort': true,
                'aaData': response['callers'].map(function(c){
                              return ['<a href="/api/analytics/key/' + c.key + '">' + c.email + '</a>', c.key, c.calls];
                          }),
                'asSorting': false,
                'aaSorting': [[2, 'desc']]
            });

        });

        return deferred;
    };


    var get_endpoint_calls_data = function (chart, callback) {
        var params = {
            'ignore_internal_keys': options.ignore_internal_keys
        }
        $.getJSON('/api/analytics/data/api/' + options.api.name + '/calls/endpoint/', params)
         .done(function(calls){
            chart.independent_label('Endpoint')
                 .dependent_label('Calls')
                 .title('API Calls By Endpoint')
                 .dependent_format(function(x){ return x.toLocaleString(); })
                 .independent_format(function(y){ return y.toString(); })
                 .height(calls['by_endpoint'].length * 30);
            callback(calls['by_endpoint'].map(function(e){
                return [e['endpoint'], e['calls']];
            }));
         });
    };

    var get_api_calls_data = function (chart, callback) {
        var params = {
            'ignore_internal_keys': options.ignore_internal_keys
        }
        if (chart.setting('chart.interval') === 'yearly') {
            $.getJSON('/api/analytics/data/api/' + options.api.name + '/calls/yearly/', params)
             .done(function(calls){
                chart.independent_label('Year')
                     .dependent_label('Calls')
                     .title('API Calls By Year')
                     .table_row_tmpl('.yearly-table-row-tmpl')
                     .independent_format(methodcaller('toString', 10))
                     .dependent_format(methodcaller('toLocaleString'));
                callback(calls['yearly'].map(function(yr){
                    return [yr['year'], yr['calls']];
                }));
             });
        } else if (chart.setting('chart.interval') === 'monthly') {
            var year = chart.setting('year');
            $.getJSON('/api/analytics/data/api/' + options.api.name + '/calls/' + year + '/', params)
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
    .margin({'top': 0, 'bottom': 20, 'left': 200, 'right': 0});

    var state_anchor_proxy = ReactiveSettingsHistoryIface({
        'compression_vocabulary': ANALYTICS_VOCAB,
        'settings': {
            'calls': api_calls_chart,
            'endpoints': endpoint_calls_chart
        }
    });
    $(state_anchor_proxy).on('settings-updated', function(event, settings_iface, setting, value){
        if (settings_iface.refresh) {
            console.log("Refreshing", settings_iface.target().attr('id'), setting, value);
            settings_iface.refresh();
        } else {
            console.log("Skipping refresh for", settings_iface.target().attr('id'));
        }
    });

    api_calls_chart.show();
    endpoint_calls_chart.show();
    display_api_callers_table();
});
