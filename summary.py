from datetime import datetime,timedelta
from collections import OrderedDict
from operator import itemgetter
import os, sys

now = datetime.now()

dateNow = datetime.strptime('%s %s %s' % (now.day,now.month,now.year),'%d %m %Y')
dateFutur = dateNow + timedelta(days=int(sys.argv[1]))

data = {}

with open('summary.log') as f:
    content = f.readlines()
i = 0
for line in content:
    if ('expires' in line):
    	tapes =  " ".join(line.split()).split(' ')[0]
        dates = " ".join(line.split()).split(' ')[2]
	dates = datetime.strptime('%s %s %s' % (dates.split('/')[0],dates.split('/')[1],dates.split('/')[2]),'%d %m %Y') 
	if dates.date() >= dateNow.date() and dates.date() <=  dateFutur.date():
	    data[tapes] = dates.strftime('%d %b %Y')
	    i = i+1
d = OrderedDict(sorted(data.items(), key=itemgetter(1)))
print d.values
if i > 0:
    print "From %s to %s, %s tapes are candidates for being expired" % (dateNow.strftime('%d %b %Y'),dateFutur.strftime('%d %b %Y'),i)
else:
    print "There is no candidate tape to be expired for this range of time"
for key, value in d.iteritems():
    print "Print tape %s as its expired the %s" % (key, value)


