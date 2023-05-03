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
aliveAnalyzings = set()


@dp.message(Command("start"))
async def cmdStart(message: types.Message):
    await message.answer("🔥Welcome to the <b>Codeforces Coach Bot!</b>🔥\nI will help you to analyze your CF rounds. \
Send me your handle via command <CODE>/handle</CODE>", parse_mode="HTML")


@dp.message(Command("handle"))
async def setHandle(message: types.Message, command: CommandObject):
    id = message.from_user.id
    if not command.args:
        await message.answer("Error! Empty handle, try again")
        return
    users[id] = CF()
    usersKeySecret[id] = ['', '']
    if not users[id].setHandle(command.args):
        await message.answer("Wrong handle, try again, bro")
    else:
        mssg = "<b>Success!</b>\nWelcome, " + '<i>' + command.args + '</i>' + '\n'
        mssg += "Current rating: " + '<CODE>' + str(users[id].getRating()) + '</CODE>'
        await message.answer(mssg, parse_mode='HTML')
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
    mssg += '<i>Note: To analyze your friend or anybody on codeforces use <CODE>/analyze [handle]</CODE>'
    await message.answer(mssg, parse_mode='HTML')


@dp.message(Command("analyze"))
async def getAnalysis(message: types.Message, command: CommandObject):
    if command.args:
        if command.args not in users:
            users[command.args] = CF()
        if not users[command.args].setHandle(command.args):
            await message.answer('Incorrect! Try again')
            return
        mssg = await message.answer("<i>Analyzing...</i>", parse_mode='HTML')
        gen = users[command.args].startAnalyzing()
        cnt = 0
        aliveAnalyzings.add(command.args)
        for _ in gen:
            with open("codeforces/" + command.args + '/' + command.args + '.txt', 'r') as f:
                await mssg.edit_text(f.read(), parse_mode='HTML')
            if cnt % 10 == 9:
                f = open("codeforces/" + command.args + '/' + command.args + '.txt', 'w')
                f.write('')
                f.close()
                mssg = await message.answer("<i>Analyzing...</i>", parse_mode='HTML')
            cnt += 1
        # with open("codeforces/" + command.args + '/' + command.args + '.txt', 'r') as f:
        #     await message.answer(f.read(), parse_mode='HTML')
    else:
        aliveAnalyzings.add(message.from_user.id)
        mssg = await message.answer("<i>Analyzing...</i>", parse_mode='HTML')
        gen = users[message.from_user.id].startAnalyzing()
        for _ in gen:
            with open("codeforces/" + users[message.from_user.id].getHandle() + '/' + users[
                message.from_user.id].getHandle() + '.txt', 'r') as f:
                await mssg.edit_text(f.read(), parse_mode='HTML')


@dp.message(Command("stop"))
async def stopAnalyzing(message: types.Message):
    for id in aliveAnalyzings:
        users[id].goStop()
    aliveAnalyzings.clear()
    await message.answer("<CODE>Analysis stopped by you!</CODE>", parse_mode='HTML')


@dp.message(Command("help"))
async def cmdHelp(message: types.Message):
    await message.answer("""<CODE>/handle [your nick]</CODE> — set handle
<CODE>/key</CODE> — set [your key] (codeforces API)
<CODE>/secret</CODE> — set [your secret] (codeforces API)
<CODE>/friends</CODE> — display all of your friends (are available only via CF API)
<CODE>/analyze [handle]</CODE> — start analyzing account. if handle missed -- will analyze your account. <b>WARNING:</b> First running can take a few minutes!
<CODE>/stop</CODE> — stop analyzing
""", parse_mode='HTML')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
