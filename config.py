import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
    PREMIUM_MONTHLY_PRICE = int(os.getenv("PREMIUM_MONTHLY_PRICE", "5"))

    FREE_DAILY_LIMIT = 10
    PREMIUM_DAILY_LIMIT = 999

    DB_PATH = "editor_bot.db"

    FILTERS_LIST = [
        ("🌅 Warm", "warm"),
        ("❄️ Cool", "cool"),
        ("🎞️ Vintage", "vintage"),
        ("📸 Sepia", "sepia"),
        ("⚫ Black & White", "bw"),
        ("🎭 Dramatic", "dramatic"),
        ("🌈 Vivid", "vivid"),
        ("🌫️ Fade", "fade"),
        ("☀️ Bright", "bright"),
        ("🌑 Dark", "dark"),
        ("💡 HDR", "hdr"),
        ("🌸 Soft", "soft"),
        ("🔪 Sharp", "sharp"),
        ("📼 Retro", "retro"),
        ("🌙 Moody", "moody"),
        ("🎬 Film", "film"),
        ("🌊 Ocean", "ocean"),
        ("🌿 Nature", "nature"),
        ("🌇 Golden Hour", "golden"),
        ("💜 Pastel", "pastel"),
        ("⚡ Neon", "neon"),
        ("🎨 Pop Art", "popart"),
        ("🖼️ Portrait", "portrait"),
        ("🏙️ Urban", "urban"),
        ("🌺 Bloom", "bloom"),
    ]

    CROP_LIST = [
        ("⬛ Square (1:1)", "crop_square"),
        ("📺 Widescreen (16:9)", "crop_wide"),
        ("📱 Story (9:16)", "crop_story"),
        ("🖼️ Classic (4:3)", "crop_classic"),
        ("📷 Photo (3:2)", "crop_photo"),
    ]

    ENHANCE_LIST = [
        ("✨ Auto Enhance", "enhance_auto"),
        ("🔆 Increase Brightness", "enhance_bright"),
        ("🔅 Decrease Brightness", "enhance_dark"),
        ("🎯 Increase Contrast", "enhance_contrast"),
        ("🎨 Boost Saturation", "enhance_saturation"),
        ("🔪 Sharpen", "enhance_sharpen"),
        ("💧 Smooth/Denoise", "enhance_smooth"),
        ("📐 Rotate 90°", "enhance_rotate"),
        ("↔️ Flip Horizontal", "enhance_flip_h"),
        ("↕️ Flip Vertical", "enhance_flip_v"),
    ]
