# Important
`DO NOT commit to main/origin`<br><br>
`Before doing anything`<br>
1. git branch <- Make sure you are on your branch
2. git status <- Make sure you are up-to-date
3. git pull <- If you are not up-to-date (step2)
4. git fetch <- Pulls from origin (main)
5. git merge origin <- Merge origin into your branch
<br><br><br><br><br>

# SETUP
`How to setup your project for this?`
## 1. Python Version
`Make sure you're running v3.10.11+`
<br><br>

## 2. Code Editor
`Lets stick to VScode`
<br><br>

## 3. Extensions
`README.md Markdown`<br>
https://marketplace.visualstudio.com/items?itemName=bierner.markdown-preview-github-styles

`Basic IntelliSense`<br>
https://marketplace.visualstudio.com/items?itemName=VisualStudioExptTeam.vscodeintellicode
https://marketplace.visualstudio.com/items?itemName=VisualStudioExptTeam.intellicode-api-usage-examples
https://marketplace.visualstudio.com/items?itemName=Zignd.html-css-class-completion
https://marketplace.visualstudio.com/items?itemName=wholroyd.jinja

`Python`<br>
https://marketplace.visualstudio.com/items?itemName=ms-python.python
https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
https://marketplace.visualstudio.com/items?itemName=ms-python.isort
<br><br>

## 4. Getting the project
`Install git`<br>
Ensure that you install both git CLI and git desktop<br>
https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

`Clone github repository`<br>
If successful, you should see a new folder appear
```sh
git clone https://github.com/caffeine-addictt/NYP_Sem2_AppDev
git clone git+https://github.com/caffeine-addictt/NYP_Sem2_AppDev
```
<br><br>

## 5. Virturalize
`Install python virtualenv`
```sh
// Try other commands if not working
py -m pip install virtualenv
python -m pip install virtualenv
python3 -m pip install virtualenv
```

`Create virtualenv`<br>
`!!IMPORTANT!!` Ensure you `cd` into the project root folder<br>
If successfuly, you should see a new folder apepar in your project root
```sh
// Try other commands if not working
py -m venv venv
python -m venv venv
python3 -m venv venv
```

`Start virtualenv`<br>
If successful, you should see `(venv)` in your terminal
```sh
// Try other commands if not working
venv\Scripts\activate
venv\Scripts\activate.bat
venv\Scripts\activate.ps1
```

`Install python packages`
```sh
// Try other commands if not working
pip install -r requirements.txt
py -m pip install -r requirements.txt
python -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
```
<br><br>

## 6. Managing git
`Ensure you do this before touching anything from git CLI`<br>
If successful, run `git branch` and ensure it says "On branch \<Your name\>"
```sh
git checkout -b <Your name>
```

If unsuccessful;
```sh
git branch <Your name>
git checkout <Your name>
```

`Next push your branch`
```sh
git push -u origin <Your name>
```
<br><br>

# 7. Running Files
`Setup enviroment variables`
```sh
$env:FLASK_APP = "app/app.py" #WINDOWS
export FLASK_APP="app/app.py" # Linux/MacOS

$env:FLASK_DEBUG=1 #WINDOWS
export FLASK_DEBUG=1 # Linux/MacOS
```
`Start server`
```sh
# -B stops generation of pycache, remove if you want it
py -B -m flask run
python -B -m flask run
python3 -B -m flask run
```


<br><br><br><br><br>

# Coding Conventions
Here is what we will follow to keep our code organized:

`Indentation will be 2 spaces`
```py
def testFunc():
| ...
| |
```

`Paranthesis () should immediately follow`
```py
def myFunc(): ...  // YES
print()            // YES

print ()           // NO
def myFunc (): ... // NO
```

`Brackets "() {} []" with more than 4 elements or with elements long enough should be spread across lines`
```py
doThis = {
  'params': ['return_response'],
  'data': [
    'myData_key_23424feuifhfwerr3rdfsie8'
  ]
}
```

`Functions and variable names have to be in camel case`
```py
myVariable = 'hi'           // YES
def myFunctionForAPI(): ... // YES
def myFunctionForAPI(): ... // YES

MyVariable = 'hi'           // NO
def MyFunctionForAPI(): ... // NO
```

`Type and Class declarations have to be in title case`
```py
class Vehicles: ...         // YES
class MyVehicles: ...       // YES
Registration = NewType(str) // YES

class vehicles: ...         // NO
class myVehicles: ...       // NO
registration = NewType(str) // NO
```
