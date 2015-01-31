// This is my first test in phantomjs, I'm thinking that is better
// move in node.js + jsdom to render javascript, I need also to
// dump the content of the HTML+JS+CSS in a file, if you've
// a better approach, open a github issue: THANKS!
//
// plus, I'm evaluating python-selenium instead calling subprocess
// here, but I need something stable to be deploy in box beside 
// linux, and so... the best solution still has to be found.

var page = require('webpage').create(),
    system = require('system'),
    fs = require('fs'),
    landing_title,
    address;


if (system.args.length === 1) {
    console.log('Usage: collect_included_url.js <some URL> <a directory>');
    phantom.exit(1);
}

address = system.args[1];


page.onResourceError = function(resourceError) {
    page.reason = resourceError.errorString;
    page.reason_url = resourceError.url;
};

page.onResourceRequested = function (req) {
    // console.log('requested: ' + JSON.stringify(req, undefined, 4));

    try {
        fs.write(system.args[2] + "/__urls", req.url + "\n", 'a+');
    } catch(e) {
        // console.log(e);
    }
};

page.onResourceReceived = function (res) {

    try {
        fs.write(system.args[2] + "/__responses", JSON.stringify(res, undefined, 4), 'a+');
    } catch(e) {
       // console.log(e);
    }
};

page.settings.resourceTimeout = 29000; // express in milliseconds, 29 sec
page.onResourceTimeout = function(e) {
    // it'll probably be 'Network timeout on resource'
    // console.log(e.errorCode + " " + e.errorString + " " + e.url);
    try {
        // the url whose request timed out
        fs.write(system.args[2] + "/__failures", e.url + "\n", 'a+');
    } catch(e) {
       // console.log(e);
    }
    // phantom.exit(1);
};

page.open(address, function (status) {
    if (status !== 'success') {
        // console.log('FAIL to load the address', address);
        // console.log(status);
        // console.log(page.reason);
        // console.log(page.reason_url);
    } else {
        landing_title =  page.evaluate(function () {
            return document.title;
        });
        // console.log(address + ' => ' + landing_title);
        fs.write(system.args[2] + "/__title", landing_title, 'w+');

        var objects_e = page.evaluate(function() {
            return document.getElementsByTagName('object');
        });

        // console.log("Final page loaded #" + objects_e.length + " <object> elements");

        for (var i = 0; i < objects_e.length; i++) {
            if (objects_e[i] != null) {
                fs.write(system.args[2] + "/__object_" + i, objects_e[i].outerHTML, 'w+');
            }
            else {

                // console.log("[!!!] dumping " + system.args[2] + "/__debug.body");
                fs.write(system.args[2] + "/__debug.body", 
                    page.evaluate(function() {
                        return document.getElementsByTagName('body')[0].outerHTML;
                    }), 'w+');
            }
            // console.log(objects_e[i].outerHTML);
        }
    }
    phantom.exit();
    fs.remove(system.args[2] + "/lock");
});

