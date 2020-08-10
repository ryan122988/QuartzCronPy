The purpose of this project is to produce a QuartzCron next date calculation function in Python that works.  All other versions 
that were available didn't handle the full set of functionality available in QuartzCron.  This version will work with all valid QuartzCron Expressions.

The only functions availble in version 1.0 is getNextTrigger which will give the next available runtime in the form of a string of format Y%M%D h:m:s

Version 1 the way to create a QuartzCronPy object is as follows:

cronExp = QuartzCronPy.QuartzCronPy(cron_expression)

calling getNextTrigger is done as follows:

nextTrigger = cronExp.getNextTrigger()
