#!/usr/bin/python

import os
import zipfile
import shutil
import tempfile

from parsers.audio_mixer import AudioMixer
from parsers.audio_synth_folder import AudioSynthFolder
from parsers.media_pool import MediaPool
from parsers.mixer_console import MixerConsole
from parsers.music_track_device import MusicTrackDevice
from parsers.song import Song

DONT_OVERWRITE = True
USE_TEMP = True


class SongModel(object):
    def __init__(self, fn):
        self.is_clean = True
        self.fn = fn
        self.prefix = None
        self.extract()
        if DONT_OVERWRITE:
            self.fn = os.path.splitext(self.fn)[0] + '-new.song'
        self.song = Song(self.prefix + '/Song/song.xml')
        self.musictrackdevice = MusicTrackDevice(
            self.prefix + '/Devices/musictrackdevice.xml')
        self.audiosynthfolder = AudioSynthFolder(
            self.prefix + '/Devices/audiosynthfolder.xml')
        self.mediapool = MediaPool(self.prefix + '/Song/mediapool.xml')
        self.mixerconsole = MixerConsole(
            self.prefix + '/Devices/mixerconsole.xml')
        self.audiomixer = AudioMixer(self.prefix + '/Devices/audiomixer.xml')

    def extract(self):
        f = zipfile.ZipFile(self.fn, 'r')
        if USE_TEMP:
            self.prefix = tempfile.mkdtemp()
        else:
            self.prefix = os.path.splitext(self.fn)[0]
        f.extractall(self.prefix)
        f.close()
        self.is_clean = False

    def compress(self):
        f = zipfile.ZipFile(self.fn, 'w', zipfile.ZIP_DEFLATED)
        old_dir = os.getcwd()
        os.chdir(self.prefix)
        for root, dirs, files in os.walk('./'):
            for file in files:
                f.write(os.path.join(root, file))
        f.close()
        os.chdir(old_dir)

    def delete_temp(self):
        if not self.is_clean:
            shutil.rmtree(self.prefix)
        self.is_clean = True

    def clean(self):
        if not self.is_clean:
            self.delete_temp()
            self.is_clean = True

    def write(self):
        self.song.write()
        self.musictrackdevice.write()
        self.audiosynthfolder.write()
        self.mediapool.write()
        self.mixerconsole.write()
        self.audiomixer.write()
        self.compress()
        self.delete_temp()

