from __future__ import unicode_literals
import discord
from discord.utils import get
from discord.ext import commands
from discord import FFmpegPCMAudio

import threading
import time
import pytube
import youtube_dl
import socket
import asyncio
import time

from pytube import Search

exe = "/usr/bin/ffmpeg"
canciones = []
conectado = False
vc = ""
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
puesto = False
conn = ""
sec = 0
inf2 = ""
info = ""
message2 = ""

intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("uff")
    await bot.change_presence(activity=discord.Game(name="Recordar al mas grande"))


@bot.event
async def on_message(message):
    global conectado
    global vc
    global puesto
    global sec
    global inf2
    global info
    global message2
    if message.content.startswith("-p"):
        link = await linkd(message.content)
        if "https" in link:
            info = pytube.YouTube(link)
            inf2 = link
        else:
            info = await texto_a_link(link)
            inf2 = await texto_a_linkf(link)
        try:
            canciones.append(link)
            canal = message.author.voice.channel
            if conectado == False:
                vc = await canal.connect()
                conectado = True
        except Exception:
            await message.channel.send("No estas conectado a un canal de voz")
            return
        
        if vc.is_playing(): #si hay una cancion reproduciendose lo pone en cola
           msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(canciones) - 1}", url=inf2)
           msg.set_thumbnail(url=info.thumbnail_url)
           msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
           await message.channel.send(embed=msg)
        else: #reproduce la cancion
            msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=inf2)
            msg.set_thumbnail(url=info.thumbnail_url)
            msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(canciones[0], download=False)
                #print(song_info)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            await message.channel.send(embed=msg)
            if puesto == False:
                asyncio.get_event_loop().create_task(xd())
                

                puesto = True
    
    if message.content.startswith("-adelantar"):
        await adelantar_y_atrasar(message.content, canciones)
    
    if message.content.startswith("-atrasar"):
        await atrasar(message.content, canciones)
    
    if message.content == "-skip":
        try:
            
            del canciones[0]
            info = pytube.YouTube(canciones[0])
            msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=canciones[0])
            msg.set_thumbnail(url=info.thumbnail_url)
            msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            ydl_opts = {}
            vc.stop()
            
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(canciones[0], download=False)
                #print(song_info)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            await message.channel.send(embed=msg)
        except Exception:
            canciones.append(link)
            await message.channel.send("No hay cancion a la que skipear")
    
    if message.content == "-stop":
        vc.pause()
        await message.channel.send("Vale bro")
    if message.content == "-resume":
        vc.resume()
        await message.channel.send("Volviendo con la musica")
    if message.content == "-disconnect":
        vc.disconnect()
    

    
    
    


        

        
        

        
async def xd():
    global sec
    global message2
    sec = 0
    
    while True:
        try:

        
            if vc.is_playing() == False and vc.is_paused() == False:
                
                time.sleep(1)
                if vc.is_playing() == False:
                    sec = 0
                    del canciones[0]
                    info = pytube.YouTube(canciones[0])
                    msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=canciones[0])
                    msg.set_thumbnail(url=info.thumbnail_url)
                    msg.set_author(name= message2.author.name, icon_url=message2.author.avatar_url) #hay que guardar autores para que esto funcione
                    await message2.channel.send(embed=msg)
                    ydl_opts = {}
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        song_info = ydl.extract_info(canciones[0], download=False)
                        #print(song_info)
                    OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
                    vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
        except Exception:
            pass
            
        
        if vc.is_playing() != False:
            sec += 1
            print(sec)
        time.sleep(1)



async def linkd(message):
    link = message[3: ]
    print(link)
    return link

async def texto_a_link(link):
    s = Search(link)
    t = s.results[0]
 
    link = f"https://youtu.be/{str(t)[41:-1]}"
    canciones.append(link)
    return pytube.YouTube(link) #para comprobar si una cancion esta puesta, al enviar el mensaje se comprueba, no todo el rato

async def texto_a_linkf(link):
    s = Search(link)
    t = s.results[0]
 
    link = f"https://youtu.be/{str(t)[41:-1]}"
    return link


async def adelantar_y_atrasar(message, canciones):
    global sec
    tiempo = message[10: ]
    print(canciones)
    
    tiempo = sec + int(tiempo)
    sec = tiempo
    
    vc.stop()
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(canciones[0], download=False)
        #print(song_info)
    OP = {'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {tiempo}', 'options': '-vn'}
    vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))


async def atrasar(message, canciones):
    global sec
    tiempo = message[8: ]
    print(canciones)
    print(sec)
    print(tiempo)
    tiempo = sec - int(tiempo)
    if tiempo < 0:
        tiempo = 0
    print(tiempo)
    sec = tiempo
    
    vc.stop()
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(canciones[0], download=False)
        #print(song_info)
    OP = {'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {tiempo}', 'options': '-vn'}
    vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))



bot.run("TOKEN")
