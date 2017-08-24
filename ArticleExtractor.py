# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 16:18:49 2017

@author: datkin10
"""

from newspaper import Article
import re
import threading
import os
import shutil

class ArticleExtractor:
    
    def __init__(self):
        self.updateThread = threading.Thread()
    
    
    def pullArticlesFromSite(self,link,p):
        page = Article(link)
        page.download()
        html = page.html.split()
        urls = []
        countLinks = 0
        nextLink = False
        for block in html:
            if re.search(p,block):
                nextLink = True
        
            if nextLink:
                pLink = re.compile('href')
                if re.search(pLink,block):
                    block = block.replace("href=\"",'')
                    block = block.replace("\"", '')
                    block = block.replace(">","")
                    block,sep,rem = block.partition(".html")
                    if sep:
                        block += sep
                    p2 = re.compile("http")
                    if re.search(p2,block):
                        if block not in urls:
                            urls.append(block)
                            countLinks += 1
                    else:
                        if link+block not in urls:
                            urls.append(link+block)
                            countLinks += 1
            
            
            if countLinks == 3:
                break
        
        articles = [] 
        for url in urls:
            try:
                a= Article(url)
                a.download()
                a.parse()
                title = a.title
                p1 = re.compile(r'[^A-Za-z0-9áéíóú ]')
                while(re.search(p1,title)):
                    title = re.sub(p1, '', title)
                thisArticle = [title,a.text,url]
                articles.append(thisArticle)
            except Exception as e:
                pass
        return articles
    
    def updateArticles(self):
        with open('files/Daily-Articles/ArticleSites.txt', 'r') as f:
            for line in f:
                line = line.split()
                try:
                    articles = self.pullArticlesFromSite(line[1],line[2])
                    try:
                        shutil.rmtree("files/Daily-Articles/" + line[0])
                    except:
                        pass
                    os.mkdir("files/Daily-Articles/" + line[0])
                    for article in articles:
                        if len(article[1].split()) >250:
                            f = open("files/Daily-Articles/" + line[0] + '/' + article[0] + '.txt', 'w')
                            try:
                                f.write(article[1])
                            except:
                                for word in article[1].split():
                                    try:
                                        f.write(word + ' ')
                                    except:
                                        pass
                except: 
                    pass