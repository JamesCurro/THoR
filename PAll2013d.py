#! /usr/bin/env python
import os
import re
import urllib2
import time
import string
from numpy import *
import xml.etree.ElementTree as ET

################################################################################################## the list of years you want
#years=["20082009","20092010","20102011","20112012"];
#years=["20092010","20102011","20112012","20122013"];
# years=["20102011","20112012","20122013"];
#years=["20102011"];
#years=["20112012"];
#years=["20102011"];
#years=["20112012","20122013"];
years=["20132014"];
################################################################################# start and end game
startgame=1;
endgame=1231;
################################################################################################## playoffs
usePlayoffs=0;
##################################################################################################


#Define the regular Expression string used to find matches in the html 
#matces for the game info
gamematch='''<table border="0" cellpadding="0" cellspacing="0" width="100%" align="center" xmlns:ext="urn:schemas-microsoft-com:xslt">
<tr>
<td valign="top">
<table id="Visitor" border="0" cellpadding="0" cellspacing="0" align="center">
<tr>
<td align="center" style="font-size: 12px;font-weight:bold">VISITOR</td>
</tr>
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="20" align="center">
<tr>
[\s\S]*
</tr>
</table>
</td>
</tr>
<tr>
<td align="center" style="font-size: 10px;font-weight:bold">(?P<visitor>.*)<br(?: /)?>(?P<visitorgamestat>.*)</td>
</tr>
</table>
</td>
<td>
<table id="GameInfo" border="0" cellpadding="0" cellspacing="0" align="center">
<tr>
.*
</tr>
<tr>
<td style="font-size: 14px;font-weight:bold" align="center">&nbsp;</td>
</tr>
<tr>
<td align="center" style="font-size: 10px;font-weight:bold">[A-Za-z0-9/ ]*</td>
</tr>
<tr>
<td align="center" style="font-size: 10px;font-weight:bold">(?P<date>.*)</td>
</tr>
<tr>
(<td[^>]*>(?:[^0-9<> ]*(?P<attendance>.*))(?:(?: at |&nbsp;@&nbsp;|&nbsp;at&nbsp;)(?P<location>.*))</td>|.*)
</tr>
<tr>
(<td [^>]*>[\s\S]*[^0-9<>]*&nbsp;(?P<starttime>.*)&nbsp;(?P<timezone>[A-Z]{3})[\s\S]*; [^0-9<>]*&nbsp;(?P<endtime>.*)&nbsp;[A-Z]{3}</td>|[\s\S]*)
</tr>
<tr>
<td [^>]*>[^<>0-9]*(?P<gamenumber>.*)</td>
</tr>
<tr>
<td align="center" style="font-size: 10px;font-weight:bold">(?P<gamestatus>.*)</td>
</tr>
</table>
</td>
<td valign="top">
<table id="Home" border="0" cellpadding="" cellspacing="0" align="center">
<tr>
<td align="center" style="font-size: 12px;font-weight:bold">HOME</td>
</tr>
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="20" align="center">
<tr>
[\s\S]*
</tr>
</table>
</td>
</tr>
<tr>
<td align="center" style="font-size: 10px;font-weight:bold">(?P<home>.*)<br(?: /)?>(?P<homegamestat>.*)</td>
</tr>
</table>
</td>
</tr>
</table>'''
gamematch=gamematch.replace('\r','')

#<td style="font-size: 10px; font-weight: bold;" align="center">
							#Start&nbsp;6:09&nbsp;CET
							#		; End&nbsp;8:35&nbsp;CET</td>
									
#this is used to match an event header and pull out info on the event
headermatch ='''<td align="center" class="(:?goal)?(:?penalty)? \+ bborder">(?P<number>.*)</td>
<td class="(:?goal)?(:?penalty)? \+ bborder" align="center">(?P<period>.*)</td>
<td class="(:?goal)?(:?penalty)? \+ bborder" align="center">(?P<strength>.*)</td>
<td class="(:?goal)?(:?penalty)? \+ bborder" align="center">(?P<time>.*)<br(:? /)?>(?P<elapsed>.*)</td>
<td class="(:?goal)?(:?penalty)? \+ bborder"[^>]*>(?P<event>.*)</td>
<td class="(:?goal)?(:?penalty)? \+ bborder">(?P<description>.*?)</td>'''

headermatch=headermatch.replace('\r','')

# this is used to split the home team from the away team
teamsplit='''</tr>
(?:\</tbody\>)*</table>
</td>
<td class="(:?italicize \+ )?(:?bold)? \+ bborder">
<table border="0" cellpadding="0" cellspacing="0">
(?:\<tbody\>)*<tr>''';
teamsplit=teamsplit.replace('\r','');

#this is used to match a player and pull out the info on the player
playermatch='''<td align="center">
<table border="0" cellpadding="0" cellspacing="0">
(\<tbody\>)?<tr>
<td align="center">
<font style="cursor:hand;" title="(?P<position>.*) - (?P<name>.*)">(?P<number>.*)</font>
</td>
</tr>
<tr>
<td align="center">(?P<positionletter>.*)</td>
</tr>
(\</tbody\>)?</table>
</td>'''
playermatch=playermatch.replace('\r','')

teammatch='''(<td align="center">
<table border="0" cellpadding="0" cellspacing="0">
(<tbody>)?<tr>
<td align="center">
<font style="cursor:hand;" title="(.*) - (.*)">(.*)</font>
</td>
</tr>
<tr>
<td align="center">(.*)</td>
(</tbody>)?</tr>
</table>
</td>){1,}'''
teammatch=teammatch.replace('\r','')

