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
    iodetails = [],
    counter = 0,
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

page.onResourceRequested = function(request) {
    iodetails.push(
        { 'Request' : request, 'When': counter }
    );
};
page.onResourceReceived = function(response) {
    iodetails.push(
        { 'Response' : response, 'When': counter }
    );
};

page.onResourceTimeout = function(e) {
    console.log("ResourceTimeout!" + e.url);
    try {
        // the url whose request timed out
        fs.write(system.args[2] + "/__failures", e.url + "\n", 'a+');
    } catch(e) {
       // console.log(e);
    }
};

setTimeout(function() {

    fs.write(system.args[2] + "/__responses", JSON.stringify(iodetails, undefined, 4), 'w+');

    iodetails.forEach(function (content) {

        if (content.Response && content.Response.url) {

            if ( content.Response.url.length > 2000) {
                truncated_url = content.Response.url.substr(0, 2000);
            } else {
                truncated_url = content.Response.url;
            }

            fs.write(system.args[2] +  "/__urls", truncated_url + "\n", 'a+');
        }
    });
    phantom.exit();
}, 58 * 1000);

/* every second, increase the 'var counter', to keep track when the answer arrive */
function set_single_second_counter() {

    setTimeout(function() {
        counter += 1;
    }, 1000);
}


page.settings.resourceTimeout = 20000; // express in milliseconds, 40 sec
page.open(address);


