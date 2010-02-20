import urllib2
import urllib
from urllib import *
#from urllib.parse import quote
import time
from operator import itemgetter
from Tkinter import *
import random
import sys
from BeautifulSoup import BeautifulStoneSoup
import re
#import lastFMOutput
#from lastFMOutput import *
#output = lastFMOutput.LastFMOutput(root)

def getWeeklyArtists(user, URLprefix, numArtists):
    artists = [[], []] #[[artistName], [playCount]]
    weeklyArtistURL = URLprefix + "user/" + user + "/weeklyartistchart.xml"
    weeklyArtists = urllib2.urlopen(weeklyArtistURL)
    s = weeklyArtists.readline() #blank line
    s = weeklyArtists.readline() #user ID line 
    for i in range(numArtists):
        try:
            s = weeklyArtists.readline() #<artist>
            s = weeklyArtists.readline() #<name>
            artists[0].append(s[10:-8])
            s = weeklyArtists.readline() #<mbid>
            s = weeklyArtists.readline() #<chartposition>
            s = weeklyArtists.readline() #<playcount>
            artists[1].append(s[15:-13])
            s = weeklyArtists.readline() #<url>
            s = weeklyArtists.readline() #</artist>
        except IOError:
            print('null')
    return artists

def getTopArtists(user, URLprefix, numArtists):
    artists = [[], []] #[[artistName], [playCount]]
    topArtistURL = URLprefix + "user/" + user + "/topartists.xml"
    topArtistsXML = urllib.urlopen(topArtistURL)
    topArtistsSoup = BeautifulStoneSoup(topArtistsXML)
    topArtistsDict = topArtistsSoup.findAll('artist')
    
    for i in range(numArtists):
        topArtistNameBlock = topArtistsDict[i].findAll('name')
        topArtistName = topArtistNameBlock[0].contents[0]
        topArtistPlaycountBlock = topArtistsDict[i].findAll('playcount')
        topArtistPlaycount = topArtistPlaycountBlock[0].contents[0]
        #topArtistURLBlock = topArtistsDict[i].findAll('url')
        #topArtistURL = topArtistURLBlock[0].contents[0]
        
        artists[0].append(topArtistName)
        artists[1].append(topArtistPlaycount)

    return artists

def getArtists(user, URLprefix, numArtists, timeFrame):
    artists = [[], [], []] #[[artistName], [playCount], [URL]]
    if (timeFrame == 'week'):
        topArtistsURL = URLprefix + "?method=user.getWeeklyArtistChart&user=" + user + "&api_key="
    else:
        topArtistsURL = URLprefix + "?method=user.getTopArtists&user=" + user + "&period=" + timeFrame + "&api_key="
    #print topArtistsURL
    topArtistsXML = urllib.urlopen(topArtistsURL)
    topArtistsSoup = BeautifulStoneSoup(topArtistsXML)
    #print topArtistsSoup.prettify()
    
    topArtistsDict = topArtistsSoup.findAll('artist')
    #print topArtistsDict[5]
    
    for i in range(numArtists):
        topArtistNameBlock = topArtistsDict[i].findAll('name')
        topArtistName = topArtistNameBlock[0].contents[0]
        #topArtistName = unicode(topArtistNameBlock[0].contents[0]).encode("ascii", "replace")
        #topArtistName = (topArtistNameBlock[0].contents[0]).encode("ascii", "replace")
        print topArtistName
        topArtistPlaycountBlock = topArtistsDict[i].findAll('playcount')
        topArtistPlaycount = topArtistPlaycountBlock[0].contents[0]
        topArtistURLBlock = topArtistsDict[i].findAll('url')
        topArtistURL = topArtistURLBlock[0].contents[0]
        
        artists[0].append(topArtistName)
        artists[1].append(topArtistPlaycount)
        
    return artists

def getTags(artists, URLprefix, numArtists):
    userTags = {}
    for i in range(numArtists):
        artistTags = ''
        try:
            artistName = artists[0][i]
            #print artistName
            artistTagsURL = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist=" + quote(artistName) + "&api_key="
            #print artistTagsURL
            #artistTagsURL = "http://" + urllib.quote(artistTagsURL)
            artistTagsXML = urllib.urlopen(artistTagsURL)
            artistTagsSoup = BeautifulStoneSoup(artistTagsXML)
            tagDict = artistTagsSoup.findAll('tag')
            #print (str(i+1) + ": " + artists[0][i])
        except IOError:
            print('failed to retrieve tags for ' + artistName)
        for j in range (5):
            present = 0
            try:
                tagNameBlock = tagDict[j].findAll('name')
                tagName = tagNameBlock[0].contents[0]
                print tagName
                tagScoreBlock = tagDict[j].findAll('count')
                tagScore = int(tagScoreBlock[0].contents[0])
        
                for key in userTags:
                    if (tagName == key):
                        userTags[key][0] += tagScore
                        present = 1
                if not present:
                    userTags[tagName] = [tagScore, 0]
            except ValueError:
                pass    
        time.sleep(1)
    return userTags