forString='''(?P<for>['\w .-]*)''';
againstString='''(?P<against>['\w .-]*)''';
numberString='''(#?([0-9]{1,2})?)''';
facMatchNoTies='''(?:(?P<winner>[A-Z.]{3}) won )?(?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)) - (((?P=winner) '''+numberString+''' '''+forString+''' vs [A-Z.]{3} '''+numberString+''' '''+againstString+''')|([A-Z.]{3} '''+numberString+''' (?P<assist_2>['\w .-]*) vs (?P=winner) '''+numberString + ''' (?P<assist_1>['\w .-]*)))?((?P<assist_1a>.*)(?P<typeOfShot>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}'''
facMatchTies='''(?:(?P<winner>[A-Z.]{3}) won )?(?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)) - ((((?P=winner) '''+numberString+''' '''+forString+''')|([A-Z.]{3} '''+numberString+''' (?P<assist_1>['\w .-]*))) vs (((?P=winner) '''+numberString+''' '''+againstString+''')|(([A-Z.]{3} '''+numberString + ''' (?P<assgMatrixFile2	ist_2>['\w .-]*)))))((?P<assist_1a>.*)(?P<typeOfShot>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}'''
facMatch=facMatchNoTies;noTies=1;
blockMatch='''([A-Z.]{3})? '''+numberString+''' '''+againstString+''' BLOCKED BY  [A-Z.]{3} '''+numberString+''' '''+forString+'''(, (?P<typeOfShot>[-\w]*))?(, (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)))?((?P<assist_1>.*)(?P<assist_1a>.*)(?P<assist_2>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}''';
missMatch='''[A-Z.]{3} '''+numberString+''' '''+forString+'''(, Penalty Shot)?(, (?P<typeOfShot>[-\w]*))?(, (?P<shotLocation>[A-Za-z ]*))?(, (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)))?, (?P<distance>[0-9]{1,3}) ft.((?P<assist_1>.*)(?P<assist_1a>.*)(?P<assist_2>.*)(?P<against>.*)){0}''';
shotMatch='''[A-Z.]{3} ONGOAL - '''+numberString+''' '''+forString+''',( Penalty Shot,)?( (?P<typeOfShot>[-\w]*),)?( (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)),)? (?P<distance>[0-9]{1,3}) ft.((?P<against>.*)(?P<assist_1>.*)(?P<assist_1a>.*)(?P<assist_2>.*)(?P<shotLocation>.*)){0}''';
hitMatch='''[A-Z.]{3} '''+numberString+''' '''+forString+''' HIT [A-Z.]{3} '''+numberString+''' '''+againstString+'''(, (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)))?((?P<assist_1>.*)(?P<assist_1a>.*)(?P<assist_2>.*)(?P<typeOfShot>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}''';
giveMatch='''[A-Z.]{3}&nbsp;GIVEAWAY - '''+numberString+''' '''+forString+'''(, (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)))?((?P<against>.*)(?P<assist_1a>.*)(?P<assist_1>.*)(?P<assist_2>.*)(?P<typeOfShot>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}''';
takeMatch='''[A-Z.]{3}&nbsp;TAKEAWAY - '''+numberString+''' '''+forString + '''(, (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)))?((?P<against>.*)(?P<assist_1>.*)(?P<assist_1a>.*)(?P<assist_2>.*)(?P<typeOfShot>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}''';
penlMatch='''[A-Z.]{3} (:?'''+numberString+''' '''+forString+''')?(:?TEAM)?&nbsp;[^,;]*(, (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)))?( Drawn By: [A-Z.]{3} '''+numberString+''' '''+againstString+''')?((?P<assist_1>.*)(?P<assist_1a>.*)(?P<assist_2>.*)(?P<typeOfShot>.*)(?P<shotLocation>.*)(?P<distance>.*)){0}''';
penlTimeMatch='''(.*)\((?P<timer>\d\d?)( min)\)(.*)''';
goalMatch='''[A-Z.]{3} '''+numberString+''' '''+forString+'''(\([0-9]{1,3}\))?,( Penalty Shot,)?( (?P<typeOfShot>[-\w]*),)?( (?P<location>(?:Neu. Zone|Def. Zone|Off. Zone)),)? (?P<distance>[0-9]{1,3}) ft.(<br(?: /)?>Assists?: #[0-9]{1,2} (?P<assist_1>\w*)(\([0-9]{1,3}\))?; '''+numberString+''' (?P<assist_2>\w*)(\([0-9]{1,3}\))?|<br(?: /)?>Assists?: '''+numberString+''' (?P<assist_1a>\w*)(\([0-9]{1,3}\))?|)((?P<against>.*)(?P<shotLocation>.*)){0}''';
descriptionMatches=[facMatch,blockMatch,missMatch,shotMatch,hitMatch,giveMatch,takeMatch,penlMatch,goalMatch];

timematch = '''"time":"(?P<time2>[^"]*)"'''
periodmatch = '''"period":(?P<period2>[^:,]*),'''
xmatch = '''"xcoord":(?P<xcoord>[^:,]*),'''
ymatch = '''"ycoord":(?P<ycoord>[^:,]*),'''
typematch = '''"type":(?P<type>[^:,]*),'''

def zerosFill(size):
	return [0 for x in range(size)];
	
def convertToString(data):
	if data is None:
		return '';
	else:
		return str(data).replace(',','').strip()
def getDescription(matcher,allPlayersOnIce,eventName):
	if not(matcher is None):
		convertNames=[convertToString(matcher.group("for")),convertToString(matcher.group("against")),convertToString(matcher.group("assist_1"))+convertToString(matcher.group("assist_1a")),convertToString(matcher.group("assist_2"))];
		if(eventName=="FAC" and convertNames[0]=='' and noTies==1):
			convertNames[0]=convertNames[2];
			convertNames[1]=convertNames[3];
			convertNames[2]='';
			convertNames[3]='';
		for x in range(0,4):
			for player in allPlayersOnIce:
				if (player.find(convertNames[x])>-1 and not convertNames[x]==''):
					convertNames[x]=player;
					break;		
		return convertNames[0]+","+convertNames[1]+","+convertNames[2]+","+convertNames[3]+","+convertToString(matcher.group("location"))+","+convertToString(matcher.group("typeOfShot"))+","+convertToString(matcher.group("shotLocation"))+","+convertToString(matcher.group("distance"));
	else:
		print "ERROR"
		return ",,,,,,,"
				
