import base64
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from config import Config


class AIEditor:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    def _bytes_to_pil(self, image_bytes: bytes) -> Image.Image:
        return Image.open(BytesIO(image_bytes)).convert("RGB")

    def analyze_image(self, image_bytes: bytes) -> str:
        """Gemini se image analyze karwao - FREE"""
        if not self.model:
            return "❌ Gemini API key nahi hai. .env file mein GEMINI_API_KEY daalo."

        try:
            img = self._bytes_to_pil(image_bytes)

            prompt = (
                "You are a professional photo editor. Analyze this image and provide:\n\n"
                "1. 🎨 **Image Description**: What is in this image?\n"
                "2. 📊 **Quality Rating**: Rate exposure, color, sharpness (1-10)\n"
                "3. ✨ **Top 5 Editing Tips**: Specific improvements\n"
                "4. 🎭 **Best Filter**: Which filter would suit this image?\n"
                "5. 📐 **Best Crop**: What crop ratio would look best?\n"
                "6. 💡 **Pro Tip**: One expert tip for this image\n\n"
                "Be concise and use emojis. Reply in simple English."
            )

            response = self.model.generate_content([prompt, img])
            return response.text

        except Exception as e:
            return f"❌ Analysis failed: {str(e)}"

    def get_caption_suggestions(self, image_bytes: bytes) -> str:
        """Image ke liye social media captions - FREE"""
        if not self.model:
            return "❌ Gemini API key nahi hai. .env file mein GEMINI_API_KEY daalo."

        try:
            img = self._bytes_to_pil(image_bytes)

            prompt = (
                "Generate 5 creative social media captions for this image:\n\n"
                "1. 📸 Instagram caption (with hashtags)\n"
                "2. 🎵 TikTok caption (short, trendy)\n"
                "3. 👥 Facebook caption (friendly)\n"
                "4. 🐦 Twitter/X caption (witty, under 280 chars)\n"
                "5. 💼 LinkedIn caption (professional)\n\n"
                "Use emojis and make them engaging!"
            )

            response = self.model.generate_content([prompt, img])
            return response.text

        except Exception as e:
            return f"❌ Caption generation failed: {str(e)}"

    def get_edit_suggestions(self, image_bytes: bytes) -> str:
        """Quick editing suggestions - FREE"""
        if not self.model:
            return "❌ Gemini API key nahi hai."

        try:
            img = self._bytes_to_pil(image_bytes)

            prompt = (
                "Look at this photo and suggest the 3 best quick edits from this list:\n"
                "Filters: warm, cool, vintage, sepia, bw, dramatic, vivid, fade, bright, dark, hdr, retro, moody\n"
                "Crops: square, wide (16:9), story (9:16)\n"
                "Enhancements: sharpen, bright, contrast, saturation\n\n"
                "Format: Just list the 3 best options with one emoji each and a short reason. Be very brief."
            )

            response = self.model.generate_content([prompt, img])
            return response.text

        except Exception as e:
            return f"❌ Suggestions failed: {str(e)}"


AI_STYLES = [
    ("🎬 Cinematic", "cinematic"),
    ("🎌 Anime Style", "anime"),
    ("🎨 Watercolor", "watercolor"),
    ("🖼️ Oil Painting", "oil_painting"),
    ("✏️ Pencil Sketch", "sketch"),
    ("🌆 Neon City", "neon_city"),
    ("📮 Vintage Poster", "vintage_poster"),
    ("📸 Professional", "professional"),
]
