# Important
`DO NOT commit to main/origin`<br><br>
`ALWAYS "git branch" before doing anything and ensure you are on your branch`<br><br>
`ALWAYS "git status" before doing anything and ensure your local files are up-to-date`<br><br>

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
`Install python virturalenv`
```sh
// Try other commands if not working
py -m pip install virturalenv
python -m pip install virturalenv
python3 -m pip install virturalenv
```

`Create virturalenv`<br>
`!!IMPORTANT!!` Ensure you `cd` into the project root folder<br>
If successfuly, you should see a new folder apepar in your project root
```sh
// Try other commands if not working
py -m venv venv
python -m venv venv
python3 -m venv venv
```

`Start virturalenv`<br>
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