#events i don't want to print out
badEvents=["PSTR", "PEND", "GEND","STOP","GOFF", "SOC", "EIEND", "EISTR"];
goodLocations=["Def. Zone","Neu. Zone","Off. Zone"];
parseDescriptionEvents=["FAC","BLOCK","MISS","SHOT","HIT","GIVE","TAKE","PENL","GOAL"];
#parseDescriptionEvents=["SHOT","HIT","PENL","GOAL"];
xyEvents=["GOAL","SHOT","HIT","PENL"]
homeTeamNameList=[["ANAHEIM DUCKS"],["BOSTON BRUINS"],["BUFFALO SABRES"],["CALGARY FLAMES"],["CAROLINA HURRICANES"],
            ["CHICAGO BLACKHAWKS"],["COLORADO AVALANCHE"],["COLUMBUS BLUE JACKETS"],["DALLAS STARS"],
            ["DETROIT RED WINGS"],["EDMONTON OILERS"],["FLORIDA PANTHERS"],["LOS ANGELES KINGS"],
            ["MINNESOTA WILD"],["MONTREAL CANADIENS","CANADIENS MONTREAL"],["NASHVILLE PREDATORS"],
            ["NEW JERSEY DEVILS"],["NEW YORK ISLANDERS"],["NEW YORK RANGERS"],["OTTAWA SENATORS"],
            ["PHILADELPHIA FLYERS"],["PHOENIX COYOTES"],["PITTSBURGH PENGUINS"],["SAN JOSE SHARKS"],
            ["ST. LOUIS BLUES"],["TAMPA BAY LIGHTNING"],["TORONTO MAPLE LEAFS"],["VANCOUVER CANUCKS"],
            ["WASHINGTON CAPITALS"],["ATLANTA THRASHERS","WINNIPEG JETS"]]
websites=[];
websites2=[];
base20122013gameNumber=400442475
#totalPlayersInNHL=2145;
#totalPlaysInLast3Seasons=892868;
numOfSeasons=4;
totalPlayersInNHL=3000;
totalPlaysInLast3Seasons=310000*numOfSeasons;
currentPlayer=0;
currentPlay=0;
xMatrix = zerosFill(totalPlayersInNHL);
positionL = zerosFill(totalPlayersInNHL);
letter = '';
gMatrix = zerosFill(totalPlaysInLast3Seasons);
gsmbMatrix = zerosFill(totalPlaysInLast3Seasons);
gsmMatrix = zerosFill(totalPlaysInLast3Seasons);
shiftVector = zerosFill(totalPlaysInLast3Seasons);
scoreEffect = zerosFill(totalPlaysInLast3Seasons);
shift_pp1 = zerosFill(totalPlaysInLast3Seasons);
shift_pp2 = zerosFill(totalPlaysInLast3Seasons);
away_m_home = []
penlMatrix= []
xMatrixOnes=[[0]*totalPlayersInNHL]*totalPlaysInLast3Seasons;
lastPlayHomePlayers = [];
lastPlayAwayPlayers = [];
homeChange=0;
awayChange=0;
pp_1_vector=zerosFill(totalPlaysInLast3Seasons);
pp_2_vector=zerosFill(totalPlaysInLast3Seasons);
distance_i = [];
#fx_bar = ['x','ducks','bruins','sabres','flames','hurricanes','blackhawks','avalanche','bluejackets','stars','redwings','oilers','panthers','kings','wild','canadiens',
#'predators','devils','islanders','rangers','senators','flyers','coyotes','penguins','sharks','blues','lightning','mapleleafs','canucks','capitals','jets']
f_x = zeros((101,2),float)
f_y = zeros((91,2),float)
f_ax = zeros((101,2),float)
f_ay = zeros((91,2),float)
r_x = zeros((101,31),float)
r_y = zeros((91,31),float)
rink_x = zeros((101,31),float)
rink_y = zeros((91,31),float)
for x in range(0,101):
	f_x[x][0] = x
	f_ax[x][0] = x
	rink_x[x][0] = x
	r_x[x][0] = x
q = 0
for x in range(-45,46):
	f_y[q][0] = x
	f_ay[q][0] = x
	rink_y[q][0] = x
	r_y[q][0] = x
	q = q + 1
xc_adj = 0
yc_adj = 0
xc_v = []
yc_v = []
home_v = []

#builds a list of the web sites to fetch
for year in years:
	beginning="http://www.nhl.com/scores/htmlreports/{0}/PL02".format(year);
	ending=".HTM"
	print 
	if(int(year[0:4])>=2012):
		beginning2="http://sports.espn.go.com/nhl/gamecast/data/masterFeed?gameId=";
		ending2="";
	else:
		beginning2="http://live.nhl.com/GameData/{0}/{1}02".format(year,year[0:4]);
		ending2="/PlayByPlay.jsonp";
	for x in range(startgame,endgame):
		numer= '%(#)04d' %  {"#": x}
		websites.append(beginning+numer+ending);
		if(int(year[0:4])>=2012):
			gameNumber=int(x)+base20122013gameNumber-1
			websites2.append(beginning2+str(gameNumber))
		else:
			websites2.append(beginning2+numer+ending2);

#adds the playoff games that can possibly happen if it doesn't exist the website will make a 404 or the file will not exist
if(usePlayoffs==1):
	for game in range(1,7):
		for series in range(1,8):
			for round in range(1,4):
				for year in years:
					beginning="http://www.nhl.com/scores/htmlreports/{0}/PL03".format(year);
					ending=".HTM"
					roundString= '%(#)02d' %  {"#": round}
					beginning2="http://live.nhl.com/GameData/{0}/{1}03".format(year,year[0:4]);
					ending2="/PlayByPlay.jsonp";
					websites.append(beginning+roundString+str(series)+str(game)+ending);
					websites2.append(beginning2+roundString+str(series)+str(game)+ending2);
#open the file i will write the csv to use w to reaplace the file and a to append the file
csvFile = open('gameAllStats.csv', 'w')
###############csvFile.write("DOW,DOM,Year,Start Time,End Time,Where,Attendance,Game Code,Away,Home,Period,Strength,Time,Event,Event_#,Description,For,Against,Assist_1,Assist_2,Location,Type of Shot,Shot Location,Distance,AWAY_1,AWAY_2,AWAY_3,AWAY_4,AWAY_5,AWAY_6,HOME_1,HOME_2,HOME_3,HOME_4,HOME_5,HOME_6,xcoord,yccord,for_I,Home_#,Away_#,Turn_I,homeTime,awayTime" +'\n');
errorLog = open('errorLog.log','w')
eventy = [];
periody = [];
gamecodey = [];
goalIndy = [];
timey = [];
timeToGoalHome = [];
timeToGoalAway = [];


