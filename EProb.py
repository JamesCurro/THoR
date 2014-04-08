#!/usr/bin/env python

# k is number of seconds until goal
k = 20;
# /theta in:  NP_k value to be (#Goals )/(#Events + \theta)
theta = 0;
# /delta in:  GOAL to NP_k*(1 + \delta)
delta=0;

import math
eps = .0000000000000001

def getValue(probPlusser,probMinuser):
	#try:
	#	logger = sum([math.log(temp) for temp in probPlusser]) - sum([math.log(temp) for temp in probMinuser])
	#except: #this is what it does when it tries to go log(0)
	logger =sum([math.log(temp) if not(temp < eps and temp > -eps) else -1/eps for temp in probPlusser]) - sum([math.log(temp) if not(temp < eps and temp > -eps) else -1/eps for temp in probMinuser])
	normaler = sum(probPlusser)-sum(probMinuser)
	return (normaler,logger)


# The main event goal data structure
def init_eg():
	eg = { }
	for event in ['HIT','TURN','BLOCK','MISS','FAC','SHOT','GOAL','PENL']:
		eg[event] = { }
		for location in ['Def. Zone', 'Neu. Zone', 'Off. Zone', '']:
			eg[event][location] = { }
			for home in ['4','5','6']:
				eg[event][location][home] = { }
				for away in ['4','5','6']:
					eg[event][location][home][away] = { }
					for for_i in ['0','1']:
						eg[event][location][home][away][for_i] = { }
						for shot_type in ['','Slap','Wrist','Snap','Tip-In','Backhand','Deflected','Wrap-around']:
							eg[event][location][home][away][for_i][shot_type] = { }
							for turn_i in ['','0','1']: 
								eg[event][location][home][away][for_i][shot_type][turn_i] = { }
								for x in ['','0','1','2','3','4','5','100','101','102']:
									eg[event][location][home][away][for_i][shot_type][turn_i][x] = { }
									for y in ['','-4','-3','-2','-1','0','1','2','3','4','100','101','102']:
										eg[event][location][home][away][for_i][shot_type][turn_i][x][y] = 0
	return eg  
    
#-----------------------------------
# M A I N    P R O G R A M
#-----------------------------------

# Make the different hash that we need

totalEvents = init_eg()
homeEvents = init_eg()
awayEvents = init_eg()
probcsv=open('Probabilities.csv','w')
value1=open('Y0.csv','w')
value2=open('Y1.csv','w')
value2log=open('logY1.csv','w')
awayGoalFlag = 0;
homeGoalFlag = 0;
playValue = 0;
playValue2 = 0;
logplayValue2 = 0;

# Make p
p = {};

# Make our homeEvents to goal and awayEvents to goal along with totalEvents

for line in file("AllStats.csv"):
	vals  = line.split(',')
	(event,location,shot_type,for_i,home,away,turn_i,x,y) = (vals[13].strip('"'), vals[20].strip('"'), vals[21].strip('"'), vals[38].strip('"'), vals[39].strip('"'), vals[40].strip('"'),vals[41].strip('"'),vals[57].strip('"'),vals[58].strip('"'))
	# print (event,location,shot_type,for_i,home,away,turn_i,x,y)
	totalEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] = totalEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] + 1
	if(int(vals[46].strip('"')) < k):
		homeEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] += 1
	if(int(vals[47].strip('"')) < k):
		awayEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] += 1
	#if(int(vals[46].strip('"')) < k) or (int(vals[47].strip('"')) < k):
	#	if str(home) + 'v' + str(away) in p.keys():
	#		p[str(home) + 'v' + str(away)] += 1
	#	else:
	#		p[str(home) + 'v' + str(away)] = 1
			
# Make each of the different probabilities
	
