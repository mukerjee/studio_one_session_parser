#!/usr/bin/python

import sys
from lxml import etree
from song_parser import Parser


class MediaPool(Parser):
    def __init__(self, fn):
        super(MediaPool, self).__init__(fn)

        self.clips = {}  # maps mediaID to XML
        self.packages = []  # list of XML package Association
        self.doc_path = None  # XML documentPath

        for c in self.tree.xpath(
                "Attributes/MediaFolder[@name='Music']/MusicClip | " +
                "Attributes/MediaFolder[@name='Audio']/AudioClip | " +
                "Attributes/MediaFolder[@name='Sound']/ExternalClip | " +
                "Attributes/MediaFolder[@name='AudioEffects']/*"):
            self.clips[c.get("mediaID")] = c

        for p in self.tree.xpath(
                "Attributes[@x:id='packageInfos']/Association",
                namespaces=self.ns):
            self.packages.append(p)

        self.doc_path = self.tree.xpath(
            "Attributes[@x:id='documentPath']", namespaces=self.ns)[0]

    def get_file(self, mediaID):
        return self.clips[mediaID].xpath("Url")[0].get("url").split("//")[1]

    def get_clip_effect_files(self, mediaID):
        cs = self.clips[mediaID].xpath("List/AudioEffectClipItem/Url")
        return [c.get("url").split("media://")[1] for c in cs]

    def get_doc_path(self):
        return self.doc_path.get("url").split("//")[1]

    def add_clip(self, clip):
        d = {"MusicClip": "Music", "AudioClip": "Audio",
             "ExternalClip": "Sound", 'AudioEffectClip': 'AudioEffects'}
        name = d[clip.tag]
        mf = self.tree.xpath("Attributes/MediaFolder[@name='%s']" % name)
        if not len(mf):
            mf = etree.fromstring('<MediaFolder name="%s"/>' % name)
            self.tree.xpath("Attributes[@x:id='rootFolder']",
                            namespaces=self.ns)[0].append(mf)
            mf = [mf]
        mf[0].append(clip)
        self.clips[clip.get("mediaID")] = clip

    def add_package(self, package):
        self.packages[0].getparent().append(package)
        self.packages.append(package)

    def set_doc_path(self, doc_path):
        self.swap(self.doc_path, doc_path)
        self.doc_path = doc_path

if __name__ == "__main__":
    mp = MediaPool(sys.argv[1])
    print mp.get_file(mp.clips.keys()[0])
    print mp.get_doc_path()
