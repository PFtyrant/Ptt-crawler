# Ptt-crawler

Created on Sun Sep 30 11:13:26 2018

@author: PFtyrant

HW1  crawl usage command list:
    Here, I will describe command usage.
    
    1. 0650744.py crawl (2017年專用，/index.html 開始一路往下爬)
    
        elapsed tiem : <= 450s 
    
        file output1-> all_article.txt
        file output2-> all_popular.txt
        
        ｐｓ：如果發生ｃｏｎｎｅｃｔｉｏｎ　ｅｒｒｏｒ類的錯誤，請重新開始
        
    2. 0650744.py push {start_date} {end_date}
    
        elapsed tiem :　<= 1 hour and half
    
        ex) 0650744.py push 101 1231
        file output-> push[101-1231].txt
    
    3. 0650744.py popular {start_date} {end_date}
    
        elapsed tiem :　<= 4s
        
        ex) 0650744.py popular 101 201
        file output - > popular[101-201].txt
    
    4. 0650744.py keyword {word} {start_date} {end_date}
    
        elapsed time: <= 422s
        
        ex) 0650744.py 正妹 101 201
        file output -> keyword(正妹)[101-201].txt
