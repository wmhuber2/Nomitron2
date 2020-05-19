#
# Admin Module For Discord Bot
################################
import sys, os,datetime
from shutil import copyfile


"""
Main Run Function
"""
async def on_message(Data, channels, server, payload):

    guild = server.id
    message = payload['raw']
    admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
    botCharacter = '>>'

    #if '❤' == payload['Content']:
    #   await message.channel.send("I NEED MORE LOVE")

    if payload['Content'] in ['!help', '! help']:
        with open('PlayerREADME.md', 'r') as helpFile:
            help = helpFile.readlines()
            msg = ""
            for line in help:
                if len(msg + line) > 1900:
                    await message.channel.send('```diff\n'+msg+'```')
                    msg = ""
                msg = msg + line
            if msg != "":
                await message.channel.send('```diff\n'+msg+'```')
    if payload['Content'] in ['!admin', '! admin']:
        with open('AdminREADME.md', 'r') as helpFile:
            help = helpFile.readlines()
            msg = ""
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
                and splitPayload[1].lower() == "restart" and splitPayload[0] == botCharacter:
            copyfile('DiscordBot_Data.pickle',
                     'BackupDataFiles/DiscordBot_Data-'+str(datetime.datetime.now())+'.pickle')
            print("Going For Restart...")
            sys.exit(0)

        if len(splitPayload) == 2 and payload['Channel Type'] == 'Text' \
                and splitPayload[1].lower() == "die" and splitPayload[0] == botCharacter:
            copyfile('DiscordBot_Data.pickle',
                     'BackupDataFiles/DiscordBot_Data-' + str(datetime.datetime.now()) + '.pickle')
            print("Going For Death...", guild)
            os.system("pkill python")


