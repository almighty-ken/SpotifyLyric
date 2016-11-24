#!/usr/bin/python

from subprocess import Popen, PIPE
import json
import urllib2
from bs4 import BeautifulSoup
import re
import psycopg2
from Tkinter import *

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
    try:
        data = urllib2.urlopen(link)
    except:
        print 'Sorry no lyrics!'
        return
    soup = BeautifulSoup(data,'html.parser')
    lyr_group = soup.find('script',text=re.compile('__mxmState'))
    lyr_text = re.search(r'"body":"([^"]*)',lyr_group.text)
    return lyr_text.group(1)

def get_link(artist,track):
    link = 'https://api.musixmatch.com/ws/1.1/track.search?format=json&callback=callback&q_track='
    link += urllib2.quote(track,safe='')
    link += '&q_artist='
    link += urllib2.quote(artist,safe='')
    link += '&quorum_factor=1&apikey=b8ee0310a43cf402ea580d6d03873447'
    response = urllib2.urlopen(link)#.read()
    data = json.load(response)
    url = data['message']['body']['track_list'][0]['track']['track_share_url']
    #print url
    return url

def artist_translate(artist,cur):
    query = "SELECT c_name FROM name_translation WHERE e_name = '" + artist+"';"
    #print query
    cur.execute(query)
    if(cur.rowcount == 0):
        return artist
    rows = cur.fetchone()
    return rows[0]

def db_connect():
    try:
        conn = psycopg2.connect("dbname='spotify_lyric' user='ken' host='localhost' password=''")
    except:
        print "DB connection fail"
    cur = conn.cursor()
    return conn,cur
    
def db_disconnect(conn,cur):
    conn.close()
    cur.close()
    
def store_lyr(artist,track,lyric,cur,conn):    
    #lyric escaping!!
    lyric = urllib2.quote(lyric.encode('utf8'),safe='')
    query = "INSERT INTO lyric VALUES ('" + artist + "','"+track+"','"+lyric+"');"
    try:
        cur.execute(query)
        conn.commit()
    except:
        print "lyric store fail"
        
def fetch_cached_lyric(artist,track,cur,conn):
    cur.execute("SELECT lyric FROM lyric WHERE lyric.artist = %s AND lyric.track = %s;",(artist,track))
    if(cur.rowcount==0):
        return False
    else:
        lyric = cur.fetchone()
        lyric = lyric[0]
        lyric = urllib2.unquote(lyric)
        return lyric

def main():
    conn,cur = db_connect()
    artist = fetch_artist()
    artist = artist_translate(artist,cur)
    track = fetch_track()
    time = fetch_time()
    lyric = fetch_cached_lyric(artist,track,cur,conn)
    if(lyric == False):
        link = get_link(artist, track)
        lyric = get_lyric_from_link(link)        
        store_lyr(artist,track,lyric,cur,conn)
    #print lyric
    lyric = lyric.replace('\\n','\n')
    print lyric
    db_disconnect(conn,cur)
    
#main()

class Application(Frame):
    def say_hi(self):
        print "hi there, everyone!"

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.master.title("LyricCrawl")
app.master.maxsize(1000, 400)
app.mainloop()
root.destroy()
    
#if __name__ == '__main__':
    #main()