#go for all the websites
forceBuildSites=0
for x in range(0,len(websites)):
	website=websites[x];
	website2=websites2[x];
	fName="websites//"+website.replace('/','').replace(':','').replace('?','')
	f2Name="websites//"+website2.replace('/','').replace(':','').replace('?','')
	
	#file method if sites are already downloaded
	if(forceBuildSites==0 and os.path.exists(fName) and os.path.exists(f2Name)):
		try:
			with open(fName,'r') as f:
				htmfile= f.read()
			with open(f2Name,'r') as f2:
				htmfile2= f2.read()
		except:
			print("File opening error")
			continue;#the file isn't there so go to next website/file
		htmfile=htmfile.replace('\r','')
		htmfile2=htmfile2.replace('\r','')
	else:
		#website method if we don't have a download or want to force a download
		try:
			print website
			f = urllib2.urlopen(website)
			print website2
			f2 = urllib2.urlopen(website2)
		except  urllib2.HTTPError, e:
			print "site had error possibly game hasn't been played yet"
			print e
			continue;
		#Open 
		htmfile= f.read()
		htmfile2= f2.read()
		#close the object used to open the web site
		f.close()
		f2.close()
		htmfile=htmfile.replace('\r','')
		htmfile2=htmfile2.replace('\r','')
		with open(fName,'w') as webSiteFile:
			webSiteFile.write(htmfile)
		with open(f2Name,'w') as webSiteFile2:
			webSiteFile2.write(htmfile2)

	gameinfo="";
	awayTeamName="";
	homeTeamName="";
	gameDate="";
	gameNumber="";
	
	#get x and y coords
	splitter=re.split("},{",htmfile2);
	periods = []
	times = []
	xs = []
	ys = []
	if(len(splitter)>10):
		for t in splitter:
			timesplit=re.search(timematch,t)
			if (timesplit is None):
				continue;
			periodsplit=re.search(periodmatch,t)
			xsplit=re.search(xmatch,t)
			ysplit=re.search(ymatch,t)
			times.append(timesplit.group("time2"));
			periods.append(periodsplit.group("period2"));
			xs.append(xsplit.group("xcoord"));
			ys.append(ysplit.group("ycoord"));
	else:
		root=ET.fromstring(htmfile2)
		for play in root.iter('Play'):
			# print play.text
			tildesplitter=re.split("~",play.text)
			periods.append(tildesplitter[4])
			times.append(tildesplitter[3])
			xs.append(tildesplitter[0])
			ys.append(tildesplitter[1])
	#determine if they count up or down
	countDown=1;
	if(len(times)>0):
		timestringlist=re.split(':',times[0]);
		timestring="";
		for timestringtemp in timestringlist:
			timestring=timestring+timestringtemp;
		if timestring=="END":
			timestring="0000"
		if(int(timestring) < 600):
			countDown=0;#this is counting up
	else:
		# skip this game cause we don't want any without the shot coords
		continue;
	#split the html file by this string in order to separate the events out
	me =re.split(r'<tr class="evenColor">',htmfile)
	#iterate over all the things i split off
	for event in me:
		#print event
		#try to get a match for the event header
		header=re.search(headermatch,event)
		penlll=re.search("PENL",event)
		#if i get a match continue if not try to see if its a gameg
		if (header is None) :
			#try and find a gamematch
			game=re.search(gamematch,event)
			#if i found a match pull info from it
			if not(game is None) and (gameinfo==""):
				#make a string with the static info AKA the stuff about this specific game
				awayTeamName=game.group('visitor').strip();
				homeTeamName=game.group('home').strip();
				gameDate=game.group("date");
				gameNumber=game.group("gamenumber");
				gameinfo= game.group("date").strip() + "," + convertToString(game.group("starttime")) + "," + convertToString(game.group("endtime")) + "," + convertToString(game.group("location")) + "," + convertToString(game.group("attendance")) + "," + game.group("gamenumber").strip() + "," + game.group('visitor').strip() + "," + game.group('home').strip() + ",";
				print "Game "+game.group("gamenumber")+" Date: "+game.group("date");
				currentHomeScore=0
				currentAwayScore=0
		else:
			if not(header.group("event") in badEvents):
				event=event.replace('\r','');
				#split into the away and home team
				teams=re.split(teamsplit,event)
				awayPlayers="";
				homePlayers="";
				awayPlayersList=[];
				homePlayersList=[];
				allPlayersOnIce=[];
				allPlayersOnIceLetter=[];
				#take the away team and pull off all the players
				awayTeam=teams[0];
				#find player matches
				players=re.finditer(playermatch,awayTeam)
				#make string with all the players in it separated by comma
				length=0;
				length2=0;
				for player in players:
					awayPlayers+= awayTeamName+"_"+player.group('number')+"_" + player.group('name') + ",";
					allPlayersOnIce.append(awayTeamName+"_"+player.group('number') + "_" + player.group('name'));
					allPlayersOnIceLetter.append(player.group('positionletter'));
					awayPlayersList.append(awayTeamName+"_"+player.group('number') + "_" + player.group('name'));
					length=length+1;
					for p in awayPlayersList:
						goalieAI = 0
						goalieA = ""
						if player.group('positionletter') == "G":
							goalieA = p + "_" +player.group('positionletter')
							goalieAI = goalieAI + 1
				for x in range(0,6-length):
						awayPlayers+=",";
				if(length==0):
					errormessage="Missing away team in Game "+gameNumber+" Date: "+gameDate+" Event # "+header.group('number');
					errorLog.write(errormessage+'\n');
					print errormessage;
				if(len(teams)<2):
					errormessage="Missing home team in Game "+gameNumber+" Date: "+gameDate+" Event # "+header.group('number');
					errorLog.write(errormessage+'\n');
					print errormessage;
				else:
					#repeat for the home team
					homeTeam=teams[3];
					players=re.finditer(playermatch,homeTeam)
					length2=0;
					for player in players:
						homePlayers+= homeTeamName+"_"+player.group('number') + "_" + player.group('name') + ",";
						allPlayersOnIce.append(homeTeamName+"_"+player.group('number') + "_" + player.group('name'));
						allPlayersOnIceLetter.append(player.group('positionletter'));
						homePlayersList.append(homeTeamName+"_"+player.group('number') + "_" + player.group('name'));
						length2=length2+1;
						for p in awayPlayersList:
							goalieHI = 0
							goalieH = ""
							if player.group('positionletter') == "G":
								goalieH = p + "_" +player.group('positionletter')
								goalieHI = goalieHI + 1
					for x in range(0,6-length2):
						homePlayers+=",";
				descriptionString=",,,,,,,"
				forPlayer='';
				eventLocation='';
				if header.group("event") in parseDescriptionEvents:
					descNumber=parseDescriptionEvents.index(header.group("event"));
					matcher= re.match(descriptionMatches[descNumber],header.group("description"));
					if matcher is None:
						errormessage= "Desc ERROR in Game "+gameNumber+" Date: "+gameDate+" Event # "+header.group('number')+" Event "+header.group('event')+"\n"+header.group("description");
						errorLog.write(errormessage+'\n');
						print errormessage;
					if header.group("event")=="PENL":
						matcher2=re.match(penlTimeMatch,header.group("description"));
						if matcher2 is None:
							errormessage="Penl description time error Game: "+gameNumber+" Date: "+gameDate+" Event # "+header.group('number')+" Event "+header.group('event')+"\n"+header.group("description");
							errorLog.write(errormessage+'\n');
							print errormessage;
							penlTime="2";
						else:
							penlTime=matcher2.group("timer");
					else:
						penlTime="0";
					descriptionString= getDescription(matcher,allPlayersOnIce,header.group("event"));	
					firstCommaIndex=descriptionString.index(',');
					secondCommaIndex=descriptionString.index(',',firstCommaIndex+1);
					forPlayer=descriptionString[0:firstCommaIndex];
					againstPlayer=descriptionString[firstCommaIndex+1:secondCommaIndex];
					eventLocation=matcher.group("location");
				#make the event info based on what we just did
				#sometimes when the strength is irrelevent they give a weird result so look for it and make it a blank
				strength=header.group("strength");
				if strength=="&nbsp;":
					strength='';
				timesplitup =re.split(':',header.group("time"));
				timeremaining=1200 - (int(timesplitup[0])*60+int(timesplitup[1]));
				timeremaining=str(timeremaining);
				nowEvent = header.group("event")
				if (header.group("event") == "GIVE" or header.group("event") == "TAKE"):
					nowEvent = "TURN"
				eventinfo= header.group("period") + "," + strength + "," + timeremaining + "," + nowEvent +","+header.group("number") + "," + header.group("description").replace(',','-')+","+descriptionString + ","  + awayPlayers  + homePlayers;
				if(gameinfo==""):
					errormessage="Missed game website "+website;
					errorLog.write(errormessage+'\n');
					print errormessage;
				xc="";
				yc="";
				debugtime="";
				debugperiod="";
				
				# do the xcoord ycoord thing
				for t in range(0,len(times)):
					if(countDown==1 and (times[t].lstrip("0") == header.group("elapsed").lstrip("0") and periods[t] == header.group("period") and header.group("event") in xyEvents)):
						xc = xs[t]
						yc = ys[t]
						debugtime=times[t];
						debugperiod=periods[t];
					elif(times[t].lstrip("0") == header.group("time").lstrip("0") and periods[t] == header.group("period") and header.group("event") in xyEvents):
						xc = xs[t]
						yc = ys[t]
						debugtime=times[t];
						debugperiod=periods[t];
	
				#For and Turn Indicators
				if(forPlayer in homePlayersList):
					for_I="0";
					penlI = "-1"
				else:
					for_I="1";
					penlI = "1"
				turn_I = "";
				if(header.group("event") == "GIVE" and forPlayer in homePlayersList): 
					turn_I = "0";
				elif(header.group("event") == "TAKE" and forPlayer in awayPlayersList):
					turn_I = "0";
				elif(header.group("event") == "GIVE" and forPlayer in awayPlayersList): 
					turn_I = "1";
				elif(header.group("event") == "TAKE" and forPlayer in homePlayersList):
					turn_I = "1";
				home_N = str(len(homePlayersList));
				away_N = str(len(awayPlayersList));
				
				#change stuff
				totalHomeMissing=0;
				totalAwayMissing=0;
				for lastPlayer in lastPlayHomePlayers:
					thisMatched=0;
					for currentPlayer2 in homePlayersList:
						if(lastPlayer==currentPlayer2):
							thisMatched=1;
					if(thisMatched==0):
						totalHomeMissing=totalHomeMissing+1;
				for lastPlayer in lastPlayAwayPlayers:
					thisMatched=0;
					for currentPlayer2 in awayPlayersList:
						if(lastPlayer==currentPlayer2):
							thisMatched=1;
					if(thisMatched==0):
						totalAwayMissing=totalAwayMissing+1;
				if(totalHomeMissing>1 or totalAwayMissing>1):
					if(header.group("event")=="FAC"):
						if((for_I=="0" and eventLocation=="Off. Zone") or (for_I=="1" and eventLocation=="Def. Zone")):
							homeChange=1;
						elif((for_I=="1" and eventLocation=="Off. Zone") or (for_I=="0" and eventLocation=="Def. Zone")):
							homeChange=-1;
						else:
							homeChange=0;
					else:
						homeChange=0;
				#shift Vector
				shiftVector[currentPlay]=homeChange;
				lastPlayHomePlayers=homePlayersList;
				#powerplay
				#1
				if((len(homePlayersList)-len(awayPlayersList))==1):
					pp_1_vector[currentPlay]=1;
				elif((len(homePlayersList)-len(awayPlayersList))==-1):
					pp_1_vector[currentPlay]=-1;
				else:
					pp_1_vector[currentPlay]=0;
				#2
				if((len(homePlayersList)-len(awayPlayersList))==2):
					pp_2_vector[currentPlay]=1;
				elif((len(homePlayersList)-len(awayPlayersList))==-2):
					pp_2_vector[currentPlay]=-1;
				else:
					pp_2_vector[currentPlay]=0;
				#shift*PP1for i in range (0,int(xc_adj)):
				if shiftVector[currentPlay] == 1 and pp_1_vector[currentPlay] == 1:
					shift_pp1[currentPlay] = 1
				elif shiftVector[currentPlay] == 1 and pp_1_vector[currentPlay] == -1:
					shift_pp1[currentPlay] = -1
				elif shiftVector[currentPlay] == -1 and pp_1_vector[currentPlay] == -1:
					shift_pp1[currentPlay] = -1
				elif shiftVector[currentPlay] == -1 and pp_1_vector[currentPlay] == 1:
					shift_pp1[currentPlay] = 1
				#shift*PP2
				if shiftVector[currentPlay] == 1 and pp_2_vector[currentPlay] == 1:
					shift_pp2[currentPlay] = 1
				elif shiftVector[currentPlay] == 1 and pp_2_vector[currentPlay] == -1:
					shift_pp2[currentPlay] = -1
				elif shiftVector[currentPlay] == -1 and pp_2_vector[currentPlay] == -1:
					shift_pp2[currentPlay] = -1
				elif shiftVector[currentPlay] == -1 and pp_2_vector[currentPlay] == 1:
					shift_pp2[currentPlay] = 1 
				#score Effect
				if(abs(currentHomeScore-currentAwayScore) > 2):
					scoreEffect[currentPlay]=currentHomeScore-currentAwayScore
				else:
					scoreEffect[currentPlay]=0
				#fix shots xy	
				if( (header.group('event') == "SHOT" or header.group('event') == "GOAL") and (matcher.group("distance") is None or  xc =="")):
					continue
				if ((header.group('event') == "SHOT" or header.group('event') == "GOAL")):
					if ((int(xc) < 0 and int(matcher.group("distance")) < 100) or (int(xc) >= 0 and int(matcher.group("distance"))) > 100):
						xc_adj = -int(xc)
						yc_adj = -int(yc)
					else:
						xc_adj = int(xc)
						yc_adj = int(yc)
					
					for i in range (int(xc_adj)+1,101):
						f_x[i][1] = f_x[i][1] + 1
					for i in range (int(yc_adj) + 46,91):
						f_y[i][1] = f_y[i][1] + 1
					if (for_I == "1"):
						for i in range (int(xc_adj)+1,101):
							f_ax[i][1] = f_ax[i][1] + 1
						for i in range (int(yc_adj) + 46,91):
							f_ay[i][1] = f_ay[i][1] + 1

					# RINK EFFECT FOR AWAY SHOTS
					teamIndex=[0 if ret==None else 1 for ret in ([thing.index(homeTeamName) if homeTeamName in thing else None for thing in homeTeamNameList])].index(1)
					teamIndex+=1	
					if(for_I=="1"):			
						for i in range (int(xc_adj)+1,101):
							rink_x[i][teamIndex] = rink_x[i][teamIndex] + 1
						for i in range (int(yc_adj) + 46,91):
							rink_y[i][teamIndex] = rink_y[i][teamIndex] + 1
					# RINK EFFECT FOR ALL SHOTS
					for i in range (int(xc_adj)+1,101):
						r_x[i][teamIndex] = r_x[i][teamIndex] + 1
					for i in range (int(yc_adj) + 46,91):
						r_y[i][teamIndex] = r_y[i][teamIndex] + 1
				##################################################### Write the CSV File
				if( not(length<4) and not (length>6) and not(length2<4) and not(length2>6) and (eventLocation in goodLocations)):
				#if( ((length == length2 == 6) or (length == length2 == 5) or (length == length2 == 4)) and  (eventLocation in goodLocations)):
				#if( ((length == 6 and length2 ==5) or (length == 5 and length2 ==6) or (length == 5 and length2 ==4) or (length == 4 and length2 ==5)) or (length == 4 and length2 ==6) or (length == 6 and length2 ==4) and (eventLocation in goodLocations)):
					csvFile.write(gameinfo + eventinfo + xc + "," + yc + "," + for_I + "," + str(len(homePlayersList)) +"," + str(len(awayPlayersList)) + "," + turn_I + "," +  goalieA + "," + goalieH + "," + str(goalieAI) + "," + str(goalieHI) + '\n');
					for x in range(0,len(allPlayersOnIce)):
						player =allPlayersOnIce[x]
						if (player not in xMatrix):
							xMatrix[currentPlayer]=player;
							positionL[currentPlayer]=allPlayersOnIceLetter[x];
							currentPlayer+=1;
					onesLines=zerosFill(totalPlayersInNHL);
					if(header.group("event")=="FAC"):
						try:
							for player in homePlayersList:
								if (header.group("event")=="FAC" and (player == forPlayer or player == againstPlayer)):
									indexr=xMatrix.index(player)
									onesLines[indexr]=1;
								#if (header.group("event")=="PENL" and player == forPlayer):
								#	indexr=xMatrix.index(player)
								#	onesLines[indexr]=1;
							for player in awayPlayersList:
								if (header.group("event")=="FAC" and (player == forPlayer or player == againstPlayer)):
									indexr=xMatrix.index(player)
									onesLines[indexr]=-1;
								#if (header.group("event")=="PENL" and player == forPlayer):
								#	indexr=xMatrix.index(player)
								#	onesLines[indexr]=-1;
						except:
							errormessage="Stupid Player in Game "+gameNumber+" Date: "+gameDate+" Event # "+header.group('number');
							print errormessage
							errorLog.write(errormessage+'\n');
					else:
						try:
							for player in homePlayersList:
								indexr=xMatrix.index(player)
								onesLines[indexr]=1;
							for player in awayPlayersList:
								indexr=xMatrix.index(player)
								onesLines[indexr]=-1;
						except:
							errormessage="Stupid Player in Game "+gameNumber+" Date: "+gameDate+" Event # "+header.group('number');
							print errormessage
							errorLog.write(errormessage+'\n');
					#add the home thing here
					homeTeamNameCommas=homeTeamName+",,"
					if(not homeTeamNameCommas in xMatrix):
						xMatrix[currentPlayer]=homeTeamNameCommas;
						positionL[currentPlayer]='';
						currentPlayer+=1;
					indexr=xMatrix.index(homeTeamNameCommas)
					onesLines[indexr]=1;
					#write this line to the xMatrix of player on off ice 1 and 0 and -1
					xMatrixOnes[currentPlay]=onesLines;
					eventName=header.group("event");
					if (str(len(homePlayersList)) == "6" and str(len(awayPlayersList)) == "6"):
						if( eventName == "GOAL" and forPlayer in homePlayersList):
							gMatrix[currentPlay]="1";
							currentHomeScore+=1
						elif(eventName == "GOAL"  and forPlayer in awayPlayersList):
							gMatrix[currentPlay]=("-1");
							currentAwayScore+=1
					else:
						gMatrix[currentPlay]="0";
					if (str(len(homePlayersList)) == "6" and str(len(awayPlayersList)) == "6"):	
						if((eventName == "GOAL" or eventName == "SHOT" or eventName == "MISS") and forPlayer in homePlayersList):
							gsmMatrix[currentPlay]="1";
						elif((eventName == "GOAL" or eventName == "SHOT" or eventName == "MISS") and forPlayer in awayPlayersList):
							gsmMatrix[currentPlay]="-1";
					else:
						gsmMatrix[currentPlay]="0";
					if (str(len(homePlayersList)) == "6" and str(len(awayPlayersList)) == "6"):		
						if((eventName == "GOAL" or eventName == "SHOT" or eventName == "MISS" or eventName == "BLOCK") and forPlayer in homePlayersList):
							gsmbMatrix[currentPlay]="1";
						elif((eventName == "GOAL" or eventName == "SHOT" or eventName == "MISS" or eventName == "BLOCK")  and forPlayer in awayPlayersList):
							gsmbMatrix[currentPlay]="-1";
					else:
						gsmbMatrix[currentPlay]="0";
				
					penlMatrix.append(int(penlTime)*.12*int(penlI))
					currentPlay+=1;
					eventy.append(eventName)
					timey.append(int(timeremaining))
					periody.append(header.group("period"))
					gamecodey.append(gameNumber)
					goalIndy.append(for_I)
					timeToGoalHome.append(1200)
					timeToGoalAway.append(1200)
					away_m_home.append(length2-length)
					home_v.append(game.group('home').strip())
					if ((header.group('event') == "SHOT" or header.group('event') == "GOAL")):
						xc_v.append(xc_adj)
						yc_v.append(yc_adj)
						if (int(matcher.group("distance")) > 100):
							distance_i.append(1)
					else:
						distance_i.append(0)
						xc_v.append('')
						yc_v.append('')

