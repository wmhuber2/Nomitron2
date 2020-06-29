#
# Blank Module For Discord Bot
################################
import pickle, sys, os, shutil

import discord
import youtube_dl
import asyncio

from discord.ext import commands


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'music_files/%(id)s.mp3',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'audio-format': 'mp3',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}



"""
For a Custom Command !commandMe
"""

async def playlist(Data, channels, server, payload, *text):
    message = payload['raw']
    playlist = "Playlist:"
    voice_channel = message.author.voice.channel
    if voice_channel is None:
        await message.channel.send("You are not in a Voice Channel")
        return

    if Data[server.id]['Music'].get(voice_channel.id) is None \
            or len(Data[server.id]['Music'][voice_channel.id]['Music Queue']) == 0:
        await message.channel.send('Playlist Empty')
        return

    i = 0
    for song in Data[server.id]['Music'][voice_channel.id]['Music Queue']:
        playlist += "\n"+str(i)+") \t "+song['title']
        i += 1
    await message.channel.send(playlist)

async def get_vc(ctx, voice_channel):
    vc = ctx.voice_clients
    if vc in [None, []]:
        vc = await voice_channel.connect()
    else:
        vc = vc[0]
    return vc

async def pause(Data, channels, server, payload, *text):
    ctx = payload['ctx']
    message = payload['raw']
    voice_channel = message.author.voice.channel
    vc = await get_vc(ctx, voice_channel)
    vc.pause()
    await message.channel.send('Paused Music')

async def next(Data, channels, server, payload, *text):
    ctx = payload['ctx']
    message = payload['raw']
    voice_channel = message.author.voice.channel
    vc = await get_vc(ctx, voice_channel)

    index = Data[server.id]['Music'][voice_channel.id]['index']
    index = index + 1
    if index >= len(Data[server.id]['Music'][voice_channel.id]['Music Queue']):
        index = 0

    vc.stop()
    vc.play(discord.FFmpegPCMAudio(Data[server.id]['Music'][voice_channel.id]['Music Queue'][index]['path']),
            after= lambda: next(Data, channels, server, payload))

async def play(Data, channels, server, payload, *text):
    message = payload['raw']
    ctx = payload['ctx']
    voice_channel = message.author.voice.channel
    text = payload['Content'].split(' ')[1:]

    if voice_channel is None:
        await message.channel.send("You are not in a Voice Channel")
        return
    vc = await get_vc(ctx,voice_channel)

    if vc.is_paused():
        vc.resume()
        return

    if Data[server.id]['Music'].get(voice_channel.id) is None:
        Data[server.id]['Music'][voice_channel.id] = {
            'Music Queue': []
        }
    if Data[server.id]['Music'][voice_channel.id].get('index') is None:
        Data[server.id]['Music'][voice_channel.id]['index'] = 0


    print(text)
    if text and not text[0].isdigit():
        await queue(Data, channels, server, payload, *text)
        text = [str(len(Data[server.id]['Music'][voice_channel.id]['Music Queue'])-1),]

    # play NUM
    if len(text) == 1 and text[0].isdigit():
        index = int(text[0])
        if index >= len(Data[server.id]['Music'][voice_channel.id]['Music Queue']):
            await message.channel.send("That is not a valid Index")
            return

        await message.channel.send(
            "Now Playing: \"" + Data[server.id]['Music'][voice_channel.id]['Music Queue'][index]['title'] + "\""
        )
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(Data[server.id]['Music'][voice_channel.id]['Music Queue'][index]['path']),
                after= lambda: next(Data, channels, server, payload))
        return

async def queue(Data, channels, server, payload, *text):
    message = payload['raw']
    ctx = payload['ctx']
    author = message.author
    text = payload['Content'].split(' ')[1:]

    voice_channel = message.author.voice.channel
    if voice_channel is None:
        await message.channel.send("You are not in a Voice Channel")
        return

    if len(text) == 0:
        await message.channel.send("Please add at least one url for a youtube video")
        return

    vc = await get_vc(ctx, voice_channel)
    if Data[server.id]['Music'].get(voice_channel.id) is None:
        Data[server.id]['Music'][voice_channel.id] = {
            'Music Queue': [],
            'index' : 0
        }

    for url in text:
        if url == '': continue
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            print(url)
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            path = 'music_files/'+info_dict.get('id')+'.mp3'
            print(path)
            try: os.remove(path)
            except: pass
            mes = await message.channel.send('Adding \"'+video_title+'\" to Playlist...')
            ydl.download([url,], )
            while not os.path.isfile(path): pass
            await mes.edit(content='Added \"'+video_title+'\" to Playlist.')

            Data[server.id]['Music'][voice_channel.id]['Music Queue'].append({
                'url': url,
                'title': video_title,
                'path':path
            })
    return Data

async def stop(Data, channels, server, payload, *text):
    message = payload['raw']
    ctx = payload['ctx']
    author = message.author
    voice_channel = message.author.voice.channel
    #vc =  Data[server.id]['Music'][voice_channel.id]['vc']
    vc = ctx.voice_clients
    if vc in [None, []]:
        await message.channel.send("No Voice Channels To Exit Channel")
        return
    else:
        vc = vc[0]
    if voice_channel is None:
        await message.channel.send("You are not in a Voice Channel")
        return
    for obj in Data[server.id]['Music'][voice_channel.id]['Music Queue']:
        os.remove(obj['path'])
    del Data[server.id]['Music'][voice_channel.id]
    await vc.disconnect()
    return Data

async def setup(Data, channels, server, payload):
    Data[server.id]['Music'] = {}
    shutil.rmtree('music_files')
    os.mkdir('music_files')
    ctx = payload['ctx']
    vc = ctx.voice_clients
    for v in vc:
        await v.disconnect()