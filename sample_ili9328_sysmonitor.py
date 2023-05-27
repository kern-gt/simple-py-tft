#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageFont
import datetime
import time

from spytft import ili9328

'''
ILI9328 System Monitor sample

This sample draws a screen like a system monitor,
displaying screen orientation in four directions.
'[ja]'=Japanese Comment

[ja]このサンプルはsystem monitor風の画面を描画します。
[ja]４方向の画面の向きを表示します。

Sample 1 : vertical drawing sample (240*320 pixel)
    func : vertical_drawing_sample()

Sample 2 : horizontal drawing sample (320*240 pixel)
    func : horizontal_drawing_sample()

Note:
    Interface : SPI (parallel IO is not supported)
    Dependent modules : numpy, spidev
    Support OS : Linux(The spidev kernel module must be enabled.)

Author: sh-goto
'''

# Sample 1 --------------------------------------------------------
# ILI9328 vertical drawing sample (240*320 pixel)
#  O --> X
#  |
#  V
#  Y
#
# (0,0)  ----------------------------- (239,0)
#       |    20YY-MM-DD HH:MM:SS     |
#       |                            |
#       |      System  Monitor       |
#       |                            |
#       |  Temperature               |
#       |   ----    ----     ----    |
#       |  |    |  |    |   |    |   |
#       |   ----    ----|    ----    |
#       |  |    |  |    |   |    | . |
#       |   ----    ----  *  ----   C|
#(0,319)|____________________________|(239,319)
#         |||||||||||||||||||||||||    <- Flexible Printed Circuits(FPC)
#         -------------------------
#
#
def vertical_drawing_sample():
    '''Sample1 vertical drawing sample (240*320 pixel)

    GPIOs must be initialized as follows in advance.
    e.g. use GPIO1022
    $ sudo echo 1022 > /sys/class/gpio/export
    $ sudo echo out > /sys/class/gpio/gpio1022/direction
    '''
    # gpio (sysfs I/F)
    RESET_PIN_PATH  = '/sys/class/gpio/gpio1023/value'   # for ili9328 reset
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

    # [ja]液晶に出力可能なサイズを取得し、画像を新規作成する
    # サイズはwidth=240,height=320に固定
    # Obtain a size that can be output to the LCD and create a new image. 
    # The size is fixed to width=240,height=320.
    width, height = tft.get_draw_image_size() 
    image = Image.new('RGB', (width, height), color=(40,40,40))

    draw_image = ImageDraw.Draw(image)

    # [ja]フォントファイルを取得.'./fonts'フォルダにttfを置いている
    # get fontfile. Font files are placed in './fonts'
    font_large = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 96)
    font_big   = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 32)
    font_mid   = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 24)
    font_small = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 18)

    # [ja]日時と時刻を取得.JSTに変換
    # get time.
    dt_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    date_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    # [ja]テキストを描画する
    # draw texts.
    draw_image.text((5,    5), date_str,            '#00FF90', font=font_mid)
    draw_image.text((75,  30), 'powered by sh-goto','#00FF90', font=font_small)
    draw_image.text((5,   50), 'System Monitor',    '#FFFFFF', font=font_big)
    draw_image.text((5,  105), 'Temperature',       '#00FFFF', font=font_mid)
    draw_image.text((210,235), '°C',                '#00FFFF', font=font_mid)
    draw_image.text((10, 145), '27.9',              '#00FFFF', font=font_large)
    draw_image.text((11, 260), 'DC12V:12.06V',      '#c0c000', font=font_small)
    draw_image.text((20, 280), 'Vdd1: 3.28V',       '#c0c000', font=font_small)
    draw_image.text((20, 300), 'Vdd2: 1.19V',       '#c0c000', font=font_small)
    draw_image.text((150,260), 'I: 6.5A',           '#c0c000', font=font_small)
    draw_image.text((150,280), 'P:78.4W',           '#c0c000', font=font_small)
    draw_image.text((150,300), 'Mode:RUN',          '#00FF90', font=font_small)

    # [ja]画面に表示する。PillowのImageをそのまま渡す
    # Display on screen. corresponding to the Image object in Pillow.
    tft.image(image)

    time.sleep(3)

    # [ja]画像の向きを逆にする。
    # Reverse the orientation of the image
    image = image.rotate(180)

    tft.image(image)




