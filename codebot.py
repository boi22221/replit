import os
import io
import asyncio
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import telegram.error
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Không tìm thấy biến môi trường BOT_TOKEN")

qr_image_path = r'D:\BOT TELEGRAM\qr_vietcombank.jpg'
account_name = "Nguyễn Văn A"
account_no = "123456789"
bank_name = "Vietcombank"
price_table = {
    '1': '169.000đ',
    '3': '369.000đ',
    '6': '569.000đ',
    '12': '869.000đ',
}
price_text = (
    "Chọn gói Telegram Premium:\n"
    "1 Tháng - 169.000đ\n"
    "3 Tháng - 369.000đ\n"
    "6 Tháng - 569.000đ\n"
    "12 Tháng - 869.000đ\n"
)

users = {}
orders = {}
qr_image_data = None

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, text: str):
    print(f"[Notify admin disabled] {text}")

def format_user(user):
    username = f"@{user.username}" if user.username else "(chưa có username)"
    return f"{user.id} {username}"

async def load_qr_image():
    global qr_image_data
    if qr_image_data is None:
        with open(qr_image_path, 'rb') as f:
            qr_image_data = io.BytesIO(f.read())
    qr_image_data.seek(0)
    return qr_image_data

async def safe_edit_message_text(query, text, reply_markup=None, parse_mode=None):
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except telegram.error.BadRequest as e:
        if 'Message is not modified' in str(e):
            pass
        else:
            raise

