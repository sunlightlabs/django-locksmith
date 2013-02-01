(function($){
    $(document).ready(function(){

        var get_endpoint_calls_data = function (chart) {
            var params = {
            }
            $.getJSON('/analytics/data/key/' + options.key + '/calls/endpoint/', params)
             .done(function(calls){
                chart.setting('independent_label', 'Endpoint')
                     .setting('dependent_label', 'Calls')
                     .setting('title', 'API Calls By Endpoint')
                     .setting('dependent_format', function(x){ return x.toLocaleString(); })
                     .setting('independent_format', function(y){ return y.toString(); })
                     .height(calls['by_endpoint'].length * 30);
                chart.data(calls['by_endpoint'].map(function(e){
                    return [e['api']['name'] + '.' + e['endpoint'], e['calls']];
                }));
             });
        };

        var api_calls_table_row_tmpl = function (chart) {
            if (chart.setting('chart.interval') === 'yearly')
                return $(this).find('.yearly-table-row-tmpl');
            else
                return $(this).find('.monthly-table-row-tmpl');
        };

        var get_api_calls_data = function (chart) {
            var params = {
            }
            if (chart.setting('chart.interval') === 'yearly') {
                $.getJSON('/analytics/data/key/' + options.key + '/calls/yearly/', params)
                 .done(function(calls){
                    chart.setting('independent_label', 'Year')
                         .setting('dependent_label', 'Calls')
                         .setting('title', 'API Calls By Year')
                         .setting('dependent_format', function(y){ return y.toLocaleString(); })
                         .setting('independent_format', function(x){ return x.toString(); });
                    chart.data(calls['yearly'].map(function(yr){
                        return [yr['year'], yr['calls']];
                    }));
                 });
            } else if (chart.setting('chart.interval') === 'monthly') {
                var year = chart.setting('year');
                $.getJSON('/analytics/data/key/' + options.key + '/calls/' + year + '/', params)
                 .done(function(calls){
                    chart.silence(true)
                         .setting('independent_label', 'Month')
                         .setting('dependent_label', 'Calls')
                         .setting('title', 'API Calls By Month for ' + year.toString())
                         .setting('independent_format', function(x){ return month_abbrevs[x-1]; })
                         .setting('dependent_format', function(y){ return y.toLocaleString(); })
                         .silence(false);
                    chart.data(calls['monthly'].map(function(m){
                        return [m['month'], m['calls']];
                    }));
                 });
            }
        };

        var api_calls_chart = new AnalyticsChart({
            'target': '#api-calls-container',
            'data_fn': get_api_calls_data
        })
        .setting('table.row.tmpl', api_calls_table_row_tmpl)
        .setting('chart.type', 'column')
        .setting('display.mode', options.api_calls_display)
        .setting('chart.interval', options.api_calls_interval)
        .setting('year', Date.today().getFullYear())
        .margin({'top': 0, 'bottom': 20, 'left': 90, 'right': 0})
        .silence(false)
        .show();

        var endpoint_calls_chart = new AnalyticsChart({
            'target': '#endpoint-calls-container',
            'data_fn': get_endpoint_calls_data
        })
        .setting('chart.type', 'bar')
        .setting('display.mode', options.endpoint_calls_display || 'chart')
        .setting('year', Date.today().getFullYear())
        .margin({'top': 0, 'bottom': 20, 'left': 200, 'right': 0})
        .silence(false)
        .show();
        
    });
})(jQuery);