xc_v_adj = []
yc_v_adj = []
xgrid = []
ygrid = []
# divide by total shots in each column 
for j in range (0,101):
	f_x[j][1] = (f_x[j][1] / f_x[100][1])
	f_ax[j][1] = (f_ax[j][1] / f_ax[100][1])
for j in range (0,91):
	f_y[j][1] = (f_y[j][1] / f_y[90][1])
	f_ay[j][1] = (f_ay[j][1] / f_ay[90][1])
for i in range (1,31):
	for j in range (0,101):
		rink_x[j][i] = (rink_x[j][i] / rink_x[100][i])
for i in range (1,31):
	for j in range (0,91):
		rink_y[j][i] = (rink_y[j][i] / rink_y[90][i])
for i in range (1,31):
	for j in range (0,101):
		r_x[j][i] = (r_x[j][i] / r_x[100][i])
for i in range (1,31):
	for j in range (0,91):
		r_y[j][i] = (r_y[j][i] / r_y[90][i])
z=0
zz=0
mini=0	
minii=0								
for x in range(0,len(eventy)):
	z = 0
	zz =0
	if (eventy[x] == "SHOT" or eventy[x] == "GOAL"):
		homeTeamName=home_v[x]
		teamIndex=[0 if isTeamThere==None else 1 for isTeamThere in ([homeTeamNames.index(homeTeamName) if homeTeamName in homeTeamNames else None for homeTeamNames in homeTeamNameList])].index(1)
		teamIndex+=1
		z = r_x[xc_v[x]][teamIndex] + f_ax[xc_v[x]][1] - rink_x[xc_v[x]][teamIndex]
		zz = r_y[yc_v[x]+45][teamIndex] + f_ay[yc_v[x]+45][1] - rink_y[yc_v[x]+45][teamIndex]
		mini=0
		minii=-45
		if z >= 1.0:
			mini = 100
			xc_v_adj.append(str(mini))
		else:
			if xc_v[x] < 0:
				xc_v_adj.append(-1)
			else:
				while z > f_x[mini][1]:
					mini=mini+1
				xc_v_adj.append(str(mini))
		if zz >= 1.0:
			minii = 42
			yc_v_adj.append(str(minii))
		else:
			while zz > f_y[minii+45][1]:
				minii=minii+1
			yc_v_adj.append(str(minii))
	else:
		xc_v_adj.append("")
		yc_v_adj.append("")

