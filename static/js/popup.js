// popup.js
// const base = 'https://phishing-detection-via-ml-654532c3f1f5.herokuapp.com/';
const base = 'http://192.168.0.102:5000';

const apiKey = 'aB3x8Yp2qR5sW9tZ';

const url = base+'/urlpredictExt';
const email = base+'/emailpredictExt';


// InitState Tab
document.getElementById("urlsTab").addEventListener("click", function() {
    openTab(0);
  });

document.getElementById("emailTab").addEventListener("click", function() {
    openTab(1);
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

function onUrlBtnClick() {
    const link = urlInput.value.trim(); // Get the URL value and trim whitespace
    
    var pattern = /^(http|https):\/\/[^ "]+$/;

    if(pattern.test(link)) {

        let urlData = { 'url':link, 'key':apiKey };
        document.getElementById('currentTabUrl').textContent = 'Checking Url';
        getUrlResult(urlData);
    } 
    else{
        alert('Invalid URL entered. Please enter a valid URL.');
    }
    
}


function onEmailBtnClick(){

    var selectElement = document.getElementById("selectOption");
    var selectedIndex = selectElement.selectedIndex;
    var selectedOption = selectElement.options[selectedIndex];
    var selectedValue = selectedOption.value;
    let urlData = { 'url':selectedValue, 'key':apiKey };
    
    document.getElementById('currentEmail').textContent = 'Checking Url';

    getUrlResult(urlData,'currentEmail');    
}


function getUrlResult(urlData,currentResult="currentTabUrl") {
    fetchData(url, urlData)
    .then(data => {
        // Handle the data returned from the server
        var currentTabUrl = document.getElementById(currentResult);
        currentTabUrl.textContent = data['result'];
        

        if (data['result'].includes('Safe')) {
            currentTabUrl.style.backgroundColor = "#006666";
            
        } else {
            currentTabUrl.style.backgroundColor = "#993333";
         }
    })
    .catch(error => {
        // Handle error
        document.getElementById(currentResult).textContent = 'Error: ' + error.message;
        
    });
}


function getEmailResult(emailData) {
    fetchData(email, emailData)
    .then(data => {
        var currentEmail =document.getElementById('currentEmail')
        currentEmail.textContent = data['result'];
        
        if (data['result'].includes('Safe')) {
            currentEmail.style.backgroundColor = "#006666";
        } else {
            currentEmail.style.backgroundColor = "#993333";
         }
    })
    .catch(error => {
        // Handle error
        document.getElementById('currentEmail').textContent = 'Error: ' + error.message;
    });
}

function urlCheck(tabs) {
    
    var currentTab = tabs[0];
    var currentTabUrl = currentTab.url;
    var submitButtonUrl = document.getElementById('submitUrl');
    let urlData = { 'url':currentTabUrl, 'key':apiKey};

    document.getElementById('currentPageink').textContent = currentTabUrl.substring(0, 25)+"...";
    getUrlResult(urlData)


    submitButtonUrl.addEventListener('click', onUrlBtnClick);
}


function getEmailHeader(results) {
        
    var message = document.getElementById('emailHeader');
    var submitButtonEmail = document.getElementById('submitEmail');
    var bodyHTML =results[0].result
    var parser = new DOMParser();
    var bodyDOM = parser.parseFromString(bodyHTML, 'text/html');
    var emailHeader = bodyDOM.querySelector('#raw_message_text');
    var selectOption = document.getElementById("selectOption")
    var match = emailHeader.innerText.match(/From:.*?(?=>)/);
    var urlRegex = /(https?:\/\/[^\s]+)/gi;
    var matches = emailHeader.innerText.match(urlRegex);
    var submitEmail = document.getElementById('submitEmail');
    let emailData = { 'email':emailHeader.innerText , 'key':apiKey};

    submitEmail.hidden = false;
    selectOption.innerHTML="";
    message.innerText =match+">";
    getEmailResult(emailData);

    if (matches) {
        matches.forEach(function(url) {
            var option = document.createElement("option");
            option.innerText = url.substring(0, 20)+"..";
            option.value = url;
            selectOption.appendChild(option);
        });
    }

    submitButtonEmail.addEventListener('click', onEmailBtnClick);
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


function emailCheck(tabs) {
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


function openTab(evt) {
    // Hide all tab contents
    
    var urlBtn = document.getElementById("urlsTab");
    var emailBtn = document.getElementById("emailTab");
    var emailTab = document.getElementById("Email");
    var urlTab = document.getElementById("URLs");

    if(evt === 0) {
        emailBtn.classList.remove("active");
        urlBtn.classList.add("active");
        emailTab.hidden = true;
        urlTab.hidden = false;
        chrome.tabs.query({ active: true, currentWindow: true }).then(function (tabs) {
            urlCheck(tabs)
        })
    }
    else if(evt === 1) {
        urlBtn.classList.remove("active");
        emailBtn.classList.add("active");
        urlTab.hidden = true;
        emailTab.hidden = false;
        chrome.tabs.query({ active: true, currentWindow: true }).then(function (tabs) {
            emailCheck(tabs)    
        })
    }
    
}
  

function main() {
    openTab(0)
}



// void Main()
window.onload = main;