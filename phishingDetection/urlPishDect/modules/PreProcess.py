import ipaddress
import re
import urllib.request
from bs4 import BeautifulSoup
import socket
import requests
from googlesearch import search
import whois
import pandas as pd
from datetime import date
from urllib.parse import urlparse
import numpy as np
import pandas as pd
import os
import numpy as np

class PreProcessURLS:

    url = ""
    domain = ""
    whois_response = ""
    urlparse = ""
    response = ""
    soup = ""
     

    def appendFeature(self,link,label = None):

        self.url = link
        
        if not re.match(r'^https?://', self.url):
            self.url = 'http://' + self.url

        try:
            self.response = requests.get(self.url)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            pass

        try:
            
            self.urlparse = urlparse(self.url)
            self.domain = self.urlparse.netloc
        except:
            pass

        try:
            self.whois_response = whois.whois(self.domain)
        except:
            pass
        
        curentF=[]
        curentF.append(self.getDomain())
        curentF.append(self.usingIp())
        curentF.append(self.longUrl())
        curentF.append(self.shortUrl())
        curentF.append(self.symbol())
        curentF.append(self.redirecting())
        curentF.append(self.prefixSuffix())
        curentF.append(self.subDomains())
        curentF.append(self.hppts())
        curentF.append(self.domainRegLen())
        curentF.append(self.favicon())

        curentF.append(self.nonStdPort())
        curentF.append(self.hTTPSDomainURL())
        curentF.append(self.requestURL())
        curentF.append(self.anchorURL())
        curentF.append(self.linksInScriptTags())
        curentF.append(self.serverFormHandler())
        curentF.append(self.infoEmail())
        curentF.append(self.abnormalURL())
        curentF.append(self.websiteForwarding())
        curentF.append(self.statusBarCust())
        curentF.append(self.getDepth())

        curentF.append(self.disableRightClick())
        curentF.append(self.usingPopupWindow())
        curentF.append(self.iframeRedirection())
        curentF.append(self.ageofDomain())
        curentF.append(self.dnsRecording())
        curentF.append(self.googleIndex())
        curentF.append(self.linksPointingToPage())
        curentF.append(self.statsReport())
        
        if label is not  None :
            curentF.append(label)

        # self.write_features_to_csv(fileName,curentF)
        
        return curentF
        


    def write_features_to_csv(self, new_data,filename):


        # if(len(self.features)> 0):
            # Ensure 'labels' is included in the feature_names list
        feature_names = [
            "getDomain", "UsingIp", "longUrl", "shortUrl", "symbol", "redirecting",
            "prefixSuffix", "SubDomains", "Hppts", "DomainRegLen", "Favicon",
            "NonStdPort", "HTTPSDomainURL", "RequestURL", "AnchorURL", "LinksInScriptTags",
            "ServerFormHandler", "InfoEmail", "AbnormalURL", "WebsiteForwarding", "StatusBarCust",
            "getDepth", "DisableRightClick", "UsingPopupWindow", "IframeRedirection", "AgeofDomain",
            "DNSRecording", "GoogleIndex", "LinksPointingToPage",
            "StatsReport", "labels"]
    
        try:
            existing_df = pd.read_csv(filename)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=feature_names)

        new_df = pd.DataFrame(new_data, columns=feature_names)

        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Write combined DataFrame to CSV file
        combined_df.to_csv(filename, index=False)

            # self.features = []
                
            
            


    # 0. Domain of the URL (Domain)
    def getDomain(self):
         
        if re.match(r"^www.", self.domain):
            return self.domain.replace("www.", "")
        return self.domain
     # 1.UsingIp
    
    def usingIp(self):
   
        try:
            ipaddress.ip_address(self.domain)
            return -1  
        except ValueError:
            return 1  


    # 2.longUrl
    def longUrl(self):
        if len(self.url) < 54:
            return 1
        if 54 <= len(self.url) <= 75:
            return 0
        return -1

    # 3.shortUrl
    def shortUrl(self):
        match = re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                    'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                    'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                    'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                    'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                    'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                    'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net', self.url)
        if match:
            return -1
        return 1

    # 4.Symbol@
    def symbol(self):
        if re.findall("@",self.url):
            return -1
        return 1
    
    # 5.Redirecting
    def redirecting(self):
        pos = self.url.rfind('//')
        if pos > 6:
            if pos > 7:
                return -1
            else:
                return 0
        else:
            return 1

    
    # 6.prefixSuffix
    def prefixSuffix(self):
        try:
            match = re.findall('\-', self.domain)
            if match:
                return -1
            return 1
        except:
            return -2
    
    # 7.SubDomains
    def subDomains(self):
        dot_count = len(re.findall("\.", self.url))
        if dot_count == 1:
            return 1
        elif dot_count == 2:
            return 0
        return -1

    # 8.HTTPS
    def hppts(self):
        try:
            https = self.urlparse.scheme
            if 'https' in https:
                return 1
            return -1
        except:
            return -2

    # 9.DomainRegLen
    def domainRegLen(self):
        try:
            expiration_date = self.whois_response.expiration_date
            creation_date = self.whois_response.creation_date
            try:
                if(len(expiration_date)):
                    expiration_date = expiration_date[0]
            except:
                pass
            try:
                if(len(creation_date)):
                    creation_date = creation_date[0]
            except:
                pass

            age = (expiration_date.year-creation_date.year)*12+ (expiration_date.month-creation_date.month)
            if age >=12:
                return 1
            return -1
        except:
            return -2

    # 10. Favicon
    def favicon(self):
        try:
            for head in self.soup.find_all('head'):
                for head.link in self.soup.find_all('link', href=True):
                    dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                    if self.url in head.link['href'] or len(dots) == 1 or self.domain in head.link['href']:
                        return 1
            return -1
        except:
            return -2

    # 11. NonStdPort
    def nonStdPort(self):
        try:
            port = self.domain.split(":")
            if len(port)>1:
                return -1
            return 1
        except:
            return -2

    # 12. HTTPSDomainURL
    def hTTPSDomainURL(self):
        try:
            if 'https' in self.domain:
                return -1
            return 1
        except:
            return -2
    
    # 13. RequestURL
    def requestURL(self):
        try:
            for img in self.soup.find_all('img', src=True):
                dots = [x.start(0) for x in re.finditer('\.', img['src'])]
                if self.url in img['src'] or self.domain in img['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for audio in self.soup.find_all('audio', src=True):
                dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
                if self.url in audio['src'] or self.domain in audio['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for embed in self.soup.find_all('embed', src=True):
                dots = [x.start(0) for x in re.finditer('\.', embed['src'])]
                if self.url in embed['src'] or self.domain in embed['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for iframe in self.soup.find_all('iframe', src=True):
                dots = [x.start(0) for x in re.finditer('\.', iframe['src'])]
                if self.url in iframe['src'] or self.domain in iframe['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            try:
                percentage = success/float(i) * 100
                if percentage < 22.0:
                    return 1
                elif((percentage >= 22.0) and (percentage < 61.0)):
                    return 0
                else:
                    return -1
            except:
                return 0
        except:
            return -2
    
    # 14. AnchorURL
    def anchorURL(self):
        try:
            i,unsafe = 0,0
            for a in self.soup.find_all('a', href=True):
                if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (self.url in a['href'] or self.domain in a['href']):
                    unsafe = unsafe + 1
                i = i + 1

            try:
                percentage = unsafe / float(i) * 100
                if percentage < 31.0:
                    return 1
                elif ((percentage >= 31.0) and (percentage < 67.0)):
                    return 0
                else:
                    return -1
            except:
                return -1

        except:
            return -2

    # 15. LinksInScriptTags
    def linksInScriptTags(self):
        try:
            i,success = 0,0
        
            for link in self.soup.find_all('link', href=True):
                dots = [x.start(0) for x in re.finditer('\.', link['href'])]
                if self.url in link['href'] or self.domain in link['href'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            for script in self.soup.find_all('script', src=True):
                dots = [x.start(0) for x in re.finditer('\.', script['src'])]
                if self.url in script['src'] or self.domain in script['src'] or len(dots) == 1:
                    success = success + 1
                i = i+1

            try:
                percentage = success / float(i) * 100
                if percentage < 17.0:
                    return 1
                elif((percentage >= 17.0) and (percentage < 81.0)):
                    return 0
                else:
                    return -1
            except:
                return 0
        except:
            return -2

    # 16. ServerFormHandler
    def serverFormHandler(self):
        try:
            if len(self.soup.find_all('form', action=True))==0:
                return 1
            else :
                for form in self.soup.find_all('form', action=True):
                    if form['action'] == "" or form['action'] == "about:blank":
                        return -1
                    elif self.url not in form['action'] and self.domain not in form['action']:
                        return 0
                    else:
                        return 1
        except:
            return -2

    # 17. InfoEmail
    def infoEmail(self):
            try:
                if re.search(r"mail\(\)|mailto:?", str(self.soup)):

                    return -1
                else:
                    return 1
            except:
                return -2


    # 18. AbnormalURL
    def abnormalURL(self):
        try:
            if self.response.text == self.whois_response:
                return 1
            else:
                return -1
        except:
            return -2

    # 19. WebsiteForwarding
    def websiteForwarding(self):
        try:
            if len(self.response.history) <= 1:
                return 1
            elif len(self.response.history) <= 4:
                return 0
            else:
                return -1
        except:
             return -2

    # 20. StatusBarCust
    def statusBarCust(self):
        try:
            if re.findall("<script>.+onmouseover.+</script>", self.response.text):
                return 1
            else:
                return -1
        except:
             return -2

    # 21. DisableRightClick
    def disableRightClick(self):
        try:
            if re.search(r"(event\.button ?== ?2)|(contextmenu)", self.response.text, re.IGNORECASE):
                return 1
            else:
                return -1
        except:
             return -2

    # 22. UsingPopupWindow
    def usingPopupWindow(self):
        try:
            if re.findall(r"alert\(", self.response.text):
                return 1
            else:
                return -1
        except:
             return -2

    # 23. IframeRedirection
    def iframeRedirection(self):
        try:
            if re.findall(r"<iframe|frameBorder", self.response.text,re.IGNORECASE):
                return 1
            else:
                return -1
        except:
             return -2

    # 24. AgeofDomain
    def ageofDomain(self):
        try:
            creation_date = self.whois_response.creation_date
            try:
                if(len(creation_date)):
                    creation_date = creation_date[0]
            except:
                pass

            today  = date.today()
            age = (today.year-creation_date.year)*12+(today.month-creation_date.month)
            if age >=6:
                return 1
            return -1
        except:
            return -2

    # 25. DNSRecording    
    def dnsRecording(self):
        try:
            creation_date = self.whois_response.creation_date
            try:
                if(len(creation_date)):
                    creation_date = creation_date[0]
            except:
                pass

            today  = date.today()
            age = (today.year-creation_date.year)*12+(today.month-creation_date.month)
            if age >=6:
                return 1
            return -1
        except:
            return -2

    # 26. WebsiteTraffic   
    def websiteTraffic(self):
        try:
            rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + self.url).read(), "xml").find("REACH")['RANK']
            if (int(rank) < 100000):
                return 1
            return 0
        except :
            return -2

    # 27. PageRank
    def pageRank(self):
        try:
            prank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {"name": self.domain})

            global_rank = int(re.findall(r"Global Rank: ([0-9]+)", prank_checker_response.text)[0])
            if global_rank > 0 and global_rank < 100000:
                return 1
            return -1
        except:
            return -2
            

    # 28. GoogleIndex
    def googleIndex(self):
        try:
            site = search(self.url, 5)
            if site:
                return 1
            else:
                return -1
        except:
            return 1

    # 29. LinksPointingToPage
    def linksPointingToPage(self):
        try:
            number_of_links = len(re.findall(r"<a href=", self.response.text))
            if number_of_links == 0:
                return 1
            elif number_of_links <= 2:
                return 0
            else:
                return -1
        except:
            return -2

    # 30. StatsReport
    def statsReport(self):
        try:
            url_match = re.search(
        'at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly', self.url)
            ip_address = socket.gethostbyname(self.domain)
            ip_match = re.search('146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
                                '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
                                '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
                                '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
                                '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
                                '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42', ip_address)
            if url_match:
                return -1
            elif ip_match:
                return -1
            return 1
        except:
            return 1
        
    def getDepth(self):
    # Parse the URL
        parsed_url = urlparse(self.url)

        # Split the path and remove empty components
        path_components = [comp for comp in parsed_url.path.split('/') if comp]

        # Calculate depth
        depth = len(path_components)

        return depth
        
    def getFeaturesList(self):
        return self.features
    
    
    # def mergeFiles(self,folder_path = 'output/',merged_file_path = 'dataset/preProcessed.csv' ):

    #     dfs = []

    #     for file_name in os.listdir(folder_path):
        
    #         if file_name.endswith('.csv'):
        
    #             file_path = os.path.join(folder_path, file_name)
    #             df = pd.read_csv(file_path)
        
    #             dfs.append(df)
        
    #     merged_df = pd.concat(dfs, ignore_index=True)
    #     merged_df.to_csv(merged_file_path, index=False)
    #     print("Merging complete. Merged file saved as:", merged_file_path)


    def mergeFiles(self, folder_path='output/', merged_file_path='dataset/preProcessed.csv'):
        # Check if the merged file exists
        if os.path.exists(merged_file_path):
            # If the merged file exists, append to it
            mode = 'a'
            header = False  # Do not write header again
        else:
            # If the merged file doesn't exist, create it
            mode = 'w'
            header = True  # Write header for the first time
        
        dfs = []

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_csv(file_path)
                dfs.append(df)
        
        merged_df = pd.concat(dfs, ignore_index=True)
        merged_df.to_csv(merged_file_path, mode=mode, index=False, header=header)
        print("Merging complete. Merged file saved as:", merged_file_path)


    def deleteFilesInDirectory(self,directory):
        # Iterate over all files in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Check if the path points to a file
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)


    def getBalancedDataframe(self,name="malicious_phish.csv"):

        df = pd.read_csv(name)

        # Filter out rows where 'type' is 'defacement'
        df = df[df['label'] != 'defacement']

        # Label benign = 0, others 1
        df['label'] = np.where(df['label'] == "benign", 0, 1)

        df = df.sample(frac=1).sample(frac=1).reset_index(drop=True)

        label_0_data = df[df['label'] == 0]
        label_1_data = df[df['label'] == 1]

        # Calculate the desired ratio
        desired_ratio = 1.5
        num_label_1 = len(label_1_data)
        num_label_0_to_keep = int(num_label_1 * desired_ratio)

        label_0_data_sampled = label_0_data.sample(n=num_label_0_to_keep, random_state=42)

        balanced_df = pd.concat([label_0_data_sampled, label_1_data])

        # Shuffle the DataFrame to mix the rows
        df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)


        return df
    
    def correlation(self,filename = "merged_file.csv"):

        df = pd.read_csv(filename)

        # Drop the 'getDomain' column
        df.drop('getDomain', axis=1, inplace=True)

        # Calculate correlation with labels
        correlation_with_label = df.corrwith(df['labels'])

        print(correlation_with_label)

