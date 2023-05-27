#!/usr/bin/env python

import spidev
import numpy as np
import time

class Ili9328Spi:
    """ILITEK ILI9328 SPI library
    This is the ILI9328 library from ILITEK.
    It can use Pillow image object on 240*320 TFT.

    Interface : SPI (parallel IO is not supported)
    Dependent modules : numpy, spidev
    OS : Linux(The spidev kernel module must be enabled.)

    Author : sh-goto
    """
    def __init__(self,
                 spibus    = 1,
                 spidevice = 0,
                 spi_speed_hz = 500*1000,
                 gpio_cs   = '/dev/null',
                 gpio_rst  = '/dev/null'
                 ) -> None:
        """
        Sets the SPI interface, SPI-ChipSelect pin and SPI speed.
        Also sets the reset pin of ILI9328.

        Args:
            spibus (int): e.g. spibus=X -> '/dev/spidevX.Y'
            spidevice (int): e.g. spidevice=Y -> '/dev/spidevX.Y'
            spi_speed_hz (int): SPI bus clock [Hz]. MAX 10MHz. 
                                But can be overclocked
            gpio_cs (str):  GPIO for SPI ChipSelect pin.
                            The interface used is SysFs GPIO.
                            e.g. '/sys/class/gpio/gpio1023/value'
            gpio_rst (str): ILI9328 Reset pin. The interface used is SysFs GPIO.
                            e.g. '/sys/class/gpio/gpio1023/value'
        """
        # spi config
        self.spibus_num    = spibus
        self.spidevice_num = spidevice
        self.spi_speed_hz  = spi_speed_hz

        # gpio config
        self.spi_cs_pin   = gpio_cs
        self.reset_pin    = gpio_rst
        self.PIN_ACTIVE   = b'0'
        self.PIN_INACTIVE = b'1'
        
        # TFT display config
        self.IMAGE_WIDTH  = 240
        self.IMAGE_HEIGHT = 320
        self.BITS_PER_PIXEL = 16 # r=5bit, g=6bit, b=5bit

        # init TFT
        self.init_ili9328()


    def set_spi_speed_hz(self, speed):
        """
        SPI bus clock setting. 

        Args:
            spi_speed_hz (int): MAX 10MHz. But can be overclocked
        """
        self.spi_speed_hz = speed


    def get_draw_image_size(self):
        """
        Returns the image size that can be transferred to the TFT.

        Returns:
            int: width
            int: height
        """
        return (self.IMAGE_WIDTH, self.IMAGE_HEIGHT)


    def image(self, pil_image):
        """
        Display images on TFT.

        Args:
            pil_image (PIL.Image): Pillow Image(240*320)
        """
        self.block_image(0, 0, pil_image)


    def block_image(self, x0, y0, pil_image):
        """
        Draws a rectangular area.
        High-speed drawing because only the data
        in the rectangular area is transferred.

        Args:
            x0 (int): Specifies the X coordinate of the upper left corner
                      of the rectangular area.
            y0 (int): Specifies the X coordinate of the upper left corner
                      of the rectangular area.
            pil_image (PIL.Image): Pillow Image(240*320)
        """
        # Convert from Pillow Image to Numpy array.
        rgb888 = np.array(pil_image)

        # 24bitRGBカラーを16bitカラー(65K)に変換する
        # Convert from RGB888(24bit) to RGB565(16bit)

        ## RGB(24bit)をred=5bit, green=6bit, blue=5bitに分解
        ## Decompose 24bitRGB into red=5bit, green=6bit, blue=5bit
        red   = (rgb888[:, :, 0] >> 3).astype(np.uint8)
        green = (rgb888[:, :, 1] >> 2).astype(np.uint8)
        blue  = (rgb888[:, :, 2] >> 3).astype(np.uint8)

        height, width, _ = rgb888.shape
        rgb565 = np.zeros((height, width, 2), dtype=np.uint8)

        ## 1byte目の下位3bitにはgreenの上位3bitを格納し、
        ## 上位5bitにはredを格納
        ## The lower 3 bits of the first byte store
        ## the upper 3 bits of GREEN,and the upper 5 bits store RED.
        rgb565[:, :, 0] = (red << 3) | (green >> 3)

        ## 2byte目の下位5bitにはblueの値を格納し、
        ## 上位3bitはgreenの下位3bitを格納
        ## The lower 5 bits of the second byte store 
        ## the value of BLUE, and the upper 3 bits store
        ## the lower 3 bits of GREEN.
        rgb565[:, :, 1] = (blue) | ((green & 0x07) << 5)

        # 長方形描画領域の左上座標を設定
        # Sets the upper left coordinate of the rectangular drawing area.
        x0 = min(max(x0, 0), (self.IMAGE_WIDTH  - 1))
        y0 = min(max(y0, 0), (self.IMAGE_HEIGHT - 1))
        self.write_cmd(0x20, x0) # GRAM horizontal start position
        self.write_cmd(0x21, y0) # GRAM vertical start position
        self.write_cmd(0x50, x0) # block area horizontal end position
        self.write_cmd(0x52, y0) # block area vertical end position

        # 長方形描画領域の右下座標を設定
        # Set the lower right coordinate of the rectangular drawing area.
        x = min(max((x0 + width  - 1), 0), (self.IMAGE_WIDTH  - 1))
        y = min(max((y0 + height - 1), 0), (self.IMAGE_HEIGHT - 1))
        self.write_cmd(0x51, x) # block area horizontal end position
        self.write_cmd(0x53, y) # block area vertical end position

        # GRAMに転送
        # write GRAM
        self.write_gram(rgb565)


    def write_cmd(self, regaddr, data16):
        # init spi
        spi = spidev.SpiDev()
        spi.open(self.spibus_num, self.spidevice_num)
        spi.max_speed_hz = self.spi_speed_hz
        spi.mode = 0b11 #spi mode3

        with open(self.spi_cs_pin, mode='wb',buffering=0) as cs_pin:
            # set reg index
            cs_pin.write(self.PIN_ACTIVE)
            send_data = [0x70]  #startbyte RS=0,R/W=W
            send_data.extend(
                list(regaddr.to_bytes(2,byteorder='big')))
            spi.writebytes(send_data)
            cs_pin.write(self.PIN_INACTIVE)

            # set reg data
            cs_pin.write(self.PIN_ACTIVE)
            send_data = [0x72]  #startbyte RS=1,R/W=W
            send_data.extend(
                list(data16.to_bytes(2,byteorder='big')))
            spi.writebytes(send_data)
            cs_pin.write(self.PIN_INACTIVE)

        spi.close()


    def write_gram(self, image_array):
        # init spi
        spi = spidev.SpiDev()
        spi.open(self.spibus_num, self.spidevice_num)
        spi.max_speed_hz = self.spi_speed_hz
        spi.mode = 0b11 #spi mode3

        with open(self.spi_cs_pin, mode='wb',buffering=0) as cs_pin:
            # set reg index
            cs_pin.write(self.PIN_ACTIVE)
            send_data = [0x70, 0x00, 0x22]  #startbyte RS=0,R/W=W
            spi.writebytes(send_data)
            cs_pin.write(self.PIN_INACTIVE)

            # send GRAM data
            cs_pin.write(self.PIN_ACTIVE)
            ## startbyte RS=1,R/W=W
            send_data = np.insert(image_array, 0, 0x72)
            spi.writebytes2(send_data)
            cs_pin.write(self.PIN_INACTIVE)

        spi.close()

    
    def init_ili9328(self):
        # init spi cs pin.
        with open(self.spi_cs_pin, mode='wb',buffering=0) as cs_pin:
            cs_pin.write(self.PIN_INACTIVE)
        
        # Reset ILI9328
        with open(self.reset_pin, mode='wb',buffering=0) as rst_pin:
            rst_pin.write(self.PIN_INACTIVE)
            time.sleep(0.01)
            rst_pin.write(self.PIN_ACTIVE)
            time.sleep(0.01)
            rst_pin.write(self.PIN_INACTIVE)
            time.sleep(0.05)
        
        # init ILI9328
        # -------------- Start Initial Sequence ----------
        self.write_cmd(0x0001, 0x0100)  # set SS and SM bit
        self.write_cmd(0x0002, 0x0700)  # set 1 line inversion
        self.write_cmd(0x0003, 0x1030)  # set GRAM write direction and BGR=1.
        self.write_cmd(0x0004, 0x0000)  # Resize register
        self.write_cmd(0x0008, 0x0207)  # set the back porch and front porch
        self.write_cmd(0x0009, 0x0000)  # set non-display area refresh cycle ISC[3:0]
        self.write_cmd(0x000A, 0x0000)  # FMARK function
        self.write_cmd(0x000C, 0x0000)  # RGB interface setting
        self.write_cmd(0x000D, 0x0000)  # Frame marker Position
        self.write_cmd(0x000F, 0x0000)  # RGB interface polarity
        # -------------- Power On sequence ---------------
        self.write_cmd(0x0010, 0x0000)  # SAP, BT[3:0], AP, DSTB, SLP, STB
        self.write_cmd(0x0011, 0x0007)  # DC1[2:0], DC0[2:0], VC[2:0]
        self.write_cmd(0x0012, 0x0000)  # VREG1OUT voltage
        self.write_cmd(0x0013, 0x0000)  # VDV[4:0] for VCOM amplitude
        self.write_cmd(0x0007, 0x0001)  # Dis-charge capacitor power voltage
        time.sleep(0.2)
        self.write_cmd(0x0010, 0x1490)  # SAP, BT[3:0], AP, DSTB, SLP, STB
        self.write_cmd(0x0011, 0x0227)  # DC1[2:0], DC0[2:0], VC[2:0]
        time.sleep(0.05)                # Delay 50ms
        self.write_cmd(0x0012, 0x001C)  # Internal reference voltage= Vci;
        time.sleep(0.05)                # Delay 50ms
        self.write_cmd(0x0013, 0x1A00)  # Set VDV[4:0] for VCOM amplitude
        self.write_cmd(0x0029, 0x0025)  # Set VCM[5:0] for VCOMH
        self.write_cmd(0x002B, 0x000C)  # Set Frame Rate
        time.sleep(0.05)                # Delay 50ms
        self.write_cmd(0x0020, 0x0000)  # GRAM horizontal Address
        self.write_cmd(0x0021, 0x0000)  # GRAM Vertical Address
        # -------------- Adjust the Gamma  Curve ---------
        self.write_cmd(0x0030, 0x0000)
        self.write_cmd(0x0031, 0x0506)
        self.write_cmd(0x0032, 0x0104)
        self.write_cmd(0x0035, 0x0207)
        self.write_cmd(0x0036, 0x000F)
        self.write_cmd(0x0037, 0x0306)
        self.write_cmd(0x0038, 0x0102)
        self.write_cmd(0x0039, 0x0707)
        self.write_cmd(0x003C, 0x0702)
        self.write_cmd(0x003D, 0x1604)
        # -------------- Set GRAM area -------------------
        self.write_cmd(0x0050, 0x0000)  # Horizontal GRAM Start Address
        self.write_cmd(0x0051, 0x00EF)  # Horizontal GRAM End Address
        self.write_cmd(0x0052, 0x0000)  # Vertical GRAM Start Address
        self.write_cmd(0x0053, 0x013F)  # Vertical GRAM End Address 
        self.write_cmd(0x0060, 0xA700)  # Gate Scan Line
        self.write_cmd(0x0061, 0x0001)  # NDL,VLE, REV
        self.write_cmd(0x006A, 0x0000)  # set scrolling line
        # -------------- Partial Display Control ---------
        self.write_cmd(0x0080, 0x0000)
        self.write_cmd(0x0081, 0x0000)
        self.write_cmd(0x0082, 0x0000)
        self.write_cmd(0x0083, 0x0000)
        self.write_cmd(0x0084, 0x0000)
        self.write_cmd(0x0085, 0x0000)
        # -------------- Panel Control -------------------
        self.write_cmd(0x0090, 0x0010)
        self.write_cmd(0x0092, 0x0600)
        # -------------- Power On sequence ---------------
        self.write_cmd(0x0007, 0x0133)  # 262K color and display ON 
