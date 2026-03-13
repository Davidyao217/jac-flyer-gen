import xml.etree.ElementTree as ET
import base64
import re

with open("clean_assets/jaseci_logo.svg", "r") as f:
    data = f.read()

match = re.search(r'data:image/png;base64,([^"]+)', data)
if match:
    b64 = match.group(1)
    with open("jaseci.png", "wb") as f:
        f.write(base64.b64decode(b64))
    print("Extracted jaseci.png")
else:
    print("Could not extract")
