#!/usr/bin/python

import os
from hashlib import sha1
from random import random



first_section=\
"""
<html>

<head>
    <title>Just the test</title>
    <script type="application/javascript" src="bower_components/jquery-2.1.0.min/index.js"></script>

    <script type="application/javascript">

        function goblog(elem) {
            $('.stigma').remove();
            $(elem).appendTo("#blogList");
        }

        function golocal(elem) {
            $('.stigma').remove();
            $(elem).appendTo("#localList");
        }

        function gonational(elem) {
            $('.stigma').remove();
            $(elem).appendTo("#nationalList");
        }

        function removebutton() {
            $('.clickable').hide();
        }

        function showbutton() {
            $('.clickable').show();
        }

        function openiframe(elem, url) {
            $('<br>').appendTo(elem);
            $('<iframe />', {
                'src' :url,
                'width': "80%",
                'height': "40%",
                'class': 'stigma'
            }).appendTo(elem);
        }

        function justfuckingdeletethisshit(elem) {
            $(elem).remove()
        }

    </script>
    <style type="text/css">
        body {
            font-family: Helvetica, Arial, sans-serif;
        }
        .urlList {
            border-color: red;
            background-color: palegoldenrod;
            border-bottom-left-radius: 2px;
            width: 100%;
            margin-bottom: 3px;
            font-family: monospace;
        }
        h1 {
            text-align: center;
            color: cadetblue;
            font-size: 3em;
        }
        .clickable {
            background-color: yellow;
            color: blueviolet;
            margin-left: 2em;
            margin-right: 2em;
        }
        .show {
            background-color: red;
        }
    </style>
</head>

<body>

<h1>
"""

second_section=\
"""
</h1>

<h2>National List</h2>
<div class="urlList" id="nationalList">
</div>

<h2>Local/Specialistic List</h2>
<div class="urlList" id="localList">
</div>

<h2>personal/community Blog List</h2>
<div class="urlList" id="blogList">
</div>

<h2>Unverified List</h2>

"""

entry_block=\
"""
<div id="%ID%">
    <a href="%URL%" target="_blank">%URL%</a>
    <span class="clickable" onclick="golocal('#%ID%');">local</span>
    <span class="clickable" onclick="gonational('#%ID%');">national</span>
    <span class="clickable" onclick="goblog('#%ID%');">blog</span>
    <span class="clickable" onclick="justfuckingdeletethisshit('#%ID%');">is shit!</span>
    <span class="clickable show" onclick="openiframe('#%ID%', '%URL%');">show now</span>
</div>
"""

final_section=\
"""
<br>
<button onclick="removebutton();">Press here when you've finished! can be easier copy/paste</button>
<br>
<button onclick="showbutton();">Press if you've made a mistake, make buttons comeback</button>
</body>
</html>
"""


if __name__ == '__main__':

    unvm = 'unverified_media_list'
    helpdir = os.path.join(unvm, 'htmlhelpers')

    # I want be executed in helpagrainsttrack root
    assert os.path.isdir(unvm), "unverified_media_list not found"
    assert os.path.isdir(helpdir), "helpers dir missing"

    for html_old in os.listdir(helpdir):
        old_helper_f = os.path.join(helpdir, html_old)
        if os.path.isfile(old_helper_f):
            print "removing previous .html", old_helper_f
            os.unlink(old_helper_f)
        
    excluded = ['htmlhelpers', 'README.md']
    for media_entry in os.listdir(unvm):

        if media_entry in excluded:
            continue

        destfile = os.path.join(helpdir, "%s.html" % media_entry)
        fp = file(destfile, 'w+')
        fp.write(first_section)
        fp.write(media_entry)
        fp.write(second_section)

        with file(os.path.join(unvm, media_entry), 'r') as mf:

            counter = 1
            for media in mf.readlines():

                counter += 1
                media_id = sha1(str(counter)).hexdigest()[:6]
                media = media[:-1]

                fp.write(
                    entry_block.replace('%ID%', media_id).replace('%URL%', media)
                )
                fp.write("\n\n")

        fp.write(final_section)
        print "created", media_entry

