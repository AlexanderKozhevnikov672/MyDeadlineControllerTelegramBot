import datetime

from aiogram import Bot, Dispatcher, executor, types
from deadlineUser import DeadlineUser, Event

DEFAULT_EARLIEST = 5
TOKEN = None
with open("token.txt") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
dataBase = dict()


async def onStartup(_):
    print("Bot is online now!")


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    userId = message.from_user.id
    userFullName = message.from_user.full_name
    args = message.text.split()
    if len(args) != 1:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    if args[0] == '/start':
        initDeadlineUser(userId)
    answer = f'''
Hello, {userFullName}! That's what I can do:

/addDeadline name date* - add new deadline
/delDeadline name - del deadline
/earliest (num) - show earliest deadlines
/changeDate name newDate* - change deadline date
/changeName oldName newName - change deadline name
/today - show today deadlines
/getNames date* - show date deadlines
/getDate name - show date of deadline
/clear - del all deadlines
/delPast - del all past deadlines
/getId - show your id
/subscribe userId - subscribe other user
/unsubscribe userId - unsubscribe other user
/sendDeadline userId name date* - add deadline to subscriber
/forget - forget your id

*date format: YYYY MM DD'''
    await bot.send_message(userId, answer)


def getEventDate(args):
    eventYear, eventMounth, eventDay = args
    if not eventYear.isdigit() or not eventMounth.isdigit() or\
       not eventYear.isdigit():
        return "Date args should be integer!"
    eventYear = int(eventYear)
    eventMounth = int(eventMounth)
    eventDay = int(eventDay)
    try:
        eventDate = datetime.date(eventYear, eventMounth, eventDay)
    except Exception:
        return "Wrong date format!"
    return eventDate


def findUser(userId):
    return userId in dataBase.keys()


def initDeadlineUser(userId):
    if not findUser(userId):
        dataBase[userId] = DeadlineUser()


def eventsToAnswer(events):
    if len(events) == 0:
        return "Nothing found!\n"
    answer = ""
    for event in events:
        answer += str(event) + "\n"
    return answer


@dp.message_handler(commands=['addDeadline'])
async def commandAddDeadline(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 5:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    eventName = args[1]
    eventDate = getEventDate(args[2:])
    if isinstance(eventDate, str):
        await bot.send_message(userId, eventDate)
        return
    initDeadlineUser(userId)
    if dataBase[userId].findEventName(eventName):
        await bot.send_message(userId, "This name is already in use!")
        return
    dataBase[userId].addNewEvent(eventName, eventDate)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['delDeadline'])
async def commandDelDeadline(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    eventName = args[1]
    initDeadlineUser(userId)
    if not dataBase[userId].findEventName(eventName):
        await bot.send_message(userId, "There is not such name!")
        return
    dataBase[userId].delEvent(eventName)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['earliest'])
async def commandEarliest(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) > 2:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    if len(args) == 2:
        earliestNum = args[1]
        if not earliestNum.isdigit() or int(earliestNum) <= 0:
            await bot.send_message(userId,
                                   "Arg number should be positive integer!")
            return
        earliestNum = int(earliestNum)
    else:
        earliestNum = DEFAULT_EARLIEST
    initDeadlineUser(userId)
    events = dataBase[userId].getEarliestEvents(earliestNum)
    await bot.send_message(userId, eventsToAnswer(events))


@dp.message_handler(commands=['changeDate'])
async def commandChangeDate(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 5:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    eventName = args[1]
    newEventDate = getEventDate(args[2:])
    if isinstance(newEventDate, str):
        await bot.send_message(userId, newEventDate)
        return
    initDeadlineUser(userId)
    if not dataBase[userId].findEventName(eventName):
        await bot.send_message(userId, "There is not such name!")
        return
    dataBase[userId].changeEventDate(eventName, newEventDate)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['changeName'])
async def commandChangeName(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 3:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    eventOldName = args[1]
    eventNewName = args[2]
    initDeadlineUser(userId)
    if not dataBase[userId].findEventName(eventOldName):
        await bot.send_message(userId, "There is not such old name!")
        return
    if dataBase[userId].findEventName(eventNewName):
        await bot.send_message(userId, "This new name is already in use!")
        return
    dataBase[userId].changeEventName(eventOldName, eventNewName)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['today'])
