from django.shortcuts import render_to_response

def index(req) :
    return render_to_response('index.html', {})

def search(req):
    if req.method=='POST':
        kw=req.POST["word"]
        print(kw)
        
        return render_to_response('index.html', {})