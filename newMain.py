import pandas as pd
import json
import tkinter.messagebox as MessageBox
import tkinter as Tk
import sys
from cryptography.fernet import Fernet
from datetime import date, timedelta
from ldap3 import Connection, Server
from mysql.connector.locales.eng import client_error
from tkinter import *
from datetime import datetime
from tkinter import ttk, Canvas, NW, simpledialog
from colorama import Fore, Style
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Table
from tkinter import ttk
from ldap3 import Connection, Server
from PIL import ImageTk, Image

root = Tk()
# root.geometry("1525x900")
root.title("Remote Check Out/In v0.2.5")

wwid = ""
currUser = ""
startDate = date.today()
endDate = startDate + timedelta(days=30)
dateRange = [startDate + timedelta(days=i) for i in range((endDate - startDate).days + 1)]
dateOptions = [d.strftime("%Y-%m-%d") for d in dateRange]
filterOptions = ["id","location","prodName","serialNo","prodStatus","codename","user","status","dueDate"]
filterOptionValue = StringVar()

#Functions
def decryptConfig():
    # Loads the encryption key from file
    with open('Assets\\encryption_key.key', 'rb') as key_file:
        key = key_file.read()
    
    # Decrypts the JSON file
    with open("config.json", 'rb') as file:
        encrypted_data = file.read()

    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data

#loads file with credentials
def loadEncryptedConfig(decryptedData):
    data = json.loads(decryptedData)
    return data
# def loadConfig(file):
#     try:
#         with open(file, 'r') as conf:
#             data = json.load(conf)
#             print(f"{Fore.GREEN}[{datetime.now()}]: Config File loaded{Style.RESET_ALL}")
#             return data
#     except Exception as e:
#         print(f"{Fore.RED}[{datetime.now()}]: Config Error : {e}{Style.RESET_ALL}")
#         sys.exit()

#Created the connection the database
def create_mysqlConnection(dbHostName, dbName, userName, userPassword, dbPort):
    print(f"{Fore.YELLOW}[{datetime.now()}]: Starting Connection to {dbName}{Style.RESET_ALL}")    
    db_connection_str = 'mysql+mysqlconnector://{0}:{1}@{2}:{4}/{3}'.format(userName,userPassword,dbHostName,dbName,dbPort)
    try:
        return (create_engine(db_connection_str))
    except Exception as e:
        print(f"{Fore.RED}[{datetime.now()}]: Failed to Connect to {dbName} : {e}{Style.RESET_ALL}")
        sys.exit()

#Pulls entrys from the database
def pullDataTree():
    print(f"{Fore.GREEN}[{datetime.now()}]: Starting Data pull for Tree 2{Style.RESET_ALL}")
    results = conn.execute("SELECT * FROM remote_lab_inventory")
    
    for row in checkTree.get_children():
        checkTree.delete(row)
        print(f"{Fore.YELLOW}[{datetime.now()}]: Deleted row {row}{Style.RESET_ALL}")
    
    for result in results:
        checkTree.insert('', 'end', text=result, values=(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8]))
        print(f"{Fore.YELLOW}[{datetime.now()}]: Tree : Row Found : {result}{Style.RESET_ALL}")

def onTreeSelectTab2(event):
    selection = checkTree.selection()    
    if len(selection) > 0: 
        item = selection[0]  
        values = checkTree.item(item, 'values')  # Get the values of the columns for the selected item
        print(f"{Fore.YELLOW}[{datetime.now()}]: Tree2 : Selected Entry {item}{Style.RESET_ALL}")

        idLabelDisp.config(text=f"{values[0]}")
        locationLabelDisp.config(text=f"{values[1]}")
        prodNameLabelDisp.config(text=f"{values[2]}")
        serialLabelDisp.config(text=f"{values[3]}")
        prodStatusLabelDisp.config(text=f"{values[4]}")
        codenameLabelDisp.config(text=f"{values[5]}")
        userLabelDisp.config(text=f"{values[6]}")
        statusLabelDisp.config(text=f"{values[7]}")
        if len(values) > 8:
            if values[8] == "":
                dateLabelDisp.config(text="None")
            else:
                dateLabelDisp.config(text=f"{values[8]}")

def onTreeSelectTab3(event):
    selection = checkTree.selection()    
    if len(selection) > 0: 
        item = selection[0]  
        values = checkTree.item(item, 'values')  # Get the values of the columns for the selected item
        print(f"{Fore.GREEN}[{datetime.now()}]: Tree2 : Selected Entry {item}{Style.RESET_ALL}")

        idLabelDisp.config(text=f"{values[0]}")
        locationLabelDisp.config(text=f"{values[1]}")
        prodNameLabelDisp.config(text=f"{values[2]}")
        serialLabelDisp.config(text=f"{values[3]}")
        prodStatusLabelDisp.config(text=f"{values[4]}")
        codenameLabelDisp.config(text=f"{values[5]}")
        userLabelDisp.config(text=f"{values[6]}")
        statusLabelDisp.config(text=f"{values[7]}")
        if len(values) > 8:
            if values[8] == "":
                dateLabelDisp.config(text="None")
            else:
                dateLabelDisp.config(text=f"{values[8]}")