async def commandToday(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 1:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    initDeadlineUser(userId)
    date = datetime.date.today()
    events = dataBase[userId].getDateEvents(date)
    await bot.send_message(userId, eventsToAnswer(events))


@dp.message_handler(commands=['getNames'])
async def commandGetNames(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 4:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    date = getEventDate(args[1:])
    if isinstance(date, str):
        await bot.send_message(userId, date)
        return
    initDeadlineUser(userId)
    events = dataBase[userId].getDateEvents(date)
    await bot.send_message(userId, eventsToAnswer(events))


@dp.message_handler(commands=['getDate'])
async def commandGetDate(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    name = args[1]
    initDeadlineUser(userId)
    if not dataBase[userId].findEventName(name):
        await bot.send_message(userId, "There is not such name!")
        return
    date = dataBase[userId].getEventDate(name)
    await bot.send_message(userId, str(date))


@dp.message_handler(commands=['clear'])
async def commandClear(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 1:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    initDeadlineUser(userId)
    dataBase[userId].clearEvents()
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['delPast'])
async def commandDelPast(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 1:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    initDeadlineUser(userId)
    date = datetime.date.today()
    dataBase[userId].delEventsBeforeDate(date)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['getId'])
async def commandGetId(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 1:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    await bot.send_message(userId, str(userId))


@dp.message_handler(commands=['subscribe'])
async def commandSubscribe(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    subscriptionId = args[1]
    if not subscriptionId.isdigit():
        await bot.send_message(userId, "Id should be integer!")
        return
    subscriptionId = int(subscriptionId)
    initDeadlineUser(userId)
    if not findUser(subscriptionId):
        await bot.send_message(userId,
                               "There is not such user to subscribe to!")
        return
    if dataBase[userId].findSubscription(subscriptionId):
        await bot.send_message(userId,
                               "You have already subscribed to this user!")
        return
    try:
        await bot.send_message(subscriptionId, f"{userId} subscribed to you!")
    except Exception:
        await bot.send_message(userId, "Wrong subscription id!")
        return
    dataBase[userId].subscribe(subscriptionId)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['unsubscribe'])
async def commandUnsubscribe(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    subscriptionId = args[1]
    if not subscriptionId.isdigit():
        await bot.send_message(userId, "Id should be integer!")
        return
    subscriptionId = int(subscriptionId)
    initDeadlineUser(userId)
    if not findUser(subscriptionId):
        await bot.send_message(userId,
                               "There is not such user to unsubscribe from!")
        return
    if not dataBase[userId].findSubscription(subscriptionId):
        await bot.send_message(userId,
                               "You have not subscribed to this user yet!")
        return
    try:
        await bot.send_message(subscriptionId,
                               f"{userId} unsubscribed from you!")
    except Exception:
        await bot.send_message(userId, "Wrong unsubscription id!")
        return
    dataBase[userId].unsubscribe(subscriptionId)
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['sendDeadline'])
async def commandSendDeadline(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 6:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    subscriberId = args[1]
    if not subscriberId.isdigit():
        await bot.send_message(userId, "Id should be integer!")
        return
    subscriberId = int(subscriberId)
    eventName = args[2]
    eventDate = getEventDate(args[3:])
    if isinstance(eventDate, str):
        await bot.send_message(userId, eventDate)
        return
    initDeadlineUser(userId)
    if not findUser(subscriberId):
        await bot.send_message(userId,
                               "There is not such user to send deadline!")
        return
    if not dataBase[subscriberId].findSubscription(userId):
        await bot.send_message(userId,
                               "This user have not subscribed to you yet!")
        return
    if dataBase[subscriberId].findEventName(eventName):
        await bot.send_message(userId,
                               "This user have already got such deadline!")
        return
    try:
        await bot.send_message(subscriberId, f"{userId} send deadline to you!")
    except Exception:
        await bot.send_message(userId, "Wrong subscriber id!")
        return
    dataBase[subscriberId].addNewEvent(eventName, eventDate)
    await bot.send_message(subscriberId, str(Event(eventName, eventDate)))
    await bot.send_message(userId, "Done!")


@dp.message_handler(commands=['forget'])
async def commandForget(message: types.Message):
    userId = message.from_user.id
    args = message.text.split()
    if len(args) != 1:
        await bot.send_message(userId, "Wrong number of command args!")
        return
    dataBase.pop(userId, None)
    await bot.send_message(userId, "Done!")


@dp.message_handler()
async def unknownCommand(message: types.Message):
    userId = message.from_user.id
    await bot.send_message(userId, "There is not such command!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=onStartup)
