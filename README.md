# CodeforcesCoach Bot

## Description
![Alt Text](utils/tutorial.gif)

## Usage
- tg: @CodeforcesCoach_bot
- your own bot
```bash
$ git clone git@github.com:letsolum/CodeforcesCoach-Bot.git
$ git checkout dev
```
Then you need to install [aiogram3.x](https://github.com/aiogram/aiogram), paste Telegram-API in ```telegram/config.py``` and run ```bot.py```
```
$ pip3 install https://github.com/aiogram/aiogram/archive/refs/heads/dev-3.x.zip requests
$ python3 bot.py
```

## Interface
- ```/handle [your nick]``` — set handle
- ```/key``` — set [your key] (codeforces API)
- ```/secret``` — set [your secret] (codeforces API)
- ```/friends``` — display all of your friends (are available only via CF API)
- ```/analyze [handle]``` — start analyzing account. if handle missed -- will analyze your account. <b>WARNING:</b> Can take a few minutes! 

## Roadmap
- ```/training``` — after analayzing bot will send you tasks, which should improve your level
- increase speed level