def profileImage():
    pfpImage = ImageTk.PhotoImage(image)

    pfpLabel = Label(pfpFrame, image=pfpImage)

    pfpLabel.image = pfpImage

    pfpLabel.grid(row=0, column=0, padx=5, pady=5)

    root.update_idletasks()

def login():
    loginDialog = Toplevel()

    geoOption = StringVar()


    logUserLabel = Label(loginDialog, text="Intel Username:")
    logUserEntry = Entry(loginDialog)
    logUserLabel.grid(row=0, column=0, padx=5, pady=5)
    logUserEntry.grid(row=0, column=1, padx=5, pady=5)

    logPassLabel = Label(loginDialog, text="Intel Password:")
    logPassEntry = Entry(loginDialog, show="•")
    logPassLabel.grid(row=1, column=0, padx=5, pady=5)
    logPassEntry.grid(row=1, column=1, padx=5, pady=5)

    geoOption.set(geoOptions[0])

    geoLabel = Label(loginDialog, text="Geo Location")
    geoLabel.grid(row=0, column=2, padx=5, pady=5)

    geoSelect = OptionMenu(loginDialog, geoOption, *geoOptions)
    geoSelect.grid(row=1, column=2, padx=5, pady=5)

    def submit():
        user = logUserEntry.get()
        passw = logPassEntry.get()

        geo = geoOption.get()

        loginDialog.destroy()

        server = Server('corpadssl.intel.com')

        userPost = f"{geo}\{user}"  

        try:
            conn = Connection(Server(host="corpadssl.intel.com", port=3269, use_ssl = True), user=userPost, password=passw, raise_exceptions=False, auto_bind=True)
            data = conn.search(search_base='DC=corp,DC=intel,DC=com', search_filter="(&(objectcategory=person)(objectclass=user)(intelflags=1)(sAMAccountName=greenwx))", attributes='memberOf')    
            # data = conn.entries
            print(f"{Fore.GREEN}[{datetime.now()}]: Login : Authenticated {userPost} Succesfully{Style.RESET_ALL}")
            authenticated = True
            loginStage2(authenticated, user)
            usersCheckedOutUnits(user)
        except Exception as e:
            MessageBox.showwarning("Login", e)
            print(e)
            pass

    submitButton = Button(loginDialog, text="Submit", command=submit)
    submitButton.grid(row=3, column=1, padx=5, pady=5)
    loginDialog.bind('<Return>', lambda event: submit())

def loginStage2(authenticated, user):
    userNew = ""
    if authenticated == True:
        print(authenticated)
        searchString = f"SELECT * FROM remote_lab_inv_users WHERE idsid = '{user}';"

        userSearch = conn.execute(searchString)

        data = userSearch.fetchall()

        if data != []:
            for row in data:
                idsid = row[1]
                wwid = row[2]
                name = row[3]
                email = row[4]
        if data == []:
            print(f"{Fore.YELLOW}[{datetime.now()}]: Login Stage 2 : {user} Not in db{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[{datetime.now()}]: Login Stage 2 : Adding {user} to db{Style.RESET_ALL}")
            userInfo = Toplevel()

            logWwidLabel = Label(userInfo, text="Intel WWID:")
            logWwidEntry = Entry(userInfo)
            logWwidLabel.grid(row=0, column=0, padx=5, pady=5)
            logWwidEntry.grid(row=0, column=1, padx=5, pady=5)

            logNameLabel = Label(userInfo, text="Name:")
            logNameEntry = Entry(userInfo)
            logNameLabel.grid(row=1, column=0, padx=5, pady=5)
            logNameEntry.grid(row=1, column=1, padx=5, pady=5)

            logEmailLabel = Label(userInfo, text="Intel Email:")
            logEmailEntry = Entry(userInfo)
            logEmailLabel.grid(row=2, column=0, padx=5, pady=5)
            logEmailEntry.grid(row=2, column=1, padx=5, pady=5)

            def submit():
                wwid = logWwidEntry.get()
                name = logNameEntry.get()
                email = logEmailEntry.get()

                userInfo.destroy()

                server = Server('corpadssl.intel.com')

                userPost = f"amr\{user}"  

                try:
                    createUserInDb(user, wwid, name, email)
                except Exception as e:
                    print(e)
            
            addButton = Button(userInfo, text="Add", command=submit)
            addButton.grid(row=4, column=3, padx=5, pady=5)

        else:
            print(f"{Fore.GREEN}[{datetime.now()}]: Login Stage 2 : {idsid} in db{Style.RESET_ALL}")
            logInLabel.grid_forget()
            logInLabelDynamic(idsid, wwid, name, email)
    else:
        print(f"{Fore.RED}[{datetime.now()}]: Tree2 : Incorrect Credentials{Style.RESET_ALL}")
        pass