for event in ['HIT','TURN','BLOCK','MISS','FAC','SHOT','GOAL','PENL']:
	for location in ['Def. Zone', 'Neu. Zone', 'Off. Zone', '']:
		for home in ['4','5','6']:
			for away in ['4','5','6']:
				for for_i in ['0','1']:
					for shot_type in ['','Slap','Wrist','Snap','Tip-In','Backhand','Deflected','Wrap-around']: 
						for turn_i in ['','0','1',]:
							for x in ['','0','1','2','3','4','5','100','101','102']:
								for y in ['','-4','-3','-2','-1','0','1','2','3','4','100','101','102']:
									# Fix NP_K for home and away
									# Can we keep it the same for faceoffs the way that we account for value taking away what the other team would gain?
									probHome = (homeEvents[event][location][home][away][for_i][shot_type][turn_i][x][y]) / (totalEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] + theta + eps)
									probAway = (awayEvents[event][location][home][away][for_i][shot_type][turn_i][x][y]) / (totalEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] + theta + eps)
									#probAway = awayEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] / (totalEvents[event][location][home][away][for_i][shot_type][turn_i][x][y] + .0000000000001)
									if ((event == "GOAL") or (event == "SHOT")):
										demon = (totalEvents['SHOT'][location][home][away][for_i][shot_type][turn_i][x][y] + totalEvents['GOAL'][location][home][away][for_i][shot_type][turn_i][x][y] + eps)
										(value,valueLog) = getValue([homeEvents['SHOT'][location][home][away][for_i][shot_type][turn_i][x][y]/demon, homeEvents['GOAL'][location][home][away][for_i][shot_type][turn_i][x][y]/demon],[awayEvents['SHOT'][location][home][away][for_i][shot_type][turn_i][x][y]/demon,awayEvents['GOAL'][location][home][away][for_i][shot_type][turn_i][x][y]/demon])
										if (event =="GOAL"):
											# Edit value of GOAL by changing value[event][location][home][away][for_i][shot_type][turn_i][x][y]*1.25
											value *= (1+delta)
											valueLog *= (1+delta)
									elif (event == "FAC"):
										if (location == 'Def. Zone'):
											new_location = 'Off. Zone'
										if (location == 'Off. Zone'):
											new_location = 'Def. Zone'
										if (for_i == '0'):
											new_for_i = '1'
										if (for_i == '1'):
											new_for_i = '0'
										new_away = home
										new_home = away
										probHomeFlip = (homeEvents[event][new_location][new_home][new_away][new_for_i][shot_type][turn_i][x][y]) / (totalEvents[event][new_location][new_home][new_away][new_for_i][shot_type][turn_i][x][y] + theta + eps)
										probAwayFlip = (awayEvents[event][new_location][new_home][new_away][new_for_i][shot_type][turn_i][x][y]) / (totalEvents[event][new_location][new_home][new_away][new_for_i][shot_type][turn_i][x][y] + theta + eps)
										(value,valueLog) = getValue([probHome,probHomeFlip],[probAway,probAwayFlip])
									else:
										(value,valueLog) = getValue([probHome],[probAway])
										
									if (event == "BLOCK" or event == "MISS" or event == "SHOT" or event == "GOAL" or shot_type == ""):
										if (event == "SHOT" or event == "GOAL" or (x == "" and y == "")):
											if not ((event == "SHOT" or event == "GOAL") and (x == "" or y =="")):
												if (event == "TURN" or turn_i == ""): 
													if not (event == "TURN" and turn_i == ""):
														# Edit value of event by editing: str(value[event][location][home][away][for_i][shot_type][turn_i][x][y]) using math.
														probcsv.write(event + "," + location + "," + for_i + "," + home + "," + away + "," + shot_type + "," + turn_i + "," + x + ',' + y + ',' + str(probHome) + "," + str(probAway) + "," + str(homeEvents[event][location][home][away][for_i][shot_type][turn_i][x][y]) + "," + str(awayEvents[event][location][home][away][for_i][shot_type][turn_i][x][y]) + "," + str(totalEvents[event][location][home][away][for_i][shot_type][turn_i][x][y]) + "," + str(value) + "," + str(valueLog) + '\n') ;

probcsv.close()

# Write to make our Y0 and Y1, this is the part we can modify in order to predict next year goals
penaltyFile = open("PenaltyVector.csv")
penaltyVector=[];
for line in penaltyFile:
	penaltyVector.append(float(line.strip()))

# Read from value file that has three years	
bigval = init_eg()
logbigval = init_eg()
with open("Probabilities.csv",'r') as probber:
	for line in probber:
		vals  = line.split(',')
		if(len(vals)>=9):
			(event,location,for_i,home,away,shot_type,turn_i,x,y) = (vals[0].strip('"'), vals[1].strip('"'), vals[2].strip('"'), vals[3].strip('"'), vals[4].strip('"'), vals[5].strip('"'),vals[6].strip('"'),vals[7].strip('"'),vals[8].strip('"'))
			#print (event,location,home,away,for_i,shot_type,turn_i,x,y)
			bigval[event][location][home][away][for_i][shot_type][turn_i][x][y] =float(vals[14].strip('"\n'))
			logbigval[event][location][home][away][for_i][shot_type][turn_i][x][y] =float(vals[15].strip('"\n'))
count=0;
for line in file("AllStats.csv"):
	vals  = line.split(',')
	(event,location,shot_type,for_i,home,away,turn_i,x,y) = (vals[13].strip('"'), vals[20].strip('"'), vals[21].strip('"'), vals[38].strip('"'), vals[39].strip('"'), vals[40].strip('"'),vals[41].strip('"'),vals[57].strip('"'),vals[58].strip('"'))
	if(int(vals[46].strip('"')) < k):
		homeGoalFlag = 1
	if(int(vals[47].strip('"')) < k):
		awayGoalFlag = 1
	if (abs(penaltyVector[count]) < .1) or True:  
		playValue = (homeGoalFlag - awayGoalFlag) - (bigval[event][location][home][away][for_i][shot_type][turn_i][x][y])
		playValue2 = bigval[event][location][home][away][for_i][shot_type][turn_i][x][y]
		logplayValue2 = logbigval[event][location][home][away][for_i][shot_type][turn_i][x][y]
	else:
		playValue = (homeGoalFlag - awayGoalFlag) - penaltyVector[count]
		playValue2= penaltyVector[count]
		logplayValue2 = math.log(penaltyVector[count])
	value1.write(str(playValue)+'\n');
	value2.write(str(playValue2) + '\n');
	value2log.write(str(logplayValue2) + '\n');
	homeGoalFlag = 0
	awayGoalFlag = 0
	count=count+1;
value1.close()
value2.close()
value2log.close()