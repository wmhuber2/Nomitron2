#! Python3
import sys, asyncio, os, importlib, glob, datetime, random,socket, multiprocessing, pickle
from shutil import copyfile


Admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
from threading import Thread
discord = None
import traceback
savefile = 'DiscordBot_Data.pickle'
default_server_id = 707705708346343434
''' 
Implement Modules By Placing Module Python File In Same Directory
Modules Must Have Different Names And Be Written With Python 3 Compatibility.
Use Blank.py as a Template for new modules.

It is recommended not to edit this file.
'''

class DiscordNomicBot():

    """
    Initialize The Bot Handling Class
    """
    def __init__(self, ):
        try:
            global discord
            discord = importlib.import_module('discord')
        except ImportError:
            print ("Discord Library Not Found, install by \"pip install discord\"")
            sys.exit(0)


        self.moduleNames = []
        self.modules = []

        self.servertree = {}
        self.Data = {}
        self.loadData()

        for mod in glob.glob("*.py"):
            mod = mod[:-3]
            if not 'Rule' in mod: continue
            print('Importing Module ',mod)
            self.modules.append(importlib.import_module(mod))
            self.moduleNames.append(mod)

        self.loop = asyncio.get_event_loop()
        self.client = discord.Client(loop = self.loop, heartbeat_timeout=120)

        if self.Data.get('DisabledModules') is None:
            self.Data['DisabledModules'] = {}
            self.saveData()

        self.token = open('/home/nomitron/secret.psk','r').readlines()[1].strip()
        print("Using Token: ..." + self.token[-6:])

        @self.client.event
        async def on_ready(): await self.on_ready()

        @self.client.event
        async def on_message(message): await self.on_message(message)

        @self.client.event
        async def on_raw_reaction_add(msg): await self.on_raw_reaction(msg, 'add')

        @self.client.event
        async def on_raw_reaction_remove(msg): await self.on_raw_reaction(msg, 'remove')


    def start(self):
        self.client.run(self.token, reconnect=True, )

    """
    Ruturn Channel Type
    """
    def getChannelType(self,obj):
        if type(obj) == discord.channel.DMChannel: return 'DM'
        if type(obj) == discord.channel.TextChannel: return 'Text'
        if type(obj) == discord.channel.GroupChannel: return 'Group'
        return ''


    """
    Convert message data To Easier Message Payload
    """
    def convertToPayload(self, message):
        payload = {}

        if message == None:  return
        payload['raw'] = message
        payload['Author'] = message.author.name + "#" + str(message.author.discriminator)
        payload['Nickname'] = message.author.name
        payload['Channel Type'] = self.getChannelType(message.channel)
        if payload['Channel Type'] == 'Text':
            #payload['Nickname'] = message.author.nick
            payload['Channel'] = message.channel.name
            payload['Category'] = message.guild.get_channel(message.channel.category_id)
        if payload['Channel Type'] == 'DM':
            payload['Channel'] = "DM"
            payload['Category'] = "DM"
        payload['Content'] = message.system_content.strip()
        payload['Attachments'] = {}

        payload['Server'] = message.guild
        print(payload['Server'])
        for file in message.attachments:
            payload['Attachments'][file.filename] = file.url
        #print(payload)
        return payload


    async def passToModule(self, function, server, channels, payload, *args):
        if server is None or server.id not in channels.keys():
            print('Server Not Found, Using Default')
            server = self.servertree[default_server_id]['Server']
        for mod, name in zip(self.modules, self.moduleNames):
            if name in self.Data['DisabledModules']: continue
            if hasattr(mod, function):
                if args is None: tmp = await getattr(mod, function)(self.Data, channels, server, payload)
                else: tmp = await getattr(mod, function)(self.Data, channels, server, payload, *args)

                if tmp is not None:  self.Data = tmp
                #else:  print("None Returned OnMessage", name)

    """
    Display All Server ,Detailssocket.gethostname()
    """
    async def on_ready(self):
        print()
        print('Logged in as ' + self.client.user.name)
        print('Bot Started!')
        print('-'*20)

        try: os.mkdir('BackupDataFiles/')
        except: pass
        copyfile('DiscordBot_Data.pickle',
                 'BackupDataFiles/DiscordBot_Data-' + str(datetime.datetime.now()) + '.pickle')

        for server in self.client.guilds:
            self.servertree[server.id] = {'Server':server}
            if self.Data['DisabledModules'].get(server.id) is None:
                self.Data['DisabledModules'][server.id] = []
                self.saveData()
            for channel in server.text_channels:
                self.servertree[server.id][channel.name] = channel

            if not server.id in self.Data: self.Data[server.id] = {}

        self.printInfo()

        for server in self.client.guilds:
            await self.passToModule('setup', server, self.servertree, None)
        self.saveData()

        while 1:
            sys.stdout.flush()
            await asyncio.sleep(30)
            for server in self.client.guilds:
                await self.passToModule('update', server, self.servertree, None)
            self.saveData()

    """
    Handle Message Event
    """

    async def on_message(self, message):
        payload = self.convertToPayload(message)
        if message.author == self.client.user: return


        found = False
        if payload['Content'].split(' ')[0][0] == '!':
            functionName = payload['Content'][1:].split(' ')[0]
            for i in range(len(self.moduleNames)):
                mod = self.modules[i]
                if hasattr(mod, functionName):
                    if found: print('Duplicate Function of Name '+functionName+' in '+self.moduleNames[i])

                    found = True
                    if 1:#try:
                        tmp = await self.passToModule(functionName, message.guild, self.servertree, payload, payload['Content'][1:].split(' ') )
                        if tmp is not None:  self.Data = tmp
                    try: pass
                    except TypeError:
                        print('Incorrectly Formatted Funtion for '+functionName+' in '+self.moduleNames[i])


        if not found:
            await self.passToModule('on_message',
                                    message.guild,
                                    self.servertree,
                                    payload)
        sys.stdout.flush()
        self.saveData()

    """
    Handle Reactions
    """
    async def on_raw_reaction(self, payload, mode):
        user = self.client.get_user(payload.user_id)
        if user == self.client.user: return

        channel = self.client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        react_payload = dict(payload)
        react_payload['mode']    = mode
        react_payload['message'] = msg
        react_payload['user']    = user
        react_payload['channel'] = channel
        react_payload['name']    = user.name + '#' + user.discriminator


        server = msg.guild
        await self.passToModule('on_reaction',
                                server,
                                self.servertree,
                                react_payload)

        if str(payload.emoji) == str('🔄') and react_payload['name'] in Admins: await self.on_message(msg)
        sys.stdout.flush()
        self.saveData()


    """
    Member Greeting And Initialization
    """
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            await self.passToModule('on_member_join', guild, self.servertree, None)
        self.saveData()

    """
    Save Memory Data From File
    Dont Modify Unless You Really Want To I Guess...
    """
    def saveData(self):
        with open(savefile, 'wb') as handle:
            pickle.dump(self.Data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    """
    Load Memory Data From File
    Dont Modify Unless You Really Want To I Guess...
    """
    def loadData(self):
        try:
            with open(savefile, 'rb') as handle:
                newData = pickle.load(handle)
                self.Data = newData
        except (OSError, IOError) as e:
            with open(savefile, 'wb') as handle:
                pickle.dump(self.Data, handle)

    """
    Diplay Server Info to Terminal
    """
    def printInfo(self):
        botCount = 0
        handlerCount = 0
        proc = os.popen("""pgrep "python" | xargs -r --no-run-if-empty ps fp | awk '{print $6}';""").read().split('\n')

        for p in proc:
            print(p.split('/')[-1])
            if 'DiscordBot.py' in p: botCount += 1
            if 'Nomitron.py' in p: handlerCount += 1
        msg = "-" * 24 + "\n" \
              + "Nomitron Bot Booting Up.\n" \
              + "System Time: " + str(datetime.datetime.now()) + '\n' \
              + "Host: " + socket.gethostname() + '\n' \
              + "Local Bot Instances: " + str(botCount) + '\n' \
              + "Local Handler Instances: " + str(handlerCount)
        for server in self.client.guilds:
            msg += "\n\nServer: " + server.name + "\nModules Loaded:"
            for m in self.moduleNames: msg += '\n- ' + m + (' [disabled]' * (m in self.Data['DisabledModules'][server.id]))
        print(msg)
        print('-'*24)


bot = DiscordNomicBot()
bot.start()
