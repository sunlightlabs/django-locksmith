
    var month_abbrevs = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

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

    var itemcomparer = function (k, f) {
        return function (a, b) {
            return f(a[k], b[k]);
        };
    };

    var methodcaller = function (method_name) {
        var method_args = Array.prototype.slice.call(arguments, 1);
        return function (/* arguments: thisarg, ...args */) {
            if (arguments.length === 0)
                throw 'methodcaller("' + method_name + '") requires a thisarg';
            var thisarg = arguments[0];
            var method = thisarg[method_name];
            if (method === undefined)
                throw 'object of type ' + (typeof thisarg) + ' has no method ' + method_name;
            var ext_method_args = $.extend(true, [], method_args);
            ext_method_args = ext_method_args.concat(Array.prototype.slice.call(arguments, 1));
            if (ext_method_args.length === 0) {
                return method.call(thisarg);
            } else {
                return method.apply(thisarg, ext_method_args);
            }
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

    var pairs = function (obj) {
        var l = [];
        for (var k in obj) {
            l.push([k, obj[k]]);
        }
        return l;
    };

    var keys = function (obj) {
        var l = [];
        for (var k in obj) {
            l.push(k);
        }
        return l;
    };

    var unicode_to_base64 = function (u) {
        return window.btoa(unescape(encodeURIComponent(u)));
    };

    var base64_to_unicode = function (b) {
        try {
            return decodeURIComponent(escape(window.atob(b)));
        } catch (e) {
            throw e;
        }
    };

    var parse_query_params = function (a) {
        if (a == "") return {};
        a = a.split("&");
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    };

    var ANALYTICS_VOCAB = [
        ['page', 'P'],
        ['calls', 'C'],
        ['keys', 'K'],
        ['all_calls', 'AC'],

        ['included', 'I'],
        ['excluded', 'E'],
        ['all-time', 'A'],
        ['year-to-date', 'Y'],
        ['past-30-days', 'M'],
        ['yearly', 'y'],
        ['monthly', 'm'],
        ['chart', 'c'],
        ['table', 't'],
        ['column', 'v'],
        ['bar', 'n'],

        ['chart.type', 'ct'],
        ['chart.interval', 'ci'],
        ['deprecated.apis', 'da'],
        ['display.mode', 'dm'],
        ['internal.keys', 'ik'],
        ['time.period', 'tp'],

        ['apis', 'a'],
        ['endpoints', 'e'],

        ['year', 'yr']
    ];

    var vocab_translate = function (v, vocab) {
        for (var ix = 0; ix < vocab.length; ix++) {
            if (v === vocab[ix][0]) {
                return vocab[ix][1];
            } else if (v === vocab[ix][1]) {
                return vocab[ix][0];
            }
        }
        return v;
    };

    var vocab_translate_object = function (obj, vocab) {
        var d = {};
        for (var k in obj) {
            var v = obj[k];
            var tk = vocab_translate(k, vocab);
            if (typeof v === 'object') {
                d[tk] = vocab_translate_object(v, vocab);
            } else {
                d[tk] = vocab_translate(v, vocab);
            }
        }
        return d;
    };

    // Based on: http://bl.ocks.org/3766585
    var intcomma = function(value) {
        // inspired by django.contrib.humanize.intcomma
        var origValue = String(value);
        var newValue = origValue.replace(/^(-?\d+)(\d{3})/, '$1,$2');
        if (origValue == newValue){
            return newValue;
        } else {
            return intcomma(newValue);
        }
    };

