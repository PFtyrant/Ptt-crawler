# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 17:35:49 2018

@author: PFace
"""

import os
import requests
import re
import urllib.parse
from requests_html import HTML
import sys
import time
from multiprocessing import Pool

domain = 'https://www.ptt.cc'



cur_year = 2018
target_year = 2017
index_diff = cur_year - target_year

notarticle = 0
def fetch(url):
    url = url.strip('\n')
    response = requests.get(url,cookies={'over18': '1'})
    return response

def parse_article_entries(doc):
        html = HTML(html=doc)
        post_entries = html.find('div.r-ent')
        return post_entries

def parse_article_meta(entry):
    global notarticle
    if '[公告]' in entry.find('div.title',first=True).text:
        notarticle += 1
        pass
    elif entry.find('div.title > a',first=True) == None:
        pass
    else:
        meta =  {
                'push': entry.find('div.nrec',first=True).text,
                'date': entry.find('div.date',first=True).text,
                'title': entry.find('div.title',first=True).text,
        }
        try:
            meta['author'] = entry.find('div.author',first=True).text
            meta['link'] = entry.find('div.title > a',first=True).attrs['href']
        except AttributeError:
            #notarticle += 1
            return       
        return meta
        
def get_metadata_from(url,count_list):
    out_list = ['/bbs/Beauty/M.1490936972.A.60D.html',
                '/bbs/Beauty/M.1494776135.A.50A.html',
                '/bbs/Beauty/M.1503194519.A.F4C.html',
                '/bbs/Beauty/M.1504936945.A.313.html',
                '/bbs/Beauty/M.1505973115.A.732.html',
                '/bbs/Beauty/M.1507620395.A.27E.html',
                '/bbs/Beauty/M.1510829546.A.D83.html',
                '/bbs/Beauty/M.1512141143.A.D31.html]']
    conti = 0 # stop flag, conti flag
    #count = 0
    def parse_next_link(doc):
        html = HTML(html=doc)
        controls = html.find('.action-bar a.btn.wide')
        link = controls[1].attrs.get('href')
        return urllib.parse.urljoin(domain, link)

    resp = fetch(url)
    post_entries = parse_article_entries(resp.text)
    next_link = parse_next_link(resp.text)
    metadata = []
    popular = []
    ''' ver1: 
    fail point -> In this function, when a page move to next page, 
    must wait response time to find the date in every article, 
    it may occur huge waiting time. Time as gold! we don't have much time!
    
    for entry in post_entries:
        meta = parse_article_meta(entry)
        if meta != None:
                compare = compare_article_metadata_date(domain+ meta['link']) #Problem point here!
                print(compare)
                if count ==0 and compare == 1:
                    break
                elif count == 0 and compare == -1 :
                    conti = 1
                else:
                    if compare == 0:
                        metadata.append(meta)
        count += 1
    print(metadata)
    '''

    # second version of function!
    # In this function, It dosen't wait reponse time that accesseing website to find a target date,
    # the second version use metadata of the main page, it calculates a starting and end point of collecting directly.
    start12 = 0
    start01 = 0
    out_flag = False
    for entry in post_entries[::-1]:
        meta = parse_article_meta(entry)

        if meta != None:
            for out in out_list:
                if meta['link'] == out:
                    out_flag = True
                    break
            if out_flag:
                out_flag = False
                continue
            date = meta['date'].split('/')
            
            if (date[0] == '1') and (start01 == 0):
                start01 = 1
                if count_list[1] == 0:
                    count_list[1] += 1
                if start12 == 1:
                    start12 = 0
                
            if (date[0] == '12') and (start12 == 0):
                start12 = 1
                if start01 == 1:
                    count_list[1] += 1
                    start01 = 0
                    
            if (count_list[1] == index_diff+1):
                metadata.append(meta)
                if meta['push'] == '爆':
                    popular.append(meta)
            if (count_list[1] > index_diff+1) and start12 == 1:
                conti = 1
    metadata.reverse()
    return metadata, next_link, conti , popular

def get_paged_meta(url):
    collected_meta = []
    popular_meta = []
    page = 0
    contin = 0
    count_list = [0,0]
    while contin != 1:
        posts, link , contin, populars = get_metadata_from(url,count_list)
        print(link)
        posts.reverse()
        collected_meta += posts
        popular_meta += populars
        url = urllib.parse.urljoin(domain, link)
        page += 1
        print (page)
        time.sleep(0.1)
    return collected_meta, popular_meta


def get_article_from_file(start_date,end_date,file_name):#2
    save = False
    data = []
    with open(file_name,'r',encoding='utf-8') as f:
        for line in f:
            date = line.split(',')
            # find first mathch start_date article
            if date[0] == start_date: 
                save = True
                
            #date = date[0].split('/')
            compare_date_month = None
            compare_date_day = None
            if(len(date[0])==3):
                string  = date[0]
                compare_date_month = int(string[0])
                compare_date_day = int(string[1] + string[2])
            else:
                string  = date[0]
                compare_date_month = int(string[0]+string[1])
                compare_date_day = int(string[2]+string[3])
            end_date_month = None
            end_date_day = None
            if(len(end_date)==3):
                end_date_month = int(end_date[0])
                end_date_day = int(end_date[1] + end_date[2])
            else:
                end_date_month = int(end_date[0]+end_date[1])
                end_date_day = int(end_date[2]+end_date[3])
                
                
            if save and (end_date_month - compare_date_month) >= 0:
                if (end_date_month - compare_date_month) == 0: #for date that same as end_date
                    if compare_date_day <= end_date_day:
                        data.append(line.split(','))
                        #print(data)
                else:
                    data.append(line.split(','))
                    #print(data)

    f.close()
    return data

def parse_push_data(entry):#2
    try:
        name = entry.find('span.f3.hl.push-userid',first=True).text
        pushOrdown = entry.find('span.hl.push-tag',first=True).text
        if pushOrdown.find('推') == 0:
            data = [name,1,0]
        elif pushOrdown.find('噓') == 0:
            data = [name,0,1]
        else:
            data = [name,0,0]
        return data
    except AttributeError:
        pass

def get_push_data_from_article_data_date(url):#2
    resp = fetch(url)
    html = HTML(html=resp.text)
    post_entries = html.find('div.push')
    data = []
    for entry in post_entries:
        check = parse_push_data(entry)
        if check != None:
            data.append(check)
    return data
        

def update_push_guest_list(guest_list,data): # void function#2
    # Complete!
    for lists in data:
        guest = guest_list.get(lists[0])
        if guest:
            lists[1] += guest[0]
            lists[2] += guest[1]
            guest_list.update({lists[0]:[lists[1],lists[2]]})
        else:
            guest_list.update({lists[0]:[lists[1],lists[2]]})

            
def calculate_total_push_from_people(guest_list):
    totalCount = [0,0]
    #for pushCount in range(len(guest_list)):
    start_time = time.time()
    push_down_list = guest_list.values()
    push_sort = [(v,k) for k,v in guest_list.items()]
    push_sort.sort()
    down_sort = [(v[::-1],k) for k,v in guest_list.items()]
    down_sort.sort()
    for pushCount in push_down_list:
        totalCount[0] += pushCount[0]
        totalCount[1] += pushCount[1]
    print("reference elapsed time : ",time.time() - start_time)        
    return totalCount, push_sort[::-1], down_sort[::-1]
            
def push(start_date,end_date):#2
    
    #2-1 Get article from start_date to end_date
    push_articles = get_article_from_file(start_date,end_date,'all_article.txt')
    #2-2 Get push people form #2-1 data
    data = []
    guest_list = {}
    article_count = 0
    for push_article in push_articles:
        #print(push_article[-1])
        data = get_push_data_from_article_data_date(push_article[-1])
        update_push_guest_list(guest_list,data)
        data.clear()
        print('article count',article_count)
        article_count += 1
        time.sleep(0.2)
    #print(guest_list)
    
    #2-3 Get Total count of push
    totalCount,push_sorted,down_sorted = calculate_total_push_from_people(guest_list)
    print("Total push and down count : ", totalCount)
    
    with open('push['+start_date+'-'+end_date+'].txt','w',encoding='utf-8') as f:
        f.write("all like: {0}\n".format(totalCount[0]))
        f.write("all boo: {0}\n".format(totalCount[1]))
        for i in range(10):
            f.write("like #{0} : {1} {2}\n".format(i+1,push_sorted[i][1],push_sorted[i][0][0] ))
        for i in range(10):
            f.write("boo #{0} : {1} {2}\n".format(i+1,down_sorted[i][1],down_sorted[i][0][0]))
    f.close()
    
    #print(push_article)


def get_popular_data_from_popular_article(url):#3
    resp = fetch(url)
    html = HTML(html=resp.text)
    img_list = []
    format_list = ['.jpg','.jpeg','.png','.gif']
    for format_ in format_list:
        post_entries = html.find('a',containing=format_)
        for entry in post_entries:
            strl = entry.attrs.get('href')
            #print(strl)
            for check in format_list:
                if (strl[-4:] == check):
                    img_list.append(strl)
    return img_list[::-1]

def popular(start_date,end_date):
    popular_articles = get_article_from_file(start_date,end_date,'all_popular.txt')
    popular_data = []
    article_count = 1
    for popular_article in popular_articles:
        data = get_popular_data_from_popular_article(popular_article[-1])
        print('article count : ',article_count)
        if data!= None:
            popular_data += data
        article_count += 1
        data.clear()

        
    with open('popular['+start_date+'-'+end_date+'].txt','w',encoding='utf-8') as f:
        f.write("number of popular articles: {0}\n".format(len(popular_articles)))
        for data in popular_data:
            f.write("{0}\n".format(data))
    f.close()
    return


def get_keyword_data_from_all_article(url,word):#3
    resp = fetch(url)
    html = HTML(html=resp.text)
    string = html.full_text
    string = string[:string.find('--')]
    img_list = []
    format_list = ['.jpg','.jpeg','.png','.gif']
    if string.find(word) != -1:
        for format_ in format_list:
            post_entries = html.find('a',containing=format_)
            for entry in post_entries:
                strl = entry.attrs.get('href')
                #print(strl)
                for check in format_list:
                    if (strl[-4:] == check):
                        img_list.append(strl)
    return  img_list[::-1]

def keyword(start_date,end_date,word):
    articles = get_article_from_file(start_date,end_date,'all_article.txt')
    image_list = []
    article_count = 1
    for article in articles:
        data = get_keyword_data_from_all_article(article[-1],word)
        print( 'article_count:',article_count )
        if data != None:
            image_list += data
        data.clear()
        article_count += 1
        time.sleep(0.5)
        
        
    with open('keyword('+word+')['+start_date+'-'+end_date+'].txt','w',encoding='utf-8') as f:
        for data in image_list:
            f.write("{0}\n".format(data))
    f.close()
        
    return

if __name__ == "__main__":
    print('hello!')
    
    if sys.argv[1] == 'crawl':
        print('crawl function')
        
        start_time = time.time()
        start_url = 'https://www.ptt.cc/bbs/Beauty/index.html'
        metadata,populardata = get_paged_meta(start_url)
        
        with open('all_article.txt','w',encoding='utf-8') as f: 
            for web in metadata[::-1]:
                date = web['date'].split('/')
                date = date[0]+date[1]
                f.write("{0},{1},{2}\n".format(date,web['title'],domain+web['link']))
        f.close()
        with open('all_popular.txt','w',encoding='utf-8') as f: 
            for pop in populardata[::-1]:
                date = pop['date'].split('/')
                date = date[0]+date[1]
                f.write("{0},{1},{2}\n".format(date,pop['title'],domain+pop['link']))
        f.close()
        
        print('Crawl elapsed time:', time.time() - start_time)
        print('Total article count : ', len(metadata))
        print('Total popular article count : ',len(populardata))
        print('Total announcement article : ', notarticle)
        metadata.clear()
        populardata.clear()
    elif len(sys.argv) == 4 and sys.argv[1] == 'push':
        print('push function start')
        start_date = sys.argv[2]
        end_date = sys.argv[3]

        start_time = time.time()
        push(start_date,end_date)
        print("Push elapsed time : ",time.time() - start_time)
    elif len(sys.argv) == 4 and sys.argv[1] == 'popular':
        print('Popular function start')
        start_date = sys.argv[2]
        end_date = sys.argv[3]
        
        start_time = time.time()
        popular(start_date,end_date)
        print("popular elapsed time : ",time.time() - start_time)
    elif len(sys.argv) == 5 and sys.argv[1] == 'keyword':
    
        print('Keyword function start')
        start_date = sys.argv[3]
        end_date = sys.argv[4]
        word = sys.argv[2]
        start_time = time.time()
        keyword(start_date,end_date,word)
        print("keyword elapsed time : ",time.time() - start_time)