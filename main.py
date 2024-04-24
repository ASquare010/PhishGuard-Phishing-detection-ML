#!/usr/bin/env python
# coding: utf-8

# In[67]:


from phishingDetection.urlPishDect.modules.Prediction import PredictionURLS
from phishingDetection.emailPishDect.modules.FeatureExtractionEmail import FeatureExtractionEmail
from flask_cors import CORS
from flask import Flask,render_template, request,jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user


import gzip
import warnings
import joblib
import os


# In[68]:


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.secret_key = 'kP6w2Xr8vN3sQ7tT'

login_manager = LoginManager()
login_manager.init_app(app)


# In[69]:


def compress_pickle(input_file, output_file):
    with open(input_file, 'rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            f_out.write(f_in.read())

def decompress_pickle(input_file, output_file):
    if not os.path.exists(output_file):
        with gzip.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
 


# In[70]:


def decompressFiles():
    decompress_pickle('phishingDetection/emailPishDect/model/best_model.gz','phishingDetection/emailPishDect/model/best_model.pkl')
    decompress_pickle('phishingDetection/urlPishDect/model/bestmodel.gz','phishingDetection/urlPishDect/model/bestmodel.pkl')


# Email 

# In[71]:


def loadPredict(predict):

    loaded_model = joblib.load('phishingDetection/emailPishDect/model/best_model.pkl')
    
    label = loaded_model.predict(predict)

    return label


def predictionEmail(email_content):    
    decompressFiles()

    obj=FeatureExtractionEmail(email_content)
    df = obj.df
    loaded_scaler = joblib.load('phishingDetection/emailPishDect/model/scaler_model.joblib')
    t_df = loaded_scaler.transform(df)
    
    prad = loadPredict(t_df)
    
    return prad


# Urls

# In[72]:


def predictionURLS( urls=[]):
    warnings.filterwarnings("ignore", category=UserWarning, message="Trying to unpickle estimator.*from version.*when using version.*")  
    
    decompressFiles()

    obj = PredictionURLS(urls)

    return obj.resultOutput


# Api Key

# In[73]:


VALID_API_KEYS = ['aB3x8Yp2qR5sW9tZ']
ADMIN_USER_NAME = "admin"
ADMIN_PASSWORD = "admin"


class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    # This callback is used to reload the user object from the user ID stored in the session
    return User(user_id)

# Replace this with your actual user authentication logic
def authenticate(username, password):
    if username == ADMIN_USER_NAME and password == ADMIN_PASSWORD:
        return User(1)
    return None

def verify_api_key(api_key):
    return api_key in VALID_API_KEYS


# For Website API Calls

# In[74]:


@app.route('/')
def home():
    return render_template('index.html')


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = authenticate(username, password)
    if user:
        login_user(user)
        return render_template('admin-page.html')
    else:
        return 'Invalid credentials'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')


# For Admin API Calls

# In[75]:


@app.route('/train', methods=['POST'])
@login_required
def train():
    data = request.json
    train = data.get('train', '')

    print(f"train-> {train}")
    return {"result": f"{train} has started Traning "}




@app.route('/urlpredict', methods=['POST'])
@login_required
def urlpredict():
    
    data = request.json
    url = data.get('data', '')
    result = 'Phishing'

    url_result = predictionURLS([url])

    if(url_result[9] == '0'):
        result = 'Safe'

    return {"result": f"Current Url Result: {result}"}



@app.route('/emailpredict', methods=['POST'])
@login_required
def emailpredict():

    data = request.json
    email = data.get('data', '')
    result = 'Phishing'
    
    email_result = predictionEmail(email)
    
    if(email_result[0] == 0):
        result = 'Safe'
 
    return {"result": f"Email Result: {result}"}


# For Extention API Calls

# In[76]:


@app.route('/urlpredictExt', methods=['POST'])
def urlpredictExt():

    data = request.json
    url = data.get('url', '')
    api_key = data.get('key', '')
    result = 'Phishing'

    # Check if the API key is valid
    if not verify_api_key(api_key):
        return jsonify({"result": "Invalid API key"})
    
    url_result = predictionURLS([url])

    if(url_result[9] == '0'):
        result = 'Safe'

    return {"result": f"Current Url Result: {result}"}

@app.route('/emailpredictExt', methods=['POST'])
def emailpredictExt():

    
    data = request.json
    email = data.get('email', '')
    api_key = data.get('key', '')
    result = 'Phishing'
    
    # Check if the API key is valid
    if not verify_api_key(api_key):
        return jsonify({"result": "Invalid API key"})    

    email_result = predictionEmail(email)
    

    if(email_result[0] == 0):
        result = 'Safe'
    # Render the result template with the prediction result
    return {"result": f"Email Result: {result}"}



# In[77]:


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


# Run this to convert .ipynb to .py for deployment only

# In[ ]:


# !jupyter nbconvert --to script main.ipynb

