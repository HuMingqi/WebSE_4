from django.shortcuts import render_to_response
import json
import hashlib
from distutils.log import INFO


def get_hashkey(word):
    md5 = hashlib.md5()         #must new hash object every time
    md5.update(word.encode("utf8"))
    key = int(md5.hexdigest(),16)%1000          #hash key
    return key

#must be laid front before used
def load_and_build(dic):
    f1,f2,f3 = open(dic+'words_dic.txt',encoding='utf8') , open(dic+'inversed_file.txt',encoding='utf8') , open(dic+'page_info.txt',encoding='utf8')
    words_json = json.loads(f1.read(),encoding='utf8')          #jsonobj-->dic , jsonarray-->list
    inversed_filee = json.loads(f2.read(),encoding='utf8')
    page_infoo = json.loads(f3.read(),encoding='utf8')
    f1.close(),f2.close,f3.close()
    
    #words_hashl = 1000*[[]] #when u append x by list[n].append(x), my god all be appended!?? this is a python bug??
    words_hashl = 1000*[0]
    for word in words_json:
        key=get_hashkey(word["word"])
        
        if words_hashl[key] == 0:           #python can campare two object though they are not the same type
            words_hashl[key]= []
        words_hashl[key].append(word)       #build hash list to make searching faster
    
    return words_hashl, inversed_filee, page_infoo


#words_hashlist , inversed_file , page_info = load_and_build('F:/DataAdapter/Eclipse_workspace/_DataAdapter/SearchEngine_3+/')
words_hashlist , inversed_file , page_info = load_and_build('C:\\Users\\mingq\\Desktop\\Temp\\webse_sample\\')    #test


def index(req) :
    return render_to_response('index.html', {})


def search(req):
    if req.method=='POST':
        kw=req.POST["word"]
        #print(kw)
    else:
        kw=req.GET["wd"]
    kw=kw.lower()          #normalization
    kws=kw.split(" ")
        
    flag=False ; result = []
    if len(kws) == 1:           # single keyword search
        key= get_hashkey(kws[0])
                
        for word in words_hashlist[key]:
            if word["word"] == kws[0]:
                flag=True
                wid=word["id"]
                pages=inversed_file[wid-1]["pages"]          #[{}...]
                pages = sorted(pages, key=lambda item:item.__getitem__("f"), reverse=True)      #descend sort by frequency of page , sorted not "in place"
                #print(pages)   
                             
                for page in pages:
                    info=page_info[page["pid"]-1]
                    info["kf"]=1
                    info["f"]=page["f"]         #no problem although change var page_info
                    result.append(info)
                #print(result)
                    
                switcher = "visible" if len(result) != 0 else "hidden"          #just for using a if exp else b                
                return render_to_response('result.html', {'item_list':result , "switcher":switcher , "switcher1": "hidden" if switcher == "visible" else "visible"})
                    
        if flag == False:       #no result
            return render_to_response('result.html', {'item_list':result , "switcher":"hidden" , "switcher1": "visible" })
                
    else:                       # multiplied keywords search
        page_ff = {}            # { pid:[kf,f] ...} kf-->keyword number   f-->all words number
        
        for wd in kws:
            key = get_hashkey(wd)
            
            for word in words_hashlist[key]:
                if word["word"] == wd:
                    #flag=True
                    wid=word["id"]
                    pages=inversed_file[wid-1]["pages"]          #[{}...]
                    
                    for page in pages:
                        ff= page_ff.get(page["pid"],[0,0])          #build page_ff
                        ff[0]+=1; ff[1]+=page["f"]
                        page_ff[page["pid"]] = ff
        #print(page_ff)
        if len(page_ff)!=0:
            page_ff = sorted(page_ff.items(), key = lambda item: (item[1][0], item[1][1]) , reverse=True)            #two-level sort -->[()...]
            #print(page_ff)
            for page in page_ff:            #page-->(pid,[kf,f])
                info = page_info[page[0]-1]
                info["kf"]=page[1][0]
                info["f"]=page[1][1]
                result.append(info)
                #print(result)                #print often lead to unicode error when include chinese char
            return render_to_response('result.html', {'item_list':result , "switcher":"visible" , "switcher1": "hidden" })
        else:
            return render_to_response('result.html', {'item_list':result , "switcher":"hidden" , "switcher1": "visible" })
