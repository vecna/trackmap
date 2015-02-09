# unverified MEDIA LISTS

These media lists has been scraped by various online resourse. 
They are not:

  * Accurate (there are websites that are not news/media related)
  * Updated (something is missing, something is expired)
  * Separated (websites need to be sorted into [national], [local] and [blog])

If your country is missing, you can provide your own list, or contact <please.replace.me@with.actual.contact.info> to provide a coarse scraped resource.

If you are aquainted with the media landscape of one of these countries, please take a few minutes to review the list on the above criteria. If you don't know the usage of git and github, just email the sorted/corrected list to <please.replace.me@with.actual.contact.info>.


## news media list file specification

The media lists are plain text files with one URL per line. Lines starting with "#" are ignored (and can thus be used for comments).

We depend on the help of volunteers to extend the lists and sort the entries in the following sections.

### Sections

The media file supports four sections: [national], [local] and [blog] head sublists of media which operate on national level, local level or are web blogs. [global] is a placeholder for the special 
media file "global" (containing media websites which are checked in all countries).

This is an example of how a verified media list may appear:

    [global]

    [national]
    http://espresso.repubblica.it/


    [local]
    http://www.giornalecampania.it/
    http://www.giornalediarona.it/
    # and comments!

    [blog]
    http://www.dagospia.it

global section, trigger the loading of the media present in [this file](https://github.com/vecna/trackmap/blob/master/special_media/global)