for x in range(0,len(eventy)):
	if (eventy[x] == "SHOT" or eventy[x] == "GOAL"):
		if (int(xc_v_adj[x]) < 0):
			xgrid.append(100)
			ygrid.append(100)
		elif (int(xc_v_adj[x]) < 30):
			xgrid.append(101)
			ygrid.append(101)
		elif(int(xc_v_adj[x]) < 90):
			if (int(xc_v_adj[x]) < 50):
				xgrid.append(0)
			elif (int(xc_v_adj[x]) < 70):
				xgrid.append(1)
			else: #(int(xc_v_adj[x]) < 90):
				xgrid.append(2)
			if (int(yc_v_adj[x]) < -10):
				ygrid.append(-1)
			elif (int(yc_v_adj[x]) <= 10):
				ygrid.append(0)
			else: #(int(yc_v_adj[x]) <= 46):
				ygrid.append(1)
		else: # (int(xc_v_adj[x]) > 90):
			xgrid.append(102)
			ygrid.append(102)
	else:
		xgrid.append("")
		ygrid.append("")
	
with open("XCumFile.csv",'w') as cumfilex:
	for x in range(0,len(f_x)):
		cumfilex.write(str(f_x[x][0]) + ',' + str(f_x[x][1]) + ',' + str(f_ax[x][1]) + ',' + str(rink_x[x][1]) + ',' + str(rink_x[x][2])+ ',' + str(rink_x[x][3])+ ',' + str(rink_x[x][4])+ ',' + str(rink_x[x][5])+ ',' + str(rink_x[x][6])+ ',' + str(rink_x[x][7])+ ',' + str(rink_x[x][8])+ ',' + str(rink_x[x][9])+ ',' + str(rink_x[x][10])+ ',' + str(rink_x[x][11])+ ',' + str(rink_x[x][12])+ ',' + str(rink_x[x][13])+ ',' + str(rink_x[x][14])+ ',' + str(rink_x[x][15])+ ',' + str(rink_x[x][16])+ ',' + str(rink_x[x][17])+ ',' + str(rink_x[x][18])+ ',' + str(rink_x[x][19])+ ',' + str(rink_x[x][20])+ ',' + str(rink_x[x][21])+ ',' + str(rink_x[x][22])+ ',' + str(rink_x[x][23])+ ',' + str(rink_x[x][24])+ ',' + str(rink_x[x][25])+ ',' +str(+ rink_x[x][26])+ ',' + str(rink_x[x][27])+ ',' + str(rink_x[x][28])+ ',' + str(rink_x[x][29])+ ',' + str(rink_x[x][30]) + '\n')