# Sample 2 --------------------------------------------------------
# ILI9328 horizontal drawing sample (320*240 pixel)
#  O --> X
#  |                        *FPC:Flexible Printed Circuits
#  V
#  Y
#     (0,0) ------------------------------------- (319,0)
#        ---| 20YY-MM-DD HH:MM:SS               |
#       |---| System  Monitor                   |
#       |---| Temperature                       |
# FPC-> |---|  ___   ___    ___                 |
#       |---| |   | |   |  |   |      DCV :12.0V|
#       |---|  ---   ---    ---       Vdd1: 3.3V|
#       |---| |   | |   |  |   |      Vdd2: 1.2V|
#        ---|  ---   ---  * ---   C      P: 105W|
#           -------------------------------------
#    (0,239)                                     (319,239)
#
def horizontal_drawing_sample():
    '''Sample2 horizontal drawing sample (320*240 pixel)

    GPIOs must be initialized as follows in advance.
    e.g. use GPIO1022
    $ sudo echo 1022 > /sys/class/gpio/export
    $ sudo echo out > /sys/class/gpio/gpio1022/direction
    '''
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

    # [ja]液晶に出力可能な画像サイズを取得.サイズはwidth=240,height=320に固定
    # Obtain the image size that can be output to the LCD. Size is fixed to width=240,height=320
    width, height = tft.get_draw_image_size() 

    # [ja]画像を横向きに描画するため、widthとheightを入れ替えてから画像新規作成
    # To draw the image horizontally, swap the width and height before creating a new image
    width_inv  = height
    height_inv = width
    image_hrzn = Image.new('RGB', (width_inv, height_inv), color=(40,40,40))
    draw_image = ImageDraw.Draw(image_hrzn)

    # [ja]フォントファイルを取得.'./fonts'フォルダにttfを置いている
    # get fontfile. Font files are placed in './fonts'
    font_large = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 84)
    font_big   = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 32)
    font_mid   = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 24)
    font_small = ImageFont.truetype('./fonts/UDEVGothic-Regular.ttf', 18)

    # [ja]日時と時刻を取得.JSTに変換
    # get time.
    dt_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    date_str = dt_now.strftime('%Y-%m-%d %H:%M:%S')

    # [ja]テキストを描画する
    # draw texts.
    draw_image.text((  5,   5), date_str,            '#00FF90', font=font_mid)
    draw_image.text(( 70,  30), 'powered by sh-goto','#00FF90', font=font_small)
    draw_image.text((  5,  50), 'System Monitor',    '#FFFFFF', font=font_big)
    draw_image.text((  5, 105), 'Temperature',       '#00FFFF', font=font_mid)
    draw_image.text((150, 215), '°C',                '#00FFFF', font=font_mid)
    draw_image.text((  5, 135), '27.9',              '#00FFFF', font=font_large)
    draw_image.text((190, 105), 'Status:',           '#C0C000', font=font_mid)
    draw_image.text((275, 105), 'RUN',               '#00FF90', font=font_mid)
    draw_image.text((210, 135), 'DC12V:12.1V',       '#C0C000', font=font_small)
    draw_image.text((210, 155), ' Vdd1: 3.3V',       '#C0C000', font=font_small)
    draw_image.text((210, 175), ' Vdd2: 1.2V',       '#C0C000', font=font_small)
    draw_image.text((210, 195), '    I: 8.7A',       '#C0C000', font=font_small)
    draw_image.text((210, 215), '    P: 105W',       '#C0C000', font=font_small)

    # [ja]縦向きに変更してから、画面に表示する。PillowのImageをそのまま渡す
    # 320*240 -> 240*320
    # Change to portrait orientation and then display on the screen,
    # taking Image of Pillow as argument.
    image = image_hrzn.rotate(90, expand=True)
    tft.image(image)

    time.sleep(3)

    # [ja]画像の向きを逆にする
    # Reverse the orientation of the image
    image = image.rotate(180)
    tft.image(image)


if __name__ == "__main__":
    # sample1
    vertical_drawing_sample()
    time.sleep(3)

    # sample2
    horizontal_drawing_sample()