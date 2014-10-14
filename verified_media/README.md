## news media list file specification

This is the file format to be used by a supporter helping us in collect a suitable media lists per country.

### Sections

The media file supports four sections: national, local and blog. 'global' mean that the special 
media file (containing media website checked in all the country) is loaded. 

This is how a verified media list appears:

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
