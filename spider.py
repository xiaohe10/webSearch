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
    def __init__(self,unvisited_url_stack_file,visited_url_table_file,visited_url_table_file_reverse,page_dir,time_interval = 30, timeout=20,threads = 8, max_pages = 10000):
        self.timeout = timeout
        self.unvisited_url_stack_file = unvisited_url_stack_file
        self.visited_url_table_file = visited_url_table_file
        self.visited_url_table_file_reverse = visited_url_table_file_reverse
        self.max_pages = max_pages
        self.page_dir = page_dir
        self.time_interval = time_interval
        self.threads = threads


    def init_from_file(self):
        try:
            f = file(self.unvisited_url_stack_file)
            self.unvisited_url_stack = json.loads(f.read())
            f.close()
        except Exception:
            print 'unvisited_url_stack_file is invalid'
            return False
        try:
            f = file(self.visited_url_table_file)
            j = json.loads(f.read())
            self.count = j["count"]
            self.visited_url_table = j["page_table"]
            f.close()
            f = file(self.visited_url_table_file_reverse)
            j = json.loads(f.read())
            self.count = j["count"]
            self.visited_url_table_reverse = j["page_table"]
            f.close()
        except Exception:
            print 'visited_url_stack_file is invalid'
            return False

    def write_into_file(self):
        try:
            f = open(self.unvisited_url_stack_file,'w')
            json.dump(self.unvisited_url_stack,f)
            f.close()
        except Exception:
            print Exception
            return False
        try:
            t = {"count":self.count, "page_table":self.visited_url_table}
            f = open(self.visited_url_table_file,'w')
            json.dump(t,f)
            f.close()
            t = {"count":self.count, "page_table":self.visited_url_table_reverse}
            f = open(self.visited_url_table_file_reverse,'w')
            json.dump(t,f)
            f.close()

            return True
        except Exception:
            print Exception
            return False
    def parse_content(self,file,html,url):
        print "######start parse########"
        url = url.encode('utf-8')
        p_pattern = re.compile(r'<p.*?</p>',re.S)
        article = ''
        for m in p_pattern.finditer(html):
            p =  m.group()
            p_sub_pattern = re.compile('&nbsp;',re.S)
            p = re.sub(p_sub_pattern,' ',p)
            p_sub_pattern = re.compile('(<style.*?</style>)|(<span.*?</span>)|(<a.*?</a>)|(<h3 class="hidden">.*?</h3>)',re.S)
            p = re.sub(p_sub_pattern,'',p)
            p_sub_pattern = re.compile('(<.*?>)|(if.*?;)}|\n',re.S)
            p = re.sub(p_sub_pattern,'',p)
            article += p
        #print article
        title_pattern = re.compile(r'<title>.*?</title>',re.S)
        m = title_pattern.findall(html)
        if m:
            title = m[0]
            title = title.replace('<title>','')
            title = title.replace('</title>','')
        #print title

        keywords_pattern = re.compile(r'<meta name="keywords".*?/>')
        m = keywords_pattern.findall(html)
        if m:
            keywords = m[0]
            keywords = keywords.replace('<meta name="keywords" content="','')
            keywords = keywords.replace('" />','')
            #print keywords

        description_pattern = re.compile(r'<meta name="description".*?/>')
        m = description_pattern.findall(html)
        if m:
            description = m[0]
            description = description.replace('<meta name="description" content="','')
            description = description.replace('" />','')
        #print description
        f = open(file,'w')
        c = url+'\n keywords:\n'+keywords+'\ntitle:\n'+title+'\n description: \n'+description+'\n article: \n'+article
        f.write(c.decode("gbk").encode("utf-8"))
        f.close()
        print "########end parse #########"
        return True
    def single_crawl(self):
        while(True):
            try:
                url = self.unvisited_url_stack.pop()
                #self.unvisited_url_stack.remove(url)
                try:
                    response = urllib2.urlopen(url,timeout = self.timeout)
                    html = response.read()
                    self.visited_url_table[url] = self.count.__str__()+'.html'
                    self.parse_url(html,url)
                    if self.parse_content(self.page_dir+self.count.__str__()+'.html',html,url):
                        self.visited_url_table_reverse[self.count.__str__()+'.html'] = url
                        self.count = self.count + 1
                        print self.count
                    if(self.count > 1000):
                        return 'enough pages'
                except urllib2.URLError, e:
                    print e.reason
                except HTTPError, e:
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
                except Exception:
                    print "some thing is wrong when parsing"
            except Exception:
                return 'None url stack'
    def parse_url(self,html,baseurl):
        base_url_pattern = re.compile(r'http://[^\s/]*')
        m = base_url_pattern.match(baseurl)
        base =  m.group()
        full_url_pattern = re.compile(r'href="'+base+'/[0-9]+/[\S]*?.html"')
        #inner_url_pattern = re.compile(r'href="/[\S]*?"')
        for m in full_url_pattern.finditer(html):
            url =  m.group()
            url = url.replace('href="','')
            url = url.replace('"','')
            #url = base + url
            if url not in self.unvisited_url_stack:
                if not self.visited_url_table.has_key(url):
                    self.unvisited_url_stack.append(url)
                    print url
    def crawl(self):
        self.init_from_file
        all_threads = []
        thread_count = 0
        while(thread_count < self.threads):
            try:
                th = threading.Thread(target=self.single_crawl, args=())
                all_threads.append(th)
                th.start()
            finally:
                thread_count = thread_count + 1
        for th in all_threads:
            try:
                th.join()
            except Exception:
                print Exception
        self.write_into_file()


if __name__ == '__main__':
    spider = Spider(unvisited_url_stack_file='unvisited_url_stack_file',visited_url_table_file='visited_url_table_file',visited_url_table_file_reverse ='visited_url_table_file_reverse',page_dir='pages/')
    spider.init_from_file()
    spider.single_crawl()
    spider.write_into_file()