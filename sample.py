import QuartzCronPy

cron_expression = "0 0 18 7 * ? *"

cron_expression2 = "0 0 18 7 * ? 2020,2021,2026"

cron_expression3 = "0 0 18 * JAN-OCT/3 ? 2017-2024/2"

cron_expression4 = "* * * ? * * *"

cronExp = QuartzCronPy.QuartzCronPy(cron_expression)

print(cronExp.getNextTrigger())

cronExp = QuartzCronPy.QuartzCronPy(cron_expression2)

print(cronExp.getNextTrigger())

cronExp = QuartzCronPy.QuartzCronPy(cron_expression3)

print(cronExp.getNextTrigger())

cronExp = QuartzCronPy.QuartzCronPy(cron_expression4)

print(cronExp.getNextTrigger())


