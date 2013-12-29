#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import re
url = u'############################'
f = codecs.open("pages/0.html",'r','utf-8')
html = f.read()
#print html
keywords_pattern = re.compile(r'<meta name="keywords".*?/>')
m = keywords_pattern.findall(html)
keywords = m[0]
keywords = keywords.replace('<meta name="keywords" content="','')
keywords = keywords.replace('" />','')
#print keywords

description_pattern = re.compile(r'<meta name="description".*?/>')
m = description_pattern.findall(html)
description = m[0]
description = description.replace('<meta name="description" content="','')
description = description.replace('" />','')
#print description


content_pattern = re.compile(r'<div id="endText".*?<span class="blank20">',re.S)
m = content_pattern.findall(html)
if m:
    content =  m[0]
    p_pattern = re.compile(r'<p.*?</p>',re.S)
    article = ''
    for m in p_pattern.finditer(content):
        p =  m.group()
        p_sub_pattern = re.compile('(<.*?>)|(if.*?;)}',re.S)
        p = re.sub(p_sub_pattern,'',p)
        article += p
    print article

'''
print html + url
full_url_pattern = re.compile(r'href="http://[\S]*?"')
inner_url_pattern = re.compile(r'href="/[\S]*?"')
for m in full_url_pattern.finditer(html):
    print m.group()
for m in inner_url_pattern.finditer(html):
    print m.group()

test = []
test1 = {'tt':1}
#test.append('tt')
if 'tt' not in test:
    if not test['tt']:
        test.append('tt')
print test
'''