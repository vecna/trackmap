var page = require('webpage').create(),
    system = require('system'),
    address;

var fs = require('fs'),
    system = require('system');

if (system.args.length === 1) {
    console.log('Usage: dumper.js <some URL> <a file>');
    phantom.exit(1);
} else {
    address = system.args[1];

    page.onResourceRequested = function (req) {
        // console.log('requested: ' + JSON.stringify(req, undefined, 4));

        try {
            fs.write(system.args[2] + "/__urls", req.url + "\n", 'a+');
        } catch(e) {
            console.log(e);
        }
    };

    page.onResourceReceived = function (res) {

        try {
            fs.write(system.args[2] + "/__responses", JSON.stringify(res, undefined, 4), 'a+');
        } catch(e) {
            console.log(e);
        }
    };

    page.open(address, function (status) {
        if (status !== 'success') {
            console.log('FAIL to load the address');
        }
        phantom.exit();
    });
}