def createUserInDb(idsid, wwid, name, email):
    addString = f"INSERT INTO remote_lab_inv_users (id, idsid, wwid, name, email) VALUES (0 , '{idsid}', '{wwid}', '{name}', '{email}')"

    try:
        conn.execute(addString)
        print(f"{Fore.GREEN}[{datetime.now()}]: DB User : {idsid} added to db{Style.RESET_ALL}")
        logInLabel.grid_forget()
        logInLabelDynamic(idsid ,wwid, name, email)
    except Exception as e:
        print(f"{Fore.RED}[{datetime.now()}]: DB User : Error : {e}{Style.RESET_ALL}")

def unitExtension():
    global dateSelection
    global unitSelection
    global dateExtenstion
    unitSelection = userUnitsOutTree.selection()
    dateSelection = StringVar()

    dateSelection.set(dateOptions[0])

    if unitSelection == ():
        MessageBox.showinfo("Unit Extension", "No Unit is selected for extension")
    else:
        dateExtenstion = Toplevel()
        
        extensionLabel = Label(dateExtenstion, text="Extend Check out by")
        extensionLabel.grid(row=0, column=0, padx=5, pady=5)

        dateDroptDown = OptionMenu(dateExtenstion, dateSelection, *dateOptions)
        dateDroptDown.grid(row=1, column=0, padx=5, pady=5)

        extButton = Button(dateExtenstion, text="Extend", command=extendDate)
        extButton.grid(row=2, column=0, padx=5, pady=5)

def extendDate():
    dueDate = dateSelection.get()
    id = unitSelection
    item = id[0] 
    values = userUnitsOutTree.item(item, 'values')  # Get the values of the columns for the selected item
    unitID = values[0] 
    extendString = f"UPDATE `remote_lab_inventory` SET dueDate='{dueDate}' WHERE id={unitID}"

    try:
        conn.execute(extendString)
        pullDataTree()
        usersCheckedOutUnits(currUser)
        dateExtenstion.destroy()
        MessageBox.showinfo("Extension", "Extended")
    except Exception as e:
        MessageBox.showwarning("Extension", e)

def logInLabelDynamic(idsid, wwid, name, email):
    global usernameLabel
    global signOutBtn
    global extensionButton
    global currUser

    currUser = idsid

    usernameLabel = Label(topBarFrame, text=idsid)
    usernameLabel.grid(row=0, column=1, padx=5, pady=5, sticky='e')

    # ldapIDResult.configure(text=id)
    ldapUserResult.configure(text=idsid)
    ldapNameResult.configure(text=name)
    ldapEmailResult.configure(text=email)
    ldapWwidResult.configure(text=wwid)
    unitsLabel.configure(text=f"{currUser}'s Current Units")

    signOutBtn = Button(topBarFrame, text="Sign Out", command=signOutUser)
    signOutBtn.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    signOutBtn.configure(background='grey')
    signOutBtn.configure(foreground='White')

    # editButton = Button(pfDetailsFrame, text="Edit", command=editUserInfo)
    # editButton.grid(row=6, column=4, padx=5, pady=5)

    extensionButton = Button(userUnitsOut, text="Extend Checkout", command=unitExtension)
    extensionButton.grid(row=2, column=0, padx=5, pady=5)

def editUserInfo():
    editBox = Toplevel()

    topTextFrame = Frame(editBox)
    topTextFrame.grid(row=0, column=0, padx=5, pady=5)

    bottomContentFrame = Frame(editBox)
    bottomContentFrame.grid(row=1, column=0, padx=5, pady=5)

    informationLabel = Label(topTextFrame, text="Only your name and email may be changed")
    informationLabel.grid(row=0, column=0, padx=5, pady=5)

    nameLabel = Label(bottomContentFrame, text="Name:")
    nameLabel.grid(row=2, column=0, padx=5, pady=5)
    nameEntry = Entry(bottomContentFrame)
    nameEntry.grid(row=2, column=1, padx=5, pady=5)

    emailLabel = Label(bottomContentFrame, text="Email:")
    emailLabel.grid(row=3, column=0, padx=5, pady=5)
    emailEntry = Entry(bottomContentFrame)
    emailEntry.grid(row=3, column=1, padx=5, pady=5)

