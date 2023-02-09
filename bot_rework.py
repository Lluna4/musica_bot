from __future__ import unicode_literals
import discord
from discord.utils import get
from discord.ext import commands
from discord import FFmpegOpusAudio
from discord import app_commands

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

vc = ""
lista = []
EXE = "/usr/bin/ffmpeg"
intents = discord.Intents.all()
intents.members = True  
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

class reproductor(discord.ui.View):
    parar : bool = True
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def parar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.parar = True
        if self.parar == True:
            vc.pause()
            button.label = "Play"
            self.parar = False
            await interaction.response.send_message("Pausado", ephemeral=True)
        else:
            vc.resume()
            button.label = "Stop"
            self.parar = True
            await interaction.response.edit_message(view=self)


@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=792826492102377504))
    print("uff")
    await bot.change_presence(activity=discord.Game(name="/play para poner canciones!"))

@tree.command(name = "play", description= "Pon el nombre o el link de youtube de la cancion que quieras", guild=discord.Object(id=792826492102377504))
async def play(interaction: discord.Interaction, link: str):
    global vc, lista, EXE
    if "https:" in link:
        info = pytube.YouTube(link)
    else:
        s = Search(link)
        s = s.results[0]
        info = pytube.YouTube(f"https://youtu.be/{str(s)[41:-1]}")
        link = f"https://youtu.be/{str(s)[41:-1]}"
    if info.title == None:
        info.title = ""
    if type(vc) != str:
        if vc.is_playing() == True:
            lista.append(link)
            msg = discord.Embed(title= f"{info.title}", description= f"Se ha puesto en cola {info.title}, esta en el puesto {len(lista)}", url=link, color=interaction.user.color)
            msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=msg)
        else:
            msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=lista[0], color=interaction.user.color)
            msg.set_thumbnail(url=info.thumbnail_url)
            msg.set_author(name= interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=msg)
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
                song_info = ydl.extract_info(lista[0], download=False)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegOpusAudio(executable=EXE, source=song_info["formats"][0]["url"], **OP))
    else:
        if interaction.user.voice != None:
            lista.append(link)
            vc = await interaction.user.voice.channel.connect()
            view = reproductor()
            msg = discord.Embed(title= f"{info.title}", description= f"Se esta reproduciendo {info.title}", url=lista[0], color=interaction.user.color)
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
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(lista[0], download=False)
            OP = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegOpusAudio(executable=EXE, source=song_info["formats"][0]["url"], **OP))
        else:
            msg = discord.Embed(title="Error", description="No estas en un canal de voz", color=0xe74c3c)

bot.run("")

