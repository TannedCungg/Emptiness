import pygame
import threading
import pygame._sdl2.audio as sdl2_audio
import logging
import log

def get_devices(capture_devices: bool = False):
    init_by_me = not pygame.mixer.get_init()
    if init_by_me:
        pygame.mixer.init()
    devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
    if init_by_me:
        pygame.mixer.quit()
    return devices

class MP3Player:
    def __init__(self):
        devices = get_devices()
        if not devices:
            raise RuntimeError("No device!")
        else:
            logging.info(f"[INFO]: Availble devices are: {devices}")
            device = devices[-1]
        pygame.init()
        pygame.mixer.init(devicename='pulse')
        pygame.font.init()
        self.paused = False

    def play(self, file_path):
        try:
            logging.info(f"[INFO]: Playing: {file_path}")
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(-1)
            self.paused = False
        except Exception as e:
            logging.info(f"[ERR]: {e}")

    def pause(self):
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        pygame.mixer.music.stop()

    def quit(self):
        pygame.mixer.quit()
        pygame.quit()

if __name__ == "__main__":
    player = MP3Player()

    while True:
        logging.info("MP3 Player Menu:")
        logging.info("1. Play")
        logging.info("2. Pause/Unpause")
        logging.info("3. Stop")
        logging.info("4. Quit")
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            file_path = input("Enter the path to the MP3 file: ")
            player.play(file_path)
            logging.info(player.paused)
        elif choice == '2':
            player.pause()
        elif choice == '3':
            player.stop()
        elif choice == '4':
            player.quit()
            break