def signOutUser():
    global currUser

    usernameLabel.destroy()
    signOutBtn.grid_forget()
    extensionButton.destroy()
    
    # editButton.grid_forget()

    logInLabel = Button(topBarFrame, text="Log In", command=login)
    logInLabel.configure(background='grey')
    logInLabel.configure(foreground='White')
    logInLabel.grid(row=0, column=0, padx=5, pady=5, sticky='e')

    ldapUserResult.configure(text="N/A")
    ldapNameResult.configure(text="N/A")
    ldapWwidResult.configure(text="N/A")
    ldapIDResult.configure(text="N/A")
    ldapEmailResult.configure(text="N/A")
    unitsLabel.configure(text="Current Unit's")

    for row in userUnitsOutTree.get_children():
        userUnitsOutTree.delete(row)
        print(f"{Fore.CYAN}[{datetime.now()}]: Deleted row {row}{Style.RESET_ALL}")

    currUser = ""

def checkUserUnits(userId, unit):
    user = userId
    engine.execute(f"SELECT unit1, unit2, unit3, unit4, unit5, unit6, unit7, unit8, unit9, unit10 FROM remote_lab_inv_users WHERE idsid = {user}")
    row = engine.fetchone()

    empty_column_index = None
    for i, value in enumerate(row):
        if not value:
            empty_column_index = i
            break

    # If an empty column is found, update the respective column with the new value
    if empty_column_index is not None:
        column_name = f"unit{empty_column_index + 1}"
        query = f"UPDATE remote_lab_inv_user SET {column_name} = {unit}"
        engine.execute(query)


def checkIn():
    global idSerialEntry
    global checkInPrompt
    global cabinetOptionRow
    global locationOptionRow
    global currUser

    if currUser == "":
        MessageBox.showwarning("CheckIn", "Please Log In first to Check out or In")
    else:
        checkInPrompt = Toplevel()
        locationOptionRow = StringVar()
        cabinetOptionRow = StringVar()

        mainContentFrame = Frame(checkInPrompt)
        mainContentFrame.grid(row=0, column=0, padx=5, pady=5)

        idSerialLabel = Label(mainContentFrame, text="Unit ID or Serial:")
        idSerialLabel.grid(row=0, column=0, padx=5, pady=5)
        idSerialEntry = Entry(mainContentFrame)
        idSerialEntry.grid(row=1, column=0, padx=5, pady=5)

        checkInBtnPrompt = Button(mainContentFrame, text="Check In", command=checkInCheck)
        checkInBtnPrompt.grid(row=2, column=0, padx=5, pady=5)

        rowLabel = Label(mainContentFrame, text="Row")
        rowLabel.grid(row=1, column=1, padx=5, pady=5)

        locationDropDown = OptionMenu(mainContentFrame, locationOptionRow, *locationRow)
        locationDropDown.grid(row=2, column=1, padx=5, pady=5)

        cabinetLabel = Label(mainContentFrame, text="Cabinet Number")
        cabinetLabel.grid(row=1, column=2, padx=5, pady=5)

        cabinetDropDown = OptionMenu(mainContentFrame, cabinetOptionRow, *locationUnitNum)
        cabinetDropDown.grid(row=2, column=2, padx=5, pady=5)


def checkOut():
    global idSerialEntry2
    global checkOutPrompt
    global cabinetOptionRow2
    global locationOptionRow2
    global selectedDay
    global currUser

    selectedDay = StringVar(root)
    selectedDay.set(dateOptions[0])

    if currUser == "":
        MessageBox.showwarning("CheckOut", "Please Log In first to Check out or In")
    else:
        checkOutPrompt = Toplevel()
        locationOptionRow2 = StringVar()
        cabinetOptionRow2 = StringVar()

        mainContentFrame = Frame(checkOutPrompt)
        mainContentFrame.grid(row=0, column=0, padx=5, pady=5)

        idSerialLabel = Label(mainContentFrame, text="Unit ID or Serial:")
        idSerialLabel.grid(row=0, column=0, padx=5, pady=5)
        idSerialEntry2 = Entry(mainContentFrame)
        idSerialEntry2.grid(row=1, column=0, padx=5, pady=5)

        checkInBtnPrompt = Button(mainContentFrame, text="Check Out", command=checkOutCheck)
        checkInBtnPrompt.grid(row=2, column=0, padx=5, pady=5)

        dateLabel = Label(mainContentFrame, text="Return Date")
        dateLabel.grid(row=0, column=3, padx=5, pady=5)

        dateDropDown = OptionMenu(mainContentFrame, selectedDay, *dateOptions)
        dateDropDown.grid(row=1, column=3, padx=5, pady=5)

