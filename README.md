# Important
`DO NOT commit directly to main`
<br><br>
Before doing anything:<br>

> 1. `git branch`<br>
>       Make sure you are on the correct feature branch
>
> 2. `git status`<br>
        Make sure your files are up-to-date
>
> 3. `git pull/merge`<br>
>       If you are not up-to-date (step2)

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

`SQLite Viewer`<br>
https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer
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
```
<br><br>

## 5a. Setup WSL (Windows)
Open CMD and run the following and restart your machine
```bash
wsl --install -d Debian
```

Open CMD and enter WSL
```bash
wsl
```

Install dependencies
```sh
sudo apt update
sudo apt upgrade
sudo apt install git nano python3 python3-pip
```

Open VSCode in Debian WSL and continue.
<br><br>

## 5. Virturalize
Create virtualenv
```sh
// !!IMPORTANT!!
//
// Ensure you `cd` into the project root folder
// If successfuly, you should see a new folder apepar in your project root

python3 -m venv venv
```

Start virtualenv<br>
If successful, you should see `(venv)` in your terminal
```sh
source venv/bin/activate
```

Install python packages
```sh
pip install -r requirements.txt
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
Start server
```sh
gunicorn --bind=0.0.0.0:8000 --threads=3 --workers=3 --reload run:app
```

Run with `--preload` and not `--reload` if the workers fail to boot for the error message



<br><br>

# 9. Clean Up
After running, you may notice generation of pycache folders.
These folders are useful as they speed up runtime execution through caching.

If you wish to remove them, Run the following:
  - (etc) Between testing or cache issues
  - Note that it will not remove pytest cache in proj root

```sh
python -B -m clear_pycache.py
```
<br><br>

# 10. Running production build locally
```sh
// Login on docker
docker login --username <github-username> --password <github-accesstoken> ghcr.io

// Pull remote docker image
docker pull ghcr.io/caffeine-addictt-edutecx-build:latest

// List existing docker images
docker images ls

// Run docker image
docker run -p 8080:8080 <first 3 characters of image ID>
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
  `password : str`, required
    Should utilise sha256 if larger than 72 characaters

  `encryption : str`, optional (default is 'sha256')
    The encryption algorithm used to encode the password
  
    
  Returns
  -------
  `HashedPassword : str`
    The fully salted hash
    

  Raises
  ------
  `NotImplementedError`
    If encryption algorithm is invalid


  Examples
  --------
  >>> hashingPassword('myPass', 'sha256')
  hash: wdjUW8w8dh8awhd83dj
  >>> hashingPassword('myPass')
  hash: wdjUW8w8dh8awhd83dj
  """
  ...
  return hashed
```