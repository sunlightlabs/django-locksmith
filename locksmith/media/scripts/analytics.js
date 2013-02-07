$(document).ready(function(){
    Apis = {};

    var fetch_api_list = function(){
        return $.getJSON('/analytics/data/apis/')
               .then(function(apis){
                   Apis['list'] = apis;
                   Apis['by_name'] = key_by(Apis.list, itemgetter('name'));
                   Apis['by_id'] = key_by(Apis.list, itemgetter('id'));
               });
    };

    var page_settings = new ReactiveSettingsIface('#page-settings')
                            .setting('deprecated.apis', 'excluded')
                            .setting('internal.keys', 'excluded')
                            .silence(false);

    var get_keys_issued = function (chart) {
        console.log('Fetching keys_issued data');
        var chart_interval = chart.setting('chart.interval');
        var params = {
            'ignore_internal_keys': (page_settings.get('internal.keys') === 'excluded')
        }
        if (chart_interval === 'yearly') {
            $.getJSON('/analytics/data/keys/issued/yearly/', params)
            .then(function(keys_issued){
                console.log('Recieved keys_issued data');
                chart.setting('title', 'Keys Issued By Year')
                     .setting('independent_format', function(year){ return year.toString(); });
                chart.data(keys_issued['yearly'].map(function(yr){
                    return [yr['year'], yr['issued']];
                }));
            });
        } else if (chart_interval === 'monthly') {
            var url = '/analytics/data/keys/issued/' + chart.setting('year') + '/';
            $.getJSON(url, params)
            .then(function(keys_issued){
                console.log('Recieved keys_issued data');
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
            'ignore_deprecated': (page_settings.get('deprecated.apis') === 'excluded'),
            'ignore_internal_keys': (page_settings.get('internal.keys') === 'excluded')
        };
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
            chart.setting('title', title)
                 .data(pairs);
        });
    };

    var localeString = methodcaller('toLocaleString');

    fetch_api_list()
    .then(function(){
        calls_chart = new AnalyticsChart({
            'target': '#calls',
            'data_fn': get_apis_by_call
        })
        .setting('chart.type', 'bar')
        .setting('display.mode', options.apis_by_call_display || 'chart')
        .setting('time.period', options.apis_by_call_period || 'all-time')
        .setting('dependent_format', localeString)
        .margin({'top': 0, 'bottom': 20, 'left': 110, 'right': 0})
        .silence(false);
        //.show();


        keys_issued_chart = new AnalyticsChart({
            'target': '#keys',
            'data_fn': get_keys_issued
        })
        .update({
            'chart.type': 'column',
            'display.mode': options.keys_issued_display || 'chart',
            'chart.interval': options.keys_issued_interval || 'yearly'
        })
        .setting('dependent_format', localeString)
        .setting('table.row.tmpl', keys_issued_row_tmpl)
        .setting('year', Date.today().getFullYear())
        .margin({'top': 0, 'bottom': 20, 'left': 80, 'right': 0})
        .silence(false);
        //.show();

        $('#calls').on('dataClick', function (event, dataElement) {
            var url = '/analytics/api/' + $(dataElement).attr('data-independent') + '/';
            window.location.href = url;
        });

        page_settings.buttons.click(function(event){
            calls_chart.refresh();
            keys_issued_chart.refresh();
        });

        var decode_state_anchor = function (anchor) {
            decodedsettings = JSON.parse(base64_to_unicode(anchor));
            console.log(JSON.stringify(decodedsettings));
            decodedsettings = vocab_translate_object(decodedsettings, ANALYTICS_VOCAB);
            console.log(JSON.stringify(decodedsettings));

            if (decodedsettings['page'] != null) {
                page_settings.update(decodedsettings['page']);
            }
            if (decodedsettings['calls'] != null) {
                calls_chart.update(decodedsettings['calls']).refresh();
            }
            if (decodedsettings['keys'] != null) {
                keys_issued_chart.update(decodedsettings['keys']).refresh();
            }
        };

        var encode_state_anchor = function (obj) {
            compressed = vocab_translate_object(obj, ANALYTICS_VOCAB);
            console.log(JSON.stringify(compressed));
            return unicode_to_base64(JSON.stringify(compressed));
        };

        var merge_settings = function () {
            return {
                'page': page_settings.settings_with_buttons(),
                'calls': calls_chart.settings_with_buttons(),
                'keys': keys_issued_chart.settings_with_buttons()
            };
        };

        var update_state_anchor = function(event, setting, value){
            console.log(event, setting, value);
            var merged = merge_settings();
            var encoded = encode_state_anchor(merged);
            var url = window.location.protocol + '//' + window.location.host + window.location.pathname +  window.location.search + '#' + encoded;
            history.pushState(encoded, null, url);
        };

        window.addEventListener('popstate', function(event){
            if (event.state !== null) {
                decode_state_anchor(event.state);
            }
        });

        $("#page-settings").on('setting-changed', update_state_anchor);
        $("#calls").on('setting-changed', update_state_anchor);
        $("#keys").on('setting-changed', update_state_anchor);

        if (window.location.hash.length > 0) {
            console.log('Decoding', window.location.hash);
            decode_state_anchor(window.location.hash.slice(1));
        } else {
            console.log('No URL hash, using default settings.');
            calls_chart.show();
            keys_issued_chart.show();
        }
        var merged = merge_settings();
        var encoded = encode_state_anchor(merged);
        history.replaceState(encoded, null, window.location.href);
    });
});