def checkOutCheck():
    global currUser

    idSerial = idSerialEntry2.get()
    searchStringId = f"SELECT * FROM remote_lab_inventory WHERE id = '{idSerial}';"
    searchStringSerial = f"SELECT * FROM remote_lab_inventory WHERE serialNo = '{idSerial}';"

    if currUser == "":
        MessageBox.showwarning("Checkout", "Please Log In first to Check out or In")
        return
    if idSerial == "":
        MessageBox.showinfo("Check In", "Please complete Check Out prompt")
        return

    idSearch = conn.execute(searchStringId)

    data = idSearch.fetchall()

    if data == []:
        print(f"Found via serial: {idSerial}")
        serialSearch = conn.execute(searchStringSerial)

        data = serialSearch.fetchall()

        for row in data:
            currentUser = row[7]

        if currentUser == "Available":
            print(f"Unit {idSerial} is available")
            checkOutCurrUserBySerial(idSerial)
            usersCheckedOutUnits(currUser)
        if currentUser == "In Use":
            MessageBox.showinfo("Check Out", "Unit cannot be checked Out as it is already assigned to a user")
            checkOutPrompt.destroy()
            return
    if len(data) > 0:
        print(f"Found via id: {idSerial}")
        for row in data:
            currentUser = row[7]

        if currentUser == "Available":
            print(f"Unit {idSerial} is available")
            checkOutCurrUserById(idSerial)
            pullDataTree()
            usersCheckedOutUnits(currUser)
            checkOutPrompt.destroy()
        if currentUser == "In Use":
            MessageBox.showinfo("Check Out", "Unit cannot be checked Out as it is already assigned to a user")
            checkOutPrompt.destroy()
            return
    else:
        print("Ruh Roh")
        pass

def checkInCheck():
    idSerial = idSerialEntry.get()
    searchStringId = f"SELECT * FROM remote_lab_inventory WHERE id = '{idSerial}';"
    searchStringSerial = f"SELECT * FROM remote_lab_inventory WHERE serialNo = '{idSerial}';"

    if idSerial == "":
        MessageBox.showinfo("Check In", "Please complete Check In prompt")
        return

    idSearch = conn.execute(searchStringId)

    data = idSearch.fetchall()

    if data == []:
        print(f"Found via serial: {idSerial}")
        serialSearch = conn.execute(searchStringSerial)

        data = serialSearch.fetchall()

        for row in data:
            currentUser = row[7]

        if currentUser == "In Use":
            print(f"Unit {idSerial} is in Use")
            checkInCurrUserBySerial(idSerial)
            usersCheckedOutUnits(currUser)
        if currentUser == "Available":
            MessageBox.showinfo("Check In", "Unit cannot be checked in as it is not assigned to a user")
            checkInPrompt.destroy()
            return
    if len(data) > 0:
        print(f"Found via id: {idSerial}")
        for row in data:
            currentUser = row[7]

        if currentUser == "In Use":
            print(f"Unit {idSerial} is In Use")
            checkInCurrUserById(idSerial)
            pullDataTree()
            checkInPrompt.destroy()
            usersCheckedOutUnits(currUser)
        if currentUser == "Available":
            MessageBox.showinfo("Check In", "Unit cannot be checked in as it is not assigned to a user")
            checkInPrompt.destroy()
            return
    else:
        print("Ruh Roh")
        pass

def checkInCurrUserById(id):
    rowOption = locationOptionRow.get()
    cabinetOption = cabinetOptionRow.get() 
    location = f"lab-{rowOption}{cabinetOption}"
    user = "None"
    status = "Available"
    dueDate = "None"
    msg = f"Unit with {id} assigned to {location}"
    setUserString = f"UPDATE `remote_lab_inventory` SET location='{location}', user='{user}', status='{status}', dueDate='{dueDate}' WHERE id={id}"
    print(setUserString)
    try:
        conn.execute(setUserString)
        MessageBox.showinfo("Check In", msg)
        usersCheckedOutUnits(user)
    except Exception as e:
        print(f"Error: {e}")
        pass

def checkInCurrUserBySerial(serial):
    rowOption = locationOptionRow.get()
    cabinetOption = cabinetOptionRow.get() 
    location = f"lab-{rowOption}{cabinetOption}"
    user = "None"
    status = "Available"
    dueDate = "None"
    msg = f"Unit with {id} assigned to {location}"
    setUserString = f"UPDATE `remote_lab_inventory` SET location='{location}', user='{user}', status='{status}', dueDate='{dueDate}' WHERE id={serial}"
    print(setUserString)
    
    try:
        conn.execute(setUserString)
        MessageBox.showinfo("Check In", msg)
        usersCheckedOutUnits(user)
    except EXCEPTION as e:
        print(f"Error: {e}")
        pass

def checkOutCurrUserById(id):
    location = "None"
    user = currUser
    status = "In Use"
    msg = f"Unit with {id} assigned to {currUser}"

    date = selectedDay.get()
    # date = date.replace("-", "")
    setUserString = f"UPDATE `remote_lab_inventory` SET location='{location}', user='{user}', status='{status}', dueDate='{date}' WHERE id={id}"
    print(setUserString)
    try:
        conn.execute(setUserString)
        # checkUserUnits(user, id)
        MessageBox.showinfo("Check Out", msg)
        usersCheckedOutUnits(user)
    except Exception as e:
        print(f"Error: {e}")
        pass

