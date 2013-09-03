$(document).ready(function(){
    var display_api_callers_table = function(){
        var params = {
            'ignore_internal_keys': options.ignore_internal_keys,
            'top': 100,
        }

        var url = $("link#callers-of-api").attr("href");
        var deferred = 
        $.getJSON(url, params)
        .then(function(response){
            $("#users table").dataTable({
                'bLengthChange': false,
                'bSort': true,
                'aaData': response['callers'].map(function(c){
                              return ['<a href="' + c.profile_url + '">' + c.email + '</a>', c.key, c.calls];
                          }),
                'asSorting': false,
                'aaSorting': [[2, 'desc']],
                'fnInitComplete': function(osettings, json){
                    $('#key-list_filter').prepend('<h3>Top 100 Users of the API</h3>')
                    var input = $('#key-list_filter').find('input').attr('placeholder', "search users").clone(true);
                    $('#key-list_filter > label').remove()
                    $('#key-list_filter').append(input);
                }
            });

        });

        return deferred;
    };


    var get_endpoint_calls_data = function (chart, callback) {
        var params = {
            'ignore_internal_keys': options.ignore_internal_keys
        }
        var url = $("link#calls-to-api-by-endpoint").attr("href");
        $.getJSON(url, params)
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
        if (chart.get('chart.interval') === 'yearly') {
            var url = $("link#calls-to-api-yearly").attr("href");
            $.getJSON(url, params)
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
        } else if (chart.get('chart.interval') === 'monthly') {
            var year = chart.get('year');
            params['year'] = year;
            var url = $("link#calls-to-api-monthly").attr("href");
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
        }else if (chart.get('chart.interval') === 'daily') {
            var today = new Date();
            params['end_date'] = today.toString('MM-dd-yyyy');
            var url = $("link#calls-to-api-daily").attr("href");
            $.getJSON(url, params)
             .done(function(calls){
                chart.independent_label('Day')
                     .dependent_label('Calls')
                     .title('API Calls by Day for the Week Ending on ' + params['end_date'])
                     .table_row_tmpl('.daily-table-row-tmpl')
                     .independent_format(function(x){ return x })
                     .dependent_format(methodcaller('toLocaleString'));
                callback(calls['daily'].map(function(m){
                    return [m['date'], m['calls']];
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
        'replace_state': true,
        'settings': {
            'calls': api_calls_chart,
            'endpoints': endpoint_calls_chart
        },
        'post_update': function (state) {
            api_calls_chart.refresh();
            endpoint_calls_chart.refresh();
        }
    });

    api_calls_chart.show();
    endpoint_calls_chart.show();
    display_api_callers_table();
});
