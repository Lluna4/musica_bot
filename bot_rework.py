from __future__ import unicode_literals
import asyncio
import discord
from discord import Color
from discord.utils import get
from discord.ext import commands
from discord import FFmpegOpusAudio
from discord import app_commands
import threading
import time
import pytube
import yt_dlp
import socket
import os
import time
import requests
from tinytag import TinyTag
from pytube import Search
import typing
import pickle
from pathlib import Path
from poke_env.player import Player, RandomPlayer
from multiprocessing import Process,Queue,Pipe


habilidades = []
interactio = ""
moves = ""
s = ""
playing = ""
FORMAT = "utf-8"
my_file = Path("db.a")
if my_file.is_file():
    tags = pickle.load(open('db.a', 'rb'))
else:
    tags = {}

skip = False
vc = ""
queue = {}
titles = []
EXE = "/usr/bin/ffmpeg"
intents = discord.Intents.all()
intents.members = True  
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)



async def desconect(interaction: discord.Interaction):
    try:
        del queue[interaction.guild_id]
    except Exception:
        pass
    queue[interaction.guild_id] = []
    await vc.disconnect()
    vc = ""
    await interaction.response.send_message("Desconectado", ephemeral=True)


async def para(interaction: discord.Interaction):
    global playing
    info = playing
    if vc.is_playing() != False:
        vc.pause()
        thumbnail_url = info.get('thumbnail', '')
        if not thumbnail_url:
            thumbnail_url = 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(info.get('id', ''))
        msg = discord.Embed(title= f"Pausado {info.get('title', '')}", description= f"Se ha pausado {playing.get('title', '')} pulsa reproducir para seguir reproduciendo la cancion", url=info.get("url", ""), color=Color.red())
        msg.set_thumbnail(url=thumbnail_url)
        msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        view = discord.ui.View(timeout=None)
        desconectar = discord.ui.Button(label="Desconectar", style=discord.ButtonStyle.danger)
        parar = discord.ui.Button(label="Reproducir", style=discord.ButtonStyle.blurple)
        try:
            a = queue[interaction.guild_id][0]
            skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.blurple)
        except IndexError:
            skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.gray)
        lista = discord.ui.Button(label="Lista", style=discord.ButtonStyle.blurple)
        desconectar.callback = desconect
        parar.callback = para
        skip.callback = skipp
        lista.callback = listaa
        view.add_item(desconectar)
        view.add_item(parar)
        view.add_item(skip)
        view.add_item(lista)
    else:
        vc.resume()
        thumbnail_url = info.get('thumbnail', '')
        if not thumbnail_url:
            thumbnail_url = 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(info.get('id', ''))
        msg = discord.Embed(title= f"{info.get('title', '')}", description= f"Se esta reproduciendo {info.get('title', '')}", url=info.get("url", ""), color=interaction.user.color)
        msg.set_thumbnail(url=thumbnail_url)
        msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        view = discord.ui.View(timeout=None)
        desconectar = discord.ui.Button(label="Desconectar", style=discord.ButtonStyle.danger)
        parar = discord.ui.Button(label="Stop", style=discord.ButtonStyle.blurple)
        try:
            a = queue[interaction.guild_id][0]
            skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.blurple)
        except IndexError:
            skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.gray)
        lista = discord.ui.Button(label="Lista", style=discord.ButtonStyle.blurple)
        desconectar.callback = desconect
        parar.callback = para
        skip.callback = skipp
        lista.callback = listaa
        view.add_item(desconectar)
        view.add_item(parar)
        view.add_item(skip)
        view.add_item(lista)
    await interaction.response.edit_message(embed=msg, view=view)
async def skipp(interaction: discord.Interaction):
    if queue[interaction.guild_id] != []:
        vc.stop()
        await interaction.response.send_message("Saltando...", ephemeral=True)
    else:
        await interaction.response.send_message("No hay cancion a la que skipear", ephemeral=True)
        return
