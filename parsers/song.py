#!/usr/bin/python

import sys
import hashlib
from lxml import etree
from collections import OrderedDict
from song_parser import Parser


class Song(Parser):
    def __init__(self, fn):
        super(Song, self).__init__(fn)

        tc = self.tree.xpath(
            "Attributes[@x:id='Root']/Attributes[@x:id='timeContext']",
            namespaces=self.ns)[0]

        self.tempo_map = tc.xpath("TempoMap")[0]
        self.time_sig_map = tc.xpath("TimeSignatureMap")[0]
        self.time_zone_map = tc.xpath("TimeZoneMap")[0]

        t = self.tree.xpath("Attributes[@x:id='Root']/List[@x:id='Tracks']",
                            namespaces=self.ns)[0]

        self.marker_track = t.xpath("MarkerTrack")[0]
        self.arranger_track = t.xpath("ArrangerTrack")[0]

        self.tracks = OrderedDict()  # maps trackID to XML MediaTrack
        self.track_names = OrderedDict()  # maps track names to trackID

        for c in t.xpath("MediaTrack | AutomationTrack | FolderTrack"):
            if c.tag == "MediaTrack" and c.get("trackID") is None:
                h = self.fix_uid(hashlib.md5(etree.tostring(c)).hexdigest())
                c.set("trackID", h)
            self.tracks[c.get("trackID")] = c
            self.track_names[c.get("name")] = c.get("trackID")

    def get_track_type(self, trackID):
        t = self.tracks[trackID]
        if t.tag == "MediaTrack":
            return t.get("mediaType")
        elif t.tag == "AutomationTrack":
            return "Automation"
        elif t.tag == "FolderTrack":
            return "Folder"
        else:
            return None

    def get_track_name(self, trackID):
        return self.tracks[trackID].get("name")

    def get_folder(self, trackID):
        return self.tracks[trackID].get("parentFolder")

    def get_channel_id(self, trackID):
        c = self.tracks[trackID].xpath(
            "UID[@x:id='channelID']", namespaces=self.ns)
        return c[0].get("uid") if len(c) else None

    def get_clip_ids(self, trackID):
        c = self.tracks[trackID].xpath(
            "*/MusicPart | */AudioEvent | */*/*/MusicPart | */*/*/AudioEvent")
        return [mp.get("clipID") for mp in c]

    def get_clip_effect_ids(self, trackID):
        c = self.tracks[trackID].xpath(
            "*/AudioEvent/Attributes[@x:id='effects'] | " +
            "*/*/*/AudioEvent/Attributes[@x:id='effects']", namespaces=self.ns)
        return [ce.get("clipID") for ce in c]

    def get_automation(self, trackID):
        a = self.tracks[trackID].xpath(
            "Attributes[@x:id='AutomationRegionList']/AutomationRegion/Url",
            namespaces=self.ns)
        return [b.get("url").split("media://")[1] for b in a]

    def set_tempo_map(self, tm):
        self.swap(self.tempo_map, tm)
        self.tempo_map = tm

    def set_time_sig_map(self, tsm):
        self.swap(self.time_sig_map, tsm)
        self.time_sig_map = tsm

    def set_time_zone_map(self, tzm):
        self.swap(self.time_zone_map, tzm)
        self.time_zone_map = tzm

    def set_marker_track(self, mt):
        self.swap(self.marker_track, mt)
        self.marker_track = mt

    def set_arranger_track(self, at):
        self.swap(self.arranger_track, at)
        self.arranger_track = at

    def add_track(self, track):
        self.tree.xpath(
            "Attributes[@x:id='Root']/List[@x:id='Tracks']",
            namespaces=self.ns)[0].append(track)
        self.tracks[track.get("trackID")] = track
        self.track_names[track.get("name")] = track.get("trackID")


if __name__ == "__main__":
    s = Song(sys.argv[1])
    name = s.track_names.keys()[1]
    print name
    tid = s.track_names[name]
    print s.get_channel_id(tid)
    print s.get_clip_ids(tid)