def get_main_inline_menu():
    keyboard = [
        [InlineKeyboardButton("🚀 Telegram Premium", callback_data='premium')],
        [InlineKeyboardButton("🏦 Bank Online", callback_data='bank')],
        [
            InlineKeyboardButton("🎯 Báo Lỗi", url='https://t.me/lamgicoloi'),
            InlineKeyboardButton("☎️ ADMIN", url='https://t.me/boibank6789'),
            InlineKeyboardButton("💰 Nạp Tiền", callback_data='nap_tien'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_reply_keyboard():
    keyboard = [
        [KeyboardButton("🏠 Home")],
        [KeyboardButton("🆔 Check ID"), KeyboardButton("🛟 Support 24/7")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users[user.id] = {
        "username": user.username,
        "balance": users.get(user.id, {}).get("balance", 0),
    }
    await notify_admin(context, f"Người dùng {format_user(user)} đã bắt đầu bot bằng lệnh /start.")

    text = (
        "👋 *Shop Bảo Bối* xin chào!\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "• Ngoài bán mình cho tư bản ra thì nay em Bối còn bán thêm cả Bank Online & Tele Premium.\n"
        "🔰 Bank Online: Giao dịch nhanh chóng, an toàn, giá rẻ!\n"
        "🔰 Tele Premium: Nick xịn, mõm hay, nâng tầm đẳng cấp!\n"
    )
    await update.message.reply_text(
        text, reply_markup=get_main_inline_menu(), parse_mode='Markdown'
    )
    await update.message.reply_text(
        "Chọn một tùy chọn từ menu dưới đây:", reply_markup=get_reply_keyboard()
    )

async def handle_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_check_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = users.get(user.id, {"balance": 0})
    profile = (
        "👤 *Hồ Sơ Của Bạn* 👤\n\n"
        f"🔹 Tên: {user.first_name}\n"
        f"🔹 Usebname: @{user.username}\n"
        f"🔹 ID: {user.id}\n\n"
        f"Số dư TK: {user_data.get('balance', 0)} tháng Premium\n"
        "📋 Lịch sử mua hàng:\n"
    )
    keyboard = [
        [InlineKeyboardButton("↩️ Quay lại", callback_data='main_menu')]
    ]
    await update.message.reply_text(profile, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support = (
        "📚 *Hướng dẫn sử dụng Bot* 📚\n\n"
        "• Shop mình không chắc hàng rẻ nhất, nhưng dịch vụ thì đỉnh cao , cam kết không làm bạn đợi quá 5 giây là “done tiền” nha! 😎\n"
        "1️⃣ Chọn đúng sản phẩm mình muốn (đừng nhầm sang món khác nha!)\n"
        "2️⃣ Xác nhận thanh toán hóa đơn (đừng quên nhá, kẻo Shop buồn!)\n"
        "3️⃣ Quét QR hoặc thanh toán thủ công, cái nào tiện thì làm thôi!\n"
        "4️⃣ Kiểm tra kỹ lại: số tài khoản, tên người nhận, số tiền cho chuẩn nhé!\n"
        "_Lưu ý: Nội dung chuyển khoản là 10 số ID của bạn (bấm nút Check ID để lấy liền)!_\n"
        "5️⃣ Hoàn tất thanh toán, xong rồi bạn chỉ việc hóng hàng về thôi! 🎉\n\n"
        "Nếu “lỡ tay” sai sót gì, nhắn ngay ADMIN @boi39 để được cứu trợ kịp thời!\n " 
    )
    keyboard = [
        [InlineKeyboardButton("↩️ Quay lại", callback_data='main_menu')]
    ]
    await update.message.reply_text(support, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_nap_tien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await notify_admin(context, f"Người dùng {format_user(user)} đã xem thông tin Nạp Tiền.")

    photo = await load_qr_image()
    bank_info = (
        "💳 Thông tin chuyển khoản:\n"
        f"- Số tài khoản: {account_no}\n"
        f"- Chủ tài khoản: {account_name}\n"
        f"- Ngân hàng: {bank_name}\n\n"
        "⚠️ Vui lòng quét mã QR hoặc dùng thông tin trên để chuyển khoản !!.\n"
    )

    keyboard = [
        [InlineKeyboardButton("✅   DONE   ✅", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=photo,
        caption=bank_info,
        reply_markup=reply_markup
    )

async def handle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "🚀 *TELEGRAM PREMIUM–LỢI ÍCH SIÊU XỊN*🚀\n\n"
        "• 📤 *Gửi file 4GB* – tha hồ gửi phim dài tập không lo bóp file.\n"
        "• ⚡️ *Tải xuống nhanh* – không giới hạn, khỏi đợi mòn mỏi.\n"
        "• 🎙️ *Voice thành chữ* – lười nghe? Đọc luôn cho tiện mình toàn thế.\n"
        "• 🖼️ *Avatar động đậy* – nổi bật giữa rừng avatar đứng im.\n"
        "• 🧼 *Không quảng cáo* – tám chuyện không bị làm phiền.\n"
        "• 🤫 *Ẩn nhãn bot* – chuyển tiếp trông như “tự nghĩ ra”, sang xịn hẳn.\n"
        "• 💎 *Sticker xịn, emoji chất* – tung ra là đối phương cười xỉu.\n"
        "• 📈 *Tăng giới hạn nhóm, kênh, ghim,...* – dành cho hội nhiều bạn, nhiều drama.\n"
    )
    keyboard = [
        [
            InlineKeyboardButton("1 Tháng", callback_data='order_premium_1'),
            InlineKeyboardButton("3 Tháng", callback_data='order_premium_3'),
            InlineKeyboardButton("6 Tháng", callback_data='order_premium_6'),
        ],
        [
            InlineKeyboardButton("12 Tháng", callback_data='order_premium_12'),
            InlineKeyboardButton("Kênh Sao", url='https://t.me/boibanvip'),
            InlineKeyboardButton("↩️ Quay lại", callback_data='main_menu')
        ],
    ]
    await safe_edit_message_text(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_order_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    period = data.split('_')[-1]
    prices = {
        '1': '169.000đ',
        '3': '369.000đ',
        '6': '569.000đ',
        '12': '869.000đ',
    }
    descriptions = {
        '1': (
            "      💎 *Gói 1 tháng cao cấp* 💎\n"
            "• Tốc độ tải xuống nhanh hơn\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• Biểu tượng siêu ngầu, huy hiệu VIP\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• *Thanh Toán  :  169.000 VND*\n"
        ),
        '3': (
            "      💎 *Gói 3 tháng cao cấp* 💎 \n"
            "• Tốc độ tải xuống nhanh hơn\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• Biểu tượng siêu ngầu, huy hiệu VIP\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• *Thanh Toán  :  369.000 VND*\n"
        ),
        '6': (
            "      💎 *Gói 6 tháng cao cấp* 💎\n"
            "• Tốc độ tải xuống nhanh hơn\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• Biểu tượng siêu ngầu, huy hiệu VIP\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• *Thanh Toán  :  569.000 VND*\n"
        ),
        '12': (
            "      💎 *Gói 12 tháng cao cấp* 💎\n"
            "• Tốc độ tải xuống nhanh hơn\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• Biểu tượng siêu ngầu, huy hiệu VIP\n"
            "• Tăng giới hạn gửi tin nhắn và tệp tin\n"
            "• *Thanh Toán  :  869.000 VND*\n"
        ),
    }
    description = descriptions.get(period, "Không có mô tả cho gói này.")
    text = f"*♦️Gói được chọn:* *{period} Tháng Premium  ♦️* \n\n{description}"
    keyboard = [
        [InlineKeyboardButton("🎁 Xác nhận mua gói này", callback_data='nap_tien')],
        [InlineKeyboardButton("↩️ Quay lại", callback_data='premium')]
    ]
    await safe_edit_message_text(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "𝐁𝐀𝐍𝐊 𝐆𝐈𝐀́ 𝐑𝐄̉ & 𝐀𝐍 𝐓𝐎𝐀̀𝐍\n\n"
        "🔹 Bank Online với hạn mức lên đến 100 triệu/tháng , 20 triệu/ngày — thoải mái giao dịch không lo giới hạn!\n"
        "🔹  Không cần giấy tờ rườm rà, chỉ cần lòng tin và… điện thoại!\n"
        "🔹 Tên CCCD random , số điện thoại của bạn sử dụng lâu dài , cực kỳ bền bỉ và riêng tư.\n"
        "🔹 Phù hợp mọi mục đích: bảo game , chạy chỉ tiêu casino , làm sạch tiền , và sử dụng cá nhân.\n"
        "🔹 Bank đã sẵn SINH TRẮC HỌC, khi nhận bank bạn chỉ cần Login và Dùng, ko cần động tác thừa nào nữa 😉"
    )
    keyboard = [
        [
            InlineKeyboardButton("Bank Web", callback_data='bank_web'),
            InlineKeyboardButton("Bank App", callback_data='bank_app'),
        ],
        [
            InlineKeyboardButton(" 🏡 Back Home", callback_data='main_menu'),
        ],
    ]
    await safe_edit_message_text(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == 'nap_tien':
        await handle_nap_tien(update, context)
    elif data == 'main_menu':
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=(
                "👋 *Shop Bảo Bối* xin chào!\n"
                "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                "• Ngoài bán mình cho tư bản ra thì nay em Bối còn bán thêm cả Bank Online & Tele Premium.\n"
                "🔰 Bank Online: Giao dịch nhanh chóng, an toàn, giá rẻ!\n"
                "🔰 Tele Premium: Nick xịn, mõm hay, nâng tầm đẳng cấp!\n"
            ),
            parse_mode='Markdown',
            reply_markup=get_main_inline_menu()
        )
    elif data == 'premium':
        await handle_premium(update, context)
    elif data and data.startswith('order_premium_'):
        await handle_order_premium(update, context)
    elif data == 'bank':
        await handle_bank(update, context)
    elif data == 'bank_web':
        await safe_edit_message_text(
            query,
            "Bạn đã chọn Bank Web.\nThông tin chi tiết sẽ được cập nhật sau.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Quay lại", callback_data='bank')]]),
            parse_mode='Markdown'
        )
    elif data == 'bank_app':
        await safe_edit_message_text(
            query,
            "Bạn đã chọn Bank App.\nThông tin chi tiết sẽ được cập nhật sau.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Quay lại", callback_data='bank')]]),
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Chức năng chưa hỗ trợ.",
        )

async def main():
    nest_asyncio.apply()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🏠 Home$"), handle_home))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🆔 Check ID$"), handle_check_id))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🛟 Support 24/7$"), handle_support))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bảo Bối Shop đang chạy 24/7...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())