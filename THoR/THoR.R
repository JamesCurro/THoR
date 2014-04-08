library(ggplot2)
library(dplyr)
library(plyr)
library(reshape2)

thor = read.csv('THoRALL12to14.csv')
thor$Rank = order(thor$WAR,decreasing=T)

# Make ranking by position
thor = ddply(thor,.(Position),transform,
             PosRank = order(WAR,decreasing=T))
thor$TeamInd = 'ZTeams'
thor$TeamInd[thor$Team == 'BOSTON BRUINS'] = 'BOSTON BRUINS'

ggplot(thor, aes(x=WAR,y=PosRank)) + 
  geom_point(alpha = I(.6),size=I(3),aes(colour=TeamInd)) + 
  facet_wrap(~Position, ncol = 2) +
  ggtitle('WAR by position') +
  scale_colour_brewer(palette = "Set1") +
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

# Make team data
teamthor = ddply(thor,.(Team,Position),summarise,
                 WAR = sum(WAR))
teamthor = ddply(teamthor,.(Position),transform,
                 PosRank = rank(-WAR,ties.method='min'))

# Make divisions
atlantic = c('BOSTON BRUINS','BUFFALO SABRES','DETROIT RED WINGS','FLORIDA PANTHERS',
	'MONTREAL CANADIENS','OTTAWA SENATORS','TAMPA BAY LIGHTNING','TORONTO MAPLE LEAFS')
metro = c('CAROLINA HURRICANES','COLUMBUS BLUE JACKETS','NEW JERSEY DEVILS','NEW YORK ISLANDERS',
	'NEW YORK RANGERS','PHILADELPHIA FLYERS','PITTSBURGH PENGUINS','WASHINGTON CAPITALS')
central = c('CHICAGO BLACKHAWKS','COLORADO AVALANCHE','DALLAS STARS','MINNESOTA WILD',
	'NASHVILLE PREDATORS','ST. LOUIS BLUES','WINNIPEG JETS')
pacific = c('ANAHEIM DUCKS','CALGARY FLAMES','EDMONTON OILERS','LOS ANGELES KINGS',
	'PHOENIX COYOTES','SAN JOSE SHARKS','VANCOUVER CANUCKS')
teamthor$Division = 'Atlantic'
teamthor$Division[teamthor$Team %in% metro] = 'Metro'
teamthor$Division[teamthor$Team %in% central] = 'Central'
teamthor$Division[teamthor$Team %in% pacific] = 'Pacific'

# Make Division indicators
teamthor$Atlantic = as.character(teamthor$Team)
teamthor$Atlantic[teamthor$Division != 'Atlantic'] = 'Other'

teamthor$Metro = as.character(teamthor$Team)
teamthor$Metro[teamthor$Division != 'Metro'] = 'Other'

teamthor$Central = as.character(teamthor$Team)
teamthor$Central[teamthor$Division != 'Central'] = 'Other'

teamthor$Pacific = as.character(teamthor$Team)
teamthor$Pacific[teamthor$Division != 'Pacific'] = 'Other'

apply(teamthor, 2, function(x){if(x$Division) x$Atlantic = x$Team})

teamthor$TeamInd = 'Other'
teamthor$TeamInd[teamthor$Team == 'BOSTON BRUINS'] = 'BOSTON BRUINS'
teamthor$TeamInd[teamthor$Team == 'CHICAGO BLACKHAWKS'] = 'CHICAGO BLACKHAWKS'
teamthor$TeamInd[teamthor$Team == 'EDMONTON OILERS'] = 'EDMONTON OILERS'
teamthor$TeamInd[teamthor$Team == 'SAN JOSE SHARKS'] = 'SAN JOSE SHARKS'
teamthor$TeamInd[teamthor$Team == 'PITTSBURGH PENGUINS'] = 'PITTSBURGH PENGUINS'
teamthor$TeamInd[teamthor$Team == 'TORONTO MAPLE LEAFS'] = 'TORONTO MAPLE LEAFS'
teamthor$TeamInd[teamthor$Team == 'BUFFALO SABRES'] = 'BUFFALO SABRES'

