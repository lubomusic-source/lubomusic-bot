"""
🎵 Lu Bo Music - Telegram Bot
Cài đặt: pip install python-telegram-bot==20.7
Chạy: python lubomusic_bot.py
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ==================== CẤU HÌNH ====================
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN chưa được thiết lập trong Railway Variables")

ADMIN_ID = int(os.getenv("ADMIN_ID", "6146312857"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== DỮ LIỆU SẢN PHẨM ====================
PRODUCTS = {
    "sp1": {
        "name": "🎼 Gói Cơ Bản – Phổ Nhạc Cho Thơ",
        "price": "500.000đ",
        "mo_ta": (
            "• 2 demo, 2 thể loại (khách chọn 1)\n"
            "• Tặng video đơn giản\n"
            "• Sáng tác lời miễn phí"
        ),
        "giao": "2–3 ngày",
        "bh": "1 tháng",
        "bq": "Thuộc về khách",
    },
    "sp2": {
        "name": "🥇 Gói Gold – Phổ Nhạc Cho Thơ/Lời",
        "price": "800.000đ",
        "mo_ta": (
            "• 3 demo, 3 thể loại (khách chọn 1)\n"
            "• Video tối đa 30 ảnh/clip hoặc Karaoke chạy chữ\n"
            "• Sáng tác lời miễn phí"
        ),
        "giao": "2–3 ngày",
        "bh": "1 tháng",
        "bq": "Thuộc về khách",
    },
    "sp3": {
        "name": "💎 Gói Diamond – Phổ Nhạc Quảng Cáo",
        "price": "1.500.000đ",
        "mo_ta": (
            "• Nhiều demo, nhiều thể loại (chọn thoải mái)\n"
            "• 1 Video Full theo yêu cầu\n"
            "• Sáng tác lời miễn phí"
        ),
        "giao": "2–3 ngày",
        "bh": "1 tháng",
        "bq": "Thuộc về khách",
    },
    "sp4": {
        "name": "🎹 Beat Nhạc Instrumental",
        "price": "100.000đ",
        "mo_ta": (
            "• Các thể loại nhạc theo yêu cầu\n"
            "• Không lời, dùng làm nền / sáng tác"
        ),
        "giao": "1 ngày",
        "bh": "1 tháng",
        "bq": "Thuộc về khách",
    },
}

QUY_TRINH = """
🎵 *QUY TRÌNH THANH TOÁN & LÀM VIỆC*

1️⃣ *Đặt cọc khởi động (40%)*
Khách chuyển 40% để bắt đầu (chuẩn bị phối, phân lời, dựng cấu trúc).

2️⃣ *Duyệt lời*
Ad gửi lời bài hát / phổ thơ để khách duyệt.
➡️ Chỉnh chữ nếu cần tại bước này.
_(Nếu lời/thơ của khách → bỏ qua bước này)_

3️⃣ *Phổ nhạc & Demo*
Sau khi duyệt lời, ad phổ nhạc và gửi các demo.
➡️ Khách ok → ad mix, master hoàn thiện.

4️⃣ *Thanh toán đợt 2 (40%)*
Ad giao bản nghe thử Full MP3 160kbps.
Khách nghe kỹ – nếu ổn, báo ad hoàn tất.

