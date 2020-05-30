#
# Blank Module For Discord Bot
################################
import pickle, sys, numpy
"""
Main Run Function On Messages
"""
async def on_message(Data, channels, server, payload):
    message = payload['raw']
    if payload['Content'][0] != '!': return
    diceInfo = payload['Content'][1:].split('d')
    if len(diceInfo) == 2:
        randNum = numpy.random.randint(1, int(diceInfo[1]), int(diceInfo[0]))
        await channels[server.id][payload['Channel']].send(str(sum(randNum))+' : '+str(randNum).replace(' ',', '))

