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
    users[(id, id)] = CF(id)
    usersKeySecret[id] = ['', '']
    if not users[(id, id)].setHandle(command.args):
        await message.answer("Wrong handle, try again, bro")
    else:
        mssg = "<b>Success!</b>\nWelcome, " + '<i>' + command.args + '</i>' + '\n'
        mssg += "Current rating: " + '<CODE>' + str(users[(id, id)].getRating()) + '</CODE>'
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
        if users[(message.from_user.id, message.from_user.id)].setKeyAndSecret(usersKeySecret[message.from_user.id][0],
                                                                               usersKeySecret[message.from_user.id][1]):
            await message.answer("Done! Now you can check all available commands via /help")
        else:
            await message.answer("Key or Secret are incorrect! Check them")


@dp.message(Command("friends"))
async def getFriends(message: types.Message):
    friends = users[(message.from_user.id, message.from_user.id)].getFriendsList()
    mssg = ''
    cnt = 0
    for friend in friends:
        mssg += str(cnt + 1) + '. ' + friend + '\n'
        cnt += 1
    mssg += '<i>Note</i>: To analyze your friend or anybody on codeforces use <CODE>/analyze [handle]</CODE>'
    await message.answer(mssg, parse_mode='HTML')


@dp.message(Command("analyze"))
async def getAnalysis(message: types.Message, command: CommandObject):
    if command.args:
        if (message.from_user.id, command.args) not in users:
            users[(message.from_user.id, command.args)] = CF(message.from_user.id)
        if not users[(message.from_user.id, command.args)].setHandle(command.args):
            await message.answer('Incorrect! Try again')
            return
        mssg = await message.answer("<i>Analyse...</i>", parse_mode='HTML')
        gen = users[(message.from_user.id, command.args)].startAnalyzing()
        cnt = 0
        aliveAnalyzings.add((message.from_user.id, command.args))
        for _ in gen:
            with open("codeforces/" + command.args + '/' + str(message.from_user.id) + '.txt', 'r') as f:
                await mssg.edit_text(f.read(), parse_mode='HTML')
            if cnt % 10 == 9:
                f = open("codeforces/" + command.args + '/' + str(message.from_user.id) + '.txt', 'w')
                f.write('')
                f.close()
                mssg = await message.answer("<i>Analyse...</i>", parse_mode='HTML')
            cnt += 1
    else:
        aliveAnalyzings.add((message.from_user.id, message.from_user.id))
        mssg = await message.answer("<i>Analyse...</i>", parse_mode='HTML')
        gen = users[(message.from_user.id, message.from_user.id)].startAnalyzing()
        cnt = 0
        for _ in gen:
            with open(
                    "codeforces/" + users[(message.from_user.id, message.from_user.id)].getHandle() + '/' + str(
                        message.from_user.id) + '.txt',
                    'r') as f:
                await mssg.edit_text(f.read(), parse_mode='HTML')
            if cnt % 10 == 9:
                f = open(
                    "codeforces/" + users[(message.from_user.id, message.from_user.id)].getHandle() + '/' + str(
                        message.from_user.id) + '.txt',
                    'w')
                f.write('')
                f.close()
                mssg = await message.answer("<i>Analyse...</i>", parse_mode='HTML')
            cnt += 1


@dp.message(Command("stop"))
async def stopAnalyzing(message: types.Message, command: CommandObject):
    tgId = message.from_user.id
    answer = 'Analysis of <CODE>'
    if command.args:
        if (tgId, command.args) in aliveAnalyzings:
            users[(tgId, command.args)].goStop()
            aliveAnalyzings.remove((tgId, command.args))
            answer += command.args + '</CODE> stopped'
        elif (tgId, tgId) in aliveAnalyzings and command.args == users[(tgId, tgId)].getHandle():
            users[(tgId, tgId)].goStop()
            aliveAnalyzings.remove((tgId, tgId))
            answer += users[(tgId, tgId)].getHandle() + '</CODE> stopped'
        else:
            answer = 'Wrong handle! Use <CODE>/process</CODE> to see all alive processes'
    else:
        toRemove = set()
        for (id_req, id) in aliveAnalyzings:
            if id_req == message.from_user.id:
                users[(tgId, id)].goStop()
                toRemove.add((id_req, id))
        for delete in toRemove:
            aliveAnalyzings.remove(delete)
        answer = "<CODE>All analysis stopped by you!</CODE>"
    await message.answer(answer, parse_mode='HTML')


@dp.message(Command("process"))
async def allProcess(message: types.Message):
    mssg = ''
    cnt = 0
    for (id_req, id) in aliveAnalyzings:
        if id_req == message.from_user.id:
            cnt += 1
            mssg += str(cnt) + '. <CODE>'
            if id == message.from_user.id:
                mssg += users[(message.from_user.id, id)].getHandle()
            else:
                mssg += id
            mssg += '</CODE>\n'
    if len(mssg) == 0:
        mssg = '<CODE>Zero analysis now</CODE>'
    await message.answer(mssg, parse_mode='HTML')


@dp.message(Command("train"))
async def train(message: types.Message):
    id = message.from_user.id
    if (id, id) not in users:
        await message.answer("Error! First of all set your handle <CODE>/handle [ur nick]</CODE>", parse_mode='HTML')
        return
    mssg = await message.answer("<i>Analyse 10 last rounds...</i>", parse_mode='HTML')
    gen = users[(id, id)].startAnalyzing(10, True)
    for _ in gen:
        with open("codeforces/" + users[(id, id)].getHandle() + '/' + str(id) + '.txt', 'r') as f:
            await mssg.edit_text(f.read(), parse_mode='HTML')
    badTask = None
    with open("codeforces/" + users[(id, id)].getHandle() + '/' + str(id) + '.txt', 'r') as f:
        txt = f.read().splitlines()[-1]
        await message.answer('<b>' + txt + '</b>', parse_mode='HTML')
        badTask = txt[-1]
    tasks = users[(id, id)].trainMode(badTask)
    url = 'https://codeforces.com/contest/'
    answer = ''
    cnt = 1
    for tsk in tasks:
        answer += str(cnt) + '. ' + '<a href="' + url + str(tsk['contestId']) + '/problem/' + tsk['index'] + '">' + str(
            tsk['contestId']) + tsk['index'] + '</a>\n'
        cnt += 1
    await message.answer(answer, parse_mode='HTML')


@dp.message(Command("help"))
async def cmdHelp(message: types.Message):
    await message.answer("""<CODE>/start</CODE> — init bot work
<CODE>/help</CODE> — displays all commands
<CODE>/handle [your nick]</CODE> — set handle
<CODE>/key</CODE> — set [your key] (codeforces API)
<CODE>/secret</CODE> — set [your secret] (codeforces API)
<CODE>/friends</CODE> — display all of your friends (available only via CF API)
<CODE>/analyze [handle]</CODE> — start analyse account. if handle missed -- will analyze your account. <b>WARNING:</b> First running can take a few minutes!
<CODE>/train</CODE> — available only for self-using (<i>you should set your handle firstly</i>)
<CODE>/process</CODE> — displays all running analysis
<CODE>/stop [num]</CODE> — stop analyse. If <CODE>[num]</CODE> is empty all analysis stopes. Else <CODE>[num]</CODE> should contain codeforces handle 
""", parse_mode='HTML')


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
