#
# Blank Module For Discord Bot
################################
import pickle, sys, random, re

fixedcards = [0] * 56
Admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
card_channel = "changelog-live"

async def weights(Data, channels, server, payload, *text):
    _checkfilesystem(Data, server)
    msg = ""
    message = payload['raw']
    sum = 0
    for i in range(56):
        msg += _card2text(i)+ "   :    " + str(Data[server.id]['Cards']['Fixedcards'][i]) + "\n"
        sum += Data[server.id]['Cards']['Fixedcards'][i]
    msg += "Total Cards:  "+str(sum)
    await message.channel.send(msg)

def _card2text(cardnum):
    suits = ["⚔️", "<:wand:734932801266122832>", "<:coin:734932801018921063>", "🍷"]
    #suits = ["Swords", "Wands", "Coins", "Cups"]
    ranks = ["2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🇵", "🐴", "🇶", "🇰", "🇦"]
    if cardnum is None: return 'None'
    return ranks[cardnum % 14] + suits[cardnum // 14]

def _fix(num,fixedcards):
    maxdrawn = max(fixedcards)
    weights = [2 ** (maxdrawn - i) for i in fixedcards]
    print('Weights',weights)

    cards = random.choices(range(56), weights=weights, k=num)
    print('R Cards',cards)
    for c in cards: fixedcards[c] += 1
    return cards

def _unfix(card, fixedcards):
    fixedcards[card] -= 1
    if (fixedcards[card] < 0): print("ALERT: # unfixed card < 0!")

async def _getPlayer(server, playerid, channel):
    guild = server.id
    print('PLayer:', playerid)
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

def _checkfilesystem(Data, server):
    if Data[server.id].get('Cards') is None:
        Data[server.id]['Cards'] = {'Hand':{},
                                    'Deck' :{},
                                    'Fixedcards':[0,]*56,
                                    'msg_board_id': None}
    if 'DiscardPile' not in Data[server.id]['Cards']:
        Data[server.id]['Cards']['DiscardPile'] = None
    if 'Pot' not in Data[server.id]['Cards']:
        Data[server.id]['Cards']['Pot'] = 0

    tmp_fixedcounter = [0,]*56
    for player in Data[server.id]['Cards']['Hand'].keys():
        for card in Data[server.id]['Cards']['Hand'][player]:
            tmp_fixedcounter[card] += 1

    for position, card in Data[server.id]['Cards']['Deck'].items():
        if type(card) is list:
            Data[server.id]['Cards']['Deck'][position] = int(card[0])
            card = int(card)
        tmp_fixedcounter[card] += 1
    if Data[server.id]['Cards']['DiscardPile'] is not None:
        tmp_fixedcounter[ Data[server.id]['Cards']['DiscardPile'] ] += 1
    Data[server.id]['Cards']['Fixedcards'] = list(tmp_fixedcounter)

async def fix(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']
    text = payload['Content'].split(' ')

    _checkfilesystem(Data, server)
    if author not in Admins: return
    cards = []
    if len(text) > 2 :
        for cardarg in text[2:]:
            card = cardarg.replace('0','').lower()
            rank = "234567891pnqka".index(card[0])
            suit = ["swords", "wands", "coins", "cups"].index(card[1:])
            card = suit * 14 + rank
            if card < 0 or rank < 0:
                await message.channel.send("Unrecognized Card Format")
                _checkfilesystem(Data, server)
                return
            cards.append(card)
            Data[server.id]['Cards']['Fixedcards'][card] += 1
    else:
        cards = _fix(1,  Data[server.id]['Cards']['Fixedcards'])

    for card in cards:
        if text[1] == 'discard':
            if Data[server.id]['Cards']['DiscardPile'] is not None:
                _unfix(Data[server.id]['Cards']['DiscardPile'],
                       Data[server.id]['Cards']['Fixedcards'])
            Data[server.id]['Cards']['DiscardPile'] = card
            _fix(card, Data[server.id]['Cards']['Fixedcards'])
        else:
            try:
                deckIndex = int(text[1])
                if Data[server.id]['Cards']['Deck'].get(deckIndex) is not None:
                    _unfix(Data[server.id]['Cards']['Deck'][deckIndex],
                           Data[server.id]['Cards']['Fixedcards'] )
                Data[server.id]['Cards']['Deck'][deckIndex] = card
            except ValueError:
                player = await _getPlayer(server, text[1], message.channel)
                if Data[server.id]['Cards']['Hand'].get(player) is None:
                    Data[server.id]['Cards']['Hand'][player] = []
                Data[server.id]['Cards']['Hand'][player].append(card)

    _checkfilesystem(Data, server)
    await generateChangelog(Data, channels, server)

async def unfix(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']
    text = payload['Content'].split(' ')

    _checkfilesystem(Data, server)
    if author not in Admins: return
    card = None
    if len(text) > 2 :
        card = text[2].replace('0','').lower()
        try:
            rank = "234567891pnqka".index(card[0])
            suit = ["swords", "wands", "coins", "cups"].index(card[1:])
        except ValueError:
            await message.channel.send('Unknown Card (Use swords, wands, coins, cups)')
            return
        card = suit * 14 + rank
        print('RS',rank, suit)
        if card < 0 or rank < 0:
            await message.channel.send("Unrecognized Card Format")
            return
    else:
        await message.channel.send('No Card To Unfix')
        return
    print('Card',card)

    try:
        deckIndex = int(text[1])
        if Data[server.id]['Cards']['Deck'].get(deckIndex) is not None\
            and Data[server.id]['Cards']['Deck'][deckIndex] == card:
                del Data[server.id]['Cards']['Deck'][deckIndex]
                _unfix(card, Data[server.id]['Cards']['Fixedcards'])
    except ValueError:
        player = await _getPlayer(server, text[1], message.channel)
        if Data[server.id]['Cards']['Hand'].get(player) is not None\
            and card in Data[server.id]['Cards']['Hand'][player]:
            index = Data[server.id]['Cards']['Hand'][player].index(card)
            del Data[server.id]['Cards']['Hand'][player][index]
            _unfix(card, Data[server.id]['Cards']['Fixedcards'])

    _checkfilesystem(Data, server)
    await generateChangelog(Data, channels, server)

async def draw(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']
    text = payload['Content'].split(' ')

    try:  numOfCards = int(text[-1])
    except:
        print ('Error finding number',text)
        return
    _draw(Data, server, numOfCards, author)
    await generateChangelog(Data, channels, server)

def _draw(Data, server, numOfCards, author):
    newDeck = dict()
    drawnCards = []
    for pos in Data[server.id]['Cards']['Deck'].keys():
        if pos > numOfCards:   newDeck[pos - numOfCards] = Data[server.id]['Cards']['Deck'][pos]
        else:                  drawnCards.append(Data[server.id]['Cards']['Deck'][pos])
    Data[server.id]['Cards']['Deck'] = newDeck

    drawnCards += _fix(numOfCards - len(drawnCards), Data[server.id]['Cards']['Fixedcards'])
    if Data[server.id]['Cards']['Hand'].get(author) is None:
        Data[server.id]['Cards']['Hand'][author] = []
    Data[server.id]['Cards']['Hand'][author] += drawnCards

async def deal(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']
    text = payload['Content'].split(' ')
    if author not in Admins: return

    target = await _getPlayer(server, text[-2], message.channel)
    if target is None: return

    try:  numOfCards = int(text[-1])
    except:
        print ('Error finding number',text)
        return

    _draw(Data, server, numOfCards, target)

    await generateChangelog(Data, channels, server)

async def generateChangelog(Data, channels, server):
    async def sendNextChunk(msgNum, text):
        try:
            if msgNum >= len(Data[server.id]['Cards']['msg_board_id']):
                msg = await channels[server.id][card_channel].send('Adding Section...')
                Data[server.id]['Cards']['msg_board_id'].append( msg.id )
            msgid = Data[server.id]['Cards']['msg_board_id'][msgNum]
            msg = await channels[server.id][card_channel].fetch_message(msgid)
        except:
            msg = None

        if msg is None:
            msg = await channels[server.id][card_channel].send(table)
            Data[server.id]['Cards']['msg_board_id'][msgNum] = msg.id
        else:
            await msg.edit(content=table)


    table = ""
    _checkfilesystem(Data,server)

    table += "\n**Discard Pile:** " + _card2text(Data[server.id]['Cards']['DiscardPile'])
    table += "\n**Pot:** " + str(Data[server.id]['Cards']['Pot'])+" Coins"
    table += "\n**Deck:** \n"
    if Data[server.id]['Cards']['Deck'].get(1) is not None:
        card = Data[server.id]['Cards']['Deck'][1]
        table += '1st Next: ' + _card2text(card) + "\n"
    else: table += '1st Next: ' + '???' + "\n"
    if Data[server.id]['Cards']['Deck'].get(2) is not None:
        card = Data[server.id]['Cards']['Deck'][2]
        table += '2nd Next: ' + _card2text(card) + "\n"
    else: table += '2st Next: ' + '???' + "\n"

    for pos,card in Data[server.id]['Cards']['Deck'].items():
        if pos in [1,2]: continue
        table += '\n' + str(pos)+'.) '+_card2text(card)
    table += '\n#################'


    if type(Data[server.id]['Cards']['msg_board_id']) is not list:
        msg = await channels[server.id][card_channel].send('Updating Configuration...')
        Data[server.id]['Cards']['msg_board_id'] = [msg.id, ]
    msgNum = 0
    for playerName in Data[server.id]['Cards']['Hand'].keys():
        if len(table) > 1750:
            await sendNextChunk(msgNum, table)
            msgNum += 1
            table = ""

        if len(Data[server.id]['Cards']['Hand'][playerName]) == 0: continue
        playertitle = playerName
        if playertitle == 'Nomitron#3034': playertitle = "Discard Pile"
        table += "\n\n**" + playertitle + "**: "
        for card in Data[server.id]['Cards']['Hand'][playerName]:
            table += _card2text(card) + "     "

    await sendNextChunk(msgNum, table)
    return table

async def setup(Data, channels, server, payload):
    _checkfilesystem(Data, server)
    await generateChangelog(Data, channels, server)