def checkOutCurrUserBySerial(serial):
    location = "None"
    user = currUser
    status = "In Use"
    msg = f"Unit with {serial} assigned to {currUser}"

    date = selectedDay.get()
    # date = date.replace("-", "")
    setUserString = f"UPDATE `remote_lab_inventory` SET location='{location}', user='{user}', status='{status}', dueDate='{date}' WHERE id={serial}"
    print(setUserString)
    
    try:
        conn.execute(setUserString)
        MessageBox.showinfo("Check Out", msg)
        usersCheckedOutUnits(user)
    except Exception as e:
        print(f"Error: {e}")
        pass

def usersCheckedOutUnits(user):
    userQuery = f"SELECT * FROM remote_lab_inventory WHERE user LIKE '{user}'"

    results = conn.execute(userQuery)

    print(f"{Fore.GREEN}[{datetime.now()}]: Starting Data pull for Tree 2{Style.RESET_ALL}")

    for row in userUnitsOutTree.get_children():
        userUnitsOutTree.delete(row)
        print(f"{Fore.CYAN}[{datetime.now()}]: Deleted row {row}{Style.RESET_ALL}")

    if results:
        for result in results:
            userUnitsOutTree.insert('', 'end', values=(result[0], result[2], result[3], result[8]))
            print(f"{Fore.CYAN}[{datetime.now()}]: Tree : Row Found : {results}{Style.RESET_ALL}")