with open("YCumFile.csv",'w') as cumfiley:
	for x in range(0,len(f_y)):
		cumfiley.write(str(f_y[x][0]) + ',' + str(f_y[x][1]) + ',' + str(f_ay[x][1]) + ',' + str(rink_y[x][1]) + ',' + str(rink_y[x][2])+ ',' + str(rink_y[x][3])+ ',' + str(rink_y[x][4])+ ',' + str(rink_y[x][5])+ ',' + str(rink_y[x][6])+ ',' + str(rink_y[x][7])+ ',' + str(rink_y[x][8])+ ',' + str(rink_y[x][9])+ ',' + str(rink_y[x][10])+ ',' + str(rink_y[x][11])+ ',' + str(rink_y[x][12])+ ',' + str(rink_y[x][13])+ ',' + str(rink_y[x][14])+ ',' + str(rink_y[x][15])+ ',' + str(rink_y[x][16])+ ',' + str(rink_y[x][17])+ ',' + str(rink_y[x][18])+ ',' + str(rink_y[x][19])+ ',' + str(rink_y[x][20])+ ',' + str(rink_y[x][21])+ ',' + str(rink_y[x][22])+ ',' + str(rink_y[x][23])+ ',' + str(rink_y[x][24])+ ',' + str(rink_y[x][25])+ ',' + str(rink_y[x][26])+ ',' + str(rink_y[x][27])+ ',' + str(rink_y[x][28])+ ',' + str(rink_y[x][29])+ ',' + str(rink_y[x][30]) + '\n')
