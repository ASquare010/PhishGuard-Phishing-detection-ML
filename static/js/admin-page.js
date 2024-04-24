// const base = 'https://phishing-detection-via-ml-654532c3f1f5.herokuapp.com/';
const base = 'http://192.168.100.102:5000';

const apiKey = 'aB3x8Yp2qR5sW9tZ';

const url = base+'/urlpredict';
const email = base+'/emailpredict';
const train = base+'/train';

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


function getResult(sendData,currentResult="result",reqType="url") {
    var currentTabUrl = document.getElementById(currentResult);
    currentTabUrl.style.color = 'white';
    var link = url;

    if (reqType == "url"){
        link = url
        currentTabUrl.textContent = "Url Checking in progress..";
    }
    else {
        link = email;
        currentTabUrl.textContent = "Email Header Checking in progress..";
    }
    console.log(sendData);
    fetchData(link,sendData)
    .then(data => {
        // Handle the data returned from the server
        currentTabUrl.textContent = data['result'];
        

        if (data['result'].includes('Safe')) {
            currentTabUrl.style.backgroundColor = "#006666";
            
        } else {
            currentTabUrl.style.backgroundColor = "#993333";
         }
    })
    .catch(error => {
        // Handle error
        currentTabUrl.textContent = 'Error: ' + error.message;
        
    });
}


function sendRequest(reqType = "url") {
    var currentTabUrl = document.getElementById("result");
    var val = document.getElementById(reqType);
    let data = { 'data' : val.value};

    currentTabUrl.textContent = reqType+" Traning has Started";

    getResult(data,"result",reqType);
}

function trainModel() {
    var selectElement = document.getElementById("trainModel");
    var selectedValue = selectElement.options[selectElement.selectedIndex].value;
    var currentTabUrl = document.getElementById('result');
    let data = { 'train' : selectedValue};

    fetchData(train,data)
    .then(data=>{currentTabUrl.textContent = data['result'];})
    .catch(error=>{console.log(error)})



}


function main()
{
    document.getElementById("urlBtn").addEventListener("click", function() {
        sendRequest()        
      });
    document.getElementById("emailBtn").addEventListener("click", function() {
        sendRequest("email")        
    });
    document.getElementById("trainBtn").addEventListener("click", function() {
        trainModel()      
    });
}


// void  main
document.addEventListener("DOMContentLoaded", function() {
    // Your code here
    main();
});