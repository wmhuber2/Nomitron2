#
# Blank Module For Discord Bot
################################
import pickle, sys, re

"""
For a Custom Command !commandMe
"""
battleship_channel = "changelog-live"
Admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']

async def battleship(Data, channels, server, payload, *text):
    playerName = payload['Author']
    Data[server.id]['Battleship']['Players'][playerName] = {
        'Ships':['A2','A3','A3','A5','J10','J9'],
        'Shots':[],
        'Undamaged': 17,
        'msg_board_id': None
    }
    await generate_display(Data, channels, server, playerName)
    return Data


async def fire(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']
    text = payload['Content'].split(' ')[1:]

    # Test if player is playing or can play
    if Data[server.id]['Battleship']['Players'].get(author) is None\
            or Data[server.id]['Battleship']['Players'][author]['Undamaged'] < 1:
        await message.channel.send("You cannot fire beacsue all your ships are sunk, or you are not playing battleship.")
        return

    # Test For Formatting
    print (text)
    if len(text) != 2:
        await message.channel.send("Use command like !fire @player B10")
        return
    else:
        coord = text[1].upper()
        if not (coord[0] in 'ABCDEFGHIJ' and coord[1:].isdigit() and int(coord[1:]) in range(1,11)):
            await message.channel.send("Use coordinates like B10, F2")
            return
        # Test For Valid Target
        playerName = await getPlayer(server, text[0], channel = message.channel)
        if playerName is None: return
        if Data[server.id]['Battleship']['Players'].get(playerName) is None:
            await message.channel.send("This Player Does Not Have An Active Battleship Game")
            return

        # Add Ship To Target Player's Shots
        Data[server.id]['Battleship']['Players'][playerName]['Shots'].append(coord)
        if coord in Data[server.id]['Battleship']['Players'][playerName]['Ships']:
            await message.add_reaction('🔥')
            if coord not in Data[server.id]['Battleship']['Players'][playerName]['Shots']:
                Data[server.id]['Battleship']['Players'][playerName]['Undamaged'] -= 1
        else:
            await message.add_reaction('💦')

    await generate_display(Data, channels, server, playerName)
    return Data


"""
Main Run Function On Messages
"""
async def on_message(Data, channels, server, payload):
    print(payload['Content'], payload['Author'])
    if payload['Content'] == '!clear battleship' and payload['Author'] in Admins:
        for player in Data[server.id]['Battleship']['Players'].keys():
            try:
                msg = await channels[server.id][battleship_channel].fetch_message(
                    Data[server.id]['Battleship']['Players'][player]['msg_board_id'])
            except:
                msg = None
            if msg is not None:
                await msg.delete()
            print('Deleting', player)
        Data[server.id]['Battleship']['Players'] = {}




"""
get Player
"""
async def getPlayer(server, playerid, channel):
    guild = server.id
    if len(playerid) == 0:
        return None
    else:
        player = server.get_member(int(re.search(r'\d+', playerid).group()))
        if player is not None:
            playerName = player.name + "#" + str(player.discriminator)
            return playerName
        else:
            await channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None



"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data, channels, server, payload):
    if Data[server.id].get('Battleship') is None:
        Data[server.id]['Battleship'] = {
            'Players' : {},
        }
    return Data

async def generate_display(Data, channels, server, playerName):
    PlayerData = Data[server.id]['Battleship']['Players'][playerName]
    table = "```prolog\n"+playerName+":"
    if PlayerData['Undamaged'] <=0 :
        table += '(All Ships Sunk)'
    table += "\n#########################\n# _|A B C D E F G H I J|#\n"
    for r in range(1,11):
        if r == 10:    table += '#' + str(r)
        else:          table += '# '+ str(r)

        for c in range(10):
            c = ('ABCDEFGHIJ')[c]
            loc = c+str(r)
            if loc in PlayerData['Shots'] and loc in PlayerData['Ships']:
                table += '|X'
            elif loc in PlayerData['Shots'] and loc not in PlayerData['Ships']:
                table += '|0'
            else: table += '| '
        table += '|#\n'
    table += '#########################```'

    try:      msg = await channels[server.id][battleship_channel].fetch_message(PlayerData['msg_board_id'])
    except:   msg = None
    if msg is None:
        msg =\
            await channels[server.id][battleship_channel].send(table)
        Data[server.id]['Battleship']['Players'][playerName]['msg_board_id'] = msg.id
    else:
        await msg.edit(content=table)


