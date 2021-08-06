from __future__ import unicode_literals
import discord
from discord.utils import get
from discord.ext import commands
from discord import FFmpegPCMAudio

import threading
import time
import pytube
import youtube_dl

import time

from pytube import Search

exe = r"C:\Users\carly\Downloads/ffmpeg-4.4-full_build/ffmpeg-4.4-full_build/bin/ffmpeg.exe"
canciones = []
conectado = False
vc = ""

puesto = False



intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("uff")
    await bot.change_presence(activity=discord.Game(name="Ser musico"))


@bot.event
async def on_message(message):
    global conectado
    global vc
    global puesto
    if message.content.startswith(".p"):
        link = await linkd(message.content)
        if "https" in link:
            info = pytube.YouTube(link)
        else:
            info = await texto_a_link(link)
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
           msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(canciones)}", url=link)
           msg.set_thumbnail(url=info.thumbnail_url)
           msg.set_author(name= message.author.name, icon_url=message.author.avatar_url)
           await message.channel.send(embed=msg)
        else: #reproduce la cancion
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(canciones[0], download=False)
                print(song_info)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
            if puesto == False:
                x1 = threading.Thread(target=xd)
                x1.start()
                

                puesto = True

        
        

        
def xd():
    while True:
        del canciones[0]
        if vc.is_playing() == False:
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(canciones[0], download=False)
                print(song_info)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(executable=exe, source=song_info["formats"][0]["url"], **OP))
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



bot.run("ODYyNzcwMTcwNjI4MTQ1MTUy.YOdLVg.ODImCoESKnuY26vjp7JioyMpUIo")