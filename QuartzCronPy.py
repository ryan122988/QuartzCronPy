import datetime
from datetime import timedelta
from dateutil.parser import parse
class QuartzCronPy:
	
	def __init__(self, cronExpression, startDate = None, endDate = None):
		if self.isValidCronExpression(cronExpression) == False:
			raise ValueError("invalid cron expression")
		self.cronExpression = cronExpression
		self.startDate = startDate

		#if startDate is not specified default to now
		if startDate is None:
			self.startDate = datetime.datetime.now()
		self.endDate = endDate

		#if endDate is not specified default to 5 years past the start date
		if endDate is None:
			self.endDate = self.startDate.replace(year = self.startDate.year + 5)
		self.splitCronExpression = cronExpression.split(' ')
		self.executionsTable = self.buildExecutionsTable()

		self.currentExecution = None
		self.currentExecutionIndex = None

	#Return None if there is no farther execution with the time frame specified
	#else return the next exectuion in the exectution table 
	def getNextTrigger(self):
		if self.currentExecution is None:
			if len(self.executionsTable) > 0:
				self.currentExecutionIndex = 0
				self.currentExecution = self.executionsTable[self.currentExecutionIndex]
		else:
			if len(self.executionsTable) > self.currentExecutionIndex+1:
				self.currentExecutionIndex += 1 
				self.currentExecution = self.executionsTable[self.currentExecutionIndex]
			else:
				return None
		return self.currentExecution

	def buildExecutionsTable(self):
		secondsExpression = self.splitCronExpression[0]
		minutesExpression = self.splitCronExpression[1]
		hoursExpression = self.splitCronExpression[2]
		dayOfMonthExpression = self.splitCronExpression[3]
		monthExpression = self.splitCronExpression[4]
		dayOfWeekExpression = self.splitCronExpression[5]

		#defualt to every year for the case that it isn't given 
		expression = '*'

		#if year expression is given set it 
		if len(self.splitCronExpression) == 7:
			expression = self.splitCronExpression[6]

		possibleExecutionYears = self.getExecutionYears(expression)
		#print(possibleExecutionYears)

		possibleExecutionSeconds = self.getMinuteOrSecondExecutionValues(secondsExpression)
		#print(possibleExecutionSeconds)

		possibleExecutionMinutes = self.getMinuteOrSecondExecutionValues(minutesExpression)
		#print(possibleExecutionMinutes)

		possibleExecutionHours = self.getHourExecutionValues(hoursExpression)
		#print(possibleExecutionHours)

		possibleExecutionMonths = self.getMonthExecutionValues(monthExpression)
		#print(possibleExecutionMonths)

		executionDates = None

		if dayOfMonthExpression == '?':
			#get execution dates based off day of week expression
			executionDates = self.calculateDatesByDayOfWeek(dayOfWeekExpression, possibleExecutionMonths, possibleExecutionYears)

		else:
			#get execution dates based off of day of month expression
			executionDates = self.calculateDatesByDayOfMonth(dayOfMonthExpression, possibleExecutionMonths, possibleExecutionYears)
		#print(executionDates)

		executionDateTimes = self.buildExecutionDateTimes(executionDates, possibleExecutionSeconds, possibleExecutionMinutes, possibleExecutionHours)

		#print(executionDateTimes)
		return executionDateTimes

	def buildExecutionDateTimes(self, executionDates, seconds, minutes, hours):
		executionDateTimes = []
		count = 0
		for date in executionDates:
			runDay = parse(date)
			if runDay < self.startDate:
				continue
			for hour in hours:
				for minute in minutes:
					for second in seconds:
						#print(count)
						executionDateTime = date+' '+str(hour)+':'+str(minute)+':'+str(second)
						edtAsDatetime = parse(executionDateTime)
						if edtAsDatetime>=self.startDate and edtAsDatetime <= self.endDate:
							executionDateTimes.append(executionDateTime)
							count += 1
						if count == 1000:
							break
					if count == 1000:
						break
				if count == 1000:
					break
			if count == 1000:
				break
		return executionDateTimes

	def calculateDatesByDayOfWeek(self, expression, months, years):
		executionDates = []
		monthLengths = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
		daysOfWeek = {'SUN':1,'MON':2,'TUE':3,'WED':4,'THU':5,'FRI':6,'SAT':7}

		#This case devolves to simply every day of the month
		if expression == '*':
			for year in years:
				for month in months:
					#adding 1 to the lenght of the month in this calculation because 
					#range isn't inclusive.  Wanted the correct month lengths in the dict
					days = [x for x in range(1,(monthLengths[month]+1))]
					if month == 2:
						if self.isYearLeapYear(year):
							days.append(29)
					for day in days:
						date = str(year)+'-'+str(month)+'-'+str(day)
						executionDates.append(date)

		elif (',' in expression and '-' in expression) or (',' in expression and '/' in expression):
			splitExpression = expression.split(',')
			resultsDict = {}
			for expression in splitExpression:

				#Recursivly call getMinuteOrSecondExecutionValues on smaller expression.  
				results = self.calculateDatesByDayOfWeek(expression, months, years)
					
				#put results in dictionary to remove dupes
				for result in results:
					#want dictionary keys to be datetime must convert before inserting
					#this guarantees correct sorting
					resultsDict[parse(result)] = True

			#we want dict keys in sorted order and must convert from datetime back to string
			resultsList = [str(x.date()) for x in sorted(resultsDict.keys())]
			return resultsList

		elif '*/' in expression:
			splitExpression = expression.split('/')
			startDay = 1
			increment = int(splitExpression[1])
			desiredDays = []
			while startDay <= 7:
				desiredDays.append(startDay)
				startDay += increment
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected in desiredDays:
							executionDates.append(str(date.date()))
						startDay +=1

		elif ',' in expression:
			desiredDaysOfWeek = expression.split(',')
			desiredDays = []
			for day in desiredDaysOfWeek:
				if day in daysOfWeek:
					desiredDays.append(daysOfWeek[day])
				else:
					desiredDays.append(int(day))
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected in desiredDays:
							executionDates.append(str(date.date()))
						startDay +=1


		elif '-' in expression and '/' in expression:
			splitExpression = expression.split('/')
			splitExpression2 = splitExpression[0].split('-')
			increment = int(splitExpression[1])
			start = splitExpression2[0]
			stop = splitExpression2[1]

			#If the ends of the range aren't numbers convert to numbers
			if start in daysOfWeek:
				start = daysOfWeek[start]
			else:
				start = int(start)
			if stop in daysOfWeek:
				stop = daysOfWeek[stop]
			else:
				stop = int(stop)

			desiredDays = []
			while start <= stop:
				desiredDays.append(start)
				start += increment

			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected in desiredDays:
							executionDates.append(str(date.date()))
						startDay +=1

		elif '-' in expression:
			splitExpression = expression.split('-')
			start = splitExpression[0]

			#If the ends of the range aren't numbers convert to numbers
			if start in daysOfWeek:
				start = daysOfWeek[start]
			else:
				start = int(start)
			stop = splitExpression[1]
			if stop in daysOfWeek:
				stop = daysOfWeek[stop]
			else:
				stop = int(stop)

			desiredDays = []
			while start <= stop:
				desiredDays.append(start)
				start += 1
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected in desiredDays:
							executionDates.append(str(date.date()))
						startDay +=1


		elif expression == 'L':
			desiredDayOfWeek = 7
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected == desiredDayOfWeek:
							executionDates.append(str(date.date()))
						startDay += 1

		elif '#' in expression:
			splitExpression = expression.split('#')
			day = splitExpression[0]
			dayNumber = int(splitExpression[1])

			#If the ends of the range aren't numbers convert to numbers
			if day in daysOfWeek:
				day = daysOfWeek[day]
			else:
				day = int(day)

			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					dayCount = 0
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected == day:
							dayCount += 1
							if dayCount == dayNumber:
								executionDates.append(str(date.date()))
						startDay += 1



		elif 'L' in expression:
			splitExpression = expression.split('L')
			day = splitExpression[0]

			#If the ends of the range aren't numbers convert to numbers
			if day in daysOfWeek:
				day = daysOfWeek[day]
			else:
				day = int(day)

			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					dayCount = 0
					lastDay = None
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected == day:
							lastDay = date
						startDay += 1
					executionDates.append(str(lastDay.date()))

		elif '/' in expression:
			splitExpression = expression.split('/')
			startDay = splitExpression[0]
			increment = int(splitExpression[1])
			if startDay in daysOfWeek:
				startDay = daysOfWeek[startDay]
			else:
				startDay = int(startDay)

			desiredDays = []
			while startDay <= 7:
				desiredDays.append(startDay)
				startDay += increment
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected in desiredDays:
							executionDates.append(str(date.date()))
						startDay +=1

		else:
			desiredDayOfWeek = None
			if expression in daysOfWeek:
				desiredDayOfWeek = daysOfWeek[expression]
			else:
				desiredDayOfWeek = int(expression)
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					startDay = 1
					while startDay <= lengthOfMonth:
						date = datetime.datetime(year, month, startDay)
						
						#This weekday scale is built in python weekday where 0 is Monday
						#and 6 is Sunday.  Cron calls 1 Sunday and 7 Saturday.  Must convert
						dayOfWeek = date.weekday()
						dayOfWeekCorrected = self.convertPythonDayOfWeekToCronDayOfWeek(dayOfWeek)
						if dayOfWeekCorrected == desiredDayOfWeek:
							executionDates.append(str(date.date()))
						startDay +=1

		return executionDates

	def convertPythonDayOfWeekToCronDayOfWeek(self, dayOfWeek):
		conversion = {0:2 ,1:3 ,2:4 ,3:5 ,4:6 ,5:7 ,6:1}
		return conversion[dayOfWeek]

	def calculateDatesByDayOfMonth(self, expression, months, years):
		executionDates = []
		monthLengths = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

		if expression == '*':
			for year in years:
				for month in months:
					#adding 1 to the lenght of the month in this calculation because 
					#range isn't inclusive.  Wanted the correct month lengths in the dict
					days = [x for x in range(1,(monthLengths[month]+1))]
					if month == 2:
						if self.isYearLeapYear(year):
							days.append(29)
					for day in days:
						date = str(year)+'-'+str(month)+'-'+str(day)
						executionDates.append(date)
		
		elif (',' in expression and '-' in expression) or (',' in expression and '/' in expression):
			splitExpression = expression.split(',')
			resultsDict = {}
			for expression in splitExpression:

				#Recursivly call getMinuteOrSecondExecutionValues on smaller expression.  
				results = self.calculateDatesByDayOfMonth(expression, months, years)
					
				#put results in dictionary to remove dupes
				for result in results:
					#want dictionary keys to be datetime must convert before inserting
					#this guarantees correct sorting
					resultsDict[parse(result)] = True

			#we want dict keys in sorted order and must convert datetimes back to string
			resultsList = [str(x.date()) for x in sorted(resultsDict.keys())]
			return resultsList

		elif '*/' in expression:
			splitExpression = expression.split('/')
			increment = int(splitExpression[1])
			for year in years:
				for month in months:
					startDay = 1
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					while startDay <= lengthOfMonth:
						if startDay >= 1:
							date = str(year)+'-'+str(month)+'-'+str(startDay)
							executionDates.append(date)
						startDay += increment
		
		elif ',' in expression:
			days = expression.split(',')
			days = [int(day) for day in days]
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					for day in days:
						if day >= 1 and day <= lengthOfMonth:
							date = str(year)+'-'+str(month)+'-'+str(day)
							executionDates.append(date)

		elif '-' in expression and '/' in expression:
			splitExpression = expression.split('/')
			daysRange = splitExpression[0].split('-')
			increment = int(splitExpression[1])
			startDay = int(daysRange[0])
			endDay = int(daysRange[1])
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					while startDay <= endDay:
						if startDay >= 1 and startDay <= lengthOfMonth:
							date = str(year)+'-'+str(month)+'-'+str(startDay)
							executionDates.append(date)
						startDay += increment

		elif '-' in expression:
			days = expression.split('-')
			startDay = int(days[0])
			endDay = int(days[1])
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					while startDay <= endDay:
						if startDay >= 1 and startDay <=lengthOfMonth:
							date = str(year)+'-'+str(month)+'-'+str(startDay)
							executionDates.append(date)
						startDay += 1

		elif '/' in expression:
			splitExpression = expression.split('/')
			startDay = int(splitExpression[0])
			increment = int(splitExpression[1])
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					while startDay <= lengthOfMonth:
						if startDay >= 1:
							date = str(year)+'-'+str(month)+'-'+str(startDay)
							executionDates.append(date)
						startDay += increment

		elif expression == 'LW':
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					date = datetime.datetime(year, month, lengthOfMonth)
					dayOfWeek = date.weekday()

					#The last day of the month is a weekday
					if dayOfWeek >= 0 and dayOfWeek <=4:
						executionDates.append(str(date.date()))
					elif dayOfWeek == 5:
						date = date - timedelta(days=1)
						executionDates.append(str(date.date()))
					elif dayOfWeek == 6:
						date = date - timedelta(days=2)
						executionDates.append(str(date.date()))

		elif expression == 'L':
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					date = str(year)+'-'+str(month)+'-'+str(lengthOfMonth)
					executionDates.append(date)

		elif 'W' in expression:
			splitExpression = expression.split('W')
			day = int(splitExpression[0])
			for year in years:
				for month in months:
					date = datetime.datetime(year, month, day)
					dayOfWeek = date.weekday()

					#day of week will be 0 for Monday and 6 for Sunday weekdays will
					#be 0, 1, 2, 3, 4
					if dayOfWeek >=0 and dayOfWeek<=4:
						executionDates.append(str(date.date()))
					elif dayOfWeek == 5:
						if day == 1: 
							date = date + timedelta(days=2)
							executionDates.append(str(date.date()))
						else:
							date = date - timedelta(days=1)
							executionDates.append(str(date.date()))
					else:
						if day == 31:
							date = date - timedelta(days = 2)
							executionDates.append(str(date.date()))
						else:
							date = date + timedelta(days=1)
							executionDates.append(str(date.date()))
		#in this case a single day is called out
		else:
			day = int(expression)
			for year in years:
				for month in months:
					lengthOfMonth = monthLengths[month]
					if month == 2:
						if self.isYearLeapYear(year):
							lengthOfMonth += 1
					if day >= 1 and day <= lengthOfMonth:
						date = str(year)+'-'+str(month)+'-'+str(day)
						executionDates.append(date)

		return executionDates

	def isYearLeapYear(self, year):
		if year%4 == 0 and year%100 != 0:
			return True
		elif year%4 == 0 and year%100 == 0:
			if year%400 == 0:
				return True
			else:
				return False
		else:
			return False

	def getMonthExecutionValues(self, expression):
		possibleExecutions = []
		monthCharReplacement = {'JAN':1, 'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
		if expression == '*':
			possibleExecutions = [x for x in range(1,13)]

		elif (',' in expression and '-' in expression) or (',' in expression and '/' in expression):
			splitExpression = expression.split(',')
			resultsDict = {}
			for expression in splitExpression:

				#Recursivly call getMinuteOrSecondExecutionValues on smaller expression.  
				results = self.getMonthExecutionValues(expression)
					
				#put results in dictionary to remove dupes
				for result in results:
					resultsDict[int(result)] = True

			#we want dict keys in sorted order
			resultsList = [x for x in sorted(resultsDict.keys())]
			return resultsList

		elif '*/' in expression:
			splitExpression = expression.split('/')
			increment = int(splitExpression[1])
			start = 1
			while start <= 12:
				possibleExecutions.append(start)
				start += increment

		elif ',' in expression:
			splitExpression = expression.split(',')
			#we know this expression is valid so all values listed will be valid values
			for exp in splitExpression:
				if exp in monthCharReplacement:
					possibleExecutions.append(monthCharReplacement[exp])
				else:
					possibleExecutions.append(int(exp))

		elif '-' in expression and '/' in expression:
			splitExpression1 = expression.split('/')
			splitExpression2 = splitExpression1[0].split('-')
			startVal = splitExpression2[0]
			#print('startval is: '+startVal)
			if startVal in monthCharReplacement:
				startVal = monthCharReplacement[startVal]
			else:
				startVal = int(startVal)
			endVal = splitExpression2[1]
			if endVal in monthCharReplacement:
				endVal = monthCharReplacement[endVal]
			else:
				endVal = int(endVal)
			increment = int(splitExpression1[1])

			while startVal <= endVal:
				possibleExecutions.append(startVal)
				startVal += increment

		elif '-' in expression:
			splitExpression = expression.split('-')
			#splitExpression2 = splitExpression1[0].split('-')
			startVal = splitExpression[0]
			#print('startval is: '+startVal)
			if startVal in monthCharReplacement:
				startVal = monthCharReplacement[startVal]
			else:
				startVal = int(startVal)
			endVal = splitExpression[1]
			if endVal in monthCharReplacement:
				endVal = monthCharReplacement[endVal]
			else:
				endVal = int(endVal)
			#Since this expression is valid start val > end val and both in 1-12
			while startVal <= endVal:
				possibleExecutions.append(startVal)
				startVal += 1

		elif '/' in expression:
			splitExpression = expression.split('/')
			startVal = splitExpression[0]
			if startVal in monthCharReplacement:
				startVal = monthCharReplacement[startVal]
			else:
				startVal = int(startVal)
			increment = int(splitExpression[1])

			while startVal <= 12:
				possibleExecutions.append(startVal)
				startVal += increment
		#since this expression is valid the last possiblity is a single number 1-12
		else:
			if expression in monthCharReplacement:
				exp = monthCharReplacement[expression]
				possibleExecutions.append(exp)
			else:
				possibleExecutions.append(int(expression))
		return possibleExecutions

	
	def getHourExecutionValues(self, expression):
		possibleExecutions = []
		if expression == '*':
			possibleExecutions = [x for x in range(24)]

		elif (',' in expression and '-' in expression) or (',' in expression and '/' in expression):
			splitExpression = expression.split(',')
			resultsDict = {}
			for expression in splitExpression:

				#Recursivly call getMinuteOrSecondExecutionValues on smaller expression.  
				results = self.getHourExecutionValues(expression)
					
				#put results in dictionary to remove dupes
				for result in results:
					resultsDict[int(result)] = True

			#we want dict keys in sorted order
			resultsList = [x for x in sorted(resultsDict.keys())]
			return resultsList

		elif '*/' in expression:
			splitExpression = expression.split('/')
			increment = int(splitExpression[1])
			start = 0
			while start <= 23:
				possibleExecutions.append(start)
				start += increment

		elif ',' in expression:
			splitExpression = expression.split(',')
			#we know this expression is valid so all values listed will be valid values
			for exp in splitExpression:
				possibleExecutions.append(int(exp))

		elif '-' in expression and '/' in expression:
			splitExpression1 = expression.split('/')
			splitExpression2 = splitExpression1[0].split('-')
			startVal = int(splitExpression2[0])
			endVal = int(splitExpression2[1])
			increment = int(splitExpression1[1])

			while startVal <= endVal:
				possibleExecutions.append(startVal)
				startVal += increment

		elif '-' in expression:
			splitExpression = expression.split('-')
			startVal = int(splitExpression[0])
			endVal = int(splitExpression[1])
			#Since this expression is valid start val > end val and both are greater than or equal 
			#to 0 and less than 24
			while startVal <= endVal:
				possibleExecutions.append(startVal)
				startVal += 1

		elif '/' in expression:
			splitExpression = expression.split('/')
			startVal = int(splitExpression[0])
			increment = int(splitExpression[1])

			while startVal <= 23:
				possibleExecutions.append(startVal)
				startVal += increment
		#since this expression is valid the last possiblity is a single number 0-23
		else:
			possibleExecutions.append(int(expression))
		return possibleExecutions

	#This same function works for both seconds and minutes since they have the same
	#allowable operations and the same 0-59 range
	def getMinuteOrSecondExecutionValues(self, expression):
		possibleExecutions = []
		if expression == '*':
			possibleExecutions = [x for x in range(60)]

		elif (',' in expression and '-' in expression) or (',' in expression and '/' in expression):
			splitExpression = expression.split(',')
			resultsDict = {}
			for expression in splitExpression:

				#Recursivly call getMinuteOrSecondExecutionValues on smaller expression.  
				results = self.getMinuteOrSecondExecutionValues(expression)
					
				#put results in dictionary to remove dupes
				for result in results:
					resultsDict[int(result)] = True

			resultsList = [x for x in sorted(resultsDict.keys())]
			return resultsList

		elif '*/' in expression:
			splitExpression = expression.split('/')
			increment = int(splitExpression[1])
			start = 0
			while start <= 59:
				possibleExecutions.append(start)
				start += increment

		elif ',' in expression:
			splitExpression = expression.split(',')
			#we know this expression is valid so all values listed will be valid values
			for exp in splitExpression:
				possibleExecutions.append(int(exp))

		elif '-' in expression and '/' in expression:
			splitExpression1 = expression.split('/')
			splitExpression2 = splitExpression1[0].split('-')
			startVal = int(splitExpression2[0])
			endVal = int(splitExpression2[1])
			increment = int(splitExpression1[1])

			while startVal <= endVal:
				possibleExecutions.append(startVal)
				startVal += increment


		elif '-' in expression:
			splitExpression = expression.split('-')
			startVal = int(splitExpression[0])
			endVal = int(splitExpression[1])
			#Since this expression is valid start val > end val and both are greater than or equal 
			#to 0 and less than 60
			while startVal <= endVal:
				possibleExecutions.append(startVal)
				startVal += 1

		elif '/' in expression:
			splitExpression = expression.split('/')
			startVal = int(splitExpression[0])
			increment = int(splitExpression[1])

			while startVal <= 59:
				possibleExecutions.append(startVal)
				startVal += increment
		#since this expression is valid the last possiblity is a single number 0-59
		else:
			possibleExecutions.append(int(expression))
		return possibleExecutions


	def getExecutionYears(self, expression):
		possibleExecutionYears = []
		startDateYear = self.startDate.year
		endDateYear = self.endDate.year

		if expression == '*':
			#all years from start date to end date are valid
			while startDateYear <= endDateYear:
				possibleExecutionYears.append(startDateYear)
				startDateYear += 1

		elif (',' in expression and '-' in expression) or (',' in expression and '/' in expression):
			splitExpression = expression.split(',')
			resultsDict = {}
			for expression in splitExpression:

				#Recursivly call getMinuteOrSecondExecutionValues on smaller expression.  
				results = self.getExecutionYears(expression)
					
				#put results in dictionary to remove dupes
				for result in results:
					resultsDict[int(result)] = True

			resultsList = [x for x in sorted(resultsDict.keys())]
			return resultsList


		elif '*/' in expression:
			splitExpression = expression.split('/')
			increment = int(splitExpression[1])
			while startDateYear <= endDateYear:
				possibleExecutionYears.append(startDateYear)
				startDateYear += increment

		elif '-' in expression and '/' in expression:
			splitExpression1 = expression.split('/')
			splitExpression2 = splitExpression1[0].split('-')
			startVal = int(splitExpression2[0])
			endVal = int(splitExpression2[1])
			increment = int(splitExpression1[1])

			while startVal <= endVal:
				if startVal >= startDateYear and startVal <= endDateYear:
					possibleExecutionYears.append(startVal)
				startVal += increment


		elif ',' in expression:
			splitexpression = expression.split(',')
			for year in splitexpression:
				#must cast the year in this case to an int for the comparison to work
				if int(year) >= startDateYear and int(year) <= endDateYear:
					possibleExecutionYears.append(year)

		elif '-' in expression:
			splitexpression = expression.split('-')
			#should only be two years if this is a valid cron expression 
			#which is checked in the constructor. Must convert to int
			startYear = int(splitexpression[0])
			endYear = int(splitexpression[1])

			while startYear <= endYear:
				if startYear >= startDateYear and startYear <= endDateYear:
					possibleExecutionYears.append(startYear)
				startYear += 1

		elif '/' in expression:
			splitexpression=expression.split('/')
			#should only be two years if this is a valid cron expression 
			#which is checked in the constructor. Must convert to int
			startYear = int(splitexpression[0])
			increment = int(splitexpression[1])

			while startYear <= endDateYear:
				if startYear >= startDateYear:
					possibleExecutionYears.append(startYear)
				startYear += increment
		#last option is for a single year specified if this expression is valid
		else:
			possibleExecutionYears.append(int(expression))

		return possibleExecutionYears
		

	#check if is a valid cron expression
	def isValidCronExpression(self, cronExpression):
		#currently just return true
		return True