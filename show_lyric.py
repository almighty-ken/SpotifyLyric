#!/usr/bin/python

from subprocess import Popen, PIPE
from requests.utils import quote
#import requests
import json
#from watson_developer_cloud import AlchemyLanguageV1
import urllib2
from bs4 import BeautifulSoup
import re

musicmatch_key = "b8ee0310a43cf402ea580d6d03873447"

def fetch_artist():
    with open('get_artist.applescript', 'r') as load_script:
        data1=load_script.read()
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    artist, stderr = p.communicate(data1)
    artist = artist[0:-1]
    return artist

def fetch_track():
    with open('get_track.applescript', 'r') as load_script:
        data2=load_script.read()     
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    track, stderr = p.communicate(data2)  
    track = track[0:-1]
    return track

def fetch_time():
    with open('get_time.applescript', 'r') as load_script:
        data3=load_script.read()    
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    time, stderr = p.communicate(data3) 
    time = time[0:-1]
    return time

def get_lyric_from_link(link):
    data = urllib2.urlopen(link)
    soup = BeautifulSoup(data,'html.parser')
    lyr_group = soup.find('script',text=re.compile('__mxmState'))
    lyr_text = re.search(r'"body":"([^"]*)',lyr_group.text)
    return lyr_text.group(1)

def get_link(artist,track):
    link = 'https://api.musixmatch.com/ws/1.1/track.search?format=json&callback=callback&q_track='
    link += quote(track,safe='')
    link += '&q_artist='
    link += quote(artist,safe='')
    link += '&quorum_factor=1&apikey=b8ee0310a43cf402ea580d6d03873447'
    response = urllib2.urlopen(link)#.read()
    data = json.load(response)
    url = data['message']['body']['track_list'][0]['track']['track_share_url']
    #print url
    return url

def main():
    artist = fetch_artist()
    track = fetch_track()
    time = fetch_time()
    link = get_link(artist, track)
    lyric = get_lyric_from_link(link)
    print lyric
    
if __name__ == '__main__':
    main()
