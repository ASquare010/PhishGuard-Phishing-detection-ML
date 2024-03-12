// // background.js

// // Wait for the extension to be fully loaded and Chrome APIs to be available
// chrome.runtime.onInstalled.addListener(function() {
//     // Add a listener for clicks on the browser action
//     chrome.browserAction.onClicked.addListener(function(tab) {
//       // Send a message to the content script to retrieve HTML content
//       chrome.tabs.sendMessage(tab.id, { action: "getHTMLContent" }, function(response) {
//         // Handle the HTML content received from the content script
//         if (response && response.htmlContent) {
//           console.log("HTML content of the webpage:", response.htmlContent);
//         } else {
//           console.error("Failed to retrieve HTML content from the webpage.");
//         }
//       });
//     });
//   });
  