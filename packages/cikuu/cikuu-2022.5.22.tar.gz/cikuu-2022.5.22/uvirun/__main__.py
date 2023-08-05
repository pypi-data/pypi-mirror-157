#uvicorn __main__:app --port 8008 --host 0.0.0.0 --reload  | python -m uvirun 
import json,os,uvicorn,time
from fastapi import FastAPI, File, UploadFile,Form, Body
from fastapi.responses import HTMLResponse
app	 = FastAPI() #app=FastAPI(title= "Essay Dsk Data API",description= "data for ***",version= "0.1.0",openapi_url="/fastapi/data_manger.json",docs_url="/fastapi/docs",redoc_url="/fastapi/redoc")
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

@app.get('/')
def home(): 
	return HTMLResponse(content=f"<h2>*_fastpi.py merged api list</h2><a href='/docs'> docs </a> | <a href='/redoc'> redoc </a><br>uvicorn uvirun:app --port 80 --host 0.0.0.0 --reload <br> {now()} <br>")

from textacy_fastapi import * 

if __name__ == '__main__':
	uvicorn.run(app, host='0.0.0.0', port=8008)

'''
for root, dirs, files in os.walk(".",topdown=False):
	for file in files: 
		if file.endswith("_fastapi.py"): 
			file = file.split(".")[0]
			__import__(file, fromlist=['*'])
'''