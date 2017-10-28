# coding: utf-8
import os
import requests
from html.parser import HTMLParser
from datetime import datetime

URL = "https://p.eagate.573.jp/game/gfdm/gitadora_matixx/p/eam/playdata/rival.html"
COOKIES = {
    'M573SSID': os.environ['SSID'],
}
WEBHOOK_URL = "https://discordapp.com/api/webhooks/{}".format(os.environ['DISCORD_ID_TOKEN'])

NAME_CLS = 'rival_name'
SKILL_CLS = 'rival_skill'


class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_skill_tag = False
        self.skills = []

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and (NAME_CLS in attrs['class'] or SKILL_CLS in attrs['class']):
            self.in_skill_tag = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_skill_tag = False

    def handle_data(self, data):
        if self.in_skill_tag:
            str = data.strip()
            if len(str) == 0:
                return

            self.skills.append(str)


def handler(event, content):
    skills = {}
    for type in ['gf', 'dm']:
        r = requests.get("{}?gtype={}".format(URL, type), cookies=COOKIES)
        r.encoding = r.apparent_encoding

        parser = Parser()
        parser.feed(r.text)
        parser.close()

        s = parser.skills
        skills[type] = dict(zip(s[0::2], map(float, s[1::2])))

    names = {k for s in skills.values() for k in s.keys()}
    strs = [datetime.now().strftime("%Y/%m/%d")]
    for n in names:
        gf = skills['gf'][n]
        dm = skills['dm'][n]
        str = "**{}:** {:04.2f} (GF = {:04.2f}, DM = {:04.2f})".format(n, gf+dm, gf, dm)
        strs.append(str)

    body = {"content": "\n".join(strs)}
    requests.post(WEBHOOK_URL, body)
