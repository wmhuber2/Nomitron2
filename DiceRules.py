#
# Blank Module For Discord Bot
################################
import pickle, sys, numpy
"""
Main Run Function On Messages
"""
async def roll(Data, channels, server, payload, *text):
    argv = text[0]
    diceInfo = argv[1].split('d')
    if len(diceInfo) == 2:
        randNum = numpy.random.randint(1, int(diceInfo[1])+1, int(diceInfo[0]))
        await channels[server.id][payload['Channel']].send(str(sum(randNum))+' : '+str(randNum).replace(' ',', '))

