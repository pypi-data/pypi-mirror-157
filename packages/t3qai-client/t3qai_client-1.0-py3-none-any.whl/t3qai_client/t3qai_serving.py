# coding: utf-8
# Copyright [t3q]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
t3qai_serving
-------------
Source that starts when the inference model is deployed
"""
import os
import io
import sys
import ast
import json
import imghdr
import logging
import zipfile
import importlib

import pandas as pd
from urllib import parse
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any
from fastapi import FastAPI, File, UploadFile, Request, Response
from fastapi.responses import StreamingResponse, PlainTextResponse

from t3qai_client.t3qai_helper import DownloadFile as DownloadFile

SERVING_PARAMS_FILE = "serving_params.json"
POD_VOLUME_PATH = "/cache"

app = FastAPI()
@app.post("/inference")
async def inference(request: Request):
    """
    Receive json and proceed with inference
    
    Parameters
    ----------
    json data from request body
    """
    
    print("inference async")
    
    results = None
    
    try:
        data = await request.body()
        data = ast.literal_eval(data.decode())
        try:
            if 'test_data' in data:
                test_data = data['test_data']
                if isinstance(test_data,dict):
                    if test_data.get("columns"):
                        test_data["values"] = ast.literal_eval(test_data.get("values"))
                        if test_data.get("columns") and test_data.get("values"):
                            test_data = pd.DataFrame(test_data.get("values"), columns = test_data.get("columns"))
                    elif test_data.get("values"):
                        test_data = ast.literal_eval(test_data.get("values"))
                else:
                    test_data = ast.literal_eval(test_data) 
        except Exception as data_e: 
            test_data = test_data
        inference_ai_module = importlib.import_module(inference_module)
        results = getattr(inference_ai_module, inference_function)(test_data,model)
        
    except Exception as e:
        logging.exception(e)
        results = {"result":"error", "msg":str(e)}
    return results

@app.post("/inference_file")
async def inference_file(files: List[UploadFile] = File(...)):
    """
    Receive the file and proceed with inference
    
    Parameters
    ----------
    a list of UploadFile objects
    """

    inference_ai_module = importlib.import_module(inference_module)
    
    # decode filename
    files_length = len(files)
    
    for i in range(files_length) :
        files[i].filename = parse.unquote(files[i].filename)
        
    results = getattr(inference_ai_module, inference_file_function)(files, model)
    # 1. inference result = 1 file
    if isinstance(results, DownloadFile):
        download_file = results
        file_contents = download_file.file_obj.read()
        
        if _is_image_file(file_contents):
            #print('decoded file name =', download_file.file_name.decode('iso-8859-1'))
            return _make_image_response(file_contents, download_file.file_name)
        else:
            return _make_binary_response(file_contents, download_file.file_name)

	
	# 2. inference result >= 2 file		
    elif isinstance(results, list) and len(results) > 0 and isinstance(results[0], DownloadFile):
        # multi file to zip
        zip_buffer = io.BytesIO()
        
        # result_zip = zipfile.ZipFile(zip_buffer, 'w')
        with zipfile.ZipFile(zip_buffer, 'w') as result_zip:
            for result in results:
                result_zip.writestr(result.file_name, result.file_obj.read())
        # result_zip.close()
        res = _make_zip_response(zip_buffer.getvalue())
        return res
        
    # 3. inference result = data (not file)
    else:
        results = str(results)
        return PlainTextResponse(results)

def _is_image_file(file_contents):   
    file_bytes = io.BytesIO(file_contents)
    return imghdr.what(file_bytes)

def _make_image_response(file_contents, file_name):
    file_bytes = io.BytesIO(file_contents)
    res = StreamingResponse(content=file_bytes, media_type="image/png")
    res.headers['X-filename'] = file_name
    return res

def _make_binary_response(file_contents, file_name):
    res = Response(content=file_contents, media_type="application/octet-stream")
    res.headers['X-filename'] = file_name
    return res

def _make_zip_response(file_contents):
    res = Response(content=file_contents, media_type="application/x-zip-compressed")
    today_date = datetime.now().strftime("%Y%m%d%H%M%S")    
    res.headers['X-filename'] = 'inference_results_'+today_date+'.zip'
    return res


file_path = f"{POD_VOLUME_PATH}/{SERVING_PARAMS_FILE}"

file_exsit = os.path.isfile(file_path)        
params = None
if file_exsit :                
    with open(file_path, 'r') as f:
        params = json.loads(f.read())    

model_id = params["model_id"]
log_path = params["log_path"]
workspace = params["workspace"]

algorithm_id = params["algorithm_id"]
algo_ver = params["algorithm_ver"]
init_model_module = params["init_model_module"]
init_model_function = params["init_model_function"]
inference_module = params["inference_module"]
inference_function = params["inference_function"]
inference_file_function = params["inference_file_function"]
    
algo_path = os.path.join(log_path, workspace, 'mods', 'algo_' + str(algorithm_id), str(algo_ver))
sys.path.append(algo_path)
logging.info("algo_path={}".format(algo_path))

init_ai_module = importlib.import_module(init_model_module)
model = getattr(init_ai_module, init_model_function)()
