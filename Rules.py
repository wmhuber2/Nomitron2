#
# Blank Module For Discord Bot
################################
import pickle, sys, urllib

"""
Main Run Function On Messages
"""
async def on_message(Data, channels, server, payload):

    # Do Stuff Here
    message = payload['raw']
    splitPayload = payload['Content'].split()
    if len(splitPayload) == 0: pass

    elif(splitPayload[0] == "!rule" and len(splitPayload) == 2):
        rulequery = int(splitPayload[1])
        if(rulequery not in Data[server.id]['RuleList'].keys()):
            await channels[server.id][payload['Channel']].send("I couldn't find that rule.")
        else:
            print("Found Rule", rulequery)
            answer = "Rule " + Data[server.id]['RuleList'][rulequery]
            response = ""
            for paragraph in answer.split("\n\n"):
                paragraph = paragraph.replace('\\xe2\\x95\\x9e', ' ')
                paragraph = paragraph.replace('\\xe2\\x95\\x90', ' ')
                paragraph = paragraph.replace('\\xe2\\x95\\xa1', ' ')
                paragraph = paragraph.replace('\\xe2\\x94\\x80', ' ')
                if(len(response) + len(paragraph) + 6 > 1850):
                    #print(response)
                    await channels[server.id][payload['Channel']].send(response)
                    response = ""
                if len(paragraph) >1900:
                    print('Error: Paragrpah too long!!! Length: ', len(paragraph))
                    print(paragraph)
                else:
                    response = response + "\n\n" + paragraph
            #print(response)
            await channels[server.id][payload['Channel']].send(response)

    elif (splitPayload[0] == "!search" or splitPayload[0] == "!find"or splitPayload[0] == "!f"):
        text = ' '.join(splitPayload[1:]).lower()
        if text[0] == '"': text = text[1:]
        if text[-1] == '"': text = text[:-1]
        print (text)
        if len(text) <= 3: await message.channel.send("Must Search Words Longer Then 3 Letters")
        else:
            found = False
            for rule in Data[server.id]['RuleList'].keys():
                low = Data[server.id]['RuleList'][rule].lower()
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
                                  +Data[server.id]['RuleList'][rule][boundLower:index]\
                                  +'**'+ Data[server.id]['RuleList'][rule][index:index+len(text)]\
                                  +'**'+ Data[server.id]['RuleList'][rule][index+len(text):boundUpper]\
                                  +'...').replace('\n','  ')+'\n\n'
                        except ValueError:
                            isIn = 0
                        count -= 1
                    if count <= 0:
                        msg += '...and more...'
                    await message.channel.send(msg)
            if not found:
                await message.channel.send("Couldn't Find A Match For "+text)

"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data, channels, server, payload):
    # Do Stuff Here
    Data[server.id]['RuleList'] = {}
    with urllib.request.urlopen('https://raw.githubusercontent.com/dmouscher/nomic/master/rules-3.md') as response:
        rules = response.read().decode("utf-8")
        ruletxt = rules.split("\n## ")[1:]
        for rule in ruletxt:
            try:
                rule = rule.strip()
                rulenum = int(rule[:3])
                Data[server.id]['RuleList'][rulenum] = rule.replace('&nbsp;', ' ').replace('\\n', '\n')
            except:
                print('ERROR')
                print(rule)

