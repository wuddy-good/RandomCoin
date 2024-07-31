import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import urllib.parse

TOKEN = '6026382077:AAF2GqgebCbvy-hucLUs7L9BZOE8OfZHeIY'
bot = telebot.TeleBot(TOKEN)

base_url = 'https://randomgamebot.site'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None
    print(referral_code)

    user = message.from_user
    photos = bot.get_user_profile_photos(user.id)

    if photos.total_count > 0:
        photo_file = photos.photos[0][-1].file_id  # Take the largest photo
        photo = bot.get_file(photo_file)
        photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo.file_path}"
    else:
        photo_url = 'https://randomgamebot.site/static/icons/user_avatar.svg'

    user_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'photo_url': photo_url,
        'is_premium': user.is_premium if hasattr(user, 'is_premium') else False,
        'referral_code': referral_code
    }

    query_string = urllib.parse.urlencode(user_data)
    web_app_url = f"{base_url}/user?{query_string}"

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Receive coins", web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton("Join community", url="https://t.me/randomcoingame")]
    ])

    # Send the welcome message with the attached image
    with open('image.jpeg', 'rb') as image:
        caption = (
            "Test your luck and get coins, log in every day to the game to get a random amount of coins\n\n"
            "Invite your friends and get 100% of their first claim and 10% of all next claims\n\n"
            "Wait for the airdrop 🎰"
        )
        bot.send_photo(
            chat_id=message.chat.id,
            photo=image,
            caption=caption,
            reply_markup=markup
        )



if __name__ == '__main__':
    bot.polling()
