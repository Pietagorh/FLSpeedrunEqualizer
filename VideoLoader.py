import os.path as path
import cv2
from pytube import YouTube
from re import match
import requests


class VideoLoader:
    def __init__(self, link: str) -> None:
        self.link = link
        self.download()
        self.raw_data = cv2.VideoCapture(self.link)
        self.framerate = self.raw_data.get(cv2.CAP_PROP_FPS)
        self.cache = []

    def download(self) -> None:
        if match("http(s)?://(www\.)?speedrun.com/fantasy_life/runs/[a-z0-9]{8}", self.link):
            res = requests.get(self.link).text  # todo probably should clean that one day but for now it works
            res = res[res.index("<iframe class=\"block aspect-video w-full border-0\" src=\"") + 56:]
            res = res[:res.index("?")].replace("embed/", "watch?v=")
            self.link = res

        if match("http(s)?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[0-9A-Za-z_-]{11}", self.link):
            yt = YouTube(self.link)
            clean_title = "".join(filter(lambda char: match("[A-Za-z0-9_-]", char), yt.title)) + ".mp4"
            self.link = f"inputs/{clean_title}"
            if not path.exists(self.link) or input("Seems like this video is already on your computer. Would you still like to download it again? (Y/N)\n\t").upper() == "Y":
                yt.streams.filter(resolution="360p", fps=30).first().download(path.dirname(path.realpath(__file__)) + "\\inputs", clean_title, skip_existing=False)

    def __iter__(self):
        for frame in self.cache:
            yield frame

        i = 0
        exists = True
        while exists:
            i += 1

            exists, frame = self.raw_data.read()
            if exists:
                self.cache.append(frame)
                yield frame

    def __len__(self) -> int:
        return int(self.raw_data.get(cv2.CAP_PROP_FRAME_COUNT))
