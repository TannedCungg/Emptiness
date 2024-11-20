import os
import glob
import time
from datetime import datetime
import uuid

from media_player import MP3Player
from connector import MQTTClient
from database import SimpleDataBase
from config.config import STATE_TOPIC, LIST_TOPIC, QUERY_TOPIC, SETTING_TOPIC, BROKER, PORT, DATABASE
import logging
import log


CLIENT_NAME = str(uuid.uuid4())
MEDIA = "./audio"
SKIP_INTERVAL = 2 # in second
ACTIVE_HOUR = [8*60*60, 10*60*60]

class MediaService:
    def __init__(self):
        self.mqtt_client = MQTTClient(CLIENT_NAME, BROKER, on_message_callback=self.message_handler)
        self.media_player = MP3Player()
        self.list_songs = {}
        self.last_update = time.time()
        self.current_song = None
        self.daily_turned_off = False
        self.active_hour = ACTIVE_HOUR
        self.database = SimpleDataBase(DATABASE)
        self.states = self.database.read()
        self.extract_dict_states(self.states)
        self.cold_start = True

    def extract_dict_states(self, states):
        for key in states.keys():
            if key == "current_song":
                self.current_song = states[key]
            elif key == "active_hour":
                self.active_hour = states[key]
            elif key == "daily_turned_off":
                self.daily_turned_off = states[key]
            else:
                logging.info(f"[WARM]: Invalid key: {key}, skipping...")
    
    def do_update_states(self):
        states = {"current_song": self.current_song,
                  "active_hour": self.active_hour,
                  "daily_turned_off": self.daily_turned_off}
        if states != self.states:
            self.states = states
            self.database.write(self.states)
            logging.info(f"[INFO]: Update new states: {states} at: {datetime.now()}")

    def generate_list_song_string(self):
        songs = glob.glob(os.path.join(MEDIA, "*.mp3"))
        for song in songs:
            self.list_songs[song.split("/")[-1].replace(",", ".")] = song
            
        list_song_string = ""
        for song in self.list_songs.keys():
            list_song_string += song + ", "
        list_song_string = list_song_string[:-2]
        return list_song_string

    def start(self):
        self.mqtt_client.topics = [STATE_TOPIC, QUERY_TOPIC, SETTING_TOPIC]
        self.mqtt_client.connect()
        songs = glob.glob(os.path.join(MEDIA, "*.mp3"))
        for song in songs:
            self.list_songs[song.split("/")[-1].replace(",", ".")] = song
        self.mqtt_client.publish(LIST_TOPIC, self.generate_list_song_string())
        self.last_update = time.time()
    
    def finish(self):
        self.media_player.quit()

    @staticmethod
    def elapsed_second():
        current_datetime = datetime.now()
        beginning_of_day = datetime(current_datetime.year, current_datetime.month, current_datetime.day)
        elapsed_time_seconds = (current_datetime - beginning_of_day).total_seconds()
        return elapsed_time_seconds

    def cron_job(self):
        while True:
            # now = datetime.now()
            now = MediaService.elapsed_second()
            logging.info(f"[DEBUG]: now: {now} - self.media_player.paused: {self.media_player.paused} - self.current_song: {self.current_song}")
            self.do_update_states()
            if self.active_hour[0] <= now < self.active_hour[1]:
                if self.current_song is None:
                    self.current_song = 0
                if self.media_player.paused:
                    self.daily_turned_off = False
                    self.media_player.play(list(self.list_songs.values())[self.current_song])
            else:
                if not self.daily_turned_off:
                    self.daily_turned_off = True
                    self.media_player.pause() if not self.media_player.paused else 0
            time.sleep(60)
    
    def message_handler(self, topic, message):
        try:
            if topic == STATE_TOPIC: # previous, play, pause, next, song_{song_name}
                if message == "play.pause":
                    logging.info(f"[INFO]: Play/pause")
                    if len(self.list_songs)>0:
                        if self.current_song is None:
                            self.current_song = 0
                            self.media_player.play(list(self.list_songs.values())[self.current_song])
                        elif self.cold_start:
                            self.media_player.play(list(self.list_songs.values())[self.current_song])
                            self.cold_start = False
                        else:
                            self.media_player.pause()
                elif message == "previous":
                    logging.info("[INFO]: Revert")
                    self.current_song = self.current_song - 1 if self.current_song - 1 >=0 else len(self.list_songs)
                    self.media_player.play(list(self.list_songs.values())[self.current_song])
                elif message == "next":
                    logging.info("[INFO]: Next")
                    self.current_song = self.current_song + 1 if self.current_song + 1 < len(self.list_songs) else 0 
                    self.media_player.play(list(self.list_songs.values())[self.current_song])
                elif message[:5] == "Song_":
                    if time.time() - self.last_update < SKIP_INTERVAL:
                        return
                    song_name = message.replace("Song_", "")
                    _song = self.list_songs.get(song_name, None)
                    if _song:
                        self.current_song = list(self.list_songs.keys()).index(song_name)
                        logging.info(f"[INFO]: Jumping to song {song_name}")
                        self.media_player.play(_song)
                    else:
                        logging.info(f"[ERROR]: Unable to find the song {song_name} in the list, skipping...")
                else:
                    logging.info(f"[WARM]: Unknown command: {message}")

            elif topic == QUERY_TOPIC:
                if message == "What are the songs?":
                    st = self.generate_list_song_string()
                    logging.info(f"[INFO]: What are the songs?: {st}")
                    self.mqtt_client.publish(LIST_TOPIC, st)
                    self.last_update = time.time()
            elif topic == SETTING_TOPIC:
                attribute = message.split(":")[0]
                setting = message.split(":")[1]
                if attribute == "active hour":
                    # "active hour: [start, end]"
                    setting = setting.replace(" ", "").replace("[", "").replace("]", "")
                    self.active_hour[0] = int(setting.split(",")[0])
                    self.active_hour[1] = int(setting.split(",")[1])
                    logging.info(f"[INFO]: Active hour set to {self.active_hour}")
                else:
                    logging.info(f"[WARN]: Unknown config: {message}, skipping...")
            else:
                logging.info("[WARM]: Strange topic received")
                return
        except Exception as e:
            logging.info(f"[ERR]: {e}, topic: {topic}, message: {message}") 


Yujii_A = MediaService()
logging.info("[INFO]: Starting ...")
Yujii_A.start()
logging.info(f"[INFO]: Media Service started...")
Yujii_A.cron_job()