from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import random
import time

# Bot API Token
TOKEN = 'YOUR_BOT_API_TOKEN'

# Basit veritabanı - Kullanıcıların bilgilerini saklamak için bir sözlük kullanıyoruz
user_data = {}

# /start komutu
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Merhaba! HanCoin Airdrop oyununa hoş geldiniz! Katılmak için /join komutunu kullanın."
    )

# /join komutu - Katılım için
def join(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id in user_data:
        update.message.reply_text("Zaten katıldınız!")
    else:
        user_data[user_id] = {
            "coins": 0,
            "last_claim_time": 0
        }
        update.message.reply_text("Başarıyla HanCoin Airdrop oyununa katıldınız! Şimdi günlük ödülünüzü almak için /claim komutunu kullanabilirsiniz.")

# /claim komutu - Günlük ödül kazanma
def claim(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id not in user_data:
        update.message.reply_text("Öncelikle /join komutuyla katılmanız gerekiyor.")
        return
    
    current_time = time.time()
    last_claim_time = user_data[user_id]["last_claim_time"]
    
    # Günlük ödül için 24 saat beklenmesi gerekiyor
    if current_time - last_claim_time < 86400:
        update.message.reply_text("Henüz günlük ödülünüzü alamazsınız. Lütfen 24 saat bekleyin.")
        return
    
    # Ödül miktarı
    reward = random.randint(1, 10)  # 1 ile 10 arasında rastgele HanCoin
    user_data[user_id]["coins"] += reward
    user_data[user_id]["last_claim_time"] = current_time
    
    update.message.reply_text(f"Tebrikler! {reward} HanCoin kazandınız! Şu an {user_data[user_id]['coins']} HanCoin'iniz var.")

# /balance komutu - Kullanıcının bakiyesi
def balance(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id not in user_data:
        update.message.reply_text("Öncelikle /join komutuyla katılmanız gerekiyor.")
        return
    
    update.message.reply_text(f"Şu anda {user_data[user_id]['coins']} HanCoin'iniz var.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Komutları bağlayalım
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("claim", claim))
    dp.add_handler(CommandHandler("balance", balance))

    # Botu başlatalım
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
