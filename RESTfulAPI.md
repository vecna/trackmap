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
A country get supported when there are at least one test successfully accepted from the country.

All the supported countries are present in the list, are [Three Letter Code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3), and in this document I refer to them as "3LC".


## Tests available per country

GET /results/3LC

    {
      "contextual": [
        { 'name' : 'health care-Thailand', 'id': 1, 'date': "2015-02-06T20:52:28Z" },
        { 'name' : 'politics-Thailand', 'id': 'date': "2015-02-06T20:57: " },
      ],
      "media": [
        { 'name': 'thailand', 'id': 340, 'date': "2015-04-01T10:31:02Z" },
      ],
      "alexa": [
        { 'name': 'top 100', 'id': 200, 'date': "2015-01-01T05:59:58Z" },
        { 'name': 'top 100', 'id': 205, 'date': "2015-01-02T05:59:58Z" },
      ],
    }


"contextual", "media" and "alexa" are fixed word. 

  * contextual: refer to a specific subject, like the health care website analyzed in a specific place
  * media: is an analysis referring to the news media on a certain nation
  * alexa: is an analysis apply to the Top 100 or 500 website in such country

Inside, the block, contain these fields:

  * name: can be ignored in **media**, in **contextual** instead specify the name of the topic addressed, and ale


### Note

The first visualization of Trackography was based only in **media** result, the **contextual** reachable only through [this research address](http://213.108.108.94:8000/details), but is an hack on the 1.0 visualization. A new visualization is in development.


## Website available per test

The 'id' value of the previous API is the test ID. A Test is uniquly identify by the **testkind**/**test\_ID** 

  * GET /website/contextual/test\_ID
  * GET /website/media/test\_ID
  * GET /website/alexa/test\_ID

They all return a list containing objects. Every object describe a website tested with some generic information about it.

    [ {
        "complete_media_url": "http://www.hurriyet.com.tr/mypage/second", 
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


  * flash: if active content was deployed 
  * type: the category with the website belong, because in every list is possible associate categories.
  * id: is a number that start from 0 and reach the number of media available, is an incremental number reset at every test, and there is not linking getween the IDs of two different tests.

more details below

## Legacy - Media website available

In the first version of Trackography was returned only one list of website per country, this request:

GET /country/3LC/

Note: you've to put "/" ad the end

Return the equivalent of 

GET /website/media/"LATEST TEST\_ID associated to the country requested"


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
    { ... } 
    ]


It return a **list** of Media. The media has been tested in the country specified in the URL. Every media is expressed with a **dict**. Every dict contains the following keys:

  * complete_media_url: the precise URL used during the test
  * flash: if the media or a third party is loading a flash object
  * id: an unique ID of the media
  * included_companies: list of company name, based on the *disconnect.me* public databased 
  * linked_hosts: number of external host linked to the analyzed URL
  * type: one of global, national, local or blog.
  * url: the HTTP domain without the parameter after the "/"

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


For every [MEDIA_ID] return a **list**. Many [MEDIA_ID]s just means longer list. 
The list has a number of objects inside, equal to the 'linked_hosts' parameter fetch in the /website or /country APIs.
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

## Company - Legacy - will be abandoned

Query to /company/ or /company/(a company name),(other company name)
Like,

GET /company/Google,Facebook 

    [
    {
        "Access_to_collected_data_by_user": true, 
        "Advertising": true, 
        "Browser_cookies": true, 
        "Clients": "Not available", 
        "Collects_Non-PII": true, 
        "Collects_PII": true, 
        "Collects_Technical_Data": true, 
        "Compliance_Safe_Harbour_Framework": true, 
        "Data_collected_by_third_parties": true, 
        "Data_retention_in_days": "Not available", 
        "Disclosure_of_data_to_third_parties": true, 
        "Disclosure_of_data_to_third_parties_COMMENTS": "Primarily to service providers", 
        "Flash_cookies": true, 
        "Market_research": true, 
        "National_laws": "US", 
        "Opt-out": true, 
        "Opt-out_comments": "But only through the Digital Advertising Alliance website", 
        "PII_Comments": null, 
        "Parent_company": null, 
        "Privacy_Policy": "https://www.facebook.com/policy.php", 
        "Profiling": true, 
        "Prohibits_third_parties_from_using_data_for_unspecified_purposes": false, 
        "Safeguards_to_prevent_the_full_identification_of_IP_addresses": false, 
        "Supports_Do_Not_Track": false, 
        "TRUSTe_Privacy_Seal_certification": true, 
        "Web_Beacons": true, 
        "Web_analytics": false, 
        "Web_crawler": true, 
        "name": "Facebook", 
        "url": "https://www.facebook.com/facebook/info?ref=page_internal"
    }, { }
    ]



# Computed results

The API above try to be more descriptive of the content receiver by the tester around the world. but some kind of interpolation and computation has been done.
These API will be developed in the Summer, therefore this section will receive updated with new details.





## Other API (that you may need)

TLS/SSL global collection, can be fetched and interpolated:  https://scans.io/
