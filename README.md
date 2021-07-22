## juungle_ui
This is an interface to interact with [juungle.net](https://juungle.net).

## Getting the code

`$ git clone https://github.com/Juungle/juungle_ui.git`

or download the files

`$ wget https://raw.githubusercontent.com/Juungle/juungle_ui/main/juungle_app.py`

`$ wget https://raw.githubusercontent.com/Juungle/juungle_ui/main/nft.py`

`$ wget https://raw.githubusercontent.com/Juungle/juungle_ui/main/requrements.txt`


place in a directory `juungle_ui`

`$ pip install -r requirements.txt`

Create a file `user-config.ini` with juungle.net credentials
in the same directory of the file:
```
LOGIN_USERNAME="username@email"
LOGIN_PASSWORD="password"
```

## Running
`$ python juungle_app.py`

## Options
* All - Show all nfts (temporary WAIFU only)
* For Sale - All nfts that are for sale
* Sold - All nfts that have been sold or are not for sale
