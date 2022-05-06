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
import pymongo
import time

client = pymongo.MongoClient("mongodb+srv://bot:<violeta17>@botdb.qeffd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["BotDB"]
col = ""



loop = False
PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '63c07f06da80472980ca73401b662652'
SPOTIPY_CLIENT_SECRET = '537bd3f87a704130b02cc48758647b82'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE ))


exe = "/usr/bin/ffmpeg"
#canciones = []
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
    global loop



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
                info = await texto_a_link(link, message.guild.id)
                inf2 = await texto_a_linkf(link)
                y = True
            try:
                col = db[str(message.guild.id)]
                x = col.insert_one({"link": link, "time": time.time()})
                canal = message.author.voice.channel
                if conectado == False:
                    vc = await canal.connect()
                    conectado = True
            except Exception:
                await message.channel.send("No estas conectado a un canal de voz")
                return
            
            if vc.is_playing() and y == True: #si hay una cancion reproduciendose lo pone en cola
                col = db[str(message.guild.id)]
                x = col.insert_one({"link": link, "time": time.time()})
                msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(col.find())}", url=inf2)
                msg.set_thumbnail(url=info.thumbnail_url)
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                await message.channel.send(embed=msg)
            if vc.is_playing() and y == False: #si hay una cancion reproduciendose lo pone en cola
                col = db[str(message.guild.id)]
                x = col.insert_one({"link": link, "time": time.time()})
                msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(col.find)}", url=link)
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
                        print(song_info)
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
                    x1 = threading.Thread(target=xd, args=(message.guild.id,))
                    x1.start()
                    

                    puesto = True
        except IndexError:
            await message.channel.send("La cancion que has puesto no es valida")
            try:
                kk = db[str(message.guild.id)]
                kk =kk.find()
                oo = 0
                for a in kk["time"]:
                    if a < oo:
                        oo = a
                kk = kk.delete_one({"time": oo})
            except Exception:
                pass
    
    if message.content.startswith("ºadelantar"):
        await adelantar_y_atrasar(message.content, db, message.guild.id)
    
    if message.content.startswith("ºatrasar"):
        await atrasar(message.content, db, message.guild.id)
    
    if message.content == "ºskip":

            
        try:
            vc.stop()
            kk = db[str(message.guild.id)]
            kk =kk.find()
            oo = 0
            for a in kk["time"]:
                if a < oo:
                    oo = a
            kk = kk.delete_one({"time": oo})

            try:
                col = db[str(message.guild.id)]
                info = pytube.YouTube(col.find_one()["link"])
                y = True
            except Exception:
                y = False
            if y == True:
                col = db[str(message.guild.id)]
                msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=col.find_one()["link"])
                msg.set_thumbnail(url=info.thumbnail_url)
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                ydl_opts = {}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    
                    song_info = ydl.extract_info(col.find_one()["link"], download=False)
                    #print(song_info)
            if y == False:
                col = db[str(message.guild.id)]
                msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=col.find_one()["link"])
                #msg.set_thumbnail(url=info.thumbnail_url)
                msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                col = db[str(message.guild.id)]

                r = requests.get(col.find_one()["link"])
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
    if message.content == "ºreconnect":
        await vc.reconnect()
        conectado = True
    if message.content == "ºloop":
        msg = discord.Embed(description= "Se ha activado el bucle", color=0x2ecc71)
        await message.channel.send(embed=msg)
        loop = True
    if message.content == "ºunloop":
        msg = discord.Embed(description= "Se ha desactivado el bucle", color=0xe74c3c)
        await message.channel.send(embed=msg)
        loop = False

    
    
    


        

        
        

        
def xd(guild):
    global sec
    global message2
    sec = 0
    
    while True:
        try:

        
            if vc.is_playing() == False and vc.is_paused() == False:
                
                time.sleep(1)
                if vc.is_playing() == False:
                    sec = 0
                    if loop == False:
                        kk = db[str(guild)]
                        kk =kk.find()
                        oo = 0
                        for a in kk["time"]:
                            if a < oo:
                                oo = a
                        kk = kk.delete_one({"time": oo})
                        
                    try:
                        col = db[str(guild)]
                        info = pytube.YouTube(col.find_one()["link"])
                        y = True
                    except Exception:
                        y = False
                    if y == True:
                        col = db[str(guild)]
                        msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=col.find_one()["link"])
                        msg.set_thumbnail(url=info.thumbnail_url)
                        #msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                        ydl_opts = {}
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            song_info = ydl.extract_info(col.find_one()["link"], download=False)
                            #print(song_info)
                    if y == False:
                        col = db[str(guild)]
                        msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=col.find_one()["link"])
                        #msg.set_thumbnail(url=info.thumbnail_url)
                        #msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                        r = requests.get(col.find_one()["link"])
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

async def texto_a_link(link, guild):
    s = Search(link)
    t = s.results[0]
 
    link = f"https://youtu.be/{str(t)[41:-1]}"
    col = db[str(guild)]
    col.insert_one({"link": link, "time": time.time()})
    return pytube.YouTube(link) #para comprobar si una cancion esta puesta, al enviar el mensaje se comprueba, no todo el rato

async def texto_a_linkf(link):
    s = Search(link)
    t = s.results[0]
 
    link = f"https://youtu.be/{str(t)[41:-1]}"
    return link


async def adelantar_y_atrasar(message, db, guild):
    global sec
    tiempo = message[10: ]
    #print(canciones)
    
    tiempo = sec + int(tiempo)
    sec = tiempo
    
    vc.stop()
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        col = db[str(guild)]
        song_info = ydl.extract_info(col.find_one(), download=False)
        #print(song_info)
    OP = {'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {tiempo}', 'options': '-vn'}
    vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))


async def atrasar(message, db, guild):
    global sec
    tiempo = message[8: ]
    
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
        col = db[str(guild)]
        song_info = ydl.extract_info(col.find_one()["link"], download=False)
        #print(song_info)
    OP = {'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {tiempo}', 'options': '-vn'}
    vc.play(discord.FFmpegOpusAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))


bot.run("NzkyNzQ3ODQ3NzYxMDAyNTM2.GY0Bi9.Ja97YIGdfFsb4qMWU1uQJ5B4Dhh2GHGtI7Z6UM")



