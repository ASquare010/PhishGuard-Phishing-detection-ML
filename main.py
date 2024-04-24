from phishingDetection.urlPishDect.modules.Prediction import PredictionURLS
from phishingDetection.emailPishDect.modules.FeatureExtractionEmail import FeatureExtractionEmail
from flask_cors import CORS
from flask import Flask,render_template, request,jsonify

import gzip
import warnings
import joblib
import os

def compress_pickle(input_file, output_file):
    with open(input_file, 'rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            f_out.write(f_in.read())


def decompress_pickle(input_file, output_file):
    if not os.path.exists(output_file):
        with gzip.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
 

def decompressFiles():
    decompress_pickle('phishingDetection/emailPishDect/model/best_model.gz','phishingDetection/emailPishDect/model/best_model.pkl')
    decompress_pickle('phishingDetection/urlPishDect/model/bestmodel.gz','phishingDetection/urlPishDect/model/bestmodel.pkl')


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



def predictionURLS( urls=[]):
    
    warnings.filterwarnings("ignore", category=UserWarning, message="Trying to unpickle estimator.*from version.*when using version.*")  
    decompressFiles()
    obj = PredictionURLS(urls)

    return obj.resultOutput





app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

VALID_API_KEYS = ['aB3x8Yp2qR5sW9tZ']

def verify_api_key(api_key):
    return api_key in VALID_API_KEYS

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/urlpredict', methods=['POST'])
def urlpredict():
    
    url = request.form.get('url', '')
    
    url_result = predictionURLS([url])

    return render_template('index.html', url_result=url_result)




@app.route('/emailpredict', methods=['POST'])
def emailpredict():
    
    email = request.form.get('email', '')
    
    email_result = predictionEmail(email)

    return render_template('index.html', email_result=email_result)






@app.route('/urlpredictExt', methods=['POST'])
def urlpredictExt():

    data = request.json
    url = data.get('url', '')
    api_key = data.get('key', '')
    
    # Check if the API key is valid
    if not verify_api_key(api_key):
        return jsonify({"result": "Invalid API key"})
    
    url_result = predictionURLS([url])

    result = 'Phishing'
    if(url_result[9] == '0'):
        result = 'Safe'

    return {"result": f"Current Url Result: {result}"}

@app.route('/emailpredictExt', methods=['POST'])
def emailpredictExt():

    
    data = request.json
    email = data.get('email', '')
    api_key = data.get('key', '')
    
    # Check if the API key is valid
    if not verify_api_key(api_key):
        return jsonify({"result": "Invalid API key"})    

    email_result = predictionEmail(email)
    
    print(email_result)

    result = 'Phishing'
    if(email_result[0] == 0):
        result = 'Safe'
    # Render the result template with the prediction result
    return {"result": f"Email Result: {result}"}



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
