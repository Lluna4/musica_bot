from __future__ import unicode_literals
import asyncio
import discord
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


my_file = Path("db.a")
if my_file.is_file():
    tags = pickle.load(open('db.a', 'rb'))
else:
    tags = {}


skip = False
vc = ""
queue = {}
EXE = "/usr/bin/ffmpeg"
intents = discord.Intents.all()
intents.members = True  
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

class reproductor(discord.ui.View):
    @discord.ui.button(label="Desconectar", style=discord.ButtonStyle.danger)
    async def desconectar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            del lista
        except Exception:
            pass
        lista = []
        await vc.disconnect()
        await interaction.response.send_message("Desconectado", ephemeral=True)

    @discord.ui.button(label="Stop/Resume", style=discord.ButtonStyle.blurple)
    async def parar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if vc.is_playing() == False:
            vc.resume()
            button.label = "Stop"
            self.parar = False
            await interaction.response.send_message("Vuelto a poner", ephemeral=True)
        else:
            vc.pause()
            button.label = "Play"
            self.parar = True
            await interaction.response.send_message("Pausado", ephemeral=True)
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if queue[interaction.guild_id] != []:
            vc.stop()
            await interaction.response.send_message("Saltando...", ephemeral=True)
        else:
            await interaction.response.send_message("No hay cancion a la que skipear")
            return
    @discord.ui.button(label="Lista", style=discord.ButtonStyle.blurple)
    async def lista(self, interaction: discord.Interaction, button: discord.ui.Button):
        if queue[interaction.guild_id] == []:
            await interaction.response.send_message("No hay nada en la cola", ephemeral=True)
            return
        msg = discord.Embed(title="Cola", description="Estas son las canciones que hay en la cola", color=interaction.user.color)
        msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        for i in range(len(queue[interaction.guild_id])):
            while True:
                try:
                    info = pytube.YouTube(queue[interaction.guild_id][i])
                    break
                except pytube.exceptions.PytubeError:
                    pass
            msg.add_field(name=f"{i+1}. {info.title}", value="", inline=False)
        await interaction.response.send_message(embed=msg, ephemeral=True)



@bot.event
async def on_ready():
    await tree.sync()
    print("Activado!")
    await bot.change_presence(activity=discord.Game(name="/play para poner canciones!"))

@tree.command(name = "play", description= "Pon el nombre o el link de youtube de la cancion que quieras")
@app_commands.describe(cancion="Pon el nombre o el link de la cancion que deseas poner, te autocompleta si lo deseas!")
async def play(interaction: discord.Interaction, cancion: str):
    global vc, queue, EXE, skip
    buff = []
    if "https:" in cancion:
        if "list" in cancion:
            playlist = pytube.Playlist(cancion)
            for url in playlist.video_urls:
                buff.append(url)
            #repeat pytube.YouTube until it works
            while True:
                try:
                    info = pytube.YouTube(playlist.video_urls[0])
                    break
                except pytube.exceptions.PytubeError:
                    pass
            print(buff)
        else:
            #repeat pytube.YouTube until it works
            while True:
                try:
                    info = pytube.YouTube(cancion)
                    break
                except pytube.exceptions.PytubeError:
                    pass
            buff.append(cancion)        
    else:
        s = Search(cancion)
        s = s.results[0]
        info = pytube.YouTube(f"https://youtu.be/{str(s)[41:-1]}")
        cancion = f"https://youtu.be/{str(s)[41:-1]}"
        buff.append(cancion)
    if info.title == None:
        info.title = ""
    
    if type(vc) == str and interaction.user.voice != None:
        vc = await interaction.user.voice.channel.connect()
    if vc.is_playing() == True:
        msg = discord.Embed(title="Añadido a la cola", description=f"{info.title} ha sido añadido a la cola", color=interaction.user.color)
        msg.set_thumbnail(url=info.thumbnail_url)
        msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=msg)
        queue[interaction.guild_id].extend(buff)
        return
    if interaction.guild_id not in queue:
        queue[interaction.guild_id] = []
    queue[interaction.guild_id].extend(buff)
    view = reproductor()
    msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=queue[interaction.guild_id][0], color=interaction.user.color)
    msg.set_thumbnail(url=info.thumbnail_url)
    msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=msg, view=view)
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
    global queue, vc
    #this function plays the next song in the queue
    if len(queue[interaction.guild_id]) == 0:
        await vc.disconnect()
        vc = ""
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
        song_info = ydl.extract_info(queue[interaction.guild_id][0], download=False)
    OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    vc.play(discord.FFmpegOpusAudio(executable=EXE, source=song_info['url'], **OP), after=lambda e: asyncio.run(playback(interaction)))
    queue[interaction.guild_id].pop(0)
    

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

