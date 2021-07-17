from __future__ import unicode_literals
import discord
from discord.utils import get
from discord.ext import commands
from discord import FFmpegPCMAudio
import os
from os import listdir
import threading
import time
import youtube_dl

from pytube import Search



cancion = False
conectado = False
canciones = []


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
    if message.content.startswith("@p"):
        link = message.content[3: ]
        print(link)
        s = Search(link)
        print(s.results)
        print(type(s.results))
        t = s.results[0]
        print(type(t))
        print(str(t)[41:-2])
        img = t.thumbnail_url
        link = f"https://youtu.be/{str(t)[41:-1]}"
        print(img)
        
        canciones.append(link)
        print(canciones[0])
        if cancion == True:
            mensaje1 = discord.Embed(title= f"{t.title}", description= f"Se ha puesto en cola {t.title}, esta en el puesto {len(canciones)}", url=link)
            await message.channel.send(embed= mensaje1)
            mensaje1.set_thumbnail(url=img)
            mensaje1.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            print(canciones)
           
            
        else:
            mensaje = discord.Embed(title= f"{t.title}", description= f"Se esta reproduciendo {t.title}", url=link)
            mensaje.set_thumbnail(url=img)
            mensaje.set_author(name= message.author.name, icon_url=message.author.avatar_url)
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            for files in listdir(path="C:/Users/carly/Downloads/bot_musica_discord"):
                print(files)
                
                
                if ".mp4" in files:
                    os.rename(files, f"{num}.mp4")
            
            cancion = True
            canal = message.author.voice.channel
            if conectado == False:
                vc = await canal.connect()
                conectado = True
            
            def con(vc, conectado, canciones, num):
                while True:
                    time.sleep(1)
                    if vc.is_playing() == False:
                        conectado = False
                        os.remove(f"{num}.mp4")
                        
                        
                        ydl_opts = {}
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            
                            ydl.download([canciones[0]])
                            
                        for files in listdir(path="C:/Users/carly/Downloads/bot_musica_discord"):
                            print(files)
                            if ".mp4" in files:
                                mensaje = discord.Embed(title= f"{t.title}", description= f"Se esta reproduciendo {t.title}", url=link)
                                mensaje.set_thumbnail(url=img)
                                mensaje.set_author(name= message.author.name, icon_url=message.author.avatar_url)
                                os.rename(files, f"{num}.mp4")
                                vc.play(discord.FFmpegPCMAudio(executable=r"C:\Users\carly\Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg.exe", source=f"0.mp4"))

                                del canciones[0]
                                num = 0

                    else:
                        conectado = True
            
            t1 = threading.Thread(target=con, args=(vc, conectado, canciones, num))
            t1.start()
            
            
            vc.play(discord.FFmpegPCMAudio(executable=r"C:\Users\carly\Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg.exe", source=f"0.mp4"))
            await message.channel.send(embed=mensaje)
            del canciones[0]
            num = 0
            




        
        

bot.run("NzkyNzQ3ODQ3NzYxMDAyNTM2.X-iN9w.gmQ76OlwPjgwbbVy_kdKZHE8G50")


