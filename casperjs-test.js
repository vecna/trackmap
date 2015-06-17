

var fs = require('fs');

var incremental = [];

var casper = require('casper').create({
    verbose: true,
    logLevel: "debug",
     pageSettings: {
        loadImages:  false,        // The WebPage instance used by Casper will
        loadPlugins: false         // use these settings
    },
    onResourceReceived: managethirdparty
});


casper.start('http://www.repubblica.it', function() {

    first = this.getHTML();
    this.echo(this.getTitle());

    this.scrollTo(500, 300);
    this.scrollToBottom();

    second = this.getHTML();


    casper.page.settings.webSecurityEnabled = false;
    url = 'http://www.repstatic.it/content/nazionale/img/2015/05/19/073133539-87467119-362b-4ad4-ab52-c47d1be833df.jpg';
    x = url.split('/');
    console.log(x.length);
    console.log(x);
    console.log('+ ' + x[x.length -1]);
    this.download(url, 'img.jpg');
    casper.page.settings.webSecurityEnabled = true;

    var html = this.page.evaluate( function() {
        return document.documentElement.outerHTML;
    });

    var links = this.page.evaluate(function() {
        return __utils__.findAll("a[href]");
    });
    this.echo(links);

    fs.write('/tmp/final-rep.html', html, 'w+');
    fs.write('/tmp/getHTML.html', this.getHTML(), 'w+');
    // this.echo(this.status(true));
});

function managethirdparty(ci, obj) {
    // console.log(ci);

    // ci.echo(JSON.stringify(obj, null, "  "));
    incremental.push(ci.getHTML());
    fs.write('/tmp/' + obj.id + '-rep.html', ci.getHTML(), 'w+');
    // ci.echo(incremental.length + ' ' + obj.url);

    var injlinks = ci.page.evaluate(function() {
        return __utils__.findAll("a[href]").length;
    });
    if (injlinks != null ) {
        ci.echo(obj.id + ' #links = ' + injlinks);
    }

    /*
    // with w+ still is in append !?
    console.log('a' + obj);
    ci.echo(obj);
    ci.echo(obj.id);
    ci.echo(obj.stage);
    ci.echo(obj.url);
    ci.echo(obj.headers);
    ci.echo(obj.toString());

    // JSON.stringify(obj);
    // console.log(obj);
    console.log('...');
    */
}

casper.run();
