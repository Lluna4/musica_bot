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
    if message.content.startswith("!p"):
        link = message.content[3: ]
        print(link)
        num += 1
        canciones.append(link)
        print(canciones[0])
        if cancion == True:
            await message.channel.send("Se ha puesto en cola")
            print(canciones)
           
            
        else:
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
            
            def con(vc, conectado, canciones):
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
                                os.rename(files, f"{num}.mp4")
                                vc.play(discord.FFmpegPCMAudio(executable=r"/ffmpeg_4.3.2.orig.tar.xz", source=f"{num}.mp4"))
                                del canciones[0]

                    else:
                        conectado = True
            
            t1 = threading.Thread(target=con, args=(vc, conectado, canciones))
            t1.start()
            
            
            vc.play(discord.FFmpegPCMAudio(executable=r"C:\Users\carly\Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg.exe", source=f"{num}.mp4"))
            del canciones[0]
            




        
        

bot.run("ODYyNzcwMTcwNjI4MTQ1MTUy.YOdLVg.ODImCoESKnuY26vjp7JioyMpUIo")


