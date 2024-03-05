// popup.js
const base = 'http://192.168.0.102:8080';
const url = base+'/urlpredictExt';
const email = base+'/emailpredictExt';

document.addEventListener('DOMContentLoaded', function() {

    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) 
    {        
        main(tabs)
    });

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





function main(tabs){
    
    var currentTab = tabs[0];
    var currentTabUrl = currentTab.url;
    submitButtonUrl = document.getElementById('submitUrl');
    submitButtonEmail = document.getElementById('submitEmail');
    let urlData = { 'url':currentTabUrl };


    fetchData(url, urlData)
    .then(data => {
        // Handle the data returned from the server
        document.getElementById('currentTabUrl').textContent = data['result'];
    })
    .catch(error => {
        // Handle error
        document.getElementById('currentTabUrl').textContent = 'Error: ' + error.message;
    });




    submitButtonUrl.addEventListener('click', function() {
        const link = urlInput.value.trim(); // Get the URL value and trim whitespace
        
        let urlData = { 'url':link };
        
        document.getElementById('currentTabUrl').textContent = 'Checking Url';
    
        if (url !== '') {
            
            fetchData(url, urlData)
            .then(data => {
                document.getElementById('currentTabUrl').textContent = data['result'];
            })
            .catch(error => {
                // Handle error
                document.getElementById('currentTabUrl').textContent = 'Error: ' + error.message;
            });
        }
    });

    submitButtonEmail.addEventListener('click', function() {
        const mail = emailInput.value; // Get the URL value and trim whitespace
        
        let emailData = { 'email':mail };
        
        document.getElementById('emailCheck').textContent = 'Checking Email';
    
        if (email !== '') {
            
            fetchData(email, emailData)
            .then(data => {
                document.getElementById('emailCheck').textContent = data['result'];
            })
            .catch(error => {
                // Handle error
                document.getElementById('emailCheck').textContent = 'Error: ' + error.message;
            });
        }
    });
}
