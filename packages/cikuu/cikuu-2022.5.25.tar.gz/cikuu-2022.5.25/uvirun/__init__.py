#from uvirun import * 
#uvicorn uvirun:app --port 80 --host 0.0.0.0 --reload
import json,os,uvicorn,time, fastapi,platform,requests
from fastapi import FastAPI, File, UploadFile,Form, Body
from fastapi.responses import HTMLResponse

app = globals().get('app', fastapi.FastAPI()) #app=FastAPI(title= "Essay Dsk Data API",description= "data for ***",version= "0.1.0",openapi_url="/fastapi/data_manger.json",docs_url="/fastapi/docs",redoc_url="/fastapi/redoc")
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

@app.get('/')
def home(): 
	return HTMLResponse(content=f"<h2> uvirun *_fastapi list</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>uvicorn uvirun:app --port 80 --host 0.0.0.0 --reload <br> started: {now()}")

if __name__ == '__main__':
	uvicorn.run(app, host='0.0.0.0', port=80)

'''
@app.get('/hello')
def hello(snt:str="I'm glad to meet you."): 
	return snt

from fastapi import FastAPI
from starlette.responses import JSONResponse 
from starlette.routing import Route

async def homepage(request):
    return JSONResponse({"index":"HOme"}) 

async def about(request):
    return JSONResponse({"index":"about"}) 

routes = [
    Route("/", endpoint=homepage,methods=["GET"]),
    Route("/about", endpoint=about,methods=["POST"]),
]
app=FastAPI(routes=routes)
'''