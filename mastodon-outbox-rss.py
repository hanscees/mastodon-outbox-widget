#!/usr/bin/env python

import re
import requests
import textwrap3
import json
from feedgen.feed import FeedGenerator

# adjusted from: 
# see https://github.com/matthewn/mastodon-homefeed-rss/blob/main/pyproject.toml
# by Hans-Cees Speel 12-2022 

#### gets statuses from an mastodon outbox (original was from homefeed)
###  and makes a RSS list of it 
### first it extracts the first X toots in the outbox, and gets their original url
###  then it looks up these original id's and puts their context in an enriched list
## then it build a feed of that list 


def get_six_mastodon_outbox_statuses(host_instance, user, numberoftoots):
    #numberoftoots must be a number, or we make it 6
    try:
        a = int(numberoftoots)
        print('numberof toots is a number: good')
    except:
        print('numberoftootls is not a number, set it at 6')
        numberoftoots = 6
    instance = host_instance

    #headers = {'Authorization': f'Bearer {pa_token}'}
    headers = {'Accept': 'application/activity+json'}
    response = requests.get(
        f'{host_instance}/users/{user}/outbox?page=true',
        headers=headers,
    )

    if response.status_code != 200:
        try:
            print(f'Error received from instance: {response.json()["error"]}')
        except requests.exceptions.JSONDecodeError:
            print(f'Error received from instance. HTTP status code: {response.status_code}')
        sys.exit(1)

    outboxdict = json.loads(response.text) # this converts the json to a python list of dictionary
    #print(statuses) # this prints the status text
    tootdictlist = outboxdict["orderedItems"]  ## this is a list with dicts like [{}.{},{},etc]
    #print(toots)

    tootdictlist5 = tootdictlist[0:numberoftoots]   #lets get the first 5

    #Now in a loop we will extract status url's only to test them lateron
    statuslist=[] # list of toots to display 
    for item in tootdictlist5:
        tootid = item["object"]
        if (type(tootid) is dict):  #it is a dict when it is a new dict, created by user
            tootid = tootid['id']
            #print("tootid is, ", tootid, " \n")
        statuslist.append(tootid)
    return statuslist


#statuslist = get_six_mastodon_outbox_statuses("https://campaign.openworlds.info", bomengidsnl, 7):

#statuslist is now somtthing like:  ['https://campaign.openworlds.info/users/bomengidsnl/statuses/109479666844357544', 
#'https://campaign.openworlds.info/users/bomengidsnl/statuses/109479651341970001', 
#'https://mstdn.social/users/JustJenny/statuses/109479437661766466', 
#'https://mastodon.social/users/PaulvdVijver/statuses/109479106175272626']


def enrich_statuses(statuslist):
    counter = 0
    enriched_list = []
    #Now in a loop we will test if toots are suitable and adjust if needed
    for item in statuslist:
        #firststatus = statuslist[0]
        currentstatus = statuslist[counter]
        counter = counter+1
        print("currentstatus is, ", currentstatus)
        headers = {'Accept': 'application/activity+json'}
        response = requests.get( currentstatus, headers=headers)
        #response = requests.get(url, headers=headers)
        #print(response.text)
        #outboxdict = json.loads(response.text) # this converts the json to a python list of dictionary
        
        if response.status_code != 200:
            try:
                print(f'Error received from instance: {response.json()["error"]}')
            except requests.exceptions.JSONDecodeError:
                print(f'Error received from instance. HTTP status code: {response.status_code}')
            sys.exit(1)

        statusdict = json.loads(response.text) # this converts the json to a python list of dictionary
        print("statusdict is \n , ", statusdict)  # ok this works we now have another complex ordered list
        print("url is ", statusdict["id"], "\n \n ")  # is the link url
        print("content text is ", statusdict["content"], "\n \n")  # is the text, may need trimming
        print(" is it sensitive? ", statusdict["sensitive"])
        if statusdict["sensitive"]:
            print("status is sensitive, well skip this toot")
            continue

        if statusdict["attachment"]:  # if it has an image get variables
            imagedict=statusdict["attachment"][0]
            print("mediatype is ", imagedict["mediaType"]) 
            print("url pic is ", imagedict["url"]) # is imagelink
            print("\n")
        else:
            print("there no pic man")
            continue #we dont want to show toots without image


        #ok, so now we have ditched sensitive toots and  toots without images (not nice for widget)
        # lets trim the content. We don't want long text, just a teaser with a link and an image
        # if website user is interested, they can click the link and go to mastodon

        ## here some text trim code please
        enriched_list.append(statusdict)

    return enriched_list


