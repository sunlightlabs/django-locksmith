(function($){
    $(document).ready(function(){
        Date.prototype.monthNames = [
            "January", "February", "March",
            "April", "May", "June",
            "July", "August", "September",
            "October", "November", "December"
        ];

        Date.prototype.getMonthName = function() {
            return this.monthNames[this.getMonth()];
        };
        Date.prototype.getShortMonthName = function () {
            return this.getMonthName().substr(0, 3);
        };

        var display_leaderboard = function (leaders, target) {
            var $target = $(target);
            var $header= $($("#leaderboard-header-tmpl").html());
            var row_tmpl = $("#leaderboard-row-tmpl").html();

            $target.find("thead").empty().append($header);
            leaders['by_key'].sort(itemcomparer('rank',
                                                function(a,b){ return a - b; }));
            leaders['by_key'] = leaders['by_key'].slice(0, 40);
            leaders['by_key'].forEach(function(leader){
                var $row = $(row_tmpl);
                $row.find(".rank").text(leader['rank']);
                $row.find("a.key").attr("href", "/api/analytics/key/" + leader['key'] + "/")
                                  .text(leader['email']);
                $row.attr("data-key", leader['key']);
                $row.attr("data-rank-diff", leader['rank_diff']);
                if (leader['rank_diff'] == null) {
                    $row.find(".diff").addClass("icon-star");
                } else if (leader['rank_diff'] > 0) {
                    $row.find(".diff").addClass("icon-arrow-down");
                } else if (leader['rank'] - leader['rank_diff'] > 40) {
                    $row.find(".diff").addClass("icon-star");
                } else if (leader['rank_diff'] < 0) {
                    $row.find(".diff").addClass("icon-arrow-up");
                } else if (leader['rank_diff'] == 0) {
                    $row.find(".diff").addClass("icon-minus");
                }
                $target.find("tbody").append($row);
            });

            var d1 = new Date(leaders['earliest_date'].replace('-', '/'));
            var d2 = new Date(leaders['latest_date'].replace('-', '/'));
            $target.find("caption").text(d1.getShortMonthName() + ' ' + d1.getFullYear() + ' - ' + d2.getShortMonthName() + ' ' + d2.getFullYear() );

            $target.find("tr")
            .on('mouseenter', function(event){
                var key_uuid = $(this).attr('data-key');
                $("#leaderboard").find("tr[data-key='" + key_uuid + "']")
                                 .addClass("highlight");
            })
            .on('mouseleave', function(event){
                var key_uuid = $(this).attr('data-key');
                $("#leaderboard").find("tr[data-key='" + key_uuid + "']")
                                 .removeClass("highlight");
            });
        };

        var refresh_qtr_leaderboard = function (year, month, target) {
            var url = '/api/analytics/data/keys/leaderboard/';
            var args = [];
            if (options.api != null)
                args.push(options.api.name);
            args.push(year);
            args.push(month);
            url = url + args.join('/') + '/';

            return $.getJSON(url)
                    .then(function(leaders){
                        display_leaderboard(leaders, target);
                    });
        };

        var refresh_leaderboard = function () {
            var $loading_container = $(".loading-container");
            var $leaderboard_container = $('#leaderboard');
            $loading_container.show();
            $leaderboard_container.hide();

            var latest_qtr_begin = Date.parse(options.latest_qtr_begin);
            latest_qtr_begin.setDate(1);
            var prev_qtr_begin = latest_qtr_begin.clone();
            prev_qtr_begin.setDate(1);
            prev_qtr_begin.addMonths(-3);
            var ancient_qtr_begin = latest_qtr_begin.clone();
            ancient_qtr_begin.setDate(1);
            ancient_qtr_begin.addMonths(-6);

            var latest_qtr_promise = refresh_qtr_leaderboard(latest_qtr_begin.getFullYear(),
                                                             latest_qtr_begin.getMonth() + 1,
                                                             '#latest-quarter');
            var prev_qtr_promise = refresh_qtr_leaderboard(prev_qtr_begin.getFullYear(),
                                                           prev_qtr_begin.getMonth() + 1,
                                                           '#previous-quarter');
            var ancient_qtr_promise = refresh_qtr_leaderboard(ancient_qtr_begin.getFullYear(),
                                                              ancient_qtr_begin.getMonth() + 1,
                                                              '#ancient-quarter');

            $.when(latest_qtr_promise,
                   prev_qtr_promise,
                   ancient_qtr_promise)
             .then(function(){
                 $loading_container.hide();
                 $leaderboard_container.show();
             });
        };
        refresh_leaderboard();
    });
})(jQuery);
