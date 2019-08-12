import telebot
import os
import re
import os.path

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
        return str(f.read())

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

    #print(getValue("token"))
    #print(getValue("proxy_type"))
    #print(getValue("proxy_ip"))
    #print(getValue("proxy_port"))

TOKEN = getToken() #getValue("token")
print(TOKEN)
#PROXY_TYPE = getValue("proxy_type")
#PROXY_IP = getValue("proxy_ip")
#PROXY_PORT = getValue("proxy_port")

#if not PROXY_IP == "" and not PROXY_IP == "127.0.0.1":
    #apihelper.proxy = {PROXY_TYPE:PROXY_IP}

bot = telebot.TeleBot(str(TOKEN))
print(bot.get_me())
api = SoundcloudAPI()

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    print(message.from_user.username, ": ", message.text)
    bot.send_message(message.from_user.id, 
        '''
Commands: \n/github - Get a link to repository with my source code on GitHub \n/support - Contact my owner
/track - Download single track by link \n/playlist - Download all tracks from playlist by link
        ''')

@bot.message_handler(commands=['github'])
def command_github(message):
    bot.send_message(message.from_user.id, "GitHub \nhttps://github.com/n1ppers/soundcloud-bot")

@bot.message_handler(commands=['support'])
def command_support(message):
    bot.send_message(message.from_user.id, "Telegram: @n1ppers")

@bot.message_handler(commands=['track'])
def command_track(message):
    msg = bot.send_message(message.from_user.id, "Please, send me a link to track that you want to download.")
    bot.register_next_step_handler(msg, download_track)

@bot.message_handler(commands=['playlist'])
def command_playlist(message):
    msg = bot.send_message(message.from_user.id, "Please, send me a link to playlist that you want to download.")
    bot.register_next_step_handler(msg, download_playlist)

def download_track(message):
    if message.text.startswith("https://soundcloud.com/"):
        track = api.resolve(message.text)
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
    else:
        bot.send_message(message.from_user.id, "Oops, looks like, that's not a SoundCloud link.")

def download_playlist(message):
    if message.text.startswith("https://soundcloud.com/"):
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
    else:
        bot.send_message(message.from_user.id, "Oops, looks like, that's not a SoundCloud link.")

bot.polling(none_stop=True, interval=0)