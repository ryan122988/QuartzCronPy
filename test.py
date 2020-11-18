import datetime
#import QuartzCronPy2
import QuartzCronPy


cron_expression = "0 0 18 7 * ? *"

cron_expression2 = "0 0 18 7 * ? 2020,2021,2026"

cron_expression3 = "0 0 18 7 * ? 2020-2026"

cron_expression4 = "0 0 18 7 * ? 2020/2"

cron_expression5 = "0 0 18 7 * ? 2021"

cron_expression6 = "* 0 18 7 * ? *"

cron_expression7 = "15,16 0 18 7 * ? *"

cron_expression8 = "5/15 0 18 7 * ? *"

cron_expression8 = "5-20 0 18 7 * ? *"

cron_expression9 = "0 0 18 7 * ? 2017-2024/2"

cron_expression10 = "0 0 18 * JAN-OCT/3 ? 2017-2024/2"

cron_expression11 = "0 0 0 * 2 ? 2020"

cron_expression12 = "0 0 0 2,7,28,29,31 2 ? 2020"

cron_expression13 = "0 0 0 3-31/2 2 ? 2021"

cron_expression14 = "0 0 0 3/2 2 ? 2021"

cron_expression15 = "0 0 0 4-29 2 ? 2021"

cron_expression16 = "0 0 0 L 2 ? 2021"

cron_expression17 = "0 0 0 31W 1 ? 2021"

cron_expression18 = "0 0 0 1W 5 ? 2021"

cron_expression19 = "0 0 0 5 * ? 2021"

cron_expression20 = "0 0 0 LW * ? 2021"

cron_expression21 = "0 0 0 ? 8 L 2020"

cron_expression22 = "0 0 0 ? 8 MON 2020"

cron_expression23 = "0 0 0 ? 8 MON,SAT,TUE 2020"

cron_expression24 = "0 0 0 ? 8 1-3 2020"

cron_expression25 = "0 0 0 ? 8 SUN-TUE 2020"

cron_expression26 = "0 0 0 ? 9 SUN/2 2020"

cron_expression27 = "0 0 0 ? 9 1/2 2020"

cron_expression28 = "0 0 0 ? 9 1-6/2 2020"

cron_expression29 = "0 0 0 ? 9 */2 2020"

cron_expression30 = "0 0 0 ? 8 SUN#4 2020"

cron_expression31 = "0 0 0 ? 9 TUE#5 2020"

cron_expression32 = "0 0 0 ? 9 3#5 2020"

cron_expression33 = "0 0 0 ? 9 6L 2020"

cron_expression34 = "* * * ? * * *"

cron_expression35 = "0 1,5,7,*/2 0 15 9 ? 2020"

cron_expression36 = "0 0 0 2,3,4-6,8-25/2 9 ? 2020"

cron_expression37 = "0 0 22 ? * THU *"
#date = datetime.datetime(2020, 3,23,23,24,55)

#print(date.weekday())

cronExp = QuartzCronPy.QuartzCronPy(cron_expression37)


print('')
print('')
print('------------------------------------------------')
print('')
print('')
first = cronExp.getNextTrigger()
print(first)
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())
print(cronExp.getNextTrigger())

start = datetime.datetime.now()
'''for x in range(1000000):
	cronExp.getNextTrigger()'''
dateTimes = cronExp.generateAllExecutions()


#for x in range(10000):
#	print(cronExp.getNextTrigger())

end = datetime.datetime.now()

print(end-start)
print(len(dateTimes))

print('first: '+first)
print('first in all executions: '+dateTimes[0])
'''
count = 0
while count < 10000:
	print(dateTimes[count])
	count += 1

count = 2000000
while count < 2001000:
	print(dateTimes[count])
	count += 1'''