async def listaa(interaction: discord.Interaction):
    global titles
    if queue[interaction.guild_id] == []:
        await interaction.response.send_message("No hay nada en la cola", ephemeral=True)
        return
    msg = discord.Embed(title="Cola", description="Estas son las canciones que hay en la cola", color=interaction.user.color)
    msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    await interaction.response.defer()
    def extract_song_info(queue_item):
        global titles
        with yt_dlp.YoutubeDL() as ydl:
            song_info = ydl.extract_info(queue_item, download=False)
        title = song_info.get('title', '')
        titles.append(title)
    
    threads = []
    for i in range(len(queue[interaction.guild_id])):
        thread = threading.Thread(target=extract_song_info, args=(queue[interaction.guild_id][i],))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
        
    for i in range(len(queue[interaction.guild_id])):
        title = titles[i]
        msg.add_field(name=f"{i+1}. {title}", value="", inline=False)
    
    await interaction.followup.send(embed=msg, ephemeral=True)



@bot.event
async def on_ready():
    await tree.sync()
    print("Activado!")
    await bot.change_presence(activity=discord.Game(name="/play para poner canciones!"))

@tree.command(name = "play", description= "Pon el nombre o el link de youtube de la cancion que quieras")
@app_commands.describe(cancion="Pon el nombre o el link de la cancion que deseas poner, te autocompleta si lo deseas!")
async def play(interaction: discord.Interaction, cancion: str):
    global vc, queue, EXE, skip, playing, interactio
    buff = []
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
    }
    await interaction.response.defer()
    if "https:" in cancion:
        if "list" in cancion:
            playlist = pytube.Playlist(cancion)
            for url in playlist.video_urls:
                buff.append(url)
            info = yt_dlp.YoutubeDL(ydl_opts).extract_info(buff[0], download=False)
        else:
            info = yt_dlp.YoutubeDL(ydl_opts).extract_info(cancion, download=False)
            buff.append(cancion)
    else:
        s = Search(cancion)
        s = s.results[0]
        info = yt_dlp.YoutubeDL(ydl_opts).extract_info(f"https://youtu.be/{str(s)[41:-1]}", download=False)
        cancion = f"https://youtu.be/{str(s)[41:-1]}"
        buff.append(cancion)
    thumbnail_url = info.get('thumbnail', '')
    if not thumbnail_url:
        thumbnail_url = 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(info.get('id', ''))
    if type(vc) == str and interaction.user.voice != None:
        vc = await interaction.user.voice.channel.connect()
    if vc.is_playing() == True:
        msg = discord.Embed(title="Añadido a la cola", description=f"{info.get('title', '')} ha sido añadido a la cola", color=interaction.user.color)
        msg.set_thumbnail(url=thumbnail_url)
        msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=msg)
        info = playing
        queue[interaction.guild_id].extend(buff)
        thumbnail_url = info.get('thumbnail', '')
        if not thumbnail_url:
            thumbnail_url = 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(info.get('id', ''))
        msg = discord.Embed(title= f"{info.get('title', '')}", description= f"Se esta reproduciendo {info.get('title', '')}", url=info.get("url", ""), color=interaction.user.color)
        msg.set_thumbnail(url=thumbnail_url)
        msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        view = discord.ui.View(timeout=None)
        desconectar = discord.ui.Button(label="Desconectar", style=discord.ButtonStyle.danger)
        parar = discord.ui.Button(label="Stop", style=discord.ButtonStyle.blurple)
        skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.blurple)
        lista = discord.ui.Button(label="Lista", style=discord.ButtonStyle.blurple)
        desconectar.callback = desconect
        parar.callback = para
        skip.callback = skipp
        lista.callback = listaa
        view.add_item(desconectar)
        view.add_item(parar)
        view.add_item(skip)
        view.add_item(lista)
        await interactio.edit_original_response(embed=msg, view=view)
        await asyncio.sleep(10)
        await interaction.delete_original_response()
        return
    if interaction.guild_id not in queue.keys():
        queue[interaction.guild_id] = []
    queue[interaction.guild_id].extend(buff)
    view = discord.ui.View(timeout=None)
    desconectar = discord.ui.Button(label="Desconectar", style=discord.ButtonStyle.danger)
    parar = discord.ui.Button(label="Stop", style=discord.ButtonStyle.blurple)
    try:
        a = queue[interaction.guild_id][1]
        skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.blurple)
    except IndexError:
        skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.gray)
    lista = discord.ui.Button(label="Lista", style=discord.ButtonStyle.blurple)
    desconectar.callback = desconect
    parar.callback = para
    skip.callback = skipp
    lista.callback = listaa
    view.add_item(desconectar)
    view.add_item(parar)
    view.add_item(skip)
    view.add_item(lista)
    msg = discord.Embed(title= f"{info.get('title', '')}", description= f"Se esta reproduciendo {info.get('title', '')}", url=queue[interaction.guild_id][0], color=interaction.user.color)
    msg.set_thumbnail(url=thumbnail_url)
    msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=msg, view=view)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(queue[interaction.guild_id][0], download=False)
    OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    vc.play(discord.FFmpegOpusAudio(executable=EXE, source=song_info['url'], **OP), after=lambda e: asyncio.run(playback(interaction)))
    playing = yt_dlp.YoutubeDL(ydl_opts).extract_info(buff[0], download=False)
    interactio = interaction
    queue[interaction.guild_id].pop(0)


