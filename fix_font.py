import urllib.request
import base64
import re

url = "https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pb0EPOreefkkbIx.woff2"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req)
font_data = resp.read()

font_b64 = base64.b64encode(font_data).decode('utf-8')

font_face_css = f"""@font-face {{{{
        font-family: 'Rajdhani';
        font-style: normal;
        font-weight: 500;
        src: url("data:font/woff2;charset=utf-8;base64,{font_b64}") format('woff2');
      }}}}"""

with open('generate_tshirt_img.py', 'r') as f:
    content = f.read()

# Replace the @import line with the injected base64 font face
content = re.sub(r"@import url\('[^']+'\);", font_face_css, content)

with open('generate_tshirt_img.py', 'w') as f:
    f.write(content)

print("Font embedded successfully.")
