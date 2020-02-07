#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sqlite3
from datetime import datetime

prefix = "typecho_kuuds"
global hexSourcePath
hexSourcePath = "./"


class Content:
    def __init__(self, content):
        self.content = content
        self.tags = []
        self.category = None

    def addTags(self, tag):
        self.tags.append(tag)

    def setCategory(self, category):
        self.category = category

    def convert(self):
        title = self.content[1]
        slug = self.content[2]
        date = datetime.fromtimestamp(self.content[3])
        updated = datetime.fromtimestamp(self.content[4])
        text = self.content[5].replace("<!--markdown-->", "").replace("\r\n", "\n")
        if text[-1:] == "%":
            text = text[:-1]
        filename = "./%s.md" % slug

        print("\n")
        print(u"title = %s" % title)
        print(u"date = %s" % date)
        print(u"updated = %s" % updated)
        print(u"category = %s" % self.category)
        print(u"tags size = %d" % len(self.tags))

        print(u"create %s." % filename)
        f = open(filename, "w+")
        f.write(u"---\n")
        f.write(u"title: %s\n" % title)
        f.write(u"date: %s\n" % date)
        f.write(u"updated: %s\n" % updated)
        if not (self.category is None):
            f.write(u"categories:\n")
            f.write(u"- %s\n" % self.category)
        if not self.tags.count:
            f.write(u"tags:\n")
            for tag in self.tags:
                f.write(u"- %s\n" % tag)
        f.write(u"---\n")

        f.write(text)
        f.close
        print("close %s.\n" % filename)


print("open db.")
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
contents = []
metas = {}
relations = []

print("query contents.")
for row in cursor.execute("SELECT * FROM %scontents where type like 'post'" % prefix):
    content = Content(row)
    contents.append(content)

print("query tags and categories.")
for row in cursor.execute("SELECT * FROM %smetas" % prefix):
    metas[row[0]] = row

print("query relationships.")
for row in cursor.execute("SELECT * FROM %srelationships" % prefix):
    relations.append(row)

print("consist data.")
for content in contents:
    cid = content.content[0]
    it = iter(relations)
    while True:
        relation = next(it, None)
        if relation is None:
            break
        if cid == relation[0]:
            meta = metas[relation[1]]
            metaType = meta[3]
            if metaType == "category":
                content.setCategory(meta[2])
            elif metaType == "tag":
                content.addTags(meta[2])
    content.convert()
