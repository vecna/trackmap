## RESTful API

This is the API specification of Trackography project, you can write application integrated to those app.

## Server

# API

## Countries supported

GET /countries


    [
        "CHE", 
        "SYR", 
        "RUS", 
        "UKR", 
        "ESP", 
        "PAK", 
        "GRC"
    ]

Return a list of three letter country code for the supported country.
A country get supported when there are at least one test successfully 
accepted from the country.


## Media supported

GET /country/[THREE_LETTER_COUNTRY_CODE]/

**THREE_LETTER_COUNTRY_CODE** is one of the supported country get by the previous API.

Note: you've to put "/" ad the end

    [ {
        "complete_media_url": "http://www.hurriyet.com.tr/", 
        "flash": false, 
        "id": 254, 
        "included_companies": [
            "Gemius", 
            "comScore", 
            "Google", 
            "Yandex", 
            "Horyzon Media"
        ], 
        "linked_hosts": 18, 
        "type": "global", 
        "url": "www.hurriyet.com.tr"
    },
    { ... },
    { ... } ]


It return a **list** of Media. The media has been tested in the country specified
in the URL. Every media is expressed with a **dict**. Every dict contains the following keys:

  * complete_media_url: the precise URL used during the test
  * flash: if the media or a third party is loading a flash object
  * id: an unique ID of the media
  * included_companies: list of company name, based on the *disconnect.me* public databased 
  * linked_hosts: number of external host linked to the analyzed URL
  * type: one of global, national, local or blog.
  * url: the HTTP domain without the paramenter after the "/"

### Media additional parameter

GET /country/[THREE_LETTER_COUNTRY_CODE]/[national,global,local,blog]

You can put a comma separated list of keyword, and this apply a filter on the returned media.


## Routes

GET /data/[THREE_LETTER_COUNTRY_CODE]/id/[MEDIA_ID],[MEDIA_ID],...


    [
    {
        "AS_chain": [
            null, 
            "65534", 
            "812", 
            null, 
            "5645", 
            "11670"
        ], 
        "company": "eyeReturn Marketing", 
        "country_chain": [
            "Reserved", 
            "Reserved", 
            "CAN", 
            "CAN", 
            "CAN", 
            "CAN"
        ], 
        "host": "cm.eyereturn.com", 
        "id": 3318, 
        "is_intended_media": false, 
        "is_same_domain": false, 
        "media_id": 134, 
        "media_url": "www.welt.de", 
        "resolved_ip": "69.90.155.234", 
        "reverse_dns": "mail.dz4ms.com", 
        "target_country": "USA"
    },
    { ... } ]


For every [MEDIA_ID] return a **list**. Many [MEDIA_ID] just means longer list.
The list is composed by dictionary which the keys are:

  * AS_chain
  * company
  * country_chain
  * host
  * id
  * is_intended_media
  * is_same_domain
  * media_id
  * media_url
  * resolved_ip
  * reverse_dns
  * target_country

## Company 

Query to /company/ or /company/(a company name),(other company name)


## Other API (that you may need)

TLS/SSL global collection, can be fetched and interpolated:  https://scans.io/