def checkFontBounds(fontSize):
    if (sys.platform == 'darwin'):
        if fontSize>60:
            fontSize = 60
        if fontSize<9:
            fontSize=9
    elif (sys.platform == 'win32'):
        if fontSize>35:
            fontSize = 35
        if fontSize<7:
            fontSize=7
    elif (sys.platform == 'linux2'):
        if fontSize>35:
            fontSize = 35
        if fontSize<7:
            fontSize=7
    return fontSize

def getFillColor(tagNumber, numberOfTags):
    red = 0x00 + (tagNumber * (0xff/numberOfTags))
    red = str(hex(red))[2:]
    if (len(red)<2):
        red = '0' + red
    green = '00'    
    blue = 0xff - (tagNumber * (0xff/numberOfTags))
    blue = str(hex(blue))[2:]
    if (len(blue)<2):
        blue = '0' + blue
    fillColor = '#' + red + green + blue
    return fillColor

def getWordWidth(sortedTags, tag, fontSize):
    if (sys.platform == 'darwin'):
        wordWidth = float(len(sortedTags[tag][0])) * (float(2)/3*fontSize)
    elif (sys.platform == 'win32'):
        wordWidth = float(len(sortedTags[tag][0])) * (float(7)/8*fontSize) +5
    elif (sys.platform == 'linux2'):
        wordWidth = float(len(sortedTags[tag][0])) * (float(7)/8*fontSize) +5
    return wordWidth
    
def output():
    print('-' * 20)
    for tag in range(len(userTags.keys())):
        print ('%05.2f%% ' + sortedTags[tag][0]) %sortedTags[tag][1][1]
    print('-' * 20)

class GetUserInfo:
    def __init__(self, parent):
        self.myParent = parent
        self.myContainer1 = Frame(parent)
        self.myContainer1.pack()

        self.myContainer2 = Frame(self.myContainer1)
        self.myContainer2.pack(side=TOP)

        user = StringVar(value='who_am_i')
        artists = IntVar(value=6)
        time = StringVar()
        
        self.label1 = Label(self.myContainer2, text="User: ").pack(side=LEFT)
        self.textArea1 = Entry(self.myContainer2, width=10, textvariable=user).pack(side=LEFT)
        self.label2 = Label(self.myContainer2, text="# of Artists: ").pack(side=LEFT)
        self.textArea2 = Entry(self.myContainer2, width=2, textvariable=artists).pack()
        
        self.myContainer3 = Frame(self.myContainer1)
        self.myContainer3.pack(side=TOP)
        
        self.radio1 = Radiobutton(self.myContainer3, text="Week", variable=time, value='week').pack(side=LEFT)
        self.radio2 = Radiobutton(self.myContainer3, text="3 mo.", variable=time, value='3month').pack(side=LEFT)
        self.radio3 = Radiobutton(self.myContainer3, text="6 mo.", variable=time, value='6month').pack(side=LEFT)
        self.radio4 = Radiobutton(self.myContainer3, text="12 mo.", variable=time, value='12month').pack(side=LEFT)
        self.radio5 = Radiobutton(self.myContainer3, text="Total", variable=time, value='overall').pack(side=LEFT)
        time.set('overall')
        
        self.myContainer5 = Frame(self.myContainer1).pack(side=TOP)
        
        self.button1 = Button(self.myContainer5)
        self.button1.configure(text="OK", background= "green")
        self.button1.pack()
        self.button1.focus_force()
        self.button1.bind("<Button-1>",
                          lambda
                          event, arg1=user, arg2=time, arg3=artists:
                          self.button1Click(arg1, arg2, arg3)
                          )
        self.button1.bind("<Return>",
                          lambda
                          event, arg1=user, arg2=time, arg3=artists:
                          self.button1Click(arg1, arg2, arg3)
                          )
        
    def button1Click(self, testuser, testTimeFrame, testNumberOfArtists):
        print(testuser.get())
        print(testTimeFrame.get())
        print(testNumberOfArtists.get())
        #self.button1.destroy()
        #self.myContainer1.destroy()
        dataWork = DataWork(testuser.get(), testTimeFrame.get(), testNumberOfArtists.get())
        
class DataWork():
    def __init__(self, user, timeFrame, numArtists):
        URLprefix = "http://ws.audioscrobbler.com/2.0/"
        percentSum = 0

        #######get data################################
        artists = getArtists(user, URLprefix, numArtists, timeFrame)
        timeTitle = timeFrame
        
        userTags = getTags(artists, URLprefix, numArtists)
        sortedTags = sorted(userTags.items(), key=itemgetter(1), reverse=True)

        #######sorting#################################
        for tag in range(len(sortedTags)):
            sortedTags[tag] = [sortedTags[tag][0].lower(), sortedTags[tag][1]]
        scoreSum = 0
        for tag in userTags.keys():
            scoreSum += userTags[tag][0]
        for tag in range(len(userTags.keys())):
            sortedTags[tag][1][1] = float((float(sortedTags[tag][1][0])/float(scoreSum))*100)
            percentSum += sortedTags[tag][1][1]

        #######output##################################    
        #output()
        for tag in range(len(sortedTags)):
            sortedTags[tag][1].append(getFillColor(tag, len(sortedTags)-1))
        tagsByPop = sortedTags[:]
        sortedTags.sort()

        lastFMOutput = LastFMOutput(root, sortedTags, userTags, artists, tagsByPop)

