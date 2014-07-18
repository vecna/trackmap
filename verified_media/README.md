## news media list file specification

This is the file format to be used by a supporter helping us in collect a suitable media lists per country.

### Sections

Like an .ini file, these media files supports sections, in example:

    [global]

    [national]
    http://espresso.repubblica.it/


    [local]
    http://www.giornalecampania.it/
    http://www.giornalediarona.it/
    # and comments!

    [blog]
    http://www.dagospia.it


global section, trigger the loading of the media present in [this file](https://github.com/vecna/helpagainsttrack/blob/master/special_media/global)
