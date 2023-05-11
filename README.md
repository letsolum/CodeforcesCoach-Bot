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
- <CODE>/start</CODE> — init bot work
- <CODE>/help</CODE> — displays all commands
- <CODE>/handle [your nick]</CODE> — set handle
- <CODE>/key</CODE> — set [your key] (codeforces API)
- <CODE>/secret</CODE> — set [your secret] (codeforces API)
- <CODE>/friends</CODE> — display all of your friends (available only via CF API)
- <CODE>/analyze [handle]</CODE> — start analyse account. if handle missed -- will analyze your account. <b>WARNING:</b> First running can take a few minutes!
- <CODE>/train</CODE> — available only for self-using (<i>you should set your handle firstly</i>)
- <CODE>/process</CODE> — displays all running analysis
- <CODE>/stop [num]</CODE> — stop analyse. If <CODE>[num]</CODE> is empty all analysis stopes. Else <CODE>[num]</CODE> should contain codeforces handle

## Version 1.2 update
- added new command ```/train```
