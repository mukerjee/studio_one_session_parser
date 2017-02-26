#!/usr/bin/python

import sys
import copy
from lxml import etree
from song_parser import Parser


class MixerConsole(Parser):
    def __init__(self, fn):
        super(MixerConsole, self).__init__(fn)

        self.channel_settings = {}  # maps (correct) UIDs to XML Section
        self.channel_banks = {}  # maps bank id to XML ChannelShowHidPresets
        self.channels_in_bank = {}  # maps UIDs to XML UID
        self.max = 0

        for c in self.tree.xpath(
                "Attributes[@x:id='channelSettings']/*", namespaces=self.ns):
            self.max = max(self.max, int(c[0].get("order")))
            self.channel_settings[self.fix_uid(c.get("path"))] = c

        for c in self.tree.xpath(
                "Attributes[@x:id='channelBanks']/*", namespaces=self.ns):
            self.channel_banks[c.get("{x}id")] = c
            for t in c.xpath("List[@x:id='visible']/UID", namespaces=self.ns):
                self.channels_in_bank[t.get("uid")] = t
        
    def get_visible_in_bank(self, bank):
        return [v.get("uid") for v in self.channel_banks[bank].xpath(
            "List[@x:id='visible']/UID", namespaces=self.ns)]

    def add_channel_setting(self, channel_setting):
        self.tree.xpath(
            "Attributes[@x:id='channelSettings']",
            namespaces=self.ns)[0].append(channel_setting)
        a = channel_setting.xpath("Attributes")[0]
        a.set("order", str(int(a.get("order")) + self.max))
        uid = self.fix_uid(channel_setting.get("path"))
        self.channel_settings[uid] = channel_setting

    def add_channel_to_banks(self, channel):
        for bank in self.channel_banks.values():
            ch = copy.deepcopy(channel)
            v = bank.xpath("List[@x:id='visible']", namespaces=self.ns)
            if not len(v):
                v = etree.SubElement(bank, "List")
                v.set("{x}id", "visible")
                v = [v]
            v[0].append(ch)
            
if __name__ == "__main__":
    mc = MixerConsole(sys.argv[1])
    for c in mc.get_visible_in_bank("ScreenBank"):
        print c in mc.channel_settings
