from PIL import Image
import io

def resize_image(image_bytes, size=(224, 224)):
    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize(size)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()