def generate_feed(enriched_list, output_file):
    if output_file is None:
        output_file = 'mastodon-homefeed.xml'
    feed = FeedGenerator()
    feed.load_extension('media')
    
    #media:content has the following fields:
    #    - *url* should specify the direct URL to the media object.
    #    - *fileSize* number of bytes of the media object.
    #    - *type* standard MIME type of the object.
    #https://github.com/lkiesow/python-feedgen/blob/master/feedgen/ext/media.py
    #                    content,
    #                set(['url', 'fileSize', 'type', 'medium', 'isDefault',
    #                     'expression', 'bitrate', 'framerate', 'samplingrate',
    #                     'channels', 'duration', 'height', 'width', 'lang',
    #                     'group']),
    #                set(['url', 'group']))

    #so media variables should be like 
    #fg.media.content=


    feed.id('https://www.bomengids.nl/mastodon-homefeed-rss') #give the id you want this rss feed to be for
    feed.title('mastodon (re)-posts')
    feed.description('bomengidsnl')
    feed.link( href='https://www.bomengids.nl/mastodon-homefeed-rss')
    statuses = enriched_list
    for status in statuses:
        if status["attachment"]:  # if it has an image get variables
            imagedict=status["attachment"][0]
            print("mediatype is ", imagedict["mediaType"]) 
            mediatype = imagedict["mediaType"]
            print("url pic is ", imagedict["url"]) # is imagelink
            media_url = imagedict["url"]
            media_width = imagedict["width"]
            media_height = imagedict["height"]
            print("\n")
        #print(status)
        #exit()
        content = status['content']
        title = re.sub('<[^<]+?>', '', content)
        title = textwrap3.shorten(title, width=80, placeholder='...')
        content = textwrap3.shorten(content, width=80, placeholder='...')
        #content = status['content']
        url = status["id"]
        entries = re.split("\/", url)
        author = entries[4]
        #url is  https://sciencemastodon.com/users/DendroLund/statuses/109490124577229238 
        #author = status['account']['display_name']
        created = status['published']
        item = feed.add_entry()
        item.id(url)
        item.media.content({"url" : media_url, "type": mediatype, "width": str(media_width), "height": str(media_height)})
        item.title(title)
        item.author({'name': author})
        item.pubDate(created)
        item.description(content)

        item.link({'href': url})
    feed.rss_file(output_file)
#see https://feedgen.kiesow.be/#generate-the-feed

#      <media:content url="https://cdn.masto.host/campaign/media_attachments/files/109/484/134/033/920/354/original/a12e99e5b669e1b8.jpg" type="image/jpeg" fileSize="71891" medium="image">
#        <media:rating scheme="urn:simple">nonadult</media:rating>
#        <media:description type="plain">lente-spring-fruhling-printemps-primavera</media:description>
#      </media:content>



#url = "https://sciencemastodon.com/users/DendroLund/statuses/109490124577229238"
#entries = re.split("\/", url)
#user = entries[4]
#print("user sdhould be : ", user) 
#exit()

statuslist = get_six_mastodon_outbox_statuses("https://campaign.openworlds.info", "bomengidsnl", 7)
enriched_list = enrich_statuses(statuslist)

generate_feed(enriched_list, "feed.rss")

