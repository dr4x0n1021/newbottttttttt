
# Reklama Oklavchi Bot

Bu bot Telegram guruhlarida reklama xabarlarini aniqlash, ularni ogohlantirish va belgilangan miqdordagi ogohlantirishlardan so'ng guruhdan chetlashtirish (ban qilish) uchun mo'ljallangan.

## Xususiyatlari
- Reklama xabarlarini aniqlaydi.
- Reklama tarqatuvchilarni ogohlantiradi (3 marta).
- 3-chi ogohlantirishdan so'ng foydalanuvchini guruhdan chetlashtiradi (ban).

## Ishga tushirish
1. Loyihani klonlang:
   ```bash
   git clone <repository_url>
   cd reklama_oklavchi_bot
   ```
2. Virtual muhit yarating va faollashtiring:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # `venv\Scripts\activate`  # Windows
   ```
3. Kerakli kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
4. `.env.example` faylini `.env` deb nomlang va ichiga bot tokeningizni kiriting:
   ```
   BOT_TOKEN=8103236910:AAGS4YR_YGEfK3__VDCzYFPPYN1taN5a3rs
   ```
5. Botni ishga tushiring:
   ```bash
   python bot.py
   ```

## Botni guruhga qo'shish
1. Botni guruhga qo'shing.
2. Botni guruhda administrator qiling va unga "xabarlarni o'chirish" va "foydalanuvchilarni chetlashtirish" huquqlarini bering.
