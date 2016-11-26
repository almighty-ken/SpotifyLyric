#!/Users/ken/anaconda2/bin/python

from subprocess import Popen, PIPE
import json
import urllib2
from bs4 import BeautifulSoup
import re
from Tkinter import *
import pickle

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
        return 'Sorry no lyrics!'
    soup = BeautifulSoup(data,'html.parser')
    lyr_group = soup.find('script',text=re.compile('__mxmState'))
    lyr_text = re.search(r'"body":"([^"]*)',lyr_group.text)
    if(not lyr_text):
        return 'Sorry no lyrics!'
    return lyr_text.group(1)

def get_link(artist,track):
    artist = artist.encode('utf-8')
    link = 'https://api.musixmatch.com/ws/1.1/track.search?format=json&callback=callback&q_track='
    link += urllib2.quote(track,safe='')
    link += '&q_artist='
    link += urllib2.quote(artist,safe='')
    link += '&quorum_factor=1&apikey=b8ee0310a43cf402ea580d6d03873447'
    try:
        response = urllib2.urlopen(link)
    except:
        return None
    data = json.load(response)
    try:
        url = data['message']['body']['track_list'][0]['track']['track_share_url']
    except:
        url = None
    #print url
    return url

def artist_translate(artist,dic):
    if artist in dic:
        return dic[artist]
    return unicode(artist,'utf-8')
    
def store_lyr(artist,track,lyric,dic):    
    dic[(artist,track)] = lyric
        
def fetch_cached_lyric(artist,track,dic):
    if((artist,track) in dic):
        return dic[(artist,track)]
    return None

def fetch_lyric():
    global name_dic
    global lyr_db
    artist = fetch_artist()
    artist = artist_translate(artist,name_dic)
    track = fetch_track()
    #time = fetch_time()
    #lyric = fetch_cached_lyric(artist,track,lyr_db)
    lyric = None
    if(lyric == None):
        link = get_link(artist, track)
        if(link==None):
            return "Lyric not available!"
        else:
            lyric = get_lyric_from_link(link)
            if(lyric != 'Sorry no lyrics!'):
                store_lyr(artist,track,lyric,lyr_db)
    #print lyric
    lyric = lyric.replace('\\n','\n')
    prefix = unicode(track,'utf-8') + '\n' + artist + '\n\n'
    lyric = prefix + lyric
    return lyric
                   
class Application(Frame):
    def get_lyric(self,txt_box):
        lyric = fetch_lyric()
        txt_box.delete(1.0,END)
        txt_box.insert(INSERT,lyric)

    def createWidgets(self):
        self.get_lyr = Button(self,text="Refresh Lyrics")
        self.get_lyr.pack({"side": "left"})
        self.show_lyr = Text(self)
        self.show_lyr.insert(END,"")
        self.show_lyr.pack({"side":"right"})        
        self.get_lyr["command"] = lambda: self.get_lyric(self.show_lyr)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        


with open('name_translation.json','r') as fp:
    name_dic = json.load(fp)
    
lyr_db = pickle.load(open('lyric_db.pkl','rb'))
#lyr_db = {}
    
#with open('lyric_db.pkl','r') as fp:
    #lyr_db = pickle.load(fp)
    
#print(fetch_lyric())

root = Tk()
app = Application(master=root)
app.master.title("LyricCrawl")
app.master.maxsize(500, 400)
app.master.minsize(500, 400)
app.mainloop()
#root.destroy()

pickle.dump(lyr_db, open('lyric_db.pkl','wb'), pickle.HIGHEST_PROTOCOL)