with open("DistanceVector.csv",'w') as distFile:
	for x in range(0,len(distance_i)):
		distFile.write(str(distance_i[x]) + '\n')
with open('PenaltyVector.csv','w') as penlFile:
	for x in range(0,len(penlMatrix)):
		penlFile.write(str(penlMatrix[x]) + '\n')
print ("Total Plays Found "+str(currentPlay))
print ("Total Players found "+str(currentPlayer))
print ("Writing gMatrix File")			
with open('PlusMinusAll.csv','w') as gMatrixFile1,open('FenwickAll.csv','w') as gMatrixFile2,open('CorsiAll.csv','w') as gMatrixFile3:
	for x in range(0,currentPlay):
		gMatrixFile1.write(str(gMatrix[x]) + '\n');
		gMatrixFile2.write(str(gsmMatrix[x]) + '\n');
		gMatrixFile3.write(str(gsmbMatrix[x]) + '\n');

# Want xMatrix for all plays
print "Writing xMatrix File"		
with open('xAll.csv','w') as xMatrixFile:
	for x in range(0,currentPlay):
		onesLines=xMatrixOnes[x];
		xMatrixFile.write(','.join(map(str,onesLines[0:currentPlayer])));
		xMatrixFile.write(',1,'+ str(shiftVector[x])+ ',' +str(scoreEffect[x]) + ',' +str(pp_1_vector[x]) + ',' + str(shift_pp1[x])+',' +str(pp_2_vector[x]) +','+str(shift_pp2[x])+',\n');
		#xMatrixFile.write(',1,'+ str(shiftVector[x]) + ',' +str(scoreEffect[x]) + ',\n');

# Want Player,PlayerLetter,Goals,Assists,Shots,Miss,ShotsWereBlocked,BlockedShots,FacWon,FacLoss,Fac%,HitsFor,HitsAgainst,Hit%,Take,Give,Possestion%
print "Writing player list File"			
with open("playersAll.csv",'w') as playerListVerticalFile:
	for x in range(0,currentPlayer):
		playerListVerticalFile.write(str(xMatrix[x])+ ',' + str(positionL[x]) + '\n');
	playerListVerticalFile.write("CONSTANT,,,\n");
	playerListVerticalFile.write("ZS,,,\n");
	playerListVerticalFile.write("SE,,,\n");
	playerListVerticalFile.write("PP1,,,\n");
	playerListVerticalFile.write("ZS*PP1,,,\n");
	playerListVerticalFile.write("PP2,,,\n");
	playerListVerticalFile.write("ZS*PP2,,,\n");
	#playerListVerticalFile.write("AWAY-HOME,,,\n");
	#playerListVerticalFile.write("SHIFT,,,\n");	

nowGoal = 0;
previousGoal = -1;
for x in range(0,len(eventy)):
	if (eventy[x] == "GOAL" and goalIndy[x] == "0"):
		nowGoal = x
		for y in range(previousGoal + 1,nowGoal + 1):
			if(periody[y] == periody[nowGoal] and gamecodey[y] == gamecodey[nowGoal]):
				timeToGoalHome[y] = timey[y] - timey[nowGoal];
		previousGoal = nowGoal

#Calculate time to next goal away
nowGoal = 0;
previousGoal = -1;
for x in range(0,len(eventy)):
	if (eventy[x] == "GOAL" and goalIndy[x] == "1"):
		nowGoal = x
		for y in range(previousGoal + 1,nowGoal + 1):
			if(periody[y] == periody[nowGoal] and gamecodey[y] == gamecodey[nowGoal]):
				timeToGoalAway[y] = timey[y] - timey[nowGoal];
	previousGoal = nowGoal

print("Writing timeAllFile ")
with open('timeAllFile.csv','w') as timeFile:
	for x in range(0,len(timeToGoalHome)):
		timeFile.write(str(timeToGoalHome[x]) + "," + str(timeToGoalAway[x]) + "," + str(eventy[x])+ "," + str(timey[x])+ "," + str(periody[x])+ "," + str(gamecodey[x])+ "," + str(goalIndy[x]) + ',' + str(xc_v[x]) + ',' + str(yc_v[x]) + ',' + str(xc_v_adj[x]) + ',' + str(yc_v_adj[x])+ ',' + str(xgrid[x]) + ',' + str(ygrid[x]) + ',\n');

#close csv file
csvFile.close();
errorLog.close();

print("Writing final files")
with open('AllStats.csv', 'w') as final, open("gameAllStats.csv") as f1, open("timeAllFile.csv") as f2 :
	for line1 in f1:
		line2 = f2.readline();
		final.write(line1.strip('\n') + "," + line2)



















