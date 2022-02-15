from __future__ import unicode_literals
import discord
from discord.utils import get
from discord.ext import commands
from discord import FFmpegOpusAudio

import threading
import time
import pytube
import youtube_dl
import socket
import os
import time
import requests
from tinytag import TinyTag
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from pytube import Search




PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '63c07f06da80472980ca73401b662652'
SPOTIPY_CLIENT_SECRET = '537bd3f87a704130b02cc48758647b82'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE ))


exe = r"C:\Users\carly\Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg.exe"
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
y = False

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
    global y



    if message.content.startswith("ºp"):
        try:
            link = await linkd(message.content)
            if "youtu" in link:
                info = pytube.YouTube(link)
                inf2 = link
                y = True
            elif "discord" in link:
                r = requests.get(link)
                with open("m1.mp4", "wb") as f:
                    f.write(r.content)
                info = TinyTag.get("m1.mp4", image=True)
                y = False
            elif "spotify" in link:
                c = sp.track(link)
                print(c["name"])

            else:
                info = await texto_a_link(link)
                inf2 = await texto_a_linkf(link)
                y = True
            try:
                canciones.append(link)
                canal = message.author.voice.channel
                if conectado == False:
                    vc = await canal.connect()
                    conectado = True
            except Exception:
                await message.channel.send("No estas conectado a un canal de voz")
                return
            
            if vc.is_playing() and y == True: #si hay una cancion reproduciendose lo pone en cola
                msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(canciones) - 2}", url=inf2)
                msg.set_thumbnail(url=info.thumbnail_url)
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=msg)
            if vc.is_playing() and y == False: #si hay una cancion reproduciendose lo pone en cola
                msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(canciones) - 2}", url=link)
                #msg.set_thumbnail(url=info.get_image())
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=msg)
            else: #reproduce la cancion
                if y == True:
                    msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=inf2)
                    msg.set_thumbnail(url=info.thumbnail_url)
                    msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist':'True',
        'outtmpl': 'song.%(ext)s',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]}
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        song_info = ydl.extract_info(inf2, download=False)
                        #print(song_info)
                if y == False:
                    msg = discord.Embed(title= f"{link}", description= f"Se esta reproduciendo {link}", url=link)
                    #msg.set_thumbnail(url=info.get_image())
                    msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
 
                
                if y == True:
                    OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
                    vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
                if y == False:
                    vc.play(discord.FFmpegOpusAudio(executable=exe, source="m1.mp4"))
                    
                await message.channel.send(embed=msg)
                if puesto == False:
                    x1 = threading.Thread(target=xd)
                    x1.start()
                    

                    puesto = True
        except IndexError:
            await message.channel.send("La cancion que has puesto no es valida")
            try:
                del canciones[0]
            except Exception:
                pass
    
    if message.content.startswith("ºadelantar"):
        await adelantar_y_atrasar(message.content, canciones)
    
    if message.content.startswith("ºatrasar"):
        await atrasar(message.content, canciones)
    
    if message.content == "ºskip":

            
        try:
            vc.stop()
            del canciones[0]
            try:
                info = pytube.YouTube(canciones[0])
                y = True
            except Exception:
                y = False
            if y == True:
                msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=canciones[0])
                msg.set_thumbnail(url=info.thumbnail_url)
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                ydl_opts = {}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    song_info = ydl.extract_info(canciones[0], download=False)
                    #print(song_info)
            if y == False:
            
                msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=canciones[0])
                #msg.set_thumbnail(url=info.thumbnail_url)
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                r = requests.get(canciones[0])
                try:
                    with open("m1.mp4", "wb") as f:
                        f.write(r.content)
                except Exception:
                    os.remove("m1.mp4")
                    with open("m1.mp4", "wb") as f:
                        f.write(r.content)

                    
                
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            if y == True:
                vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            if y == False:
                vc.play(discord.FFmpegOpusAudio(executable=exe, source="m1.mp4"))

            await message.channel.send(embed=msg)
        except Exception:
            await message.channel.send("No hay cancion a la que skipear")
    
    if message.content == "ºstop":
        await vc.pause()
        await message.channel.send("Vale bro")
    if message.content == "ºresume":
       await vc.resume()
       await message.channel.send("Volviendo con la musica")
    if message.content == "ºdisconnect":
        await vc.disconnect()
        conectado = False
    

    
    
    


        

        
        

        
def xd():
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
                    try:
                        info = pytube.YouTube(canciones[0])
                        y = True
                    except Exception:
                        y = False
                    if y == True:
                        msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=canciones[0])
                        msg.set_thumbnail(url=info.thumbnail_url)
                        #msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                        ydl_opts = {}
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            song_info = ydl.extract_info(canciones[0], download=False)
                            #print(song_info)
                    if y == False:
                    
                        msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=canciones[0])
                        #msg.set_thumbnail(url=info.thumbnail_url)
                        #msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                        r = requests.get(canciones[0])
                        try:
                            with open("m1.mp4", "wb") as f:
                                f.write(r.content)
                        except Exception:
                            os.remove("m1.mp4")
                            with open("m1.mp4", "wb") as f:
                                f.write(r.content)

                    
                
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            if y == True:
                vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            if y == False:
                vc.play(discord.FFmpegOpusAudio(executable=exe, source="m1.mp4"))
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
    vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))


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
    vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))



bot.run("TOKEN")



