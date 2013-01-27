
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
        return function (/* arguments: thisarg, ...args */) {
            if (arguments.length === 0)
                throw 'methodcaller("' + method_name + '") requires a thisarg';
            var thisarg = arguments[0];
            var method = thisarg[method_name];
            if (method === undefined)
                throw 'object of type ' + (typeof thisarg) + ' has no method ' + method_name;
            if (arguments.length === 1) {
                return method.call(thisarg);
            } else {
                return method.apply(thisarg, Array.prototype.slice.call(arguments, 1));
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