@tree.command(name ="lofi", description= "Pone lofi (del canal de lofi girl) en el canal que estes!")
async def lofi(interaction: discord.Interaction):
    global vc
    if type(vc) == str and interaction.user.voice != None:
        vc = await interaction.user.voice.channel.connect()
    if vc.is_playing() == True:
        msg = discord.Embed(title="Error", description="Ya hay musica poniendose!", color=0xe74c3c)
        await interaction.response.send_message(embed=msg)
        return

    ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist':'True',
    'outtmpl': 'song.%(ext)s',
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
    }]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info("https://www.youtube.com/watch?v=jfKfPfyJRdk", download=False)
    OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    vc.play(discord.FFmpegOpusAudio(executable=EXE, source=song_info['url'], **OP), after=lambda e: asyncio.run(playback(interaction)))
    msg = discord.Embed(title="💖Lofi💖", description="Se esta reproduciendo lofi", color=0xe91e63)
    await interaction.response.send_message(embed=msg)

@tree.command(name ="un-lofi", description= "Quita el lofi de tu canal")
async def unlofi(interaction: discord.Interaction):
    global vc
    if type(vc) != str and vc.is_playing() == True:
        await vc.disconnect()
        vc = ""
        msg = discord.Embed(title="Hecho!", description="Se ha desconectado el lofi de tu canal", color=0x2ecc71)
    else:
        msg = discord.Embed(title="Error", description="No hay musica poniendose", color=0xe74c3c)
    
    await interaction.response.send_message(embed=msg)




@play.autocomplete('cancion')
async def fruits_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    fruits = Search(current).completion_suggestions
    print(type(fruits))
    print(len(fruits))
    return [
        app_commands.Choice(name=fruit, value=fruit)
        for fruit in fruits if current.lower() in fruit.lower()
    ]

async def playback(interaction: discord.Interaction):
    global queue, vc, playing
    print(len(queue[interaction.guild_id]))
    ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist':'True',
    'outtmpl': 'song.%(ext)s',
    'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
    }]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(queue[interaction.guild_id][0], download=False)
    OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    vc.play(discord.FFmpegOpusAudio(executable=EXE, source=song_info['url'], **OP), after=lambda e: asyncio.run(playback(interaction)))
    queue[interaction.guild_id].pop(0)
    info = song_info
    thumbnail_url = info.get('thumbnail', '')
    if not thumbnail_url:
        thumbnail_url = 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(info.get('id', ''))
    msg = discord.Embed(title= f"{info.get('title', '')}", description= f"Se esta reproduciendo {info.get('title', '')}", url=info.get("url", ""), color=interaction.user.color)
    msg.set_thumbnail(url=thumbnail_url)
    msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    view = discord.ui.View(timeout=None)
    desconectar = discord.ui.Button(label="Desconectar", style=discord.ButtonStyle.danger)
    parar = discord.ui.Button(label="Stop", style=discord.ButtonStyle.blurple)
    try:
        a = queue[interaction.guild_id][1]
        skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.blurple)
    except IndexError:
        skip = discord.ui.Button(label="Skip", style=discord.ButtonStyle.gray)
    lista = discord.ui.Button(label="Lista", style=discord.ButtonStyle.blurple)
    desconectar.callback = desconect
    parar.callback = para
    skip.callback = skipp
    lista.callback = listaa
    view.add_item(desconectar)
    view.add_item(parar)
    view.add_item(skip)
    view.add_item(lista)
    send_fut = asyncio.run_coroutine_threadsafe(interaction.edit_original_response(embed=msg, view=view), bot.loop)
    send_fut.result()
    playing = song_info

