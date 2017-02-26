#!/usr/bin/python

import sys
from song_parser import Parser


class AudioSynthFolder(Parser):
    def __init__(self, fn):
        super(AudioSynthFolder, self).__init__(fn)

        self.synths = {}  # maps synth deviceData UID to XML Synth Attributes

        for synth in self.tree.xpath("Attributes[@name]"):
            a = synth.xpath(
                "Attributes[@x:id='deviceData']/UID", namespaces=self.ns)[0]
            self.synths[a.get("uid")] = synth

    def get_name(self, uid):
        return self.synths[uid].get("name")

    def get_synth_name(self, uid):
        a = self.synths[uid].xpath(
            "Attributes[@x:id='deviceData']", namespaces=self.ns)[0]
        return a.get("name")

    def get_synth_preset(self, uid):
        a = self.synths[uid].xpath(
            "String[@x:id='presetPath']", namespaces=self.ns)[0]
        return "/" + a.get("text")

    def add_synth(self, synth):
        self.tree.append(synth)
        a = synth.xpath(
            "Attributes[@x:id='deviceData']/UID", namespaces=self.ns)[0]
        self.synths[a.get("uid")] = synth

if __name__ == "__main__":
    asf = AudioSynthFolder(sys.argv[1])
    print asf.synths
    tid = asf.synths.keys()[0]
    print asf.get_synth_name(tid)
    print asf.get_name(tid)
    print asf.get_synth_preset(tid)
