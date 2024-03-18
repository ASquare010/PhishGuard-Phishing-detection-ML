from phishingDetection.urlPishDect.modules.PreProcess import PreProcessURLS
import joblib
import pandas as pd

class PredictionURLS: 

        resultOutput = ''

        def __init__(self,urls = [],modelPath = "phishingDetection/urlPishDect/model/bestmodel.pkl"):                

                for url in urls:
                        self.resultOutput = self.resultOutput + self.predictUrl(url,modelPath)


        def preProcess(self,url):

                # Extract features from the URL
                return PreProcessURLS().appendFeature(url)

        def predictUrl(self,url,modelPath = "phishingDetection/urlPishDect/model/bestmodel.pkl"):

                # Load the trained model
                rf = joblib.load(modelPath)

                # Extract features from the URL
                features = self.preProcess(url)

                # Define feature names
                feature_names = [
                "getDomain", "UsingIp", "longUrl", "shortUrl", "symbol", "redirecting",
                "prefixSuffix", "SubDomains", "Hppts", "DomainRegLen", "Favicon",
                "NonStdPort", "HTTPSDomainURL", "RequestURL", "AnchorURL", "LinksInScriptTags",
                "ServerFormHandler", "InfoEmail", "AbnormalURL", "WebsiteForwarding", "StatusBarCust",
                "getDepth", "DisableRightClick", "UsingPopupWindow", "IframeRedirection", "AgeofDomain",
                "DNSRecording", "GoogleIndex", "LinksPointingToPage", "StatsReport"
                ]


                df = pd.DataFrame([features], columns=feature_names)

                df = df.drop(columns=["getDomain"])


                result = rf.predict(df)

                return f'Result: {result}'