def filterTree():
    print(f"{Fore.GREEN}[{datetime.now()}]: Running filterTree{Style.RESET_ALL}")
    filterColumn = filterOptionValue.get()
    searchTerm = searchTermEntry.get().lower()
    print(f"{Fore.GREEN}[{datetime.now()}]: filterTreeView1 : Deleting tree contentn{Style.RESET_ALL}")
    checkTree.delete(*checkTree.get_children())
    try:
        with engine.connect() as conn:
            result = conn.execute(f"SELECT * FROM remote_lab_inventory WHERE {filterColumn} LIKE '%{searchTerm}%'")
            for row in result:
                checkTree.insert('', 'end', text=row, values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                print(f"{Fore.GREEN}[{datetime.now()}]: filterTree: Inserting Row {row}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.GREEN}[{datetime.now()}]: Error : {e}{Style.RESET_ALL}")
        MessageBox.showinfo("FilterTreeView1", {e})

#Tkinter GUI 
# create the notebook (tabbed widget)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky='nsew')

# create tabs
mainTab = ttk.Frame(notebook)
notebook.add(mainTab, text='NUC Check In/Out')

#Frames
mainFrame = Frame(mainTab, width='1525', height='900', background='black')
mainFrame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

topBarFrame = Frame(mainTab)
topBarFrame.grid_rowconfigure(0, weight=1)
topBarFrame.grid_columnconfigure(0, weight=1)
topBarFrame.configure(height=40)
topBarFrame.configure(background='black')
topBarFrame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

treeContainer = Frame(mainFrame)
treeContainer.grid(row=0, column=0, padx=5, pady=5)

selOptionFrame = Frame(mainFrame, width=100, height=100)
selOptionFrame.grid(row=0, column=1, padx=5, pady=5)
mainlabelSelOpt = Frame(selOptionFrame)
mainlabelSelOpt.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
mainlabelSelOpt.grid_rowconfigure(0, weight=1)
mainlabelSelOpt.grid_columnconfigure(0, weight=1)
labelFrames = Frame(selOptionFrame)
labelFrames.grid(row=1, column=0, padx=5, pady=5)

treeFrameInside = Frame(treeContainer)
treeFrameInside.grid(row=0, column=0, padx=5, pady=5)

treeListFrame = Frame(treeContainer)
treeListFrame.grid(row=1, column=0, padx=5, pady=5)

checkButtonsFrame = Frame(mainFrame)
checkButtonsFrame.grid(row=1, column=1, padx=5, pady=5)

searchFrame = Frame(mainFrame)
searchFrame.grid(row=1, column=0, padx=5, pady=5)

userDetailsFrame = Frame(mainFrame)
userDetailsFrame.grid(row=2, column=0, padx=5, pady=5)

pfpFrame = Frame(userDetailsFrame)
pfpFrame.grid(row=0, column=0, padx=5, pady=5)

pfDetailsFrame = Frame(userDetailsFrame)
pfDetailsFrame.grid(row=0, column=1, padx=5, pady=5)

userUnitsOut = Frame(userDetailsFrame)
userUnitsOut.grid(row=0, column=2, padx=5, pady=5)

#Topbarstuff
logInLabel = Button(topBarFrame, text="Log In", command=login)
logInLabel.configure(background='grey')
logInLabel.configure(foreground='White')
logInLabel.grid(row=0, column=0, padx=5, pady=5, sticky='e')

#Tree
checkTree = ttk.Treeview(treeListFrame)
checkTree.grid(row=1, column=0, padx=5, pady=5)
checkTree['columns'] = ('ID', 'Location', 'Product Name', 'Serial Number', 'Production Status', 'Codename', 'User', 'Status', 'Date Due')

treeLabel = Label(treeFrameInside, text="NUC Remote Lab")
treeLabel.grid(row=0, column=0, padx=5, pady=5)

scrollbar = ttk.Scrollbar(treeListFrame, orient="vertical", command=checkTree.yview)
scrollbar.grid(row=1, column=1, sticky='ns')

checkTree.column("#0", width=0, stretch="NO")
checkTree.heading('ID', text='ID')
checkTree.column('ID', width=30)
checkTree.heading('Location', text='Location')
checkTree.column('Location', width=60)
checkTree.heading('Product Name', text='Product Name')
checkTree.column('Product Name', width=100)
checkTree.heading('Serial Number', text='Serial Number')
checkTree.column('Serial Number', width=100)
checkTree.heading('Production Status', text='Production Status')
checkTree.column('Production Status', width=150)
checkTree.heading('Codename', text='Codename')
checkTree.column('Codename', width=100)
checkTree.heading('User', text='User')
checkTree.column('User', width=60)
checkTree.heading('Status', text='Status')
checkTree.column('Status', width=60)
checkTree.heading('Date Due', text='Date Due')
checkTree.column('Date Due', width=70)
checkTree.configure(yscrollcommand=scrollbar.set)
checkTree.bind('<<TreeviewSelect>>', onTreeSelectTab2)

#Selected entry details section
detailsLabel = Label(mainlabelSelOpt, text="Unit Details")
detailsLabel.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

idLabel = Label(labelFrames, text="ID")
idLabel.grid(row=0, column=0, padx=5, pady=5)
locationLabel = Label(labelFrames, text="Location")
locationLabel.grid(row=1, column=0, padx=5, pady=5)
prodNameLabel = Label(labelFrames, text="Product Name")
prodNameLabel.grid(row=2, column=0, padx=5, pady=5)
serialLabel = Label(labelFrames, text="Serial No.")
serialLabel.grid(row=3, column=0, padx=5, pady=5)
prodStatusLabel = Label(labelFrames, text="Production Status")
prodStatusLabel.grid(row=4, column=0, padx=5, pady=5)
codenameLabel = Label(labelFrames, text="Codename")
codenameLabel.grid(row=5, column=0, padx=5, pady=5)
userLabel = Label(labelFrames, text="User")
userLabel.grid(row=6, column=0, padx=5, pady=5)
statusLabel = Label(labelFrames, text="Status")
statusLabel.grid(row=7, column=0, padx=5, pady=5)
dateLabel = Label(labelFrames, text="Date")
dateLabel.grid(row=8, column=0, padx=5, pady=5)

idLabelDisp = Label(labelFrames, text="None")
idLabelDisp.grid(row=0, column=1, padx=5, pady=5)
locationLabelDisp = Label(labelFrames, text="None")
locationLabelDisp.grid(row=1, column=1, padx=5, pady=5)
prodNameLabelDisp = Label(labelFrames, text="None")
prodNameLabelDisp.grid(row=2, column=1, padx=5, pady=5)
serialLabelDisp = Label(labelFrames, text="None")
serialLabelDisp.grid(row=3, column=1, padx=5, pady=5)
prodStatusLabelDisp = Label(labelFrames, text="None")
prodStatusLabelDisp.grid(row=4, column=1, padx=5, pady=5)
codenameLabelDisp = Label(labelFrames, text="None")
codenameLabelDisp.grid(row=5, column=1, padx=5, pady=5)
userLabelDisp = Label(labelFrames, text="None")
userLabelDisp.grid(row=6, column=1, padx=5, pady=5)
statusLabelDisp = Label(labelFrames, text="None")
statusLabelDisp.grid(row=7, column=1, padx=5, pady=5)
dateLabelDisp = Label(labelFrames, text="None")
dateLabelDisp.grid(row=8, column=1, padx=5, pady=5)

#Buttons
checkInBtn = Button(checkButtonsFrame, text="Check In", command=checkIn)
checkInBtn.configure(background='grey')
checkInBtn.configure(foreground='White')
checkInBtn.grid(row=0, column=0, padx=5, pady=5)
checkOutBtn = Button(checkButtonsFrame, text="Check Out", command=checkOut)
checkOutBtn.configure(background='grey')
checkOutBtn.configure(foreground='White')
checkOutBtn.grid(row=0, column=1, padx=5, pady=5)

#userdetaills stuff
ldapUserLabel = Label(pfDetailsFrame, text="User:")
ldapUserLabel.grid(row=1, column=1, padx=5, pady=5)
ldapNameLabel = Label(pfDetailsFrame, text="Name:")
ldapNameLabel.grid(row=2, column=1, padx=5, pady=5)
ldapWwidLabel = Label(pfDetailsFrame, text="WWID:")
ldapWwidLabel.grid(row=3, column=1, padx=5, pady=5)
ldapIDLabel = Label(pfDetailsFrame, text="ID:")
ldapIDLabel.grid(row=4, column=1, padx=5, pady=5)
ldapEmailLabel = Label(pfDetailsFrame, text="Email:")
ldapEmailLabel.grid(row=5, column=1, padx=5, pady=5)

ldapUserResult = Label(pfDetailsFrame, text="N/A")
ldapUserResult.grid(row=1, column=2, padx=5, pady=5)
ldapNameResult = Label(pfDetailsFrame, text="N/A")
ldapNameResult.grid(row=2, column=2, padx=5, pady=5)
ldapWwidResult = Label(pfDetailsFrame, text="N/A")
ldapWwidResult.grid(row=3, column=2, padx=5, pady=5)
ldapIDResult = Label(pfDetailsFrame, text="N/A")
ldapIDResult.grid(row=4, column=2, padx=5, pady=5)
ldapEmailResult = Label(pfDetailsFrame, text="N/A")
ldapEmailResult.grid(row=5, column=2, padx=5, pady=5)

#User unit tree
userUnitsOutTree = ttk.Treeview(userUnitsOut)
userUnitsOutTree.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
userUnitsOutTree['columns'] = ('ID', 'Product Name', 'Serial No.', 'Due Date')

unitsLabel = Label(userUnitsOut, text=f"{currUser} Current Units")
unitsLabel.grid(row=0, column=0, padx=5, pady=5)

unitsScrollbar = ttk.Scrollbar(userUnitsOut, orient="vertical", command=userUnitsOutTree.yview)
unitsScrollbar.grid(row=1, column=3, sticky='ns')

userUnitsOutTree.column("#0", width=0, stretch="NO")
userUnitsOutTree.heading("ID", text='ID')
userUnitsOutTree.column("ID", width=50)
userUnitsOutTree.heading("Product Name", text='Product Name')
userUnitsOutTree.column("Product Name", width=100)
userUnitsOutTree.heading("Serial No.", text='Serial No.')
userUnitsOutTree.column("Serial No.", width=100)
userUnitsOutTree.heading("Due Date", text='Date Due')
userUnitsOutTree.column("Due Date", width=100)

# userUnitsOutTree.configure(width=200, height=200)
userUnitsOutTree.configure(yscrollcommand=scrollbar.set)
userUnitsOutTree.bind('<<TreeviewSelect>>', onTreeSelectTab2)

#Search stuff
filterLabel = Label(searchFrame, text="Filter Options")
filterLabel.grid(row=0, column=0, padx=5, pady=5)
searchTermLabel = Label(searchFrame, text="Search Term")
searchTermLabel.grid(row=0, column=2, padx=5, pady=5)

filterDropDown = OptionMenu(searchFrame, filterOptionValue, *filterOptions)
filterDropDown.grid(row=0, column=1, padx=5, pady=5)
filterOptionValue.set(filterOptions[0])

searchTermEntry = Entry(searchFrame)
searchTermEntry.grid(row=0, column=3, padx=5, pady=5)

searchButton = Button(searchFrame, text="Search", command=filterTree)
searchButton.configure(background='grey')
searchButton.configure(foreground='White')
searchButton.grid(row=0, column=4, padx=5, pady=5)

searchButton = Button(searchFrame, text="Reset Table", command=pullDataTree)
searchButton.configure(background='grey')
searchButton.configure(foreground='White')
searchButton.grid(row=0, column=5, padx=5, pady=5)

#Variables and function calls
#
geoOptions = ["AMR", "GER", "GAR"]
locationRow = ["a","b","c","d","e"]
locationUnitNum = ["1","2","3","4","5"]
searchOptions = ["id", "location", "serial", "Production Status", "Codename", "User", "Status", "Due Date" ]
columns = ["id","location","prodName","serialNo","prodStatus","codename","user","status","dueDate"]

defaultPfp = "Assets/Images/pfp.jpg"
image = Image.open(defaultPfp)

# data = loadConfig("config.json")
decrypted_config = decryptConfig()
data = loadEncryptedConfig(decrypted_config)

dbHostName = data['dbHost']
dbName = data['dbName']
userName = data['dbUser']
userPassword = data['dbPass']
dbPort = data['dbPort']

try:
    engine = create_mysqlConnection(dbHostName, dbName, userName, userPassword, dbPort)
    conn = engine.connect()
    print(f"{Fore.YELLOW}[{datetime.now()}]: DB Connection : Connected to {dbName}{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[{datetime.now()}]: DB Connection : Error : {e}{Style.RESET_ALL}")

pullDataTree()

profileImage()

root.mainloop()
