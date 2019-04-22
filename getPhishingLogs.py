import base64
import ConfigParser
import csv
import os
import re
import string
import time

# Write data to a csv
def write_csv(fileName, editType, data):

        # Open the file
        with open(fileName, editType) as csvFile:

                # Create the csv writer
                csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # Write the row to the file
                csvWriter.writerow(data)

# Set filenames
outputFilesDirectory = "logs"
configFileName = "config.ini"
uniqueIdFileName = outputFilesDirectory + "/" + "UniqueIds.csv"
clicksFileName = outputFilesDirectory + "/" + "Clicks.csv"
logFileName = "/var/log/apache2/access.log"

# Check if the output directory does not exist
if not os.path.exists(outputFilesDirectory):

        # Create the output directory
        os.makedirs(outputFilesDirectory)

##### Config - Start #####
        
config = ConfigParser.ConfigParser()
config.read(configFileName)

_tokenForLogParsing = config.get("Settings", "token_for_log_parsing")

_encrypt = config.get("Settings", "encrypt")
_encode = config.get("Settings", "encode")

_alphabet = config.get("Settings", "alphabet")
_encoding = config.get("Settings", "encoding")

##### Config - End #####

# Create the regex to match the logs
regex = '([(:\d\.)]+) (-) (.*) \[(.*?)\] \"(.*?) (.*?) (.*?)\" (\d+) (.*) \"(.*?)\" \"(.*?)\"'

# Create the unique ID file header
uniqueIdFileHeader = ["ID", "Value"]

# Create clicks file header
clicksFileHeader = ["IP Address", "Internal Identity", "User ID", "Timestamp", "Method", "Resource", "Protocol", "Status", "Size", "Referer", "User-Agent", "Unique ID", "ID Value"]

# Write the header to the unique ID file
write_csv(uniqueIdFileName, "wb", uniqueIdFileHeader)

# Write the header to the clicks file
write_csv(clicksFileName, "wb", clicksFileHeader)

# Open the log file
logFile = open(logFileName, "r")

# Loop through the logs
for line in logFile:

        # Try to get the regex match
	regexMatch = re.match(regex, line)

        # Check if there were regex results
	if regexMatch != None:

		# Check if the line matches the token for log parsing
		if _tokenForLogParsing in regexMatch.groups()[5]:

                        # Get the unique ID
			uniqueId = line.split("?id=")[1]
			uniqueId = uniqueId.split(" ")[0]

                        # Set the unique ID
			uniqueLinkId = uniqueId

			# Check if the unique ID is encoded
			if(_encode == "True"):

                                # Check the length of the ID
				paddingMissing = len(uniqueLinkId) % 4

                                # Check if the padding is missing
				if paddingMissing != 0:

                                        # Add padding
					uniqueLinkId += b'=' * (4 - paddingMissing)

                                # Decode the unique ID
				encryptedUniqueLinkId = base64.urlsafe_b64decode(uniqueLinkId)

                        # Unique ID is not encoded
			else:

                                # No changes to the unique ID
				encryptedUniqueLinkId = uniqueLinkId

			# Check if the unique ID is encrypted
			if(_encrypt == "True"):

                                # Decrypt the ID
				transTable = string.maketrans(_encoding, _alphabet)
				idValue = encryptedUniqueLinkId.translate(transTable)

                        # Unique ID is not encrypted
			else:

                                # No changes to the unique ID
				idValue = encryptedUniqueLinkId

                        # Print the ID and value
			print(uniqueId + ", " + idValue)

                        # Write to the unique ID file
                        write_csv(uniqueIdFileName, "ab", [uniqueId, idValue])

                        # Write to the clicks file
                        write_csv(clicksFileName, "ab", [regexMatch.groups()[0], regexMatch.groups()[1], regexMatch.groups()[2], regexMatch.groups()[3], regexMatch.groups()[4], regexMatch.groups()[5], regexMatch.groups()[6], regexMatch.groups()[7], regexMatch.groups()[8], regexMatch.groups()[9], regexMatch.groups()[10], uniqueId, idValue])

# Set to True to keep looking for clicks
keepLookingForCicks = False

# Check to keep looking for clicks
if(keepLookingForCicks == True):

        # Keep waiting for more lines
        while True:

                # Read the line
                line = logFile.readline()

                # Check if there is data
                if line:

                        # Print the data
                        print(line.strip())

                # Sleep for one second
                time.sleep(1)

# Done
else:

        # Close the file
        logFile.close()
