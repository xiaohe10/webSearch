#!/usr/bin/env python
#encoding: utf-8
import sys   #引用sys模块进来，并不是进行sys的第一次加载
reload(sys)  #重新加载sys
sys.setdefaultencoding('utf8')  ##调用setdefaultencoding函数

# a web spider to crawl web pages
# author : xiaoh16@gmail.com

# a spider can crawl pages  in BFS Strategy
#  after getting a page, the spider analyze the page to decide which is next to crawl
# the spider can open multi threads to GET page from web servers

import json
import threading
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
import re

class Spider():
    def __init__(self,page_dir,time_interval = 30, timeout=20,threads = 10, max_pages = 10000):
        self.timeout = timeout
        self.max_pages = max_pages
        self.page_dir = page_dir
        self.time_interval = time_interval
        self.threads = threads
        self.unvisited_url_stack = []
        self.unvisited_url_stack.append(["http://war.163.com/"])
        self.unvisited_url_stack.append(["http://money.163.com/"])
        self.unvisited_url_stack.append(["http://sports.163.com/"])
        self.unvisited_url_stack.append(["http://ent.163.com/"])
        self.unvisited_url_stack.append(["http://lady.163.com/"])
        self.unvisited_url_stack.append(["http://tech.163.com/"])
        self.unvisited_url_stack.append(["http://auto.163.com/"])
        self.unvisited_url_stack.append(["http://travel.163.com/"])
        self.unvisited_url_stack.append(["http://edu.163.com/"])
        self.unvisited_url_stack.append(["http://game.163.com/"])

        self.visited_url_table = {}

        self.count = [0,0,0,0,0,0,0,0,0,0]

    def parse_content(self,file,html,url,thread_count):
        url = url.encode('utf-8')
        try:
            title_pattern = re.compile(r'<title>.*?</title>',re.S)
            m = title_pattern.findall(html)
            title = ''
            if m:
                title = m[0]
                title = title.replace('<title>','')
                title = title.replace('</title>','')
        except:
            print "parse title error"

        try:
            keywords_pattern = re.compile(r'<meta name="keywords".*?>')
            m = keywords_pattern.findall(html)
            keywords=''
            if m:
                keywords = m[0]
                keywords = keywords.replace('<meta name="keywords" content="','')
                remove_tail = False
                try:
                    keywords = keywords.replace('" />','')
                    keywords = keywords.replace('">','')
                except:
                    remove_tail = True
        except:
            print "parse keywords error"

        try:
            description_pattern = re.compile(r'<meta name="description".*?>')
            m = description_pattern.findall(html)
            description =''
            if m:
                description = m[0]
                description = description.replace('<meta name="description" content="','')
                remove_tail = False
                try:
                    description = description.replace('" />','')
                    description = description.replace('">','')
                except:
                    remove_tail = True

        except:
            print "parse description error"

        try:
            f = open(file,'w')
            content = url+'\n keywords:\n'+keywords+'\ntitle:\n'+title+'\n description: \n'+description
            f.write(content.decode("gbk").encode("utf-8"))
            f.close()
        except:
            print "file error"
        if title != '':
            self.count[thread_count] = 1 + self.count[thread_count]


    def single_crawl(self,thread_count):
        while(True):
            try:
                url = self.unvisited_url_stack[thread_count].pop()

                try:
                    response = urllib2.urlopen(url,timeout = self.timeout)
                    html = response.read()
                    self.visited_url_table[url] = self.count[thread_count].__str__()+'.html'
                    try:
                        self.parse_url(html,url,thread_count)
                    except:
                        print "parse url error"
                    try:
                        self.parse_content(self.page_dir+thread_count.__str__()+'_'+self.count[thread_count].__str__()+ '.html',html,url,thread_count)
                        print thread_count.__str__()+'_'+(self.count[thread_count]-1).__str__()+ '.html'
                    except:
                        print "parse content error"
                        print url
                    if(self.count[thread_count] > 1000):
                        return 'enough pages'
                except urllib2.URLError, e:
                    print e.reason
                except HTTPError, e:
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
                except Exception:
                    print "unknown error"
            except Exception:
                return 'None url stack'

    def parse_url(self,html,baseurl,thread_count):
        base_url_pattern = re.compile(r'http://[^\s/]*')
        m = base_url_pattern.match(baseurl)
        base =  m.group()
        full_url_pattern = re.compile(r'href="'+base+'/([0-9]+/[\S]*?.html)|(specail/[\S]*/)"')
        #inner_url_pattern = re.compile(r'href="/[\S]*?"')
        for m in full_url_pattern.finditer(html):
            url =  m.group()
            url = url.replace('href="','')
            url = url.replace('"','')
            #url = base + url
            if url not in self.unvisited_url_stack[thread_count]:
                if not self.visited_url_table.has_key(url):
                    self.unvisited_url_stack[thread_count].append(url)

    def crawl(self):
        all_threads = []
        thread_count = 0
        while(thread_count < self.threads):
            try:
                th = threading.Thread(target=self.single_crawl, args=(thread_count,))
                all_threads.append(th)
                th.start()
            finally:
                thread_count = thread_count + 1
        for th in all_threads:
            try:
                th.join()
            except Exception:
                print Exception


if __name__ == '__main__':
    spider = Spider(page_dir='pages/')
    #spider.crawl()
    spider.single_crawl(6)
