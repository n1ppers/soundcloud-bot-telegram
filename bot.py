import telebot
import os
import re

from sclib import SoundcloudAPI, Track, Playlist
from telebot import types

TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot(TOKEN)
api = SoundcloudAPI()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.from_user.id, 
        '''
Commands: \n/github - Get a link to repository with my source code on GitHub \n/support - Contact my owner
/track - Download single track by link \n/playlist - Download all tracks from playlist by link
        ''')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.from_user.username, ": ", message.text)
    if message.text == "/github":
        command_github(message)
    elif message.text == "/support":
        command_support(message)
    elif message.text == "/track":
        command_track(message)
    elif message.text == "/playlist":
        command_playlist(message)
    else:
        bot.send_message(message.from_user.id, "I don't understand you. If you want to get a list of commands - type /help.")

def command_github(message):
    bot.send_message(message.from_user.id, "GitHub \nhttps://github.com/n1ppers/soundcloud-bot")

def command_support(message):
    bot.send_message(message.from_user.id, "Telegram: @n1ppers")

def command_track(message):
    msg = bot.send_message(message.from_user.id, "Please, send me a link to track that you want to download.")
    bot.register_next_step_handler(msg, download_track)

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