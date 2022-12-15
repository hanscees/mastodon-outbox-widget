# mastodon-outbox-widget

Hi, I wanted a widget on my website to show the latest X posts or reboosts of my mastodon account.

This widget consists of a few pieces: 

1. A python script wich gets the latest articles from the mastodon outbox and writes them to an rss file

2. A html page which reads in this rss file and shows it on a website


So to deploy this you will need: 
1. A Webserver where you automatically run the python script, which generates the rss and serves the rss-file.

2. A webserver where your mastodon widget shows your latest posts and reboosts. This server should of course point the javascript bit in the html code to the rss file you generate. 


Why generate this rss feed? Because mastodon at this time does not generatye an rss file for the outbox. It does for several other streams. 
