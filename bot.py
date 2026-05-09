
import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ChatPermissions
from collections import defaultdict

load_dotenv()

# Logger sozlamalari
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Reklama ogohlantirishlari uchun lug'at: {chat_id: {user_id: count}}
GROUP_WARNINGS = defaultdict(lambda: defaultdict(int))
MAX_WARNINGS = 3

# Router obyektini yaratish
router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    /start buyrug'iga javob beruvchi handler.
    Foydalanuvchini salomlaydi va bot haqida ma'lumot beradi.
    """
    if message.chat.type == 'private':
        await message.answer(
            f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
            "Men Telegram guruhlarida reklama xabarlarini nazorat qiluvchi botman. "
            "Meni guruhga qo'shib, admin huquqlarini bersangiz (xabarlarni o'chirish va foydalanuvchilarni bloklash), "
            "guruhdagi reklama spamini tozalashga yordam beraman.\n\n"
            "Guruhda reklama tarqatgan foydalanuvchilarni 3 marta ogohlantiraman, so'ngra ularni guruhdan chetlashtiraman."
        )
    else:
        await message.answer("Salom! Men guruhdagi reklama xabarlarini nazorat qilaman. Meni admin qilsangiz, vazifamni bajaraman.")

@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    /help buyrug'iga javob beruvchi handler.
    Botning ishlash tamoyillari va komandalari haqida ma'lumot beradi.
    """
    help_message = (
        "<b>Yordam bo'limi:</b>\n\n"
        "Mening vazifam - Telegram guruhlaringizdagi reklama spamini minimallashtirishdir.\n\n"
        "<b>Qanday ishlayman?</b>\n"
        "1. Meni guruhingizga qo'shing.\n"
        "2. Menga guruhda <b>administrator huquqlarini</b> bering. Ayniqsa, <b>xabarlarni o'chirish</b> va <b>foydalanuvchilarni bloklash</b> ruxsatlari muhim.\n"
        "3. Men guruhdagi barcha yangi xabarlarni kuzataman.\n"
        "4. Agar xabarda reklama belgilari (masalan, linklar, kanal yoki bot userlari) aniqlansa, "
        "o'sha xabarni o'chiraman va foydalanuvchini ogohlantiraman.\n"
        f"5. Foydalanuvchi {MAX_WARNINGS} marta ogohlantirilgach, u guruhdan chetlatiladi.\n\n"
        "<b>Komandalar:</b>\n"
        "/start - Bot haqida qisqa ma'lumot.\n"
        "/help - Ushbu yordam bo'limi.\n\n"
        "Agar savollaringiz bo'lsa, adminga murojaat qiling."
    )
    await message.answer(help_message, parse_mode=ParseMode.HTML)

@router.message(F.text, F.chat.type.in_({'group', 'supergroup'}))
async def handle_group_messages(message: Message) -> None:
    """
    Guruhdagi har bir matnli xabarni tekshiradi.
    Reklama tarqatuvchilarni aniqlaydi va chora ko'radi.
    """
    if message.from_user is None or message.from_user.is_bot:
        return # Botlardan kelgan xabarlarni e'tiborsiz qoldirish

    # Oddiy reklama belgilari: URL, @user, t.me/qanaqadir_kanal
    is_promo = False
    if message.entities:
        for entity in message.entities:
            # URL, text_link, mention yoki cashtag (t.me bilan boshlanuvchi linklar ham)
            if entity.type in ['url', 'text_link', 'mention', 'cashtag'] or \
               (entity.type == 'text_mention' and entity.user and entity.user.is_bot): # bot mention
                is_promo = True
                break
            if entity.type == 'tg_url' or entity.type == 'url' and ('t.me/' in message.text[entity.offset:entity.offset+entity.length] or '@' in message.text[entity.offset:entity.offset+entity.length]):
                is_promo = True
                break

    if "http" in message.text.lower() or "t.me/" in message.text.lower() or "@" in message.text.lower():
         is_promo = True # Qoshimcha tekshiruv

    if is_promo:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.full_name

        try:
            # Reklama xabarini o'chirish
            await message.delete()
            logger.info(f"Chat {chat_id}: Reklama xabar o'chirildi. Foydalanuvchi: {user_name} ({user_id})")

            GROUP_WARNINGS[chat_id][user_id] += 1
            warnings_count = GROUP_WARNINGS[chat_id][user_id]

            if warnings_count >= MAX_WARNINGS:
                # Foydalanuvchini ban qilish
                await message.chat.ban_sender_chat(sender_chat_id=user_id) if message.sender_chat else await message.chat.ban(user_id)
                del GROUP_WARNINGS[chat_id][user_id] # Ogohlantirishlarni qayta tiklash
                await message.answer(
                    f"⚠️ {user_name} (ID: {user_id}) guruhdan chetlatildi. "
                    f"Reklama qoidalarini {MAX_WARNINGS} marta buzdi."
                )
                logger.warning(f"Chat {chat_id}: Foydalanuvchi {user_name} ({user_id}) reklama uchun ban qilindi.")
            else:
                # Ogohlantirish
                await message.answer(
                    f"⚠️ Hurmatli {user_name} ({user_id}), bu guruhda reklama tarqatish taqiqlangan! "
                    f"Sizda {warnings_count}/{MAX_WARNINGS} ogohlantirish mavjud."
                )
                logger.info(f"Chat {chat_id}: Foydalanuvchi {user_name} ({user_id}) ogohlantirildi. Ogohlantirishlar: {warnings_count}")

        except Exception as e:
            logger.error(f"Xabar o'zgartirish yoki foydalanuvchini chetlatishda xato: {e}")
            await message.answer("Menda kerakli ruxsatlar yo'q yoki qandaydir xato yuz berdi. Iltimos, meni admin qiling yoki texnik adminga murojaat qiling.")


async def main() -> None:
    """Botni ishga tushiruvchi asosiy funksiya."""
    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Router'ni Dispatcherga ulash
    dp.include_router(router)

    # Pollingni boshlash
    logger.info("Bot ishga tushirildi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
