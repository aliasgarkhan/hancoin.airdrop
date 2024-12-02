import json
import random
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Bot API Token
TOKEN = 'YOUR_BOT_API_KEY'

# Veritabanı için JSON dosyasını yükleme
def load_data():
    try:
        with open('players.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Veritabanına verileri kaydetme
def save_data(data):
    with open('players.json', 'w') as f:
        json.dump(data, f)

# Referal linki oluşturma
def generate_referral_link(user_id):
    return f"https://t.me/{user_id}?ref={user_id}"

# Kullanıcı ekleme
def add_player(user_id, username, referrer_id=None):
    data = load_data()
    referral_link = generate_referral_link(user_id)
    
    if user_id not in data:
        data[user_id] = {
            "username": username,
            "coins": 0,
            "last_claim_time": 0,
            "referrer": referrer_id,
            "referral_link": referral_link,
            "referred_players": []
        }
        # Referans varsa, referer'a 100 puan ekle
        if referrer_id:
            if referrer_id in data:
                data[referrer_id]["coins"] += 100
            else:
                data[referrer_id] = {
                    "username": "",
                    "coins": 100,
                    "last_claim_time": 0,
                    "referrer": None,
                    "referral_link": "",
                    "referred_players": []
                }
        save_data(data)

# /start komutu
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Merhaba! HanCoin Airdrop oyununa hoş geldiniz! Katılmak için /join komutunu kullanın."
    )

# /join komutu - Katılım için
def join(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    referrer_id = context.args[0] if context.args else None  # Argüman olarak referer alıyoruz

    if user_id in load_data():
        update.message.reply_text("Zaten katıldınız!")
    else:
        add_player(user_id, username, referrer_id)
        update.message.reply_text(f"Başarıyla katıldınız! Referans linkiniz: {generate_referral_link(user_id)}")

# /claim komutu - Günlük ödül kazanma
def claim(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    data = load_data()

    if user_id not in data:
        update.message.reply_text("Öncelikle /join komutuyla katılmanız gerekiyor.")
        return

    current_time = time.time()
    last_claim_time = data[user_id]["last_claim_time"]
    
    # Günlük ödül için 24 saat beklenmesi gerekiyor
    if current_time - last_claim_time < 86400:
        update.message.reply_text("Henüz günlük ödülünüzü alamazsınız. Lütfen 24 saat bekleyin.")
        return
    
    # Ödül miktarı
    reward = random.randint(1, 10)  # 1 ile 10 arasında rastgele HanCoin
    data[user_id]["coins"] += reward
    data[user_id]["last_claim_time"] = current_time
    save_data(data)

    update.message.reply_text(f"Tebrikler! {reward} HanCoin kazandınız! Şu an {data[user_id]['coins']} HanCoin'iniz var.")

# /balance komutu - Kullanıcının bakiyesi
def balance(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    data = load_data()

    if user_id not in data:
        update.message.reply_text("Öncelikle /join komutuyla katılmanız gerekiyor.")
        return

    update.message.reply_text(f"Şu anda {data[user_id]['coins']} HanCoin'iniz var.")

# /leaderboard komutu - Liderlik tablosu
def leaderboard(update: Update, context: CallbackContext):
    data = load_data()
    # Verileri puana göre sıralıyoruz
    leaderboard_data = sorted(data.items(), key=lambda x: x[1]["coins"], reverse=True)[:100]

    leaderboard_text = "🏆 **Leaderboard** 🏆\n\n"
    for i, (user_id, player_data) in enumerate(leaderboard_data):
        leaderboard_text += f"{i+1}. {player_data['username']} - {player_data['coins']} HanCoin\n"

    update.message.reply_text(leaderboard_text)

# Ana işlev
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Komutları bağlayalım
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("claim", claim))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))

    # Botu başlatalım
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
