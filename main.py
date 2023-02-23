import dp as dp
import equals as equals

# Your code using the python-telegram-bot library
from aiogram import executor
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text, Command
import random
import logging
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
import pymongo

client = pymongo.MongoClient("mongodb+srv://bekslan:1234@cluster0.3hyojvq.mongodb.net/?retryWrites=true&w=majority")
db = client["Beer_DB"]
TOKEN_API = "6263090368:AAE8SPOa_cvkQ7VCjieJrD8ZkWTYQ8yleKo"
HELP_COMMAND = """
/help - list of commands
/start - start the work
/guinness - meet the Guinness
/use - 
"""
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)
collection = db["Beer_Collection"]

async def add_user(username):
    db.users.insert_one({
        "username":username
    })

@dp.message_handler(commands=['create'])
async def handle_create(message: Message, state: FSMContext):
    data = await state.get_data()
    document = {
        "type_id": message.from_user.id,
        "text": data.get("text")
    }
    result = collection.insert_one(document)
    await message.answer("Record created with ID: {result.inserted_id}")


async def read_record(message: Message):
    result = collection.find_one({"type_id": message.from_user.id})
    if result:
        await message.answer(result["text"])
    else:
        await message.answer("Record not found")

async def update_record(message: Message, state: FSMContext):
    data = await state.get_data()
    result = collection.update_one(
        {"type_id": message.from_user.id},
        {"$set": {"text": data.get("text")}}
    )
    if result.modified_count > 0:
        await message.answer("Record updated")
    else:
        await message.answer("Record not found")


async def delete_record(message: Message):
    result = collection.delete_one({"type_id": message.from_user.id})
    if result.deleted_count > 0:
        await message.answer("Record deleted")
    else:
        await message.answer("Record not found")




arr_photos = [
    "https://www.eurosama.dk/includes/upload/images/AFA35168-86BB-4960-9C1A-FD823CD74A80___900.jpg",
    "https://i.pinimg.com/736x/ea/4f/65/ea4f6561dc39cd8bef9f8fc61614aaa9--polish-beer-polish-food.jpg",
    "https://i.pinimg.com/736x/7b/a2/20/7ba220695442977ec63650ca319d990b--ibiza-nightlife-ibiza-style.jpg"]

photos = dict(zip(arr_photos, ['Amber beer', 'Zywiec beer', 'Corona']))


kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('/help')
b2 = KeyboardButton('/start')
b3 = KeyboardButton('/guinness')
b3 = KeyboardButton('Best photos')
b4 = KeyboardButton('use')
kb.add(b1).add(b2).add(b3).add(b4)

kb_photo = ReplyKeyboardMarkup(resize_keyboard=True)
bp1 = KeyboardButton(text='Heineken')
bp2 = KeyboardButton('Main Page')
kb_photo.add(bp1, bp2)

crud = ReplyKeyboardMarkup(resize_keyboard=True)
cd1 = KeyboardButton(text='create')
cd2 = KeyboardButton(text='read')
cd3 = KeyboardButton(text='update')
cd4 = KeyboardButton(text='delete')
crud.add(cd1, cd2, cd3, cd4)

ikb = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text='Guinness',
                           url="https://www.guinness.com/en/beers/guinness-draught")

ikb.add(ib1)

iks = InlineKeyboardMarkup(row_width=2)
ib3 = InlineKeyboardButton(text='Next photo',
                           callback_data='next')
iks.add(ib3)


async def on_startup(_):
    print('bot is ready')


async def send_random(message: types.Message):
    random_photo = random.choice(list(photos.keys()))
    await bot.send_photo(chat_id=message.chat.id,
                         photo=random_photo,
                         caption=photos[random_photo],
                         reply_markup=iks)


@dp.message_handler(Text(equals="use"))
async def open_kb(message: types.Message):
    await message.answer(text='use crud operations',
                         reply_markup=crud)


@dp.message_handler(Text(equals="Best photos"))
async def open_kb_photo(message: types.Message):
    await message.answer(text='to generate best beer photos - click the button "Heineken"',
                         reply_markup=kb_photo)
    await message.delete()


@dp.message_handler(Text(equals="create"))
async def handle_create(message: Message, state: FSMContext):
    await message.answer("Enter text:")
    await state.set_state("create")
    await state.update_data(text=message.text)


@dp.message_handler(Text(equals="Heineken"))
async def send_random_photo(message: types.Message):
    await send_random(message)


@dp.message_handler(Text(equals="Main Page"))
async def open_kb(message: types.Message):
    await message.answer(text='Greeting in Main Page',
                         reply_markup=kb)
    await message.delete()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text=HELP_COMMAND)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="<em>Hello! Welcome to world of Beer </em>",
                           parse_mode="HTML",
                           reply_markup=kb)
    username = message.from_user.username
    await add_user(username)


@dp.message_handler(commands=['guinness'])
async def photo_command(message: types.Message):
    await bot.send_photo(message.from_user.id,
                         photo='https://online.idea.rs/images/products/460/460103554_1l.jpg?1654784110',
                         caption='The most popular beer in the world',
                         reply_markup=ikb)


@dp.callback_query_handler()
async def callback_random_photo(callback: types.CallbackQuery):
    await send_random(message=callback.message)
    await callback.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
