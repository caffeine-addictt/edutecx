# Important
`DO NOT commit directly to master`
<br><br>
Before doing anything:<br>

> 1. `git branch`<br>
>       Make sure you are on the expected branch
>
> 2. `git status`<br>
        Make sure you are up-to-date
>
> 3. `git pull`<br>
>       If you are not up-to-date (step2)
>
> 4. `git fetch <parent branch name / 'main'>`<br>
>       Pulls from origin (main)
>
> 5. `git merge origin`<br>
>       Merge origin into your branch

<br><br><br><br><br>

# SETUP
How to setup your project for this?
<br><br><br>

## 1. Python Version
Make sure you're running v3.10.11+
<br><br>

## 2. Code Editor
Lets stick to VScode
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
Install git
<br><br>
Ensure that you install both git CLI and git desktop<br>
https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

Clone github repository<br>
If successful, you should see a new folder appear
```sh
git clone https://github.com/caffeine-addictt/NYP_Sem2_AppDev
git clone git+https://github.com/caffeine-addictt/NYP_Sem2_AppDev
```
<br><br>

## 5. Virturalize
Install python virtualenv
```sh
// Try other commands if not working
py -m pip install virtualenv
python -m pip install virtualenv
python3 -m pip install virtualenv
```

Create virtualenv
```sh
// !!IMPORTANT!!
//
// Ensure you `cd` into the project root folder
// If successfuly, you should see a new folder apepar in your project root

// Try other commands if not working
py -m venv venv
python -m venv venv
python3 -m venv venv
```

Start virtualenv<br>
If successful, you should see `(venv)` in your terminal
```sh
// Try other commands if not working
venv\Scripts\activate
venv\Scripts\activate.bat
venv\Scripts\activate.ps1

// Linux
source venv/bin/activate
```

Install python packages
```sh
// Try other commands if not working
pip install -r requirements.txt
py -m pip install -r requirements.txt
python -m pip install -r requirements.txt
python3 -m pip install -r requirements.txt
```
<br><br>

## 6. Creating a feature
Ensure there isn't already an exisitng branch for it by running:<br>
```sh
// Globally lists branches
git branch -r
```

If there is an existing branch, move on to **Step 7**<br>
<br>
Else, choose an all-encompassing name `(UserLoginPage, DatabaseHandler, etc.)`<br>
Then create a branch;<br><br>
If successful, running `git branch` will show your branch name.

```sh
// **from** > sub branch for structure:
//   master:
//     from:
//       newFeature
//
// Leave blank if its a direct branch:
//   master:
//      newFeature


// Creates branch and auto checkout(s) to branch
git checkout -b <Your Feature Branch Name> <from>

// OR //

// Creates a branch
git branch <Your Feature Branch Name> <from>

// Checkout(s) to branch
// **If it is a sub branch, checkout to the sub branch first**
git checkout <Your Feature Branch Name> <from>
```

Next push your branch

```sh
// Sets up origin remote for new branch
git push -u origin <Your Feature Branch Name>
```
<br><br>

# 7. Accessing a feature
Search for the feature's branch name with:

```sh
// Globally lists branches
git branch -r
```

Checkout the branch
```sh
// Checkout the whole branch trace from master if not successful
git checkout <Feature Branch Name>
```

Next push your branch

```sh
// Sets up origin remote for new branch
git push -u origin <Your Feature Branch Name>
```


<br><br>

# 8. Running Files
Setup enviroment variables
```sh
$env:FLASK_APP = "app/app.py" #WINDOWS
export FLASK_APP="app/app.py" # Linux/MacOS

$env:FLASK_DEBUG=1 #WINDOWS
export FLASK_DEBUG=1 # Linux/MacOS
```
Start server
```sh
# -B stops generation of pycache, remove if you want it
py -B -m flask run
python -B -m flask run
python3 -B -m flask run
```


<br><br><br><br><br>

# Coding Conventions
`Here is what we will follow to keep our code organized`
<br>


<br>
Indentation should be 2 spaces

```py
def testFunc():
**testString = 'aa'
**
**for i in testString:
****print(i)
```


<br>
Paranthesis () should immediately follow

```py
def myFunc(): ...  // YES
print()            // YES

print ()           // NO
def myFunc (): ... // NO
```


<br>
Brackets "() {} []" with more than 4 elements or with elements long enough should be spread across lines

```py
doThis = {
  'params': ['return_response'],
  'data': [
    'myData_key_23424feuifhfwerr3rdfsie8'
  ]
}
```


<br>
Functions and variable names should be in camel case

```py
myVariable = 'hi'           // YES
def myFunctionForAPI(): ... // YES
def myFunctionForAPI(): ... // YES

MyVariable = 'hi'           // NO
def MyFunctionForAPI(): ... // NO
```


<br>
Type and Class declarations should be in title case

```py
class Vehicles: ...         // YES
class MyVehicles: ...       // YES
Registration = NewType(str) // YES

class vehicles: ...         // NO
class myVehicles: ...       // NO
registration = NewType(str) // NO
```


<br>
Doc strings should follow this convention

```py
HashedPassword = str

def hashingPassword(
  password: str,
  encryption: str = 'sha256'
) -> HashedPassword:
  """
  Hashes Password
  Follows encryption conventions with sha256

  Parameters
  ----------
  password : str, required
    Should utilise sha256 if larger than 72 characaters

  encryption : str, optional (default is 'sha265')
    The encryption algorithm used to encode the password
  
    
  Returns
  -------
  HashedPassword : str
    The fully salted hash
    

  Raises
  ------
  NotImplementedError
    If encryption algorithm is invalid

  """
  ...
  return hashed
```