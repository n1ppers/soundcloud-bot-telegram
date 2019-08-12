import telebot
import os
import re
import os.path
import sys

from sclib import SoundcloudAPI, Track, Playlist
from telebot import types
from telebot import apihelper

def getToken():
    with open("token.txt") as f:
        return str(f.read().replace("\n", ""))

if __name__ == "__main__":
    if not os.path.isdir("cache"):
        os.mkdir("cache")
        print("cache directory created.")
    
    if not os.path.isfile("token.txt"):
        f = open("token.txt", "w+")
        f.write("ur token here")
        f.close()
        print("token.txt created.")
        sys.exit()
    
    print(":^)")

TOKEN = getToken()

bot = telebot.TeleBot(TOKEN)
api = SoundcloudAPI()

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.from_user.username, ": ", message.text)
    if message.text.startswith("/start"):
        command_start(message)
    elif message.text.startswith("/help"):
        command_help(message)
    elif message.text.startswith("/github"):
        command_github(message)
    elif message.text.startswith("/support"):
        command_support(message)
    elif message.text.startswith("/track"):
        command_track(message)
    elif message.text.startswith("/playlist"):
        command_playlist(message)

def command_start(message):
    bot.send_message(message.from_user.id, "Oh, Hello there :^)")
    bot.send_message(message.from_user.id, 
        '''
Commands: 
/github - Get a link to repository with my source code on GitHub 
/support - Contact my owner
/track - Download single track by link 
/playlist - Download all tracks from playlist by link
        ''')

def command_help(message):
    bot.send_message(message.from_user.id, 
        '''
Commands: 
/github - Get a link to repository with my source code on GitHub 
/support - Contact my owner
/track - Download single track by link 
/playlist - Download all tracks from playlist by link
        ''')

def command_github(message):
    bot.send_message(message.from_user.id, "GitHub \nhttps://github.com/n1ppers/soundcloud-bot-telegram")

def command_support(message):
    bot.send_message(message.from_user.id, "Telegram: @n1ppers")

def command_track(message):
    msg = bot.send_message(message.from_user.id, "Please, send me a link to track that you want to download.")
    bot.register_next_step_handler(msg, download_track)

def command_playlist(message):
    msg = bot.send_message(message.from_user.id, "Please, send me a link to playlist that you want to download.")
    bot.register_next_step_handler(msg, download_playlist)

def isLinkValid(link):
    if link.startswith("https://soundcloud.com/"):
        return True
    if link.startswith("http://soundcloud.com/"):
        return True
    if link.startswith("http://m.soundcloud.com/"):
        return True
    if link.startswith("https://m.soundcloud.com/"):
        return True
    
    print("Link is not valid")
    return False

def getURL(msg):
    url = msg
    if not msg.startswith("https://soundcloud.com/"):
        if msg.startswith("http://soundcloud.com/"):
            url = msg.replace("http://soundcloud.com/", "https://soundcloud.com/")
        elif msg.startswith("http://m.soundcloud.com/"):
            url = msg.replace("http://m.soundcloud.com/", "https://soundcloud.com/")
        elif msg.startswith("https://m.soundcloud.com/"):
            url = msg.replace("https://m.soundcloud.com/", "https://soundcloud.com/")
        else:
            url = msg
    
    if "?in=" in url:
        return url.split("?in=")[0]

    return url

def download_track(message):
    if not isLinkValid(message.text):
        bot.send_message(message.from_user.id, "Oops, looks like, that's not a SoundCloud link.")
        return
    
    track = api.resolve(getURL(message.text))
    assert type(track) is Track
    name = f'{track.artist} - {track.title}.mp3'
    fixedname = re.sub('[\|/|:|*|?|"|<|>\|]', '', name)
    filename = f'cache/{fixedname}'
    try:
        with open(filename, 'wb+') as fp:
            track.write_mp3_to(fp)
            audio = open(filename, 'rb')
            bot.send_audio(message.from_user.id, audio)
            os.remove(filename)
    except:
        bot.send_message(message.from_user.id, f"An error has occured while downloading {track.artist} - {track.title}")
        return

def download_playlist(message):
    if not isLinkValid(message.text):
        bot.send_message(message.from_user.id, "Oops, looks like, that's not a SoundCloud link.")
        return
    
    playlist = api.resolve(getURL(message.text))
    assert type(playlist) is Playlist
    for track in playlist.tracks:
        name = f'{track.artist} - {track.title}.mp3'
        fixedname = re.sub('[\|/|:|*|?|"|<|>\|]', '', name)
        filename = f'cache/{fixedname}'
        try:
            with open(filename, 'wb+') as fp:
                track.write_mp3_to(fp)
                audio = open(filename, 'rb')
                bot.send_audio(message.from_user.id, audio)
                os.remove(filename)
        except:              
            bot.send_message(message.from_user.id, f"An error has occured while downloading {track.artist} - {track.title}")
            continue

bot.polling(none_stop=True, interval=0)