5️⃣ *Bàn giao bản gốc (20% còn lại)*
Ad gửi bản WAV 44.1kHz – 24bit full quality và video.
"""

# ==================== MENU CHÍNH ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Xem Sản Phẩm", callback_data="menu_sanpham")],
        [InlineKeyboardButton("📋 Quy Trình Làm Việc", callback_data="menu_quitrinh")],
        [InlineKeyboardButton("💬 Liên Hệ Tư Vấn", callback_data="menu_lienhe")],
        [InlineKeyboardButton("ℹ️ Giới Thiệu Shop", callback_data="menu_gioithieu")],
    ])

def sanpham_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎼 Gói Cơ Bản – 500k", callback_data="sp_sp1")],
        [InlineKeyboardButton("🥇 Gói Gold – 800k", callback_data="sp_sp2")],
        [InlineKeyboardButton("💎 Gói Diamond – 1.500k", callback_data="sp_sp3")],
        [InlineKeyboardButton("🎹 Beat Instrumental – 100k", callback_data="sp_sp4")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")],
    ])

def datmua_keyboard(sp_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Đặt Mua Ngay", callback_data=f"datmua_{sp_id}")],
        [InlineKeyboardButton("🔙 Quay lại danh sách", callback_data="menu_sanpham")],
    ])

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"Chào {name}! 🎵\n\n"
        "Chào mừng đến với *Lu Bo Music* — nơi biến thơ và ý tưởng của bạn thành âm nhạc!\n\n"
        "• Phổ nhạc cho thơ / lời có sẵn\n"
        "• Sáng tác ca khúc theo yêu cầu\n"
        "• Bán beat nhạc Instrumental\n\n"
        "Chọn mục bên dưới để bắt đầu 👇"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- MENU CHÍNH ---
    if data == "back_main" or data == "menu_main":
        await query.edit_message_text(
            "🎵 *Lu Bo Music* — Chọn mục bạn cần 👇",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    elif data == "menu_sanpham":
        await query.edit_message_text(
            "🛍️ *Danh Sách Dịch Vụ*\n\nChọn gói để xem chi tiết 👇",
            parse_mode="Markdown",
            reply_markup=sanpham_keyboard()
        )

    elif data == "menu_quitrinh":
        await query.edit_message_text(
            QUY_TRINH,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")]
            ])
        )

    elif data == "menu_lienhe":
        await query.edit_message_text(
            "💬 *Liên Hệ Tư Vấn*\n\n"
            "Bạn có thể nhắn trực tiếp tại đây.\n"
            "Ad sẽ phản hồi trong thời gian sớm nhất! 🎵\n\n"
            "Hoặc mô tả yêu cầu của bạn ngay bên dưới 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")]
            ])
        )

    elif data == "menu_gioithieu":
        await query.edit_message_text(
            "🎵 *Lu Bo Music*\n\n"
            "Chúng tôi cung cấp dịch vụ âm nhạc chuyên nghiệp:\n\n"
            "🎼 Phổ nhạc cho thơ & lời có sẵn\n"
            "🎤 Sáng tác ca khúc theo yêu cầu\n"
            "🎹 Beat nhạc Instrumental các thể loại\n\n"
            "✅ Bản quyền thuộc về khách\n"
            "✅ Bảo hành 1 tháng\n"
            "✅ Giao hàng 1–3 ngày\n"
            "✅ Thanh toán 3 đợt an toàn",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ Xem Sản Phẩm", callback_data="menu_sanpham")],
                [InlineKeyboardButton("🔙 Quay lại", callback_data="back_main")],
            ])
        )

    # --- CHI TIẾT SẢN PHẨM ---
    elif data.startswith("sp_"):
        sp_id = data[3:]
        sp = PRODUCTS.get(sp_id)
        if sp:
            text = (
                f"*{sp['name']}*\n\n"
                f"💰 Giá: *{sp['price']}*\n\n"
                f"📌 Mô tả:\n{sp['mo_ta']}\n\n"
                f"⏱ Thời gian giao: {sp['giao']}\n"
                f"🛡 Bảo hành: {sp['bh']}\n"
                f"©️ Bản quyền: {sp['bq']}"
            )
            await query.edit_message_text(
                text, parse_mode="Markdown",
                reply_markup=datmua_keyboard(sp_id)
            )

    # --- ĐẶT MUA ---
    elif data.startswith("datmua_"):
        sp_id = data[7:]
        sp = PRODUCTS.get(sp_id)
        if sp:
            user = query.from_user
            # Thông báo cho admin
            admin_text = (
                f"🔔 *ĐƠN HÀNG MỚI!*\n\n"
                f"👤 Khách: {user.full_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📦 Sản phẩm: {sp['name']}\n"
                f"💰 Giá: {sp['price']}\n\n"
                f"➡️ Liên hệ: @{user.username or 'không có username'}"
            )
            try:
                await context.bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Không gửi được cho admin: {e}")

            # Phản hồi khách
            await query.edit_message_text(
                f"✅ *Đặt hàng thành công!*\n\n"
                f"📦 {sp['name']}\n"
                f"💰 {sp['price']}\n\n"
                f"Ad đã nhận yêu cầu và sẽ liên hệ bạn sớm nhất!\n\n"
                f"📋 Bước tiếp theo:\n"
                f"• Ad sẽ nhắn xác nhận & gửi thông tin chuyển cọc 40%\n"
                f"• Sau khi cọc, tiến hành sản xuất ngay 🎵",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Về Trang Chủ", callback_data="back_main")]
                ])
            )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chuyển tiếp tin nhắn thường của khách cho admin"""
    user = update.effective_user
    text = update.message.text

    # Forward cho admin
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"💬 *Tin nhắn từ khách*\n\n"
            f"👤 {user.full_name} (@{user.username or 'N/A'})\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"📝 Nội dung:\n{text}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Lỗi forward: {e}")

    await update.message.reply_text(
        "✅ Ad đã nhận tin nhắn của bạn!\n"
        "Sẽ phản hồi trong thời gian sớm nhất 🎵\n\n"
        "Hoặc xem thêm dịch vụ:",
        reply_markup=main_menu_keyboard()
    )

# ==================== MAIN ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("🎵 Lu Bo Music Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
