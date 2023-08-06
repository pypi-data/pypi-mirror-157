# 2022.6.30 uvicorn __main__:app --port 8008 --host 0.0.0.0 --reload  | python -m uvirun 
from uvirun import *

from fastapi import FastAPI, File, UploadFile,Form, Body,Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

from gec_fastapi import *
from dsk_fastapi import *
from cos_fastapi import *
from util_fastapi import *
from spacy_fastapi import *

try:
	from textacy_fastapi import * 
except Exception as e:
	print( "import error:", e ) 

if os.getenv('eshost','') : from es_fastapi import * 
if os.getenv('rhost','') : from uviredis import * 

@app.get("/input", response_class=HTMLResponse)
async def input_item(request: Request):
	return templates.TemplateResponse("input.html", {"request": request})
@app.get("/getdata")
async def getdata(fname:str="first name", lname:str="last name"):
	return { "fname":fname, 'lname':lname }

if __name__ == '__main__':
	uvicorn.run(app, host='0.0.0.0', port=8008)

'''
for root, dirs, files in os.walk(".",topdown=False):
	for file in files: 
		if file.endswith("_fastapi.py"): 
			file = file.split(".")[0]
			__import__(file, fromlist=['*'])
'''