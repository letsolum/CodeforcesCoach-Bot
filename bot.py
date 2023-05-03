import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from telegram.config import API_KEY
from codeforces.codeforces import CF
from aiogram.filters import CommandObject

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_KEY)

dp = Dispatcher()
users = dict()
usersKeySecret = dict()


@dp.message(Command("start"))
async def cmdStart(message: types.Message):
    await message.answer("🔥Welcome to the <b>Codeforces Coach Bot!</b>🔥\nI will help you to analyze your CF rounds. \
Send me your handle via command /handle", parse_mode="HTML")


@dp.message(Command("handle"))
async def setHandle(message: types.Message, command: CommandObject):
    users[message.from_user.id] = CF()
    usersKeySecret[message.from_user.id] = ['', '']
    if not users[message.from_user.id].setHandle(command.args):
        await message.answer("Wrong handle, try again, bro")
    else:
        await message.answer("Success!")
        await message.answer("Now you need to create CF-API on https://codeforces.com/settings/api \
and send in two messages: /key [apiKey] and /secret [apiSecret]")


@dp.message(Command("key"))
async def setKey(message: types.Message, command: CommandObject):
    usersKeySecret[message.from_user.id][0] = command.args
    if usersKeySecret[message.from_user.id][1] != '':
        if users[message.from_user.id].setKeyAndSecret(usersKeySecret[message.from_user.id][0],
                                                       usersKeySecret[message.from_user.id][1]):
            await message.answer("Done! Now you can check all available commands via /help")
        else:
            await message.answer("Key or Secret are incorrect! Check them")


@dp.message(Command("secret"))
async def setKey(message: types.Message, command: CommandObject):
    usersKeySecret[message.from_user.id][1] = command.args
    if usersKeySecret[message.from_user.id][0] != '':
        if users[message.from_user.id].setKeyAndSecret(usersKeySecret[message.from_user.id][0],
                                                       usersKeySecret[message.from_user.id][1]):
            await message.answer("Done! Now you can check all available commands via /help")
        else:
            await message.answer("Key or Secret are incorrect! Check them")


@dp.message(Command("friends"))
async def getFriends(message: types.Message):
    friends = users[message.from_user.id].getFriendsList()
    mssg = ''
    cnt = 0
    for friend in friends:
        mssg += str(cnt + 1) + '. ' + friend + '\n'
        cnt += 1
    mssg += '<i>Note: To analyze your friend or anybody on codeforces use</i> /analyze [handle]'
    await message.answer(mssg, parse_mode='HTML')


@dp.message(Command("analyze"))
async def getAnalysis(message: types.Message, command: CommandObject):
    if command.args:
        if command.args not in users:
            users[command.args] = CF()
        if not users[command.args].setHandle(command.args):
            await message.answer('Incorrect! Try again')
            return
        users[command.args].startAnalyzing()
        with open("codeforces/" + command.args + '/' + command.args + '.txt', 'r') as f:
            await message.answer(f.read(), parse_mode='HTML')
    else:
        users[message.from_user.id].startAnalyzing()
        with open("codeforces/" + users[message.from_user.id].getHandle() + '/' + users[
            message.from_user.id].getHandle() + '.txt', 'r') as f:
            await message.answer(f.read(), parse_mode='HTML')


@dp.message(Command("help"))
async def cmdHelp(message: types.Message):
    await message.answer("""1. /handle [your nick] — set handle
2. /key — set [your key] (codeforces API)
3. /secret — set [your secret] (codeforces API)
4. /friends — display all of your friends (are available only via CF API)
5. /analyze [handle] — start analyzing account. if handle missed -- will analyze your account. <b>WARNING:</b> First running can take a few minutes! 
""", parse_mode='HTML')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

