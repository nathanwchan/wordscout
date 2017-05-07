#!/usr/bin/python

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

# Authorize server-to-server interactions from Google Compute Engine.
from oauth2client.contrib import gce
import httplib2
import os
import sys

from apiclient.discovery import build_from_document, build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

credentials = gce.AppAssertionCredentials(scope='https://www.googleapis.com/auth/devstorage.read_write')
http = credentials.authorize(httplib2.Http())

CLIENT_SECRETS_FILE = "client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# Authorize the request and store authorization credentials.
def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage)

  # Trusted testers can download this discovery document from the developers page
  # and it should be in the same directory with the code.
  with open("youtube-v3-api-captions.json", "r") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))



# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyCvnft_5siETbjUyq8qyIuPHzM6s75Owk4"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(search_term):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
  youtube2 = get_authenticated_service()

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q="%s,cc" % search_term,
    part="id,snippet",
    type="video",
    videoCaption="closedCaption",
    maxResults=10
  ).execute()

  videos = []
  video_ids = []
  video_ids_seconds_map = {}
  #print "Found %s results." % len(search_response.get("items", []))

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    video_id = search_result["id"]["videoId"]
    if search_result["id"]["kind"] == "youtube#video":
      videos.append("%s (%s)" % (search_result["snippet"]["title"], video_id))
      video_ids.append(video_id)

    results = youtube.captions().list(
      part="snippet",
      videoId=video_id
    ).execute()

    if len(results["items"]):
      item = results["items"][0]
      caption_id = item["id"]
      name = item["snippet"]["name"]
      language = item["snippet"]["language"]
      #print "######### For video_id '%s', Caption track '%s(%s)' in '%s' language." % (video_id, name, caption_id, language)

      try:
	subtitle = youtube2.captions().download(
	  id=caption_id #, tfmt=tfmt
	).execute()
	#print "Found subtitles for video_id %s" % video_id
        #print subtitle[:200]
        subtitlelist = subtitle.split('\n')
        lastline = ''
	found = False
	for line in subtitlelist:
	  if str.lower(search_term) in str.lower(line):
	    found = True
	    break
	  lastline = line
	
	if found:
	  try:
	    seconds = int(lastline.split(':')[1]) * 60 + int(lastline.split(':')[2].split('.')[0])
	    if seconds:
	      video_ids_seconds_map[video_id] = seconds
	  except:
	    pass

	  #print "Found! last line: %s" % lastline
		
      except Exception as e:
        #print "*****failed to get subtitles %s" % e
	pass

  return video_ids, video_ids_seconds_map


#print "Videos:\n", "\n".join(videos), "\n"


@app.route('/', methods=['GET', 'POST'])
@app.route("/<search_term>", methods=['GET', 'POST'])
def wordscout(search_term=None):
  if request.method == 'POST':
    search_term = request.form['search_term']
    return redirect('/%s' % search_term)

  video_urls = ["https://www.youtube.com/embed/nlODa5QOm3Y?cc_load_policy=1&cc_lang_pref=en&start=75",
                "https://www.youtube.com/embed/8vogXQaGp5M?cc_load_policy=1&cc_lang_pref=en&start=68",
                "https://www.youtube.com/embed/v-FhAKwbELU"]
  return render_template('home.html',
			 search_term=search_term,
			 video_urls=video_urls)

  #search_terms = ['kick the bucket', 'spill the beans', 'hot potato', 'insult to injury', 'drop of a hat', 'back to the drawing board', 'beat around the bush', 'costs an arm and a leg', '"far cry from"', 'benefit of the doubt', 'hit the nail on the head', 'in the heat of the moment', 'jump on the bandwagon', 'miss the boat', 'on the ball', 'once in a blue moon', 'piece of cake', 'sit on the fence', 'take it with a grain of salt', 'whole nine yards', "wouldn't be caught dead", 'bucket list', 'up in the air', 'out of woods']
  #search_terms = ['a dime a dozen', 'chip on your shoulder', 'picture paints a thousand words', 'slap on the wrist', 'taste of your own medicine', 'a toss up', 'actions speak louder than words', 'add fuel to the fire', 'against the clock', 'all in the same boat', 'axe to grind', 'apple of my eye', "baker's dozen", 'back to square one', 'beat a dead horse', 'between a rock and a hard place', 'bite your tongue', 'break a leg', 'crack someone up', 'cup of joe', 'cut to the chase', "devil's advocate", 'down to the wire', 'dry run', 'drop like flies', 'pardon my french', 'field day', "fool's errand", 'rags to riches', 'full monty', 'go the extra mile', 'go out on a limb', 'good samaritan', 'gut feeling', 'hit the sack', 'hold your horses', 'icing on the cake', 'in the bag', 'in your face', 'its a small world', 'cat out of the bag', 'level playing field', 'bite the hand that feeds you', 'no dice', 'off on the wrong foot', 'off the hook', 'off the record', 'out of the blue', 'over my dead body', 'over the top', 'rise and shine', 'start from scratch', 'tie the knot', 'tongue in cheek', 'turn a blind eye', 'under the weather', 'when pigs fly', 'judge a book by its cover']
  #search_terms = ['benefit of the doubt', 'insult to injury', 'beat around the bush', 'devil\'s advocate', 'rise and shine', 'turn a blind eye']
'''
  #for search_term in search_terms:
  video_urls = []
  video_ids = []
  video_ids_seconds_map = {}
  if search_term:
    search_term = str(search_term)
    try:
      video_ids, video_ids_seconds_map = youtube_search(search_term)
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
      video_ids = ["_8qfufCxk40", "X-hs2G33Kvc", "xMYdtZq2bIo"]

    #print video_ids_seconds_map
    for video_id in video_ids:
      video_url = "https://www.youtube.com/embed/%s?cc_load_policy=1&cc_lang_pref=en" % video_id
      seconds = video_ids_seconds_map.get(video_id)
      if seconds:
        video_url += "&start=%s" % seconds
      video_urls.append(video_url)
        #print video_url
      if len(video_urls) > 0:
        print "%s %s" % (len(video_urls), search_term)
  print video_urls
'''

if __name__ == "__main__":
  app.run()
