from phishingDetection.urlPishDect.modules.Prediction import PredictionURLS
from phishingDetection.emailPishDect.modules.FeatureExtractionEmail import FeatureExtractionEmail
from flask_cors import CORS
from flask import Flask,render_template, request,jsonify

import warnings
import joblib
import os


def loadPredict(predict):
    
    loaded_model = joblib.load('phishingDetection/emailPishDect/model/best_model.pkl')
    label = loaded_model.predict(predict)

    return label


def predictionEmail(email_content):
        
    obj=FeatureExtractionEmail(email_content)
    df = obj.df
    prad = loadPredict(df)
    
    return prad



def predictionURLS( urls=[]):
    
    warnings.filterwarnings("ignore", category=UserWarning, message="Trying to unpickle estimator.*from version.*when using version.*")  

    obj = PredictionURLS(urls)

    return obj.resultOutput





app = Flask(__name__)
CORS(app)  # Enable CORS for all routes



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/urlpredict', methods=['POST'])
def urlpredict():
    
    url = request.form.get('url', '')
    
    url_result = predictionURLS([url])

    # Render the result template with the prediction result
    return render_template('index.html', url_result=url_result)




@app.route('/emailpredict', methods=['POST'])
def emailpredict():
    
    email = request.form.get('email', '')
    
    email_result = predictionEmail(email)

    # Render the result template with the prediction result
    return render_template('index.html', email_result=email_result)





@app.route('/urlpredictExt', methods=['POST'])
def urlpredictExt():
    
    data = request.json
    url = data.get('url', '')
    
    url_result = predictionURLS([url])

    result = 'Phishing'
    if(url_result[9] == '0'):
        result = 'Safe'

    return {"result": f"Current Url Result: {result}"}

@app.route('/emailpredictExt', methods=['POST'])
def emailpredictExt():
    
    data = request.json
    email = data.get('email', '')
    

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