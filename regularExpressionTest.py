import re
import math
original = 'ssss[s:s:111]aaa ssss bbb[s:e:111][s:s:112]aaa ssddss bbb[s:e:112]ddssdddd[s:s:113]aaa ssddss bbb[s:e:113]ff'
wkval = original

wk = ''
wk2 = ''
endFlag = False
convertedwords = ''
beforword = 'ss'
afterword = '@@'
while endFlag == False:
    search = re.search('\[s:s:[0-9]+\]', wkval)
    if bool(search) == False:
        convertedwords = convertedwords + wkval.replace(beforword,afterword)
        endFlag = True
    else:
        convertedwords = convertedwords + wkval[:search.start()].replace(beforword,afterword)
        search = re.search('\[s:s:[0-9]+\]', wkval)
        wkval = wkval[search.start():]
        search = re.search('\[s:e:[0-9]+\]', wkval)
        convertedwords = convertedwords + wkval[:search.end()]
        wkval = wkval[search.end():]
print(original)
print(convertedwords)

# wkval = 'ssss[s:s:111]aaa ssss bbb[s:e:111]'
#list = re.findAll('ssss', wkval)

