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
t3qai_helper
------------
The t3q.ai platform is an AI platform capable of preprocessing, AI training, and model deployment.

t3qai_helper is a client module for interworking with the t3q.ai platform.
"""
import os, json, datetime, pathlib, logging
import requests
from logging.handlers import RotatingFileHandler
import pandas as pd

T3QAI_TRAIN_PRRAMS_FILE = "t3qai_train_params.json"
OPER_PARAMS_FILE = "oper_params.json"
OPER_PATH_FILE = "oper_path.json"
POD_VOLUME_PATH = "/cache"


LOG_FORMAT = '%(asctime)s [%(levelname)5s] %(name)s: %(message)s'

# API 호출 에서 공통 PARAMS 관련 변수 
_T3QAI_PARAMS = None
_t3qai_params_file_path = f"{POD_VOLUME_PATH}/{T3QAI_TRAIN_PRRAMS_FILE}"
_t3qai_params_file_exsit = os.path.isfile(_t3qai_params_file_path)        
if _t3qai_params_file_exsit :                
    with open(_t3qai_params_file_path, 'r') as f:
        _T3QAI_PARAMS = json.loads(f.read())            

# API 호출 HOST, PORT 변수
_T3QAI_API_HOST = "t3qai-svc"
_T3QAI_API_PORT = 5000
if _T3QAI_PARAMS:
    _T3QAI_API_HOST = _T3QAI_PARAMS.get("SVC_HOSTNAME") if _T3QAI_PARAMS.get("SVC_HOSTNAME") else "t3qai-svc"
    _T3QAI_API_PORT = _T3QAI_PARAMS.get("SVC_PORT") if _T3QAI_PARAMS.get("SVC_PORT") else 5000

def _t3qai_api_call(svc_url, api_data=None, error_msg=None):
    """
    Call t3qai rest api
    """
    response = None
    req_data = {}
    req_url = 'http://{}:{}/api/v2/t3qai_client/'.format(_T3QAI_API_HOST, _T3QAI_API_PORT) + svc_url
    
    # tm 객체 생성을 위한 api 공통 params 
    req_data['t3qai_params'] = _T3QAI_PARAMS
    req_data['api_data'] = api_data
    
    msg = svc_url
    if error_msg:
        msg = error_msg
        
    try:
        response = requests.post(req_url, json=req_data, timeout=30)
        res_data = json.loads(response.text)
    
        if res_data.get("code") == "ERROR":
            logging.warn("succeed to call api : {}, but occurred data error".format(msg))
            
    except Exception as e:
        res_data = None
        logging.warn("failed to call api : {} ".format(msg))   
    
    return response


def _configure_logger(logger, log_path, log_filename=None, log_level=logging.WARN):
    """
    Internal function to set up logger
    """
    logger.setLevel(log_level)
    
    # add Console Handler
    _add_console_handler(logger, log_level)
    
    # add File Handler
    if log_filename:
        _add_file_handler(logger, log_path, log_filename, log_level)
    
    
def _add_console_handler(logger, log_level=logging.INFO):
    """
    Internal function to set up logger
    """
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)


def _add_file_handler(logger, log_path, log_filename, log_level=logging.DEBUG):
    """
    Internal function to set up logger
    """
    pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_path, log_filename), when='d', interval=1, backupCount=30,
        encoding=None, delay=False, utc=False)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)



def _load_dataset(id_column,rule_info,dataset_path, data_index_path):
    """
    Internal function to load dataset
    
    Returns
    -------
    dataframe
    """
    
    id_name = id_column
    df = None
    if data_index_path:
        if os.path.exists(data_index_path):
            df = pd.read_csv(data_index_path)
    for rule in rule_info:
        data_path = os.path.join(dataset_path, "_{}_data_.csv".format(str(rule['rule_no'])))
        # HDFS 미지원
        if not os.path.exists(data_path):
            continue
        # HDFS 미지원
        rule_df = pd.read_csv(data_path)
        if df is None:
            df = rule_df
        else:
            cols_to_use = [id_name]
            cols_to_use.extend(df.columns.difference(rule_df.columns, sort=False))
            
            df = df[cols_to_use].merge(rule_df, on=id_name, how='left')
    return df

def train_start():
    """
    Change learning state to start
    """
    train_set_logger()
    
    url = 'train_start'
    _t3qai_api_call(url)
        
    
def train_finish(err, error_msg=None):
    """
    Change the learning state to End
    
    Parameters
    ----------
    err : None or Exception Object
        If None, normal end, if there is a value, change the learning state to error.

    error_msg : None or Exception Object
        Default is None, if an error occurs, enter Exception Object
            
    """
    end_time_json = {
      "status": 3
    }
    
    if err:
        end_time_json["status"] = 4
        end_time_json["error_msg"] = str(error_msg)
    
    url = 'train_finish'
    
    _t3qai_api_call(url, end_time_json)
    

def train_load_param():
    """
    Returns training parameter information
    
    Returns
    -------
    dictionary
        The dictionary key consists of the common parameters and model parameters selected when registering the learning algorithm.
        
        - dictionary structure
            - 'init_method' : str , Initialization method (internal definition)   ex) '21001' : Xavier uniform, '21002' : Xavier normal, '21003' : Random uniform, '21004' : Random normal, '21005' : HE uniform, '21006' : HE normal, '21007' : LeCun uniform, '21008' : LeCun normal
            - 'opt_method' : str , Optimization method (internal definition)      ex) '22002' : Gradient Descent, '22002' : Adagrad, '22003' : Adagrad, '22004' : Momemtum
            - 'learning_rate' : str , Learning Rate                               ex) '0.001'
            - 'dropout_ratio' : str , Dropout Ratio                               ex) '0.3'
            - 'random_seed' : str , Random seed                                   ex) '777'
            - 'autosave_p' : str , autosave cycle                                 ex) '50'
            - 'epoch' : str , Number of times of learning                         ex)'10'
            - 'batch_size' : str , batch size                                     ex) '100'
            - 'cpu': float , cpu(number of cores)                                 ex) 1.0
            - 'memory': str , memory(Gi)                                          ex)'4Gi'
            - 'gpu': int , gpu                                                    ex) 0, 1, ..            
            
    """
    url = 'train_load_param'
    res_data = None
    response = _t3qai_api_call(url)
    if response:
        res_data = json.loads(response.text)
    
    return_data = {}
    if res_data and res_data.get("data"):
        return_data = res_data.get("data")
    
    return return_data
    
    
    
def inference_load_param():
    """
    Returns inference parameter information
    
    Returns
    -------
    dictionary
        The dictionary key consists of common parameters selected when registering the learning algorithm, model parameters, and information related to training data.
        
        - dictionary structure
            - 'init_method' : str , Initialization method (internal definition)  ex) '21001' : Xavier uniform, '21002' : Xavier normal, '21003' : Random uniform, '21004' : Random normal, '21005' : HE uniform, '21006' : HE normal, '21007' : LeCun uniform, '21008' : LeCun normal
            - 'learning_rate' : str , Learning Rate                              ex) '0.001'
            - 'opt_method' : str , Optimization method (internal definition)     ex) '22002' : Gradient Descent, '22002' : Adagrad, '22003' : Adagrad, '22004' : Momemtum
            - 'dropout_ratio' : str , Dropout Ratio                              ex) '0.3'
            - 'random_seed' :  str , Random seed                                 ex) '777'
            - 'autosave_p' : str , autosave cycle                                ex) '50'
            - 'epoch' : str , Number of times of learning                        ex)'10'
            - 'batch_size' : str , batch size                                    ex) '100'
            - 'y_value' : list , Training data label type                                                              ex)['0', '1']
            - 'id_column' : str , Column name of id column selected when designing preprocessing                       ex) 'Id'
            - 'label_column' : str , The column name of the label column selected when designing the preprocessing     ex)'target'
            - 'feature_info' : dict , About training data properties                                                   ex) {'x': ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg'], 'id': 'Id', 'y': ['target'], 'y_value': ['0', '1'],  'y_chart_data': [['x', 0, 1], ['value', 138, 165]]}
        
    """
    file_path = f"{POD_VOLUME_PATH}/{OPER_PARAMS_FILE}"
    
    file_exsit = os.path.isfile(file_path)        
    params = None
    if file_exsit :                
        with open(file_path, 'r') as f:
            params = json.loads(f.read())    
            
    return params

def train_load_path():
    """
    Returns learning path information
    
    Returns
    -------
    dictionary
        Available Paths in Learning Algorithms
        
        - dictionary structure
            - 'model_path': str , Path to store the training model
            - 'train_data_path': str , training data path
            - 'test_data_path': str , test data path
            - 'train_index_path': str , The path of train data in which the preprocessed data is divided by a specific ratio through the evaluation index
            - 'test_index_path': str , The path of train data in which the preprocessed data is divided by a specific ratio through the evaluation index
            - 'module_path': str , Path where the algorithm is stored
            
    """
    url = 'train_load_path'
    res_data = None
    response = _t3qai_api_call(url)
    if response:
        res_data = json.loads(response.text)
    
    return_data = {}
    if res_data and res_data.get("data"):
        return_data = res_data.get("data")
    
    return return_data
    

def load_data():
    """
    In the case of a csv file with id and label specified in the preprocessing model, data is returned.
    
    When Train-Test split or K-fold Cross Validation is selected among the evaluation methods during learning design, two train and test tuples are created, divided by the set ratio.
    In the remaining cases, two train and test tuples created with the entire data are created.
    
    Returns
    --------
    tuple
    
        - tuple items info
            - train_id : dataframe, unique
            - train_x : dataframe
            - train_y : dataframe
            - test_id : dataframe, unique
            - test_x : dataframe
            - test_y : dataframe
            
    """
    url = 'train_load_data'
    res_data = None
    response = _t3qai_api_call(url)
    if response:
        res_data = json.loads(response.text)
    
    params = {}
    train_id, train, train_y, test_id, test, test_y = None, None, None, None, None, None
    if res_data and res_data.get("data"):
        params = res_data.get("data")
    
        id_name = params.get("id_column")
        y_name = params.get("label_column")
        
        rule_info = params.get("rule_info")
        train = _load_dataset(id_name,rule_info,params.get("train_dataset_path"), params.get("train_index_path"))
        
        train_id = None
        if id_name:
            train_id = train.pop(id_name)
        train_y = None
        if y_name:
            y_columns = [column for column in list(train) if column.startswith(y_name) == True]
            train_y = pd.concat([train.pop(x) for x in y_columns], 1)
    
        test = _load_dataset(id_name,rule_info,params.get("test_dataset_path"), params.get("test_index_path"))
        test_id = None
        if id_name:
            test_id = test.pop(id_name)
        test_y = None
        if y_name:
            test_y = pd.concat([test.pop(x) for x in y_columns], 1)

    return (train_id, train, train_y), (test_id, test, test_y)


def load_test_data():
    """
    In the case of a csv file with id and label specified in the preprocessing model, test data is returned.
    
    Returns
    -------
    tuple
    
        - tuple items info
            - test_id : dataframe, unique
            - test_x : dataframe
            - test_y : dataframe
    """
    url = 'train_load_data'
    res_data = None
    response = _t3qai_api_call(url)
    if response:
        res_data = json.loads(response.text)
    
    params = {}
    test_id, test, test_y = None, None, None
    if res_data and res_data.get("data"):
        params = res_data.get("data")
                
        id_name = params.get("id_column")
        y_name = params.get("label_column")
        
        rule_info = params.get("rule_info")
        
        test = _load_dataset(id_name,rule_info,params.get("test_dataset_path"), None)
        test_id = None
        if id_name:
            test_id = test.pop(id_name)
        test_y = None
        if y_name:
            y_columns = [column for column in list(test) if column.startswith(y_name) == True]
            test_y = pd.concat([test.pop(x) for x in y_columns], 1)    
    
        return test_id, test, test_y

def inference_load_path():
    """
    Returns inference path information
    
    Invoking available parameters from the platform during model inference
    
    Returns
    -------
    dictionary
        
        - dictionary structure
            - 'model_path' : str , Model path to infer
            - 'meta_path' : str , Inference preprocessing model path
            - 'module_path' : str , Algorithm path
            - 'logger_path' : str , Log file path
    
    """
    file_path = f"{POD_VOLUME_PATH}/{OPER_PATH_FILE}"
    
    file_exsit = os.path.isfile(file_path)        
    params = None
    if file_exsit :                
        with open(file_path, 'r') as f:
            params = json.loads(f.read())    
            
    return params

def train_save_stat_metrics(data):
    """
    Show the learning results chart : 
        Train variable values ​​for each epoch in Accuracy and Loss charts
    
    Parameters
    ----------
    data : dictionary
    
        - dictionary structure
            - 'loss' : float , Training loss ​​per epoch            ex) 0.6725882838984005
            - 'accuracy' : float , Training accuracy ​​per epoch    ex) 0.9226190476190477
            - 'step' : int , epoch                                ex) 1, 2, 3 ..
         
    Examples
    --------
    >>> from t3qai_client import train_load_param
    >>> from t3qai_client import train_save_stat_metrics
    >>> params = train_load_param()
    >>> epoch = int(params.get('epoch'))
    >>> for i in epoch:
    ...     data = {}
    ...     data["loss"] = train_loss[i]  # train_loss is a list of training loss values ​​per epoch
    ...     data["accuracy"] = train_accuracy[i]  # train_accuracy is a list of training accuracies per epoch
    ...     data["step"] = i
    ...     train_save_stat_metrics(data)
    """
    logging.info("train_save_stat_metrics : {}".format(data))
    
    url = 'train_save_stat_metrics'
    _t3qai_api_call(url, data)
        

def train_save_classification_result(data):
    """
    Show the learning results chart : 
        test variable values ​​of Accuracy and Loss chart, Confusion Matrix, Precision/Recall/F1-score
    
    Parameters
    ----------
    data : dictionary 

        - dictionary structure
            - 'predict_y' : list , Enter the predicted y value         ex) [0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
            - 'actual_y' : list , Enter the actual y value             ex) [[0], [1], [0], [1], [1], [0], [0], [0], [0], [1]]
            - 'test_id' : list , Enter the id list of the tested data  ex) [167, 30, 284, 92, 32, 220, 300, 290, 177, 127]
            - 'loss' : float , Enter training loss                     ex) 0.6926398492250286

    Examples
    --------
    >>> from sklearn.linear_model import LogisticRegression
    >>> from sklearn.metrics import log_loss
    >>> from t3qai_client import train_save_classification_result
    
    #### Skip the step before model creation
    
    >>> model_ = LogisticRegression(penalty=penalty ,C=C, solver= solver, n_jobs= n_jobs)
    >>> hist = model_.fit(train_x,train_y) # train_x, train_y are the x,y list of training data
    
    #### evaluation
    
    >>> predictions = model_.predict(test_x)
    >>> eval_results={}
    >>> predict_y = []

    >>> for p in predictions:
    ...     predict_y.append(np.asscalar(p))
    
    >>> y_pred = model_.predict_proba(test_x)
    >>> val_loss = log_loss(test_y,y_pred)
    
    #### create charts
    
    >>> eval_results['predict_y'] = predict_y
    >>> eval_results['actual_y'] = test_y.iloc[:].values.tolist()
    >>> eval_results['test_id'] = test_id.values.tolist()
    >>> eval_results['loss']=val_loss    
    >>> train_save_classification_result(eval_results)
    """
    logging.info("train_save_classification_result : {}".format(data))
    
    url = 'train_save_classification_result'
    _t3qai_api_call(url, data)
    

def train_save_result_metrics(data):
    """
    Show the learning results chart : test variable values ​​of Accuracy and Loss chart, PCA chart
    
    Parameters
    ----------
    data : dictionary

        - dictionary structure (If you want to draw only the PCA chart, you can use the ``pca_2d`` key. And if you want to draw only the Accuracy and Loss charts, you can use the other keys, ``loss``, ``accuracy``, and ``step``.)
            - 'pca_2d' : 
                - 'x' : list , The x-coordinate of each data in 2D PCA    ex) [-31.86938118401984, 0.765592182497871, -57.407825296941176, ...]
                - 'y' : list , The y-coordinate of each data in 2D PCA    ex) [-33.00107881369991, -56.84193518152965, -13.126986903900985, ...]
                - 'c' : list , label value of each data                   ex) [0, 1, 0, ...]
            - 'loss' : float , Training loss ​​per epoch                    ex) 0.6725882838984005
            - 'accuracy' : float , Training accuracy ​​per epoch            ex) 0.9226190476190477
            - 'step' : int , epoch                                        ex) 1, 2, 3 ..

    Examples
    --------
    #### PCA chart output
    >>> from sklearn.decomposition import PCA
    >>> from t3qai_client import train_save_result_metrics
    >>> pca = PCA(n_components=2)
    >>> pca_2d = pca.fit_transform(train_x)     # train_x is the feature column data of the training data, dataframe 
    >>> data, pca_chart = {}, {}
    >>> pca_chart['x'] = pca_2d[:,0].tolist()   # x-coordinate list of transformed train_x
    >>> pca_chart['y'] = pca_2d[:,1].tolist()   # y-coordinate list of the transformed train_x
    >>> pca_chart['c'] = label_list             # list of label types of training data
    >>> data['pca_2d'] = pca_chart
    >>> train_save_result_metrics(data)
    """
    logging.info("train_save_result_metrics : {}".format(data))
    
    url = 'train_save_result_metrics'
    _t3qai_api_call(url, data)
    

def train_set_logger():
    """"
    Learning logger setup
    """
    _log_directory = 'logs'
    _log_filename = 'train.log'
    _log_level = 'DEBUG'
    
    logger = logging.getLogger()
    path_info = train_load_path()
    if path_info:
        model_path = path_info.get("model_path")
        if model_path and os.path.exists(model_path):
            train_log_path = os.path.join(model_path, _log_directory)
            pathlib.Path(train_log_path).mkdir(parents=True, exist_ok=True)
            if os.path.exists(os.path.join(train_log_path,_log_filename)):
                os.remove(os.path.join(train_log_path,_log_filename))
            _configure_logger(logger, train_log_path, log_filename=_log_filename, log_level=_log_level)
    
    
def inference_set_logger():
    """
    Inference logger setup
    """
    _log_filename = 'oper.log'
    #_log_level = 'DEBUG'
    _log_level = 'INFO'
    
    logger = logging.getLogger()
    logger.setLevel(_log_level)
    
    #logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    
    logger_path = inference_load_path().get("logger_path")
    if logger_path and  os.path.exists(logger_path):
        log_name = os.path.join(logger_path, _log_filename)
        pathlib.Path(logger_path).mkdir(parents=True, exist_ok=True)
        
        #_add_console_handler(logger, log_level=_log_level)
        
        handler = RotatingFileHandler(log_name, mode="w", maxBytes=10 * 1024 * 1024, backupCount=10)
        handler.setLevel(_log_level)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        logger.addHandler(handler)


class DownloadFile():
    """
    Inference file obj setup
    """
    def __init__(self, file_name=None, file_obj=None, file_path=None):
        self.file_name = file_name
        self.file_obj = file_obj
        self.file_path = file_path
                
        if (file_path is None) and (file_obj is None):
            raise Exception("Please input file_path or file_obj")
        
        # load file_obj from file_path
        if file_path and (file_obj is None):
            self.file_obj = open(file_path, 'rb')        

_train_path_params = train_load_path()
_inference_path_params = inference_load_path()

T3QAI_TRAIN_OUTPUT_PATH =  None
T3QAI_TRAIN_MODEL_PATH = None
T3QAI_TRAIN_DATA_PATH = None
T3QAI_TEST_DATA_PATH = None
T3QAI_MODULE_PATH = None
T3QAI_INIT_MODEL_PATH = None
if _train_path_params : 
    T3QAI_TRAIN_OUTPUT_PATH = os.path.join(_train_path_params.get("model_path"),'t3qai_output') if _train_path_params else None
    T3QAI_TRAIN_MODEL_PATH = _train_path_params.get("model_path") if _train_path_params else None
    T3QAI_TRAIN_DATA_PATH = _train_path_params.get("train_data_path") if _train_path_params else None
    T3QAI_TEST_DATA_PATH = _train_path_params.get("test_data_path") if _train_path_params else None
    T3QAI_MODULE_PATH = _train_path_params.get("module_path") if _train_path_params else None
if _inference_path_params:
    T3QAI_INIT_MODEL_PATH = _inference_path_params.get("model_path") if _inference_path_params else None
