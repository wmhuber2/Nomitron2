#! Python3
import sys, asyncio, os, importlib, glob, datetime, random,socket, multiprocessing, pickle


Admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
from threading import Thread
discord = None
import traceback
savefile ='DiscordBot_Data.pickle'

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
        self.Data = {}
        self.loadData()

        for mod in glob.glob("*.py"):
            mod = mod[:-3]
            if mod in sys.argv[0] or 'Nomitron' == mod or 'run' == mod or mod[0]=='T':
                continue
            print ('Importing Module ',mod)
            self.modules.append(importlib.import_module(mod))
            self.moduleNames.append(mod)

        self.loop = asyncio.get_event_loop()
        self.client = discord.Client(loop = self.loop,heartbeat_timeout=120)

        if self.Data.get('disabled') is None:
            self.Data['disabled'] = {}
            self.saveData()

        self.token = open('/home/nomitron/secret.psk','r').read().strip()

        # If Host Is Insperon Use Daniel's Bot Account
        if socket.gethostname() == 'daniel-Inspiron-660s':
            pass
        print("Using Token: " + self.token)

        @self.client.event
        async def on_ready(): await self.on_ready()

        @self.client.event
        async def on_message(message): await self.on_message(message)

        @self.client.event
        async def on_raw_reaction_add(msg): await self.on_raw_reaction(msg, 'add')

        @self.client.event
        async def on_raw_reaction_remove(msg): await self.on_raw_reaction(msg, 'remove')


        self.logChannel = "bot-lounge"

    def start(self):
        self.client.run(self.token, reconnect=True, )

    """
    Process All Messages
    """
    def getChannelType(self,obj):
        if type(obj) == discord.channel.DMChannel: return 'DM'
        if type(obj) == discord.channel.TextChannel: return 'Text'
        if type(obj) == discord.channel.GroupChannel: return 'Group'
        return ''


    """
    Convert message data To Payload
    """
    def convertToPayload(self, message):
        payload = {}

        if message == None:  return

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

        for file in message.attachments:
            payload['Attachments'][file.filename] = file.url
        #print(payload)
        return payload


    """
    Handle Message Event
    """
    async def on_message(self, message):
        payload = self.convertToPayload(message)
        if message.author == self.client.user: return

        await self.processCommands(payload,message)
        for mod, name in zip(self.modules, self.moduleNames):
            if payload['Channel Type'] == 'DM': continue
            if name in self.Data['disabled'][message.guild.id]: continue
            if hasattr(mod, 'run'):
                if 1: #try:
                    tmp = await mod.run(self.Data, payload, message)
                    if tmp is not None: self.Data = tmp
                    else: print("None Returned OnMessage",name)
                #except Exception as e:
                #    print('Error:', e)

        sys.stdout.flush()
        self.saveData()


    """
    Display All Server ,Detailssocket.gethostname()
    """
    async def on_ready(self):
        print()
        print('Logged in as ' + self.client.user.name)
        print('Bot Started!')
        print('-'*20)
        for server in self.client.guilds:
            channels = {}
            if self.Data['disabled'].get(server.id) is None:
                self.Data['disabled'][server.id] = []
                self.saveData()
            for channel in server.text_channels:
                channels[channel.name] = channel
            botCount = 0
            handlerCount = 0
            proc  = os.popen("""pgrep "python" | xargs -r --no-run-if-empty ps fp | awk '{print $6}';""").read().split('\n')

            for p in proc:
                print (p.split('/')[-1])
                if 'DiscordBot.py' in p: botCount +=1
                if 'Nomitron.py' in p: handlerCount +=1
            msg = "**__"+" "*450 + "__\n" \
                + "Nomitron Bot Booting Up.\n" \
                + "System Time: "+str(datetime.datetime.now())+'\n' \
                + "Host: "+socket.gethostname() +'\n' \
                + "Local Bot Instances: "+str(botCount) +'\n' \
                + "Local Handler Instances: "+str(handlerCount) +'**\n'

            await channels[self.logChannel].send(msg)

            tasks = []
            for mod, name in zip(self.modules, self.moduleNames):
                if name in self.Data['disabled']: continue
                if hasattr(mod, 'setup'):
                    try:
                        tmp = await mod.setup(self.Data, channels,self.logChannel,server)
                        if tmp is not None: self.Data = tmp
                        else: print("None Returned OnMessage", name)
                    except Exception as e:
                        print ("Exception On Startup")
                        try:
                            self.Data['disabled'][server.id].append(name)
                            await channels[self.logChannel].send("Disabling "+name+" due to Error:"+str(e))
                            self.saveData()
                        except Exception as e2:
                            print('Error Disabling After Error', str(e2))
                        raise e

            msg =  "```diff\nModules Loaded:"
            for m in self.moduleNames:
                if m in self.Data['disabled'][server.id]:        msg += '\n- ' + m + ' [disabled]'
                else:                                            msg += '\n+ ' + m
            msg += "```"
            await channels[self.logChannel].send(msg)

        while 1:
            sys.stdout.flush()
            await asyncio.sleep(30)

            tasks = []

            for mod, name in zip(self.modules, self.moduleNames):
                for server in self.client.guilds:
                    if name in self.Data['disabled'][server.id]: continue
                    if hasattr(mod, 'update'):
                        tmp = await mod.update(self.Data, server)
                        if tmp is not None: self.Data = tmp
                        else: print("None Returned OnMessage", name)
                        #except Exception as e:
                        #    print('Error:',mod,e)
            self.saveData()


    """
    Handle Reactions
    """
    async def on_raw_reaction(self, payload, mode):
        user = self.client.get_user(payload.user_id)
        if user == self.client.user: return

        channel = self.client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        reactorName = user.name + '#' + user.discriminator
        if str(payload.emoji) == str('🔄') and reactorName in Admins:
            await self.on_message(msg)

        tasks = []
        for mod, name in zip(self.modules, self.moduleNames):
            if name in self.Data['disabled'][msg.guild.id]: continue
            if hasattr(mod, 'reaction'):
                tmp = await mod.reaction(self.Data, mode, user, msg, payload.emoji)
                if tmp is not None: self.Data = tmp
                else: print("None Returned OnMessage", name)

        sys.stdout.flush()
        self.saveData()


    """
    Member Greeting And Initialization
    """
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            tasks = []
            for mod, name in zip(self.modules, self.moduleNames):
                if name in self.Data['disabled'][guild.id]: continue
                if hasattr(mod, 'addMember'):
                    tmp = await mod.addMember(self.Data, member)
                    if tmp is not None: self.Data = tmp
                    else: print("None Returned OnMessage", name)
        self.saveData()

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


    async def processCommands(self, payload, message):
        admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
        botCharacter = '>>'

        if payload['Content'][:len(botCharacter)] == botCharacter and  payload['Content'][len(botCharacter)] != ' ':
            payload['Content'] = payload['Content'][:2] + ' ' + payload['Content'][2:]
        splitPayload = payload['Content'].split(' ')

        if len(splitPayload) == 3 and payload['Channel Type'] == 'Text' \
                and splitPayload[1].lower() == "disable" and splitPayload[0] == botCharacter:
            if splitPayload[2] in self.moduleNames:
                self.Data['disabled'][message.guild.id].append( splitPayload[2] )
                msg = "```diff\nModules Loaded:"
                for mod, name in zip(self.modules, self.moduleNames):
                    if name in self.Data['disabled'][message.guild.id]:
                        msg += '\n- ' + name + ' [disabled]'
                    else:
                        msg += '\n+ ' + name
                msg += "```"
                await message.channel.send(msg)
            else:
                await message.channel.send("Module {0} cannot be found".format(splitPayload[2]))

        if len(splitPayload) == 3 and payload['Channel Type'] == 'Text' \
                and splitPayload[1].lower() == "enable" and splitPayload[0] == botCharacter:
            if splitPayload[2] in self.moduleNames:
                mod = self.modules[self.moduleNames.index(splitPayload[2])]
                reloaded = True
                channels = {}
                for channel in message.guild.text_channels:
                    channels[channel.name] = channel
                if hasattr(mod, 'setup'):
                    try:
                        await mod.setup(self.Data, channels, self.logChannel, message.guild)
                        #print('Enabling',self.Data)
                        self.Data['disabled'][message.guild.id] = [x for x in self.Data['disabled'][message.guild.id] if x != splitPayload[2]]
                    except Exception as e:
                        print('Disabling')
                        await message.channel.send("Disabling " + splitPayload[2] + " due to Error:" + str(e))

                    msg = "```diff\nModules Loaded:"
                    for mod, name in zip(self.modules, self.moduleNames):
                        if name in self.Data['disabled'][message.guild.id]:
                            msg += '\n- ' + name + ' [disabled]'
                        else:
                            msg += '\n+ ' + name
                    msg += "```"
                    await message.channel.send(msg)
            else:
                await message.channel.send("Module {0} cannot be found".format(splitPayload[2]))
        self.saveData()

bot = DiscordNomicBot()
bot.start()