# Specific team rankings
ggplot(teamthor, aes(y=WAR,x=PosRank)) + 
  geom_point(aes(size=1.5,colour=TeamInd)) + 
  facet_wrap(~Position, ncol = 2) +
  ggtitle('WAR by position') +
  scale_colour_brewer(palette = "Set1") +
  xlim(c(32,0))+
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

# Conference rankings
ggplot(teamthor, aes(y=WAR,x=PosRank)) + 
  geom_point(aes(size=1.5,colour=Division)) + 
  facet_wrap(~Position, ncol = 2) +
  ggtitle('THoR by position') +
  scale_colour_brewer(palette = "Set1") +
  xlim(c(32,0))+
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

# Atlantic Conference
ggplot(teamthor, aes(y=WAR,x=PosRank)) + 
  geom_point(aes(size=1.5,color=Atlantic)) + 
  scale_colour_manual(values = c('yellow','grey','red','orange','purple','black','brown','green','pink')) +
  facet_wrap(~Position, ncol = 2) +
  ggtitle('THoR by position') +
  xlim(c(32,0))+
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

# Metro Conference
ggplot(teamthor, aes(y=WAR,x=PosRank)) + 
  geom_point(aes(size=1.5,color=Metro)) + 
  scale_colour_manual(values = c('yellow','grey','red','orange','purple','black','brown','green','pink')) +
  facet_wrap(~Position, ncol = 2) +
  ggtitle('THoR by position') +
  xlim(c(32,0))+
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

# Central Conference
ggplot(teamthor, aes(y=WAR,x=PosRank)) + 
  geom_point(aes(size=1.5,color=Central)) + 
  scale_colour_manual(values = c('yellow','grey','red','orange','purple','black','brown','green')) +
  facet_wrap(~Position, ncol = 2) +
  ggtitle('THoR by position') +
  xlim(c(32,0))+
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

# Pacific Conference
ggplot(teamthor, aes(y=WAR,x=PosRank)) + 
  geom_point(aes(size=1.5,color=Pacific)) + 
  scale_colour_manual(values = c('yellow','grey','red','orange','black','purple','brown','green')) +
  facet_wrap(~Position, ncol = 2) +
  ggtitle('THoR by position') +
  xlim(c(32,0))+
  theme(plot.title = element_text(face="bold", size=30, vjust = 2)) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 18)) +
  theme(axis.text.y = element_text(size = 16))

library(dplyr)
library(plyr)
library(reshape2)
header = c('DayofWeek','MonthDay','Year','StartTime','EndTime','Rink','ID','GameofYear','AwayTeam','HomeTeam',
           'Period','Strength','TimetoPeriod','Event','EventCount','Description','ForPlayer','TakePlayer',
           'Assist1','Assist2','Location','ShotType','ShotLocation','Distance','AP1','AP2','AP3','AP4','AP5','AP6',
           'HP1','HP2','HP3','HP4','HP5','HP6','xcoord','ycoord','ForInd','AwayNum','HomeNum','TurnInd')

all = read.csv('AllStats.csv',header=F,
               col.names=c(header,rep('V',20)))
s = select(all,GameofYear,Period,Event,EventCount,ForPlayer,TakePlayer,Location,ShotType,AP1,AP2,AP3,AP4,AP5,AP6,HP1,HP2,HP3,HP4,HP5,HP6,
                ForInd,TurnInd,AwayNum,HomeNum)  
smelt = melt(s, id=c('GameofYear','Period','Event', 'EventCount', 'ForPlayer', 'TakePlayer','Location', 'ShotType', 
                     'ForInd', 'TurnInd', 'AwayNum', 'HomeNum'))
colnames(smelt) = c('GameofYear','Period','Event', 'EventCount', 'ForPlayer', 'TakePlayer','Location', 'ShotType', 
                    'ForInd', 'TurnInd', 'AwayNum', 'HomeNum', 'Dummy', 'Player')

# Change Event, ForInd to change what we are looking at
# Some ideas I had would be to look at the number of events by location
eventsonice = ddply(smelt,.(Event,ForInd,Player),summarize,
               count = length(Player))
head(eventsonice)
# By looking at ForPlayer, we can see the events where the player did the action for example shots
# The example I have below looks at each player and the number of shots they took by shottype
eventsaction = ddply(smelt[smelt$Event == 'SHOT',],.(ShotType,Player),summarize,
                  count = length(Player))
head(eventsaction)