class LastFMOutput:
    def __init__(self, parent, sortedTags, userTags, artists, tagsByPop):
        x=10
        cloudHeight = 60
        if (sys.platform == 'darwin'):
            heightOffset = 45
            fontName = 'Andale Mono'
        elif (sys.platform == 'win32'):
            heightOffset = 40 #was 50
            fontName = 'Lucida Console'
        elif (sys.platform == 'linux2'):
            heightOffset = 40
            fontName = 'Monospace'
        for tag in range(len(sortedTags)):
            fontSize = int(sortedTags[tag][1][1]*10)
            fontSize = checkFontBounds(fontSize)
            wordWidth = getWordWidth(sortedTags, tag, fontSize)
            xOffset = wordWidth/2
            x += xOffset
            if ((x+xOffset)>=700):
                cloudHeight+=heightOffset
                x=xOffset+0
            x += xOffset
        self.myParent = parent
        getUserInfo.myContainer1.destroy()
        getUserInfo.button1.destroy()
        #cloudHeight = 375
        chartHeight = (len(userTags)*10+20)
        totalHeight = chartHeight + cloudHeight
        #print cloudHeight, chartHeight, totalHeight
        ### topmost frame
        #parent.myContainer1.destroy()
        self.topFrame = Frame(parent, bg='grey')
        self.topFrame.pack()

        ### output_frames
        self.output_frame = Canvas(self.topFrame, background="grey", width=700, height=cloudHeight)
        self.output_frame.pack(side=TOP)

        self.output_frame2 = Canvas(self.topFrame, background='grey', width=350, height=chartHeight)
        self.output_frame2.pack(side=LEFT)
        
        self.output_frame3 = Canvas(self.topFrame, background='grey', width=350, height=chartHeight)
        self.output_frame3.pack(side=BOTTOM)


        geometryString = ('700x' + str(totalHeight) + '+100+0')
        root.geometry(geometryString)
        self.drawCloud(fontName, sortedTags)
        self.drawChart1(fontName, artists)
        self.drawChart2(fontName, tagsByPop)


    def drawCloud(self, fontName, sortedTags):
        cloudX=10
        chartY = 10
        if (sys.platform == 'darwin'):
            cloudY = 30
            yOffset = 45
        elif (sys.platform == 'win32'):
            cloudY = 30
            yOffset = 40 #was 50
        elif (sys.platform == 'linux2'):
            cloudY = 30
            yOffset = 40 #was 50
        for tag in range(len(sortedTags)):
            fontSize = int(sortedTags[tag][1][1]*10)
            fontSize = checkFontBounds(fontSize)
            wordWidth = getWordWidth(sortedTags, tag, fontSize)
            xOffset = wordWidth/2
            tagText = sortedTags[tag][0]
            cloudX += xOffset
            fillColor = sortedTags[tag][1][2]

            if ((cloudX+xOffset)>=700):
                cloudY+=yOffset
                cloudX=xOffset+10
            self.output_frame.create_text(cloudX, cloudY, fill=fillColor, text=tagText, font=(fontName, fontSize))
            cloudX += xOffset

    def drawChart1(self, fontName, artists):
        chartY=10
        for tag in range(len(artists[0])):
            tagText = artists[0][tag]
            if len(tagText)>14:
                tagText = tagText[:14]
            for x in range(15-len(tagText)):
                tagText = tagText + '-'
            tagText = tagText + ":"

            self.output_frame2.create_text(5, chartY+3, text=tagText, anchor=W, font=(fontName, 9))
            barSize = 115+(230*(float(artists[1][tag])/float(artists[1][0])))
            fillColor = getFillColor(tag, len(artists[0])-1)
            self.output_frame2.create_rectangle(118, chartY-3, barSize, chartY+7, fill=fillColor)
            chartY+=10
        
    def drawChart2(self, fontName, tagsByPop):
        chartY=10
        for tag in range(len(tagsByPop)):
            tagText = tagsByPop[tag][0]
            if len(tagText)>14:
                tagText = tagText[:14]
            for x in range(15-len(tagText)):
                tagText = tagText + '-'
            tagText = tagText + ":"

            self.output_frame3.create_text(5, chartY+3, text=tagText, anchor=W, font=(fontName, 9))
            barSize = 115+(220*(float(tagsByPop[tag][1][0])/float(tagsByPop[0][1][0])))
            fillColor = tagsByPop[tag][1][2]
            self.output_frame3.create_rectangle(118, chartY-3, barSize, chartY+7, fill=fillColor)
            chartY+=10

root = Tk()
root.title("LastFMStats")
getUserInfo = GetUserInfo(root)
root.mainloop()
