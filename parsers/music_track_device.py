#!/usr/bin/python

import sys
from lxml import etree
from song_parser import Parser


class MusicTrackDevice(Parser):
    def __init__(self, fn):
        super(MusicTrackDevice, self).__init__(fn)

        self.channels = {}  # maps UID to XML MusicTrackChannel

        for c in self.tree.xpath(
                "Attributes[@name='Channels']/ChannelGroup/*"):
            self.channels[c.xpath("UID")[0].get("uid")] = c

    def get_instrument_out(self, uid):
        c = self.channels[uid].xpath(
            "Connection[@x:id='instrumentOut']", namespaces=self.ns)
        return c[0].get("objectID").split('/')[0] if len(c) else None

    def get_destination(self, uid):
        c = self.channels[uid].xpath(
            "Connection[@x:id='destination']", namespaces=self.ns)
        return c[0].get("objectID").split('/')[0] if len(c) else None

    def add_channel(self, channel):
        cg = self.tree.xpath("Attributes/ChannelGroup[@name='MusicTrack']")
        if not len(cg):
            cg = etree.fromstring(
                "<ChannelGroup name='MusicTrack' flags='1'/>")
            self.tree.xpath("Attributes")[0].append(cg)
            cg = [cg]
        cg[0].append(channel)

        self.channels[channel.xpath("UID")[0].get("uid")] = channel

            
if __name__ == "__main__":
    mtd = MusicTrackDevice(sys.argv[1])
    print mtd.get_instrument_out(mtd.channels.keys()[0])
    print mtd.get_destination(mtd.channels.keys()[0])
