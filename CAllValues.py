#!/usr/bin/env python

from numpy import matrix
from numpy import linalg
from numpy import *
from numpy.linalg import *

# Make all the Matrices 

xAll = genfromtxt('xAll.csv',dtype=int,delimiter=',')
xAllM = matrix(xAll)
y0 = genfromtxt('Y0.csv',dtype=float,delimiter=',')
y0M = matrix(y0)
y1 = genfromtxt('Y1.csv',dtype=float,delimiter=',')
y1M = matrix(y1)

shizmatrix_1=abs(xAllM);
shizmatrix=shizmatrix_1.cumsum(0);
shizmatrix2=shizmatrix[size(xAllM,0)-1,:];



# Calculate thetas

size = size(xAllM)
n = len(xAll)
p = size / n


print size
print p
print n

xAllTxAll = xAllM.T*xAllM 

######################################################################### lamba constant
vector = []
for i in range(0,len(xAllTxAll)):
	vector.append(xAllTxAll[i,i])
vector_s = sorted(vector)	
tile = int(round(.9 * len(vector_s),0))
print vector_s[tile]
lamba_same = .075 * vector_s[tile]


######################################################################### lamba changing
e = eye(p)
for i in range(0,p):
	e[i,i] = vector[i]
lamba_change = 0.15*e


######################################################################### first is same second is changing
xAllTxAll_L = xAllTxAll + lamba_same*eye(p)
#xAllTxAll_L = xAllTxAll + lamba_change



# finish X
xAllInv = inv(xAllTxAll_L)
xAllFinal = xAllInv*xAllM.T

print "1"

theta0 = xAllFinal*y0M.T
theta1 = xAllFinal*y1M.T

yHat0 = xAllM*theta0
yHat1 = xAllM*theta1

print "2"

thing1=yHat0.T-y0M;
thing2=thing1.T;
thing3=(n - p);
thing4= thing1*thing2;
sigma0 = thing4 / thing3;
thing5=yHat1.T-y1M;
thing6=(thing5).T;
thing7=thing5*thing6;
sigma1 =  thing7/thing3;

print "3"

crazymatrix1 = sigma0[0,0]*(xAllInv)
crazymatrix2 = sigma1[0,0]*(xAllInv)

crazymatrix1Diag=[];
for x in range(0,ma.size(crazymatrix1,0)):
	crazymatrix1Diag.append(crazymatrix1[x,x]);
crazymatrix2Diag=[];
for x in range(0,ma.size(crazymatrix2,0)):
	crazymatrix2Diag.append(crazymatrix2[x,x]);
	
# Print thetas

theta01csv = open('Theta01.csv','w')
for x in range(0,len(theta0)):
	theta01csv.write(str(theta1[x]).strip('[]') + '\n')

theta01csv.close();


# Print thetas with player name for 0 and 1

final = open('SchuckersValue.csv', 'w')
f1 = open("playersAll.csv")
f2 = open("Theta01.csv")

final.write("Team,Number,Player Name,Position,Number of Plays,E(A),St Dev" +'\n');
counter=0;
for line1 in f1:
	line2 = f2.readline();
	final.write(line1.strip('\n[]').replace('_',',') +","+str(shizmatrix2[0,counter])+ "," + line2.strip("\n][")+','+str(crazymatrix2Diag[counter])+'\n')
	counter=counter+1;

final.close();
