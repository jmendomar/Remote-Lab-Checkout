import json
import os
import smtplib
import sys
import datetime as dt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from colorama import Fore, Style
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Table
from cryptography.fernet import Fernet

def decryptConfig():
    # Loads the encryption key from file
    with open('Assets\\encryption_key.key', 'rb') as key_file:
        key = key_file.read()
        print(f"{Fore.GREEN}[{datetime.now()}]: decryptConfig : Encryption Key loaded{Style.RESET_ALL}")
    
    # Decrypts the JSON file
    with open("config.json", 'rb') as file:
        encrypted_data = file.read()

    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data

def sqlEngine():
    print(f"{Fore.YELLOW}[{datetime.now()}]: Starting Connection to {dbName}{Style.RESET_ALL}")    
    db_connection_str = 'mysql+mysqlconnector://{0}:{1}@{2}:{4}/{3}'.format(userName,userPassword,dbHostName,dbName,dbPort)
    try:
        print(f"{Fore.GREEN}[{datetime.now()}]: sqlEngine : Connected to {dbName}{Style.RESET_ALL}")
        return (create_engine(db_connection_str))
    except Exception as e:
        print(f"{Fore.RED}[{datetime.now()}]: Failed to Connect to {dbName} : {e}{Style.RESET_ALL}")
        sys.exit()

#loads file with credentials
def loadEncryptedConfig(decryptedData):
    data = json.loads(decryptedData)
    print(f"{Fore.GREEN}[{datetime.now()}]: loadEncryptedConfig : Encryption Key decrypted{Style.RESET_ALL}")
    return data

def loadDbEntries():
    entryData = engine.execute(query)

    for row in entryData:
        print(f"{Fore.GREEN}[{datetime.now()}]: loadDbEntries : Entry found : {row}{Style.RESET_ALL}")
        column_value = row['user']
        userList[column_value] = None

def loadUserEmails():
    for user in userList:
        queryEmail = f"SELECT * FROM remote_lab_inv_users WHERE idsid = '{user}';"
        emailData = engine.execute(queryEmail)

        for email in emailData:
            print(f"{Fore.GREEN}[{datetime.now()}]: loadUserEmails : Email Found : {email}{Style.RESET_ALL}")
            column_value = email['email']
            emailList[user] = column_value

def lookForOverdue():
    for user in userList:
        query = "SELECT * FROM remote_lab_inventory WHERE DATE(dueDate) IS NOT NULL;"
        unitData = engine.execute(query)

        for unit in unitData:
            columnId = unit['id']
            columnUser = unit['user']
            columnDueDate = unit['dueDate']
            
            naughtyList[columnId] = {
                'user': columnUser,
                'dueDate': columnDueDate
            }

def preCheckAndPrepare():
    for item in naughtyList:
        userProfile = naughtyList[item]
        currUserDueDate = userProfile['dueDate']
        currDate = str(dt.date.today())
        currUser = userProfile['user']
        userEmail = emailList[currUser]

        if currUserDueDate <= currDate:
            print(f"{Fore.RED}[{datetime.now()}]: preCheckAndPrepare : User {currUser} has unit {item} Past Due{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[{datetime.now()}]: preCheckAndPrepare : Sending email to {currUser} at {userEmail}{Style.RESET_ALL}")
            sendEmail(userEmail, currUser, item)
        else:
            print(f"{Fore.CYAN}[{datetime.now()}]: preCheckAndPrepare : User {currUser} has unit {item} unit not due{Style.RESET_ALL}")

def sendEmail(receiver, user, unit):
    sender = "gcs_remote_lab_fl@intel.com"
    subject = "NUC Checkout(Do not Reply!!!)"
    message = f"Hello {user},\nNuc unit with ID: {unit} is due today or past due please extend or return the unit.\n If this is a mistake please contact jesusi2x @ jesusx.isaac.mendoza.martinez@intel.com "

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    smtp_server = headlessServer
    smtp_port = 587

    try:
        smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
        smtp_obj.starttls()
        smtp_obj.login(sender, headlessPass)
        smtp_obj.sendmail(sender, receiver, msg.as_string())
        print(f"{Fore.GREEN}[{datetime.now()}]: sendEmail : Email sent successfully!{Style.RESET_ALL}")
    except smtplib.SMTPException as e:
        print(f"{Fore.CYAN}[{datetime.now()}]: sendEmail : Error : Unable to send email.{Style.RESET_ALL}")
        print(e)
    finally:
        smtp_obj.quit()

decrypted_config = decryptConfig()
data = loadEncryptedConfig(decrypted_config)

query = "SELECT * FROM remote_lab_inventory WHERE DATE(dueDate) IS NOT NULL;"
today = dt.date.today()
dbHostName = data['dbHost']
dbName = data['dbName']
userName = data['dbUser']
userPassword = data['dbPass']
dbPort = data['dbPort']
headlessPass = data['headlessPass']
headlessServer = data['headlessServer']

emailList = {}
naughtyList = {}
userList = {}

engine = sqlEngine()

# loadDbEntries()
# loadUserEmails()
# lookForOverdue()
loadDbEntries()
loadUserEmails()
lookForOverdue()
preCheckAndPrepare()