@tree.command(name = "set-fc", description= "Pon los gamertags que quieras de la lista!")
@app_commands.describe(n3ds="Pon tu codigo de amigo de 3ds. Ejemplo: 4141-9637-9341")
@app_commands.describe(switch="Pon tu codigo de amigo de switch. Ejemplo: SW-2809-4574-2883")
@app_commands.describe(pogo="Pon tu codigo de amigo de pokemon go. Ejemplo: 9387-7346-1802")
@app_commands.describe(masters="Pon tu codigo de amigo de pokemon masters. Ejemplo: 9181-3142-9313-6046")
@app_commands.describe(home="Pon tu codigo de amigo de pokemon home. Ejemplo: LKMWQXNKLZLZ")
@app_commands.describe(unite="Pon tu codigo de amigo de pokemon unite. Ejemplo: Y1292Q6")
async def setfc(interaction: discord.Interaction, n3ds: typing.Optional[str], switch: typing.Optional[str], pogo: typing.Optional[str], masters: typing.Optional[str], home: typing.Optional[str], unite: typing.Optional[str]):
    global tags
    gamertags = []
    if (n3ds):
        gamertags.append({"n3ds":n3ds})
    if (switch):
        gamertags.append({"switch":switch})
    if (pogo):
        gamertags.append({"pogo":pogo})
    if (masters):
        gamertags.append({"masters":masters})
    if (home):
        gamertags.append({"home":home})
    if (unite):
        gamertags.append({"unite":unite})
    try:
        if (tags[interaction.user.id]):
            li = tags[interaction.user.id]
            for i in li:
                gamertags.append(i)
    except Exception:
        pass
    tags.update({interaction.user.id: gamertags})
    pickle.dump(tags, open("db.a", "wb"))
    msg = discord.Embed(title="Hecho!", description="Se ha establecido correctamente tu código de amigo.", color=0x2ecc71)
    print(tags)
    await interaction.response.send_message(embed=msg, ephemeral=True)

@tree.command(name = "fc", description= "Muestra los gamertags de algiuen o si no pones argumentos son los tuyos propios")
@app_commands.describe(usuario="Pinguea el usuario del cual quieres ver los tags, sino pones nada pone los tuyos")
async def fc(interaction: discord.Interaction, usuario: typing.Optional[str]):
    global tags
    if usuario:
        int(usuario[2:-1])
        user = bot.get_user(int(usuario[2:-1]))
    else:
        user = interaction.user
    desc = ""
    try:
        datos = tags[user.id]
    except Exception:
        msg = discord.Embed(title="Error", description="La persona que has mencionado no tiene puestos sus tags!", color=0xe74c3c)
        await interaction.response.send_message(embed=msg)
        return
    for i in datos:
        key = i.keys()
        for a in key:
            desc = desc + f"**{a.upper()}**\n{i[a]}\n\n"
    if desc == "":
        msg = discord.Embed(title="Error", description="La persona que has mencionado no tiene puestos sus tags!")
    else:
        msg = discord.Embed(title=f"Codigos de amigo de {user.display_name}", description=desc, color=user.color)
    await interaction.response.send_message(embed=msg)

@tree.command(name = "del-fc", description= "Borra tu perfil de codigos de amigo")
async def delete(interaction: discord.Interaction):
    global tags
    user = interaction.user
    try:
        del tags[user.id]
        pickle.dump(tags, open("db.a", "wb"))
        msg = discord.Embed(title="Hecho!", description="Se ha borrado correctamente tu perfil", color=0x2ecc71)
    except Exception:
        msg = discord.Embed(title="Error", description="No tienes tus tags puestos", color=0xe74c3c)
    await interaction.response.send_message(embed=msg, ephemeral=True)

@tree.command(name = "custom-fc", description= "Pon el codigo que quieras del juego que quieras!")
async def custom(interaction: discord.Interaction, juego: str, codigo: str):
    global tags
    gamertags = []

    try:
        if (tags[interaction.user.id]):
            li = tags[interaction.user.id]
            for i in li:
                gamertags.append(i)
    except Exception:
        pass
    gamertags.append({juego: codigo})
    tags.update({interaction.user.id: gamertags})
    pickle.dump(tags, open("db.a", "wb"))
    msg = discord.Embed(title="Hecho!", description="Se ha establecido correctamente tu código de amigo.", color=0x2ecc71)
    print(tags)
    await interaction.response.send_message(embed=msg, ephemeral=True)
    
bot.run("")

