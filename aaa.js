//for this to work, you have to call phantomjs with the cache enabled:
//usage:  phantomjs --disk-cache=true test.js

var page = require('webpage').create();
var fs = require('fs');
var cache = require('./cache');
var mimetype = require('./mimetype');

//this is the path that QTNetwork classes uses for caching files for it's http client
//the path should be the one that has 16 folders labeled 0,1,2,3,...,F
cache.cachePath = '/Users/brandon/Library/Caches/Ofi Labs/PhantomJS/data7/';

var url = 'http://amazon.com';
page.viewportSize = { width: 1300, height: 768 };

//when the resource is received, go ahead and include a reference to it in the cache object
page.onResourceReceived = function(response) {
  //I only cache images, but you can change this
    if(response.contentType.indexOf('image') >= 0)
    {
        cache.includeResource(response);
    }
};

//when the page is done loading, go through each cachedResource and do something with it, 
//I'm just saving them to a file
page.onLoadFinished = function(status) {
    for(index in cache.cachedResources) {
        var file = cache.cachedResources[index].cacheFileNoPath;
        var ext = mimetype.ext[cache.cachedResources[index].mimetype];
        var finalFile = file.replace("."+cache.cacheExtension,"."+ext);
        fs.write('saved/'+finalFile,cache.cachedResources[index].getContents(),'b');
    }
};

page.open(url, function () {
    page.render('saved/amazon.pdf');
    phantom.exit();
});
