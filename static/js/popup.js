// popup.js
const base = 'http://192.168.0.106:8080';

const url = base+'/urlpredictExt';
const email = base+'/emailpredictExt';


document.getElementById('customBtn').addEventListener('click', function() {
    var customDetectionDiv = document.getElementById('customDetection');
    if (customDetectionDiv) {
        if (customDetectionDiv.hasAttribute('hidden')) {
            customDetectionDiv.removeAttribute('hidden'); 
            this.textContent = 'Hide custom options'; 
        } else {
            customDetectionDiv.setAttribute('hidden', true);
            this.textContent = 'Show custom options'; 
        }
    }
});



function fetchData(url, dataToSend) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend) 
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server returned non-OK status');
        }
        return response.json();
    })
    .catch(error => {
        
        throw error;  
    });
}


function getUrlResult(urlData)
{
    fetchData(url, urlData)
    .then(data => {
        // Handle the data returned from the server
        document.getElementById('currentTabUrl').textContent = data['result'];
    })
    .catch(error => {
        // Handle error
        document.getElementById('currentTabUrl').textContent = 'Error: ' + error.message;
    });
}


function getEmailResult(emailData)
{
    fetchData(email, emailData)
    .then(data => {
        document.getElementById('currentEmail').textContent = data['result'];
    })
    .catch(error => {
        // Handle error
        document.getElementById('currentEmail').textContent = 'Error: ' + error.message;
    });
}

function urlCheck(tabs)
{
    
    var currentTab = tabs[0];
    var currentTabUrl = currentTab.url;
    submitButtonUrl = document.getElementById('submitUrl');
    submitButtonEmail = document.getElementById('submitEmail');
    let urlData = { 'url':currentTabUrl };

    document.getElementById('currentPageink').textContent = currentTabUrl.substring(0, 25)+"...";

    getUrlResult(urlData)


    submitButtonUrl.addEventListener('click', function() {
        const link = urlInput.value.trim(); // Get the URL value and trim whitespace
        
        let urlData = { 'url':link };
        
        document.getElementById('currentTabUrl').textContent = 'Checking Url';
    
        getUrlResult(urlData)
    });

    submitButtonEmail.addEventListener('click', function() {

        var mail =  document.getElementById('emailInput').value;
        
        let emailData = { 'email':mail };
        
        document.getElementById('currentEmail').textContent = 'Checking Email';
    
        getEmailResult(emailData);
        
    });
}


function getEmailHeader(results) {
        
    var message = document.getElementById('emailHeader');
    var bodyHTML =results[0].result
    var parser = new DOMParser();
    var bodyDOM = parser.parseFromString(bodyHTML, 'text/html');
    var emailHeader = bodyDOM.querySelector('#raw_message_text');
    
    document.getElementById('emailInput').value = emailHeader.innerText;

    
    var match = emailHeader.innerText.match(/From:.*?(?=>)/);
    message.innerText =match+">";
    let emailData = { 'email':emailHeader.innerText };
    getEmailResult(emailData);

}


function DOMtoString(selector) {
    if (selector) {
        selector = document.querySelector(selector);
        if (!selector) return "ERROR: querySelector failed to find node";
    } else {
        selector = document.documentElement;
    }
    return selector.outerHTML;
}


function emailCheck(tabs)
{
    var message = document.getElementById('currentEmail');
    var activeTab = tabs[0];
    var activeTabId = activeTab.id;
    
    chrome.scripting.executeScript({
        target: { tabId: activeTabId },
        func: DOMtoString,
        args: ['body']
    }).then(getEmailHeader).catch(function (error) {
        message.innerText = 'Navigate to email header page';
    });
}

function main() {
    

    chrome.tabs.query({ active: true, currentWindow: true }).then(function (tabs) {
 
        urlCheck(tabs)
        emailCheck(tabs)

    })
}



// void Main()
window.onload = main;


