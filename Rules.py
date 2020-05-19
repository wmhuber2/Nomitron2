#
# Blank Module For Discord Bot
################################
import pickle, sys, urllib
channels   = {}
logChannel = ""
Data = {}
AllData = {}
savefile = str(__name__) # + '_Data.pickle'

"""
Initiate New Player
"""
async def addMember(inData, member):
    global Data
    loadData(inData)
    # Do Stuff Here

    return saveData()



"""
Function Called on Reaction
"""
async def reaction(inData, action, user, messageid, emoji):
    global Data
    loadData(inData)
    # Do Stuff Here

    return saveData()



"""
Main Run Function On Messages
"""
async def run(inData, payload, message):
    global Data
    loadData(inData)
    # Do Stuff Here

    splitPayload = payload['Content'].split()
    if len(splitPayload) == 0: pass

    elif(splitPayload[0] == "!rule" and len(splitPayload) == 2):
        rulequery = int(splitPayload[1])
        if(rulequery not in Data.keys()):
            await channels[payload['Channel']].send("I couldn't find that rule.")
        else:
            print("Found Rule", rulequery)
            answer = "Rule " + Data[rulequery]
            response = ""
            for paragraph in answer.split("\n\n"):
                paragraph = paragraph.replace('\\xe2\\x95\\x9e', ' ')
                paragraph = paragraph.replace('\\xe2\\x95\\x90', ' ')
                paragraph = paragraph.replace('\\xe2\\x95\\xa1', ' ')
                paragraph = paragraph.replace('\\xe2\\x94\\x80', ' ')
                if(len(response) + len(paragraph) + 6 > 1850):
                    #print(response)
                    await channels[payload['Channel']].send(response)
                    response = ""
                if len(paragraph) >1900:
                    print('Error: Paragrpah too long!!! Length: ', len(paragraph))
                    print(paragraph)
                else:
                    response = response + "\n\n" + paragraph
            #print(response)
            await channels[payload['Channel']].send(response)

    elif (splitPayload[0] == "!search" or splitPayload[0] == "!find"or splitPayload[0] == "!f"):
        text = ' '.join(splitPayload[1:]).lower()
        if text[0] == '"': text = text[1:]
        if text[-1] == '"': text = text[:-1]
        print (text)
        if len(text) <= 3: await message.channel.send("Must Search Words Longer Then 3 Letters")
        else:
            found = False
            for rule in Data.keys():
                low = Data[rule].lower()
                if text in low:
                    isIn = 1
                    count = 2
                    initIndex = 0
                    msg = '`'+str(rule)+':`\n'
                    while isIn and count > 0:
                        found = True
                        try:
                            index = low[initIndex:].index(text)
                            index += initIndex

                            initIndex = index + len(text)

                            boundLower = index - 40
                            if boundLower < 0:boundLower = 0

                            boundUpper = index + 120
                            if boundUpper >= len(low): boundUpper = len(low)-1

                            msg +=('\t...'\
                                  +Data[rule][boundLower:index]\
                                  +'**'+ Data[rule][index:index+len(text)]\
                                  +'**'+ Data[rule][index+len(text):boundUpper]\
                                  +'...').replace('\n','  ')+'\n\n'
                        except ValueError:
                            isIn = 0
                        count -= 1
                    if count <= 0:
                        msg += '...and more...'
                    await message.channel.send(msg)
            if not found:
                await message.channel.send("Couldn't Find A Match For "+text)
    return saveData()


"""
Update Function Called Every 10 Seconds
"""
async def update(inData, server):
    global Data
    loadData(inData)
    # Do Stuff Here

    return saveData()


"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(inData, chans, logchan, guild):
    global channels, logChannel, Data
    loadData(inData)
    channels = chans
    logChannel = logchan

    # Do Stuff Here
    Data = {}
    with urllib.request.urlopen('https://raw.githubusercontent.com/dmouscher/nomic/master/rules-3.md') as response:
        rules = response.read().decode("utf-8")
        ruletxt = rules.split("\n## ")[1:]
        for rule in ruletxt:
            try:
                rule = rule.strip()
                rulenum = int(rule[:3])
                Data[rulenum] = rule.replace('&nbsp;', ' ').replace('\\n', '\n')
            except:
                print('ERROR')
                print(rule)
    return saveData()

#####################################################
#  Necessary Module Functions
#####################################################

"""
Log Bot Activity To The Specified Guild/Server
Dont Modify Unless You Really Want To I Guess...
"""
async def log(msg):
    await channels[logChannel].send(msg)


"""
Save Memory Data To File
Dont Modify Unless You Really Want To I Guess...
"""
def saveData():
    global Data, AllData
    AllData[savefile] = Data
    return AllData

"""
Load Memory Data From File
Dont Modify Unless You Really Want To I Guess...
"""
def loadData(inData):
    global Data, AllData
    AllData = inData
    if inData.get(savefile) is None:
        try:
            with open(savefile + '_Data.pickle', 'rb') as handle:
                global Data
                AllData[savefile] = pickle.load(handle)
        except:
            AllData[savefile] = {}
    Data = AllData[savefile]
