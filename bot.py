from __future__ import unicode_literals
import discord
from discord.utils import get
from discord.ext import commands
from discord import FFmpegPCMAudio
import os
from os import listdir
import threading
import time
import pytube
import youtube_dl

from pytube import Search


exe = "/usr/bin/ffmpeg"
cancion = False
conectado = False
canciones = []
num = 0
pausado = False

vc = ""

num = 0

intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("uff")
    await bot.change_presence(activity=discord.Game(name="Ser musico"))


@bot.event
async def on_message(message):
    global cancion
    global conectado
    global num
    global canciones
    global vc
    global num
    global pausado
    if message.content.startswith(".p"):
        link = message.content[3: ]
        print(link)
        if "https" in link:
           t = pytube.YouTube(link)
           #img = t.thumbnail_url
        
        else:

            s = Search(link)
            print(s.results)
            print(type(s.results))
            t = s.results[0]
            print(type(t))
            print(str(t)[41:-2])
            #img = t.thumbnail_url
            link = f"https://youtu.be/{str(t)[41:-1]}"
            #print(img)
            
        canciones.append(link)
        print(canciones[0])
        if cancion == True:
            mensaje1 = discord.Embed(title= f"{t.title}", description= f"Se ha puesto en cola {t.title}, esta en el puesto {len(canciones)}", url=link)
            #mensaje1.set_thumbnail(url=img)
            #mensaje1.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            await message.channel.send(embed= mensaje1)
            
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(canciones[0], download=False)


            print(canciones)
           
            
        else:
            mensaje = discord.Embed(title= f"{t.title}", description= f"Se esta reproduciendo {t.title}", url=link)
            #mensaje.set_thumbnail(url=img)
            mensaje.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(canciones[0], download=False)
 
            
            cancion = True
            canal = message.author.voice.channel
            if conectado == False:
                vc = await canal.connect()
                conectado = True
            
            def con(vc, conectado, canciones, num, pausado):
                while True:
                    time.sleep(1)
                    if vc.is_playing() == False and pausado == False:
                        print(pausado)

                        try:
                            conectado = False
                            #os.remove(f"{num}.mp4")
                        
                        
                            ydl_opts = {}
                            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                                
                                song_info = ydl.extract_info(canciones[0], download=False)

                            

                                mensaje = discord.Embed(title= f"{t.title}", description= f"Se esta reproduciendo {t.title}", url=link)
                                #mensaje.set_thumbnail(url=img)
                                mensaje.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                                OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
                                vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP ))
                                del canciones[0]
                                num = 0
                            
                        except Exception:
                            pass
                        

                    else:
                        conectado = True
            
            t1 = threading.Thread(target=con, args=(vc, conectado, canciones, num, pausado))
            t1.start()
            
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            
            await message.channel.send(embed=mensaje)
            del canciones[0]
            num = 0
    
    if message.content == ".skip":
        vc.stop()
        #os.remove(f"{num}.mp4")
    
    
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            
            song_info = ydl.extract_info(canciones[0], download=False)
            t = pytube.YouTube(canciones[0])

        

            mensaje = discord.Embed(title= f"{t.title}", description= f"Se esta reproduciendo {t.title}", url=link)
            #mensaje.set_thumbnail(url=img)
            mensaje.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}
            vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            del canciones[0]
            num = 0
        
    if message.content == ".calla":
        vc.pause()
        pausado = True
        await message.channel.send("Vale bro :(")
    
    if message.content == ".continua":
        vc.resume()
        pausado = False
        await message.channel.send("Procedo a continuar 🎶")
        

            




        
        

bot.run("NzkyNzQ3ODQ3NzYxMDAyNTM2.X-iN9w.gmQ76OlwPjgwbbVy_kdKZHE8G50")


