from PIL import Image, ImageFilter
import re
from aip import AipOcr



def xuanzhuan(b,c):
     # 加载原始图片
    img = Image.open(b)

    # 逆时针方向旋转
    img2 = img.rotate(c)
    img2.save("img2.png")

def daxiao(c,w,h):
    # 加载原始图片
    img = Image.open(c)


    img2 = img.resize((w, h))
    img2.save("img2.png")



