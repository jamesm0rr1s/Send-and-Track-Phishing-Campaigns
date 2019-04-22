# Send and Track Phishing Campaigns (PhishSend)

PhishSend is a penetration testing and red teaming tool that automates the process of sending phishing emails and tracking unique links that are clicked. These scripts were tested with Python 2.7

## Installation

Clone the GitHub repository
```
git clone https://github.com/jamesm0rr1s/Send-and-Track-Phishing-Campaigns /opt/jamesm0rr1s/Send-and-Track-Phishing-Campaigns
```

## Usage

 - Update the "config.ini" configuration file
 - Add email addresses to the "emailAddresses.txt" file
 - Add an HTML message to the "messageHtml.txt" file. (Leave the placeholders "phishing_domain" and "tracking_id" as the script will replace the phishing domain with the value from the "config.ini" configuration file and unique IDs are created based off the email addresses.)
 - (Optional) Add a plain text message to the "messagePlain.txt" file
 - Start the phishing campaign with the following command:
```
python /opt/jamesm0rr1s/Send-and-Track-Phishing-Campaigns/sendPhishingEmails.py
```

## Viewing Phishing Logs

Check for phishing clicks with the following command:
```
python /opt/jamesm0rr1s/Send-and-Track-Phishing-Campaigns/getPhishingLogs.py
```

## Example Screenshots

Campaign Details from "sendPhishingEmails.py"
![ExampleOutput-sendPhishingEmails.py](screenshot1.png?raw=true "ExampleOutput-sendPhishingEmails.py")

Email Details from "sendPhishingEmails.py"
![ExampleOutput-sendPhishingEmails.py](screenshot2.png?raw=true "ExampleOutput-sendPhishingEmails.py")

Click Details from "getPhishingLogs.py"
![ExampleOutput-getPhishingLogs.py](screenshot3.png?raw=true "ExampleOutput-getPhishingLogs.py")
