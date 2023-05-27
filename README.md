# simple-pytft

## 概要(Overview)
これは組込み向けのPythonTFT液晶ライブラリです。
This is a Python TFT-LCD library for embedded applications.

## 特徴(Feature)
* ユーザアプリ用です。
* Linux環境向けです.Micropythonは未対応.
* Raspherry Pi環境に依存しません.SPI(spidev)やGPIO(Sysfs)など最小限のI/Fを使用します.
* PillowのImageオブジェクトを画面に表示できます.
* 動画表示はパフォーマンス的にできません.
* For user applications.
* Micropython is not supported.
* Uses minimal I/F such as SPI(spidev) and GPIO(Sysfs).
* Can display Pillow's Image object on the screen.
* Video display is not possible for performance reasons.

## 対応デバイス(Supported Devices)
<dl>
    <dt>ILITEK ILI9328 SPI mode 240*320</dt>
    <dd>依存module : Numpy,pyspidev<br>
        Class : ili9328spi<br>
        I/F : spidev, GPIO(Sysfs)</dd>
</dl>

## Sample Code
<dl>
    <dt>ILITEK ILI9328 SPI mode 240*320</dt>
    <dd>System Monitor</dd>

![sysmon](doc/images/sample_ili9328_sysmon.jpg "system monitor")
    <dd>matplotlib graph</dd>

![graph](doc/images/sample_ili9328_graph.jpg "matplotlib graph")
</dl>
