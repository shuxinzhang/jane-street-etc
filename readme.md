#### Linux Operations
`ls` : See what files are in the current directory.
`pwd` : See the current directory
`mkdir` create a new folder in current directory. e.g. `mkdir helloworld`
`cd`: Change the working directory to some folder other than the current directory.
`nano <fileName>` : Create or open(if exists) the file with the name given. e.g. `nano trade.py`
`python3 ???.py`: Run the designated python codes. 
#### Worklow on uploading and downloading source codes
- if you have not downloaded the repo: `git clone <git repo address>`: Download the current files in the current directory. 
- if you have already downloaded the repo and need to download the changes: `git pull`
- if you made some changes and want to upload it online: (For example, you added trade.py)
```
git add .
git commit -m '<A description on the change you made>'
git push 
```