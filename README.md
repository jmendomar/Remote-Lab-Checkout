```
 __   ___        __  ___  ___               __      __        ___  __        __       ___ 
|__) |__   |\/| /  \  |  |__     |     /\  |__)    /  ` |__| |__  /  ` |__/ /  \ |  |  |  
|  \ |___  |  | \__/  |  |___    |___ /~~\ |__)    \__, |  | |___ \__, |  \ \__/ \__/  |  
```

# Version: v0.2.4
### By *jesusi2x*
### Contact @ *jesusx.isaac.mendoza.martinez@intel.com* for any Issues

## Required Python Version
- Python 3.11 (https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K?hl=en-us&gl=us)
- (Code issues have been encountered due to older python versions please use 3.11)

## Required Libraries
- sqlalchemy
- tkinter(Only Required to install if on a non Windows OS)
- mysql-connector-python
- colorama
- ldap3
- pillow
- pandas
- cryptography

## How to get started
- Install Python 3.11 from the link above. It is recommended that it is installed from the
Microsoft Store as it sets up paths and ensures python is properly installed

### Run dependancy installer
- Open a terminal and change the directory to where the Program is located below is an example.
 Remember if your path has spaces, Add quotes to the beginning and end of the section with spaces
```
cd C:\Users\jesusi2x\"OneDrive - Intel Corporation"\Desktop\Remote-Lab-Checkout
```
- Now run the dependency auto installer
```
python3 .\dependInstaller.py
```
- If a proxy is required for your intel network input y to continue and provide your proxy
address and port the format will be provided below.
```
Do you want to use a proxy? (y/n): y

Proxy host: proxy-dmz.intel.com

Proxy port: 912
```
### Run Check out program
- Once all dependancies have been installed you should now be able to run the program with a terminal shell
```
python3 .\newMain.py
```
