import telebot
import os
import re
import os.path
import sys

from sclib import SoundcloudAPI, Track, Playlist
from telebot import types
from telebot import apihelper

#def getValue(variable):
#    string = ""
#    value = ""
#    if ("=" not in variable):
#        string = str(variable + "=")
#    else:
#        string = variable
#    with open("main.cfg") as f:
#        cfg = f.readlines()
#        for i in range(len(cfg)):
#           if (cfg[i].startswith(string)):
#               value = cfg[i].replace(string, "")
#            else:
#                continue
#
#        return value

def getToken():
    with open("token.txt") as f:
        return str(f.read().replace("\n", ""))

if __name__ == "__main__":
    #if not os.path.exists("main.cfg"):
    #    f = open("main.cfg", "w+")
    #    f.write("%s\n%s\n%s\n%s" % ("token=urtokenhere", "proxy_type=http", "proxy_ip=127.0.0.1", "proxy_port=80"))
    #    #f.write("token=urtokenhere \n")
    #    #f.write("proxy_type=http \n")
    #    #f.write("proxy_ip=127.0.0.1 \n")
    #    #f.write("\nproxy_port=80")
    #    f.close()
    if not os.path.exists("token.txt"):
        f = open("token.txt", "w+")
        f.write("ur token here")
        f.close()
        print("token.txt created.")
        sys.exit()

    print(":^)")

    #print(getValue("token"))
    #print(getValue("proxy_type"))
    #print(getValue("proxy_ip"))
    #print(getValue("proxy_port"))

TOKEN = getToken() #getValue("token")
#PROXY_TYPE = getValue("proxy_type")
#PROXY_IP = getValue("proxy_ip")
#PROXY_PORT = getValue("proxy_port")

#if not PROXY_IP == "" and not PROXY_IP == "127.0.0.1":
    #apihelper.proxy = {PROXY_TYPE:PROXY_IP}

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
    name = f'./{track.artist} - {track.title}.mp3'
    filename = re.sub('[\|/|:|*|?|"|<|>\|]', '', name)
    with open(filename, 'wb+') as fp:
        try:
            track.write_mp3_to(fp)
            audio = open(filename, 'rb')
            bot.send_audio(message.from_user.id, audio)
            os.remove(filename)
        except (FileNotFoundError):
            bot.send_message(message.from_user.id, "An error has occured while downloading this track. Please, tell @n1ppers about this error.")
            return

def download_playlist(message):
    if not isLinkValid(message.text):
        bot.send_message(message.from_user.id, "Oops, looks like, that's not a SoundCloud link.")
        return
    
    playlist = api.resolve(message.text)
    assert type(playlist) is Playlist
    for track in playlist.tracks:
        name = f'./{track.artist} - {track.title}.mp3'
        filename = re.sub('[\|/|:|*|?|"|<|>\|]', '', name)
        with open(filename, 'wb+') as fp:
            try:
                track.write_mp3_to(fp)
                audio = open(filename, 'rb')
                bot.send_audio(message.from_user.id, audio)
                os.remove(filename)
            except (FileNotFoundError):
                bot.send_message(message.from_user.id, "An error has occured while downloading this track. Please, tell @n1ppers about this error.")
                return

bot.polling(none_stop=True, interval=0)