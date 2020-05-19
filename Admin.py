#
# Admin Module For Discord Bot
################################
import pickle, sys, os, random, glob, math, discord
channels   = {}
logChannel = ""
Data = {}
AllData = {}
savefile = str(__name__) #+ '_Data.pickle'


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
async def reaction(inData, action, user, message, emoji):
    global Data
    loadData(inData)
    # Do Stuff Here
    guild = message.guild.id
    if message.channel.name.lower() in ['voting','actions']:
        await log('Player {0} has reacted to {1} in #{2} by '.format(user, message.author.name, message.channel.name)
                  + action+'ing {0}'.format(emoji) + ' (ID: %d)'%(message.id), guild)


    return saveData()



"""
Main Run Function
"""
async def run(inData, payload, message):
    loadData(inData)
    global Data

    guild = message.guild.id
    admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
    botCharacter = '>>'

    #if '❤' == payload['Content']:
    #   await message.channel.send("I NEED MORE LOVE")

    if payload['Content'] in ['!help', '! help']:
        with open('README.md', 'r') as helpFile:
            help = open('PlayerREADME.md', 'r').readlines()
            msg = ""
            if payload['Author'] in ["Doby's Peri#6151", 'Fenris Wolf#6136']:
                await message.channel.send("https://tenor.com/view/clippy-microsoft-office-word-publisher-gif-5630386")
            for line in help:
                if len(msg + line) > 1900:
                    await message.channel.send('```diff\n'+msg+'```')
                    msg = ""
                msg = msg + line
            if msg != "":
                await message.channel.send('```diff\n'+msg+'```')
    if payload['Content'] in ['!admin', '! admin']:
        with open('README.md', 'r') as helpFile:
            help = open('AdminREADME.md', 'r').readlines()
            msg = ""
            if payload['Author'] in ["Doby's Peri#6151", 'Fenris Wolf#6136']:
                await message.channel.send("https://tenor.com/view/clippy-microsoft-office-word-publisher-gif-5630386")
            for line in help:
                if len(msg + line) > 1900:
                    await message.channel.send('```diff\n'+msg+'```')
                    msg = ""
                msg = msg + line
            if msg != "":
                await message.channel.send('```diff\n'+msg+'```')

    if payload['Author'] in admins and payload['Channel'].lower() in ['actions','action', 'mod-lounge', 'bot-lounge']:
        if payload['Content'][:len(botCharacter)] == botCharacter and  payload['Content'][len(botCharacter)] != ' ':
            payload['Content'] = payload['Content'][:2] + ' ' + payload['Content'][2:]
        splitPayload = payload['Content'].split(' ')

        if len(splitPayload) == 2 and payload['Channel Type'] == 'Text' \
                and splitPayload[1].lower() == "help" and splitPayload[0] == botCharacter:
            with open('README.md', 'r') as helpFile:
                help = open('README.md', 'r').readlines()
                msg = ""
                for line in help:
                    if len(msg + line) > 1900:
                        await message.channel.send('```' + msg + '```')
                        msg = ""
                    msg = msg + line
                if msg != "":
                    await message.channel.send('```' + msg + '```')


        if len(splitPayload) == 2 and payload['Channel Type'] == 'Text' \
                and splitPayload[1].lower() == "restart" and splitPayload[0] == botCharacter:
            await channels[message.guild.id][logChannel].send('Save File Backup:',
                    file=discord.File(open('DiscordBot_Data.pickle', 'br')))
            await log("Going For Restart...",guild)
            sys.exit(0)

        if len(splitPayload) == 2 and payload['Channel Type'] == 'Text' \
                and splitPayload[1].lower() == "die" and splitPayload[0] == botCharacter:
            await channels[message.guild.id][logChannel].send('Save File Backup:',
                                                              file=discord.File(open('DiscordBot_Data.pickle', 'br')))
            await log("Going For Death...", guild)
            os.system("pkill python")
    return saveData()


"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(inData, chans, logchan, server):
    global channels, logChannel, Data
    channels, logChannel = chans, logchan
    channels[server.id] = chans
    loadData(inData)
    # Do Stuff Here

    quotes = [
        "Oooyyy! 10,000 years will give you such a crick in the neck!",
        "Wabalaba-dubdub! Im Back Baby!",
        "What is my purpose?\n*You pass changelogs. -Crorem*\nOh my god...  \n\n[ °□°|\n [ ╯_]╯\n(OOO)"
    ]
    msg = random.choice(quotes)
    await log(msg,server.id)
    
    return saveData()


"""
Update Function Called Every 10 Seconds
"""
async def update(inData,server):
    global Data
    loadData(inData)
    # Do Stuff Here

    return saveData()


#####################################################
#  Necessary Module Functions
#####################################################

"""
Log Bot Activity To The Specified Guild/Server
Dont Modify Unless You Really Want To I Guess...
"""
async def log(msg,guildid):
    await channels[guildid][logChannel].send(msg)


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
