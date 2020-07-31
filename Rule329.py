#
# Blank Module For Discord Bot
################################
import pickle, sys, discord, re
import Rule327
"""
For a Custom Command !commandMe
"""

def _text2card(rank, suit, server):
    #suits = ["⚔️", "<:wand:734932801266122832>", "<:coin:734932801018921063>", "🍷"]
    suits = ["⚔️", "🥢", "<:coin:738700971961614406>", "🍷"]

    ranks = ["2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🇵", "🐴", "🇶", "🇰", "🇦"]

    if rank not in ranks or suit not in suits:
        return None

    return ranks.index(rank) + suits.index(suit) * 14

async def discard(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']

    if author not in Admins = ['Fenris Wolf#6136', 'Crorem#6962']: return

    text = payload['Content'].replace('  ',' ').split(' ')
    if len(text) == 2:
        message.channel.send("PLease separate your emojis with a space. ")
        return
    print(text)
    card = _text2card(text[1],text[2], server)
    print(card)
    if card not in Data[server.id]['Cards']['Hand'][author]:
        await message.channel.send("You dont have that card!")
        return

    oldcard = Data[server.id]['Cards']['DiscardPile']
    Rule327._draw(Data, server, 1, author)
    Data[server.id]['Cards']['DiscardPile'] = card
    Rule327._unfix(card, Data[server.id]['Cards']['Fixedcards'])
    Data[server.id]['Cards']['Hand'][author].remove(card)

    rankVal  = card%14+2
    suitVal  = card//14

    if suitVal == 0:  # sword
        if rankVal > 10: rankVal = 1

        swapcard = Data[server.id]['Cards']['Deck'].get(rankVal)
        if swapcard is None:
            swapcard = Rule327._fix(1, Data[server.id]['Cards']['Fixedcards'])[0]
        Data[server.id]['Cards']['Deck'][rankVal] = oldcard
    elif suitVal == 1: # wand
        Data[server.id]['Cards']['Hand'][author].append(oldcard)
    elif suitVal == 2: #coin
        if rankVal > 10: rankVal = 11
        Data[server.id]['Cards']['Pot'] += rankVal
    elif suitVal == 3: #cup
        if rankVal > 10: rankVal = 1

        if Data[server.id]['Cards']['Deck'].get(rankVal) is None:
            card = Rule327._fix(1, Data[server.id]['Cards']['Fixedcards'])[0]
            if Data[server.id]['Cards']['Deck'].get(rankVal) is not None:
                Rule327._unfix(Data[server.id]['Cards']['Deck'][rankVal],
                       Data[server.id]['Cards']['Fixedcards'])
            Data[server.id]['Cards']['Deck'][rankVal] = card

        else:
            Rule327._unfix(Data[server.id]['Cards']['Deck'][rankVal],
                           Data[server.id]['Cards']['Fixedcards'])
            del Data[server.id]['Cards']['Deck'][rankVal]

    await Rule327.generateChangelog(Data,channels, server)

async def submit(Data, channels, server, payload, *text):
    message = payload['raw']
    author = payload['Author']
    text = payload['Content'].split(' ')
    print(text)

"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data, channels, server, payload):
    pass