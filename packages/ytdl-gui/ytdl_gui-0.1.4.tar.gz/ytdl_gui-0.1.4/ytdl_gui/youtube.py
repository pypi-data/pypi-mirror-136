import re
import threading
from yt_dlp import YoutubeDL
import yt_dlp

class YTDL_Controller():
    def __init__(self, window):
        self.ydl_opts = {
            'logger': self.Logger(),
            'nocheckcertificate': True,
        }
        self.window = window

    def hook(self, data):
        self.window.emit('hook', data)

    class Logger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    def download(self, url: str, formats: str, savepath: str):
        try:
            with YoutubeDL({**self.ydl_opts, 'progress_hooks': [self.hook], 'format': formats, 'outtmpl': f'{savepath}/%(title)s.%(ext)s'}) as ydl:
                ydl.download([url])
        except:
            with YoutubeDL({**self.ydl_opts, 'progress_hooks': [self.hook], 'format': formats, 'outtmpl': f'{savepath}/%(id)s.%(ext)s'}) as ydl:
                ydl.download([url])

    def download_threaded(self, url: str, formats: str = 'bestvideo+bestaudio/best', savepath: str = '.'):
        thread = threading.Thread(
            target=self.download, args=(url, formats, savepath))
        thread.start()


def validate_link(url: str):
    return re.match(r"^((?:https?:)?\/\/)((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$", url)


def convert_link(url: str):
    id: str = re.search(r"(?:\?v=|v\/|embed\/|youtu\.be\/)([\w\-]+)", url).group(1)
    return id
