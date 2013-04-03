$(document).ready(function(){
    Apis = {};

    var fetch_api_list = function(){
        var url = $("link#api-list").attr("href");
        return $.getJSON(url)
               .then(function(apis){
                   Apis['list'] = apis;
                   Apis['by_name'] = key_by(Apis.list, itemgetter('name'));
                   Apis['by_id'] = key_by(Apis.list, itemgetter('id'));
               });
    };

    var page_settings = new ReactiveSettingsIface('#page-settings')
                            .set('deprecated.apis', 'excluded')
                            .set('internal.keys', 'excluded');

    var get_keys_issued = function (chart, callback) {
        console.log('Fetching keys_issued data');
        var chart_interval = chart.get('chart.interval');
        var params = {
            'ignore_internal_keys': (page_settings.get('internal.keys') === 'excluded')
        }
        if (chart_interval === 'yearly') {
            var url = $("link#keys-issued-yearly").attr("href");
            $.getJSON(url, params)
            .then(function(keys_issued){
                console.log('Recieved keys_issued data');
                chart.title('Keys Issued By Year')
                     .independent_format(methodcaller('toString', 10))
                     .table_row_tmpl('.yearly-table-row-tmpl');
                callback(keys_issued['yearly'].map(function(yr){
                    return [yr['year'], yr['issued']];
                }));
            });
        } else if (chart_interval === 'monthly') {
            var url = $("link#keys-issued-monthly").attr("href");
            params['year'] = chart.get('year');
            $.getJSON(url, params)
            .then(function(keys_issued){
                console.log('Recieved keys_issued data');
                chart.title('Keys Issued by Month for ' + chart.set('year'))
                     .independent_format(function(x){ return month_abbrevs[x-1]; })
                     .table_row_tmpl('.monthly-table-row-tmpl');
                callback(keys_issued['monthly'].map(function(m){
                    return [m['month'], m['issued']];
                }));
            });
        }
    };

    var get_apis_by_call = function (chart, callback) {
        var params = {
            'ignore_deprecated': (page_settings.get('deprecated.apis') === 'excluded'),
            'ignore_internal_keys': (page_settings.get('internal.keys') === 'excluded')
        };
        var time_period = chart.get('time.period');
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

        var url = $("link#apis-by-calls").attr("href");
        $.getJSON(url, params)
        .then(function(calls){
            var apis = $.extend(true, {}, Apis.by_name);

            calls['by_api'].forEach(function(api){
                var name = api['api_name'];
                apis[name]['calls'] = api['calls'];
            });

            apis = as_list(apis);
            if (page_settings.get('deprecated.apis') === 'excluded') {
                apis = apis.filter(function(api){
                    return api.deprecated === false;
                });
            }
            var pairs = apis.map(function(api){
                            return [api['name'], api['calls'] || 0];
                        });
            pairs.sort(itemcomparer(0, methodcaller('localeCompare')));
            chart.title(title)
                 .dependent_format(methodcaller('toLocaleString'));
            callback(pairs);
        });
    };

    fetch_api_list()
    .then(function(){
        var calls_chart = new AnalyticsChart({
            'target': '#calls',
            'data_fn': get_apis_by_call
        })
        .set('chart.type', 'bar')
        .set('display.mode', options.apis_by_call_display || 'chart')
        .set('time.period', options.apis_by_call_period || 'all-time')
        .margin({'top': 0, 'bottom': 20, 'left': 110, 'right': 0});


        var keys_issued_chart = new AnalyticsChart({
            'target': '#keys',
            'data_fn': get_keys_issued
        })
        .update({
            'chart.type': 'column',
            'display.mode': options.keys_issued_display || 'chart',
            'chart.interval': options.keys_issued_interval || 'yearly'
        })
        .set('year', Date.today().getFullYear())
        .margin({'top': 0, 'bottom': 20, 'left': 80, 'right': 0});

        $('#calls').on('dataClick', function (event, dataElement) {
            var url = '/api/analytics/api/' + $(dataElement).attr('data-independent') + '/';
            window.location.href = url;
        });

        page_settings.buttons.click(function(event){
            calls_chart.refresh();
            keys_issued_chart.refresh();
        });

        var state_anchor_proxy = ReactiveSettingsHistoryIface({
            'compression_vocabulary': ANALYTICS_VOCAB,
            'replace_state': true,
            'settings': {
                'page': page_settings,
                'calls': calls_chart,
                'keys': keys_issued_chart
            },
            'post_update': function () {
                calls_chart.refresh();
                keys_issued_chart.refresh();
            }
        });

        calls_chart.show();
        keys_issued_chart.show();
    });
});
