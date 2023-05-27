#!/usr/bin/env python
from PIL import Image
import time
import io
import numpy as np
import matplotlib.pyplot as plt

from spytft import ili9328

'''
ILI9328 Rectangle Area Drawing Sample

Rectangle area drawing is, for example, the ability to draw
a 100*100 pixel image at any position on a 240*320 TFT.
Feature: Since only image data within a rectangular area is
transferred, screen updates are faster.
What I did not expect, however, is that matplotlib's
software rendering is so slow.
'[ja]'=Japanese Comment

[ja]このサンプルは画面内に矩形領域の描画をします.
[ja]矩形領域のデータ転送のみ行うので高速です.
[ja]画像はpatplotlibのsin波グラフです.
[ja]しかし、matplotlibのレンダリングが激遅過ぎて速さがうまく伝わりません...

Sample   : draw graph (240*320 pixel)
    func : draw_graph()

Note:
    Interface : SPI (parallel IO is not supported)
    Dependent modules for ili9328: numpy, spidev
    Support OS : Linux(The spidev kernel module must be enabled.)

Author: sh-goto
'''

# Sample 1 --------------------------------------------------------
# ILI9328 draw graph(200*150) in 240*320 TFT
#  O --> X
#  |
#  V
#  Y
#
# (0,0)  ----------------------------- (239,0)
#       |                            |
#       |(20,100)_____________       |
#       |       |   __        |      |
#       |       |  /  \       |      |
#       |       | /    \      |      |
#       |       |       \    /|      |
#       |       |        \__/ |      |
#       |        ------------- (200+20,150+100)
#       |                            |
#       |                            |
#(0,319)|____________________________|(239,319)
#         |||||||||||||||||||||||||    <- Flexible Printed Circuits(FPC)
#         -------------------------
#
#
def draw_graph():

    # Create a graph
    x = np.linspace(0, 2*np.pi, 200)
    y = np.sin(x)

    # [ja]200*150ピクセルにするため、dpi=80の場合、figsizeを下記の様に設定
    # [ja]ただし、正確なピクセル値にはならない.
    # To make 200*150 pixels, if dpi=80, set figsize as follows.
    # However, it will not be an exact pixel value.
    plt.figure(figsize=(2.5, 1.875))
    plt.style.use('dark_background')
    plt.plot(x, y)

    # [ja]Pillowオブジェクトに変換するため、一時的にバイトストリームに変換
    # Temporarily converted to a byte stream for conversion to a Pillow object.
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=80)
    plt.close()
    buf.seek(0)

    # [ja]PillowのImageオブジェクトに変換
    # Converted to Pillow Image object
    img = Image.open(buf)
    img = img.resize((200, 150))
    img = img.convert('RGB')

    # TFT setting

    # gpio (sysfs I/F)
    RESET_PIN_PATH = '/sys/class/gpio/gpio1023/value'   # for ili9328 reset
    SPI_CS_PIN_PATH = '/sys/class/gpio/gpio1022/value'  # for spi chip select
    # setting spibus (e.g. /dev/spidev1.0)
    SPI_BUS_NUM = 1
    SPI_DEVICE_NUM = 0
    # MAX 10MHz. But can be overclocked
    SPI_SPEED_HZ = 1*1000*1000

    # Init TFT Display
    tft = ili9328.Ili9328Spi(   spibus    = SPI_BUS_NUM,
                                spidevice = SPI_DEVICE_NUM,
                                spi_speed_hz = SPI_SPEED_HZ,
                                gpio_cs   = SPI_CS_PIN_PATH,
                                gpio_rst  = RESET_PIN_PATH)

    # draw background
    background = Image.new('RGB', (240, 320), color='white')
    tft.image(background)

    # [ja]矩形領域を描画する.描画位置の座標を指定
    # [ja]座標は矩形領域の左上が基準
    # Draws a rectangular area. Specify the coordinates of
    # the drawing position. The coordinates are based on
    # the upper left corner of the rectangle area.
    tft.block_image(20,100, img)

    time.sleep(3)

    # [ja]画像の向きを逆にする。
    # Reverse the orientation of the image
    img = img.rotate(180)
    tft.block_image(20,100, img)


if __name__ == "__main__":
    draw_graph()