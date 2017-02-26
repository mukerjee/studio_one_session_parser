#!/usr/bin/python

import sys
from lxml import etree
from song_parser import Parser


class AudioMixer(Parser):
    def __init__(self, fn):
        super(AudioMixer, self).__init__(fn)

        self.channels = {}  # maps channel uid to XML

        for child in self.tree.xpath(
                "Attributes[@x:id='channels']/ChannelGroup",
                namespaces=self.ns):
            self.channels.update(self.parse_channels(child))

    def parse_channels(self, root):
        return {child.xpath("UID")[0].get("uid"): child for child in root}

    def get_inserts(self, channelID):
        i = self.channels[channelID].xpath(
            "Attributes[@x:id='Inserts']/Attributes/String[@x:id='presetPath']",
            namespaces=self.ns)
        return ["/" + a.get("text") for a in i]

    def get_name(self, channelID):
        return self.channels[channelID].get("label")

    def get_type(self, channelID):
        return self.channels[channelID].tag \
            if channelID in self.channels else 'None'

    def get_destination(self, channelID):
        d = self.channels[channelID].xpath(
            "Connection[@x:id='destination']", namespaces=self.ns)
        return d[0].get("objectID").split("/")[0] if len(d) else None

    def get_vca(self, channelID):
        vca = self.channels[channelID].xpath(
            "Attributes[@x:id='VCATarget']/Connection[@x:id='vcaTarget']",
            namespaces=self.ns)
        return vca[0].get("objectID").split("/")[0] if len(vca) else None

    def get_sends(self, channelID):
        sends = self.channels[channelID].xpath(
            "Attributes[@x:id='Sends']/*/Connection[@x:id='destination']",
            namespaces=self.ns)
        return [s.get("objectID").split("/")[0] for s in sends]

    def add_channel(self, channel):
        cgname = channel.tag.split("Channel")[0]
        cg = self.tree.xpath("*/ChannelGroup[@name='%s']" % cgname)
        if not len(cg):
            cg = etree.fromstring('<ChannelGroup name="%s" flags="1"/>'
                                  % cgname)
            self.tree.xpath("Attributes[@name='Channels']")[0].append(cg)
            cg = [cg]
        cg[0].append(channel)
        uid = channel.xpath("UID")[0].get("uid")
        self.channels[uid] = channel

if __name__ == "__main__":
    am = AudioMixer(sys.argv[1])
    uid = am.channels.keys()[0]
    print uid
    print am.get_name(uid)
    print am.get_destination(uid)
    print am.get_inserts(uid)
