from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
from io import BytesIO
import numpy as np


class ImageProcessor:

    def process(self, image_bytes: bytes, action: str) -> bytes:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")

        filter_map = {
            "warm": self._warm,
            "cool": self._cool,
            "vintage": self._vintage,
            "sepia": self._sepia,
            "bw": self._bw,
            "dramatic": self._dramatic,
            "vivid": self._vivid,
            "fade": self._fade,
            "bright": self._bright,
            "dark": self._dark,
            "hdr": self._hdr,
            "soft": self._soft,
            "sharp": self._sharp,
            "retro": self._retro,
            "moody": self._moody,
            "film": self._film,
            "ocean": self._ocean,
            "nature": self._nature,
            "golden": self._golden,
            "pastel": self._pastel,
            "neon": self._neon,
            "popart": self._popart,
            "portrait": self._portrait,
            "urban": self._urban,
            "bloom": self._bloom,
            "crop_square": self._crop_square,
            "crop_wide": self._crop_wide,
            "crop_story": self._crop_story,
            "crop_classic": self._crop_classic,
            "crop_photo": self._crop_photo,
            "enhance_auto": self._enhance_auto,
            "enhance_bright": self._enhance_bright,
            "enhance_dark": self._enhance_dark,
            "enhance_contrast": self._enhance_contrast,
            "enhance_saturation": self._enhance_saturation,
            "enhance_sharpen": self._enhance_sharpen,
            "enhance_smooth": self._enhance_smooth,
            "enhance_rotate": self._enhance_rotate,
            "enhance_flip_h": self._enhance_flip_h,
            "enhance_flip_v": self._enhance_flip_v,
        }

        if action in filter_map:
            img = filter_map[action](img)

        output = BytesIO()
        img.save(output, format="JPEG", quality=95)
        output.seek(0)
        return output.read()

    def _to_bytes(self, img: Image.Image) -> bytes:
        output = BytesIO()
        img.save(output, format="JPEG", quality=95)
        output.seek(0)
        return output.read()

    # ─── FILTERS ───────────────────────────────────────────────────────────

    def _warm(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _cool(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.85, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.20, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _sepia(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        r = arr[:, :, 0] * 0.393 + arr[:, :, 1] * 0.769 + arr[:, :, 2] * 0.189
        g = arr[:, :, 0] * 0.349 + arr[:, :, 1] * 0.686 + arr[:, :, 2] * 0.168
        b = arr[:, :, 0] * 0.272 + arr[:, :, 1] * 0.534 + arr[:, :, 2] * 0.131
        arr[:, :, 0] = np.clip(r, 0, 255)
        arr[:, :, 1] = np.clip(g, 0, 255)
        arr[:, :, 2] = np.clip(b, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _bw(self, img: Image.Image) -> Image.Image:
        img = ImageOps.grayscale(img)
        return img.convert("RGB")

    def _vintage(self, img: Image.Image) -> Image.Image:
        img = self._sepia(img)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.85)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.9)
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _dramatic(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.85)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.7)
        return img

    def _vivid(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.9)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        return img

    def _fade(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.7)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.75)
        return img

    def _bright(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.4)

    def _dark(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(0.65)

    def _hdr(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)
        return img

    def _soft(self, img: Image.Image) -> Image.Image:
        return img.filter(ImageFilter.GaussianBlur(radius=1.2))

    def _sharp(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(3.0)

    def _retro(self, img: Image.Image) -> Image.Image:
        img = self._warm(img)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.8)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        arr = np.array(img, dtype=np.float32)
        noise = np.random.randint(-10, 10, arr.shape, dtype=np.int16)
        arr = np.clip(arr.astype(np.int16) + noise, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _moody(self, img: Image.Image) -> Image.Image:
        img = self._cool(img)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.8)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.85)
        return img

    def _film(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.9)
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05 + 5, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.95, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _ocean(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.8, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.1, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.3, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _nature(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.9, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.2, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.9, 0, 255)
        enhancer = ImageEnhance.Color(Image.fromarray(arr.astype(np.uint8)))
        return enhancer.enhance(1.3)

    def _golden(self, img: Image.Image) -> Image.Image:
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.2, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.05, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.7, 0, 255)
        enhancer = ImageEnhance.Brightness(Image.fromarray(arr.astype(np.uint8)))
        return enhancer.enhance(1.1)

    def _pastel(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.6)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        arr = np.array(img, dtype=np.float32)
        arr = np.clip(arr * 0.85 + 38, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _neon(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(3.0)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(0.9)

    def _popart(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(4.0)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(2.0)

    def _portrait(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        arr = np.array(img, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.05, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))
        return img.filter(ImageFilter.SMOOTH)

    def _urban(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.4)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.85)
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(1.5)

    def _bloom(self, img: Image.Image) -> Image.Image:
        blurred = img.filter(ImageFilter.GaussianBlur(radius=8))
        arr_orig = np.array(img, dtype=np.float32)
        arr_blur = np.array(blurred, dtype=np.float32)
        arr = np.clip(arr_orig + arr_blur * 0.3, 0, 255)
        img2 = Image.fromarray(arr.astype(np.uint8))
        enhancer = ImageEnhance.Color(img2)
        return enhancer.enhance(1.2)

    # ─── CROPS ─────────────────────────────────────────────────────────────

    def _crop_to_ratio(self, img: Image.Image, ratio_w: float, ratio_h: float) -> Image.Image:
        w, h = img.size
        target_ratio = ratio_w / ratio_h
        current_ratio = w / h

        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        return img

    def _crop_square(self, img: Image.Image) -> Image.Image:
        return self._crop_to_ratio(img, 1, 1)

    def _crop_wide(self, img: Image.Image) -> Image.Image:
        return self._crop_to_ratio(img, 16, 9)

    def _crop_story(self, img: Image.Image) -> Image.Image:
        return self._crop_to_ratio(img, 9, 16)

    def _crop_classic(self, img: Image.Image) -> Image.Image:
        return self._crop_to_ratio(img, 4, 3)

    def _crop_photo(self, img: Image.Image) -> Image.Image:
        return self._crop_to_ratio(img, 3, 2)

    # ─── ENHANCEMENTS ──────────────────────────────────────────────────────

    def _enhance_auto(self, img: Image.Image) -> Image.Image:
        img = ImageOps.autocontrast(img, cutoff=1)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(1.3)

    def _enhance_bright(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Brightness(img).enhance(1.3)

    def _enhance_dark(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Brightness(img).enhance(0.7)

    def _enhance_contrast(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Contrast(img).enhance(1.5)

    def _enhance_saturation(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Color(img).enhance(1.6)

    def _enhance_sharpen(self, img: Image.Image) -> Image.Image:
        return ImageEnhance.Sharpness(img).enhance(2.5)

    def _enhance_smooth(self, img: Image.Image) -> Image.Image:
        return img.filter(ImageFilter.SMOOTH_MORE)

    def _enhance_rotate(self, img: Image.Image) -> Image.Image:
        return img.rotate(-90, expand=True)

    def _enhance_flip_h(self, img: Image.Image) -> Image.Image:
        return ImageOps.mirror(img)

    def _enhance_flip_v(self, img: Image.Image) -> Image.Image:
        return ImageOps.flip(img)
