~~~ bash
sudo apt update
~~~

~~~ bash
sudo apt upgrade -y
~~~

~~~ bash
sudo reboot
~~~

~~~ bash
sudo raspi-config
~~~






~~~

├── .gitattributes
├── README.md
├── main.py
├── src/
│   ├── .gitkeeep
│   ├── downlink/
│   │   ├── .gitkeeep
│   │   ├── downlink.py
│   │   ├── event_listeners/
│   │   │   ├── bmp280_event_listener.py
│   │   │   ├── mpu6050_event_listener.py
│   │   │   └── sim7600E_event_listener.py
│   │   └── event_triggers/
│   │       ├── bmp280_event_trigger.py
│   │       ├── mpu6050_event_trigger.py
│   │       └── sim7600E_event_trigger.py
│   ├── logger/
│   │   ├── bmp280_logger.py
│   │   ├── data/
│   │   │   ├── DHT11.txt
│   │   │   ├── MPU6050.txt
│   │   │   ├── sound_data_D0.txt
│   │   │   └── sound_data_D0_backup.txt
│   │   ├── dht_logger.py
│   │   ├── mpu6050_logger.py
│   │   └── sound_logger.py
│   ├── photography/
│   │   ├── footage/
│   │   │   ├── .gitkeep
│   │   │   ├── images/
│   │   │   │   └── .gitkeep
│   │   │   └── videos/
│   │   │       └── .gitkeep
│   │   ├── image_capture.py
│   │   └── video_capture.py
│   ├── plotter/
│   │   ├── bmp280_plotter.py
│   │   ├── dht_plotter.py
│   │   ├── mpu6050_plotter.py
│   │   └── sound_plotter.py
│   └── tracking/
│       └── gps.py
├── venv/
│   ├── bin/
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── activate.csh
│   │   ├── activate.fish
│   │   ├── pinout
│   │   ├── pintest
│   │   ├── pip3
│   │   ├── pip3.11
│   │   ├── python
│   │   ├── python3
│   │   └── ttx
│   ├── lib/
│   │   ├── python3.11
│   │   └── python3.11/
│   │       └── site-packages/
│   │           ├── Adafruit_DHT/
│   │           │   ├── Beaglebone_Black.py
│   │           │   ├── Raspberry_Pi.py
│   │           │   ├── Raspberry_Pi_2.py
│   │           │   ├── Raspberry_Pi_2_Driver.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── Test.py
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── Beaglebone_Black.cpython-311.pyc
│   │           │   │   ├── Raspberry_Pi.cpython-311.pyc
│   │           │   │   ├── Raspberry_Pi_2.cpython-311.pyc
│   │           │   │   ├── Test.cpython-311.pyc
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── common.cpython-311.pyc
│   │           │   │   └── platform_detect.cpython-311.pyc
│   │           │   ├── common.py
│   │           │   └── platform_detect.py
│   │           ├── PIL/
│   │           │   ├── AvifImagePlugin.py
│   │           │   ├── BdfFontFile.py
│   │           │   ├── BlpImagePlugin.py
│   │           │   ├── BmpImagePlugin.py
│   │           │   ├── BufrStubImagePlugin.py
│   │           │   ├── ContainerIO.py
│   │           │   ├── CurImagePlugin.py
│   │           │   ├── DcxImagePlugin.py
│   │           │   ├── DdsImagePlugin.py
│   │           │   ├── EpsImagePlugin.py
│   │           │   ├── ExifTags.py
│   │           │   ├── FitsImagePlugin.py
│   │           │   ├── FliImagePlugin.py
│   │           │   ├── FontFile.py
│   │           │   ├── FpxImagePlugin.py
│   │           │   ├── FtexImagePlugin.py
│   │           │   ├── GbrImagePlugin.py
│   │           │   ├── GdImageFile.py
│   │           │   ├── GifImagePlugin.py
│   │           │   ├── GimpGradientFile.py
│   │           │   ├── GimpPaletteFile.py
│   │           │   ├── GribStubImagePlugin.py
│   │           │   ├── Hdf5StubImagePlugin.py
│   │           │   ├── IcnsImagePlugin.py
│   │           │   ├── IcoImagePlugin.py
│   │           │   ├── ImImagePlugin.py
│   │           │   ├── Image.py
│   │           │   ├── ImageChops.py
│   │           │   ├── ImageCms.py
│   │           │   ├── ImageColor.py
│   │           │   ├── ImageDraw.py
│   │           │   ├── ImageDraw2.py
│   │           │   ├── ImageEnhance.py
│   │           │   ├── ImageFile.py
│   │           │   ├── ImageFilter.py
│   │           │   ├── ImageFont.py
│   │           │   ├── ImageGrab.py
│   │           │   ├── ImageMath.py
│   │           │   ├── ImageMode.py
│   │           │   ├── ImageMorph.py
│   │           │   ├── ImageOps.py
│   │           │   ├── ImagePalette.py
│   │           │   ├── ImagePath.py
│   │           │   ├── ImageQt.py
│   │           │   ├── ImageSequence.py
│   │           │   ├── ImageShow.py
│   │           │   ├── ImageStat.py
│   │           │   ├── ImageTk.py
│   │           │   ├── ImageTransform.py
│   │           │   ├── ImageWin.py
│   │           │   ├── ImtImagePlugin.py
│   │           │   ├── IptcImagePlugin.py
│   │           │   ├── Jpeg2KImagePlugin.py
│   │           │   ├── JpegImagePlugin.py
│   │           │   ├── JpegPresets.py
│   │           │   ├── McIdasImagePlugin.py
│   │           │   ├── MicImagePlugin.py
│   │           │   ├── MpegImagePlugin.py
│   │           │   ├── MpoImagePlugin.py
│   │           │   ├── MspImagePlugin.py
│   │           │   ├── PSDraw.py
│   │           │   ├── PaletteFile.py
│   │           │   ├── PalmImagePlugin.py
│   │           │   ├── PcdImagePlugin.py
│   │           │   ├── PcfFontFile.py
│   │           │   ├── PcxImagePlugin.py
│   │           │   ├── PdfImagePlugin.py
│   │           │   ├── PdfParser.py
│   │           │   ├── PixarImagePlugin.py
│   │           │   ├── PngImagePlugin.py
│   │           │   ├── PpmImagePlugin.py
│   │           │   ├── PsdImagePlugin.py
│   │           │   ├── QoiImagePlugin.py
│   │           │   ├── SgiImagePlugin.py
│   │           │   ├── SpiderImagePlugin.py
│   │           │   ├── SunImagePlugin.py
│   │           │   ├── TarIO.py
│   │           │   ├── TgaImagePlugin.py
│   │           │   ├── TiffImagePlugin.py
│   │           │   ├── TiffTags.py
│   │           │   ├── WalImageFile.py
│   │           │   ├── WebPImagePlugin.py
│   │           │   ├── WmfImagePlugin.py
│   │           │   ├── XVThumbImagePlugin.py
│   │           │   ├── XbmImagePlugin.py
│   │           │   ├── XpmImagePlugin.py
│   │           │   ├── __init__.py
│   │           │   ├── __main__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── AvifImagePlugin.cpython-311.pyc
│   │           │   │   ├── BdfFontFile.cpython-311.pyc
│   │           │   │   ├── BlpImagePlugin.cpython-311.pyc
│   │           │   │   ├── BmpImagePlugin.cpython-311.pyc
│   │           │   │   ├── BufrStubImagePlugin.cpython-311.pyc
│   │           │   │   ├── ContainerIO.cpython-311.pyc
│   │           │   │   ├── CurImagePlugin.cpython-311.pyc
│   │           │   │   ├── DcxImagePlugin.cpython-311.pyc
│   │           │   │   ├── DdsImagePlugin.cpython-311.pyc
│   │           │   │   ├── EpsImagePlugin.cpython-311.pyc
│   │           │   │   ├── ExifTags.cpython-311.pyc
│   │           │   │   ├── FitsImagePlugin.cpython-311.pyc
│   │           │   │   ├── FliImagePlugin.cpython-311.pyc
│   │           │   │   ├── FontFile.cpython-311.pyc
│   │           │   │   ├── FpxImagePlugin.cpython-311.pyc
│   │           │   │   ├── FtexImagePlugin.cpython-311.pyc
│   │           │   │   ├── GbrImagePlugin.cpython-311.pyc
│   │           │   │   ├── GdImageFile.cpython-311.pyc
│   │           │   │   ├── GifImagePlugin.cpython-311.pyc
│   │           │   │   ├── GimpGradientFile.cpython-311.pyc
│   │           │   │   ├── GimpPaletteFile.cpython-311.pyc
│   │           │   │   ├── GribStubImagePlugin.cpython-311.pyc
│   │           │   │   ├── Hdf5StubImagePlugin.cpython-311.pyc
│   │           │   │   ├── IcnsImagePlugin.cpython-311.pyc
│   │           │   │   ├── IcoImagePlugin.cpython-311.pyc
│   │           │   │   ├── ImImagePlugin.cpython-311.pyc
│   │           │   │   ├── Image.cpython-311.pyc
│   │           │   │   ├── ImageChops.cpython-311.pyc
│   │           │   │   ├── ImageCms.cpython-311.pyc
│   │           │   │   ├── ImageColor.cpython-311.pyc
│   │           │   │   ├── ImageDraw.cpython-311.pyc
│   │           │   │   ├── ImageDraw2.cpython-311.pyc
│   │           │   │   ├── ImageEnhance.cpython-311.pyc
│   │           │   │   ├── ImageFile.cpython-311.pyc
│   │           │   │   ├── ImageFilter.cpython-311.pyc
│   │           │   │   ├── ImageFont.cpython-311.pyc
│   │           │   │   ├── ImageGrab.cpython-311.pyc
│   │           │   │   ├── ImageMath.cpython-311.pyc
│   │           │   │   ├── ImageMode.cpython-311.pyc
│   │           │   │   ├── ImageMorph.cpython-311.pyc
│   │           │   │   ├── ImageOps.cpython-311.pyc
│   │           │   │   ├── ImagePalette.cpython-311.pyc
│   │           │   │   ├── ImagePath.cpython-311.pyc
│   │           │   │   ├── ImageQt.cpython-311.pyc
│   │           │   │   ├── ImageSequence.cpython-311.pyc
│   │           │   │   ├── ImageShow.cpython-311.pyc
│   │           │   │   ├── ImageStat.cpython-311.pyc
│   │           │   │   ├── ImageTk.cpython-311.pyc
│   │           │   │   ├── ImageTransform.cpython-311.pyc
│   │           │   │   ├── ImageWin.cpython-311.pyc
│   │           │   │   ├── ImtImagePlugin.cpython-311.pyc
│   │           │   │   ├── IptcImagePlugin.cpython-311.pyc
│   │           │   │   ├── Jpeg2KImagePlugin.cpython-311.pyc
│   │           │   │   ├── JpegImagePlugin.cpython-311.pyc
│   │           │   │   ├── JpegPresets.cpython-311.pyc
│   │           │   │   ├── McIdasImagePlugin.cpython-311.pyc
│   │           │   │   ├── MicImagePlugin.cpython-311.pyc
│   │           │   │   ├── MpegImagePlugin.cpython-311.pyc
│   │           │   │   ├── MpoImagePlugin.cpython-311.pyc
│   │           │   │   ├── MspImagePlugin.cpython-311.pyc
│   │           │   │   ├── PSDraw.cpython-311.pyc
│   │           │   │   ├── PaletteFile.cpython-311.pyc
│   │           │   │   ├── PalmImagePlugin.cpython-311.pyc
│   │           │   │   ├── PcdImagePlugin.cpython-311.pyc
│   │           │   │   ├── PcfFontFile.cpython-311.pyc
│   │           │   │   ├── PcxImagePlugin.cpython-311.pyc
│   │           │   │   ├── PdfImagePlugin.cpython-311.pyc
│   │           │   │   ├── PdfParser.cpython-311.pyc
│   │           │   │   ├── PixarImagePlugin.cpython-311.pyc
│   │           │   │   ├── PngImagePlugin.cpython-311.pyc
│   │           │   │   ├── PpmImagePlugin.cpython-311.pyc
│   │           │   │   ├── PsdImagePlugin.cpython-311.pyc
│   │           │   │   ├── QoiImagePlugin.cpython-311.pyc
│   │           │   │   ├── SgiImagePlugin.cpython-311.pyc
│   │           │   │   ├── SpiderImagePlugin.cpython-311.pyc
│   │           │   │   ├── SunImagePlugin.cpython-311.pyc
│   │           │   │   ├── TarIO.cpython-311.pyc
│   │           │   │   ├── TgaImagePlugin.cpython-311.pyc
│   │           │   │   ├── TiffImagePlugin.cpython-311.pyc
│   │           │   │   ├── TiffTags.cpython-311.pyc
│   │           │   │   ├── WalImageFile.cpython-311.pyc
│   │           │   │   ├── WebPImagePlugin.cpython-311.pyc
│   │           │   │   ├── WmfImagePlugin.cpython-311.pyc
│   │           │   │   ├── XVThumbImagePlugin.cpython-311.pyc
│   │           │   │   ├── XbmImagePlugin.cpython-311.pyc
│   │           │   │   ├── XpmImagePlugin.cpython-311.pyc
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── __main__.cpython-311.pyc
│   │           │   │   ├── _binary.cpython-311.pyc
│   │           │   │   ├── _deprecate.cpython-311.pyc
│   │           │   │   ├── _tkinter_finder.cpython-311.pyc
│   │           │   │   ├── _typing.cpython-311.pyc
│   │           │   │   ├── _util.cpython-311.pyc
│   │           │   │   ├── _version.cpython-311.pyc
│   │           │   │   ├── features.cpython-311.pyc
│   │           │   │   └── report.cpython-311.pyc
│   │           │   ├── _avif.pyi
│   │           │   ├── _binary.py
│   │           │   ├── _deprecate.py
│   │           │   ├── _imaging.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _imaging.pyi
│   │           │   ├── _imagingcms.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _imagingcms.pyi
│   │           │   ├── _imagingft.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _imagingft.pyi
│   │           │   ├── _imagingmath.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _imagingmath.pyi
│   │           │   ├── _imagingmorph.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _imagingmorph.pyi
│   │           │   ├── _imagingtk.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _imagingtk.pyi
│   │           │   ├── _tkinter_finder.py
│   │           │   ├── _typing.py
│   │           │   ├── _util.py
│   │           │   ├── _version.py
│   │           │   ├── _webp.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _webp.pyi
│   │           │   ├── features.py
│   │           │   ├── py.typed
│   │           │   └── report.py
│   │           ├── __pycache__/
│   │           │   ├── lgpio.cpython-311.pyc
│   │           │   ├── pylab.cpython-311.pyc
│   │           │   └── six.cpython-311.pyc
│   │           ├── _distutils_hack/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   └── override.cpython-311.pyc
│   │           │   └── override.py
│   │           ├── _lgpio.cpython-311-arm-linux-gnueabihf.so
│   │           ├── adafruit_dht-1.4.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   └── top_level.txt
│   │           ├── blinker-1.9.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.txt
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   └── WHEEL
│   │           ├── blinker/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _utilities.cpython-311.pyc
│   │           │   │   └── base.cpython-311.pyc
│   │           │   ├── _utilities.py
│   │           │   ├── base.py
│   │           │   └── py.typed
│   │           ├── click-8.3.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   └── licenses/
│   │           │       └── LICENSE.txt
│   │           ├── click/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _compat.cpython-311.pyc
│   │           │   │   ├── _termui_impl.cpython-311.pyc
│   │           │   │   ├── _textwrap.cpython-311.pyc
│   │           │   │   ├── _utils.cpython-311.pyc
│   │           │   │   ├── _winconsole.cpython-311.pyc
│   │           │   │   ├── core.cpython-311.pyc
│   │           │   │   ├── decorators.cpython-311.pyc
│   │           │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   ├── formatting.cpython-311.pyc
│   │           │   │   ├── globals.cpython-311.pyc
│   │           │   │   ├── parser.cpython-311.pyc
│   │           │   │   ├── shell_completion.cpython-311.pyc
│   │           │   │   ├── termui.cpython-311.pyc
│   │           │   │   ├── testing.cpython-311.pyc
│   │           │   │   ├── types.cpython-311.pyc
│   │           │   │   └── utils.cpython-311.pyc
│   │           │   ├── _compat.py
│   │           │   ├── _termui_impl.py
│   │           │   ├── _textwrap.py
│   │           │   ├── _utils.py
│   │           │   ├── _winconsole.py
│   │           │   ├── core.py
│   │           │   ├── decorators.py
│   │           │   ├── exceptions.py
│   │           │   ├── formatting.py
│   │           │   ├── globals.py
│   │           │   ├── parser.py
│   │           │   ├── py.typed
│   │           │   ├── shell_completion.py
│   │           │   ├── termui.py
│   │           │   ├── testing.py
│   │           │   ├── types.py
│   │           │   └── utils.py
│   │           ├── colorzero-2.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.txt
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   └── top_level.txt
│   │           ├── colorzero/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── attr.cpython-311.pyc
│   │           │   │   ├── color.cpython-311.pyc
│   │           │   │   ├── conversions.cpython-311.pyc
│   │           │   │   ├── deltae.cpython-311.pyc
│   │           │   │   ├── easings.cpython-311.pyc
│   │           │   │   ├── tables.cpython-311.pyc
│   │           │   │   └── types.cpython-311.pyc
│   │           │   ├── attr.py
│   │           │   ├── color.py
│   │           │   ├── conversions.py
│   │           │   ├── deltae.py
│   │           │   ├── easings.py
│   │           │   ├── tables.py
│   │           │   └── types.py
│   │           ├── contourpy-1.3.3.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   └── WHEEL
│   │           ├── contourpy/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _version.cpython-311.pyc
│   │           │   │   ├── array.cpython-311.pyc
│   │           │   │   ├── chunk.cpython-311.pyc
│   │           │   │   ├── convert.cpython-311.pyc
│   │           │   │   ├── dechunk.cpython-311.pyc
│   │           │   │   ├── enum_util.cpython-311.pyc
│   │           │   │   ├── typecheck.cpython-311.pyc
│   │           │   │   └── types.cpython-311.pyc
│   │           │   ├── _contourpy.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _contourpy.pyi
│   │           │   ├── _version.py
│   │           │   ├── array.py
│   │           │   ├── chunk.py
│   │           │   ├── convert.py
│   │           │   ├── dechunk.py
│   │           │   ├── enum_util.py
│   │           │   ├── py.typed
│   │           │   ├── typecheck.py
│   │           │   ├── types.py
│   │           │   └── util/
│   │           │       ├── __init__.py
│   │           │       ├── __pycache__/
│   │           │       │   ├── __init__.cpython-311.pyc
│   │           │       │   ├── _build_config.cpython-311.pyc
│   │           │       │   ├── bokeh_renderer.cpython-311.pyc
│   │           │       │   ├── bokeh_util.cpython-311.pyc
│   │           │       │   ├── data.cpython-311.pyc
│   │           │       │   ├── mpl_renderer.cpython-311.pyc
│   │           │       │   ├── mpl_util.cpython-311.pyc
│   │           │       │   └── renderer.cpython-311.pyc
│   │           │       ├── _build_config.py
│   │           │       ├── bokeh_renderer.py
│   │           │       ├── bokeh_util.py
│   │           │       ├── data.py
│   │           │       ├── mpl_renderer.py
│   │           │       ├── mpl_util.py
│   │           │       └── renderer.py
│   │           ├── cycler-0.12.1.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   └── top_level.txt
│   │           ├── cycler/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   └── __init__.cpython-311.pyc
│   │           │   └── py.typed
│   │           ├── dateutil/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _common.cpython-311.pyc
│   │           │   │   ├── _version.cpython-311.pyc
│   │           │   │   ├── easter.cpython-311.pyc
│   │           │   │   ├── relativedelta.cpython-311.pyc
│   │           │   │   ├── rrule.cpython-311.pyc
│   │           │   │   ├── tzwin.cpython-311.pyc
│   │           │   │   └── utils.cpython-311.pyc
│   │           │   ├── _common.py
│   │           │   ├── _version.py
│   │           │   ├── easter.py
│   │           │   ├── parser/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _parser.cpython-311.pyc
│   │           │   │   │   └── isoparser.cpython-311.pyc
│   │           │   │   ├── _parser.py
│   │           │   │   └── isoparser.py
│   │           │   ├── relativedelta.py
│   │           │   ├── rrule.py
│   │           │   ├── tz/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _common.cpython-311.pyc
│   │           │   │   │   ├── _factories.cpython-311.pyc
│   │           │   │   │   ├── tz.cpython-311.pyc
│   │           │   │   │   └── win.cpython-311.pyc
│   │           │   │   ├── _common.py
│   │           │   │   ├── _factories.py
│   │           │   │   ├── tz.py
│   │           │   │   └── win.py
│   │           │   ├── tzwin.py
│   │           │   ├── utils.py
│   │           │   └── zoneinfo/
│   │           │       ├── __init__.py
│   │           │       ├── __pycache__/
│   │           │       │   ├── __init__.cpython-311.pyc
│   │           │       │   └── rebuild.cpython-311.pyc
│   │           │       ├── dateutil-zoneinfo.tar.gz
│   │           │       └── rebuild.py
│   │           ├── distutils-precedence.pth
│   │           ├── flask-3.1.2.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   ├── entry_points.txt
│   │           │   └── licenses/
│   │           │       └── LICENSE.txt
│   │           ├── flask
│   │           ├── flask/
│   │           │   ├── __init__.py
│   │           │   ├── __main__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── __main__.cpython-311.pyc
│   │           │   │   ├── app.cpython-311.pyc
│   │           │   │   ├── blueprints.cpython-311.pyc
│   │           │   │   ├── cli.cpython-311.pyc
│   │           │   │   ├── config.cpython-311.pyc
│   │           │   │   ├── ctx.cpython-311.pyc
│   │           │   │   ├── debughelpers.cpython-311.pyc
│   │           │   │   ├── globals.cpython-311.pyc
│   │           │   │   ├── helpers.cpython-311.pyc
│   │           │   │   ├── logging.cpython-311.pyc
│   │           │   │   ├── sessions.cpython-311.pyc
│   │           │   │   ├── signals.cpython-311.pyc
│   │           │   │   ├── templating.cpython-311.pyc
│   │           │   │   ├── testing.cpython-311.pyc
│   │           │   │   ├── typing.cpython-311.pyc
│   │           │   │   ├── views.cpython-311.pyc
│   │           │   │   └── wrappers.cpython-311.pyc
│   │           │   ├── app.py
│   │           │   ├── blueprints.py
│   │           │   ├── cli.py
│   │           │   ├── config.py
│   │           │   ├── ctx.py
│   │           │   ├── debughelpers.py
│   │           │   ├── globals.py
│   │           │   ├── helpers.py
│   │           │   ├── json
│   │           │   ├── json/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── provider.cpython-311.pyc
│   │           │   │   │   └── tag.cpython-311.pyc
│   │           │   │   ├── provider.py
│   │           │   │   └── tag.py
│   │           │   ├── logging.py
│   │           │   ├── py.typed
│   │           │   ├── sansio/
│   │           │   │   ├── README.md
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── app.cpython-311.pyc
│   │           │   │   │   ├── blueprints.cpython-311.pyc
│   │           │   │   │   └── scaffold.cpython-311.pyc
│   │           │   │   ├── app.py
│   │           │   │   ├── blueprints.py
│   │           │   │   └── scaffold.py
│   │           │   ├── sessions.py
│   │           │   ├── signals.py
│   │           │   ├── templating.py
│   │           │   ├── testing.py
│   │           │   ├── typing.py
│   │           │   ├── views.py
│   │           │   └── wrappers.py
│   │           ├── fontTools/
│   │           │   ├── __init__.py
│   │           │   ├── __main__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── __main__.cpython-311.pyc
│   │           │   │   ├── afmLib.cpython-311.pyc
│   │           │   │   ├── agl.cpython-311.pyc
│   │           │   │   ├── annotations.cpython-311.pyc
│   │           │   │   ├── fontBuilder.cpython-311.pyc
│   │           │   │   ├── help.cpython-311.pyc
│   │           │   │   ├── tfmLib.cpython-311.pyc
│   │           │   │   ├── ttx.cpython-311.pyc
│   │           │   │   └── unicode.cpython-311.pyc
│   │           │   ├── afmLib.py
│   │           │   ├── agl.py
│   │           │   ├── annotations.py
│   │           │   ├── cffLib/
│   │           │   │   ├── CFF2ToCFF.py
│   │           │   │   ├── CFFToCFF2.py
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── CFF2ToCFF.cpython-311.pyc
│   │           │   │   │   ├── CFFToCFF2.cpython-311.pyc
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── specializer.cpython-311.pyc
│   │           │   │   │   ├── transforms.cpython-311.pyc
│   │           │   │   │   └── width.cpython-311.pyc
│   │           │   │   ├── specializer.py
│   │           │   │   ├── transforms.py
│   │           │   │   └── width.py
│   │           │   ├── colorLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── builder.cpython-311.pyc
│   │           │   │   │   ├── errors.cpython-311.pyc
│   │           │   │   │   ├── geometry.cpython-311.pyc
│   │           │   │   │   ├── table_builder.cpython-311.pyc
│   │           │   │   │   └── unbuilder.cpython-311.pyc
│   │           │   │   ├── builder.py
│   │           │   │   ├── errors.py
│   │           │   │   ├── geometry.py
│   │           │   │   ├── table_builder.py
│   │           │   │   └── unbuilder.py
│   │           │   ├── config/
│   │           │   │   ├── __init__.py
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── cu2qu/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── benchmark.cpython-311.pyc
│   │           │   │   │   ├── cli.cpython-311.pyc
│   │           │   │   │   ├── cu2qu.cpython-311.pyc
│   │           │   │   │   ├── errors.cpython-311.pyc
│   │           │   │   │   └── ufo.cpython-311.pyc
│   │           │   │   ├── benchmark.py
│   │           │   │   ├── cli.py
│   │           │   │   ├── cu2qu.py
│   │           │   │   ├── errors.py
│   │           │   │   └── ufo.py
│   │           │   ├── designspaceLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── split.cpython-311.pyc
│   │           │   │   │   ├── statNames.cpython-311.pyc
│   │           │   │   │   └── types.cpython-311.pyc
│   │           │   │   ├── split.py
│   │           │   │   ├── statNames.py
│   │           │   │   └── types.py
│   │           │   ├── encodings/
│   │           │   │   ├── MacRoman.py
│   │           │   │   ├── StandardEncoding.py
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── MacRoman.cpython-311.pyc
│   │           │   │   │   ├── StandardEncoding.cpython-311.pyc
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── codecs.cpython-311.pyc
│   │           │   │   └── codecs.py
│   │           │   ├── feaLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── ast.cpython-311.pyc
│   │           │   │   │   ├── builder.cpython-311.pyc
│   │           │   │   │   ├── error.cpython-311.pyc
│   │           │   │   │   ├── lexer.cpython-311.pyc
│   │           │   │   │   ├── location.cpython-311.pyc
│   │           │   │   │   ├── lookupDebugInfo.cpython-311.pyc
│   │           │   │   │   ├── parser.cpython-311.pyc
│   │           │   │   │   └── variableScalar.cpython-311.pyc
│   │           │   │   ├── ast.py
│   │           │   │   ├── builder.py
│   │           │   │   ├── error.py
│   │           │   │   ├── lexer.py
│   │           │   │   ├── location.py
│   │           │   │   ├── lookupDebugInfo.py
│   │           │   │   ├── parser.py
│   │           │   │   └── variableScalar.py
│   │           │   ├── fontBuilder.py
│   │           │   ├── help.py
│   │           │   ├── merge
│   │           │   ├── merge/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── base.cpython-311.pyc
│   │           │   │   │   ├── cmap.cpython-311.pyc
│   │           │   │   │   ├── layout.cpython-311.pyc
│   │           │   │   │   ├── options.cpython-311.pyc
│   │           │   │   │   ├── tables.cpython-311.pyc
│   │           │   │   │   ├── unicode.cpython-311.pyc
│   │           │   │   │   └── util.cpython-311.pyc
│   │           │   │   ├── base.py
│   │           │   │   ├── cmap.py
│   │           │   │   ├── layout.py
│   │           │   │   ├── options.py
│   │           │   │   ├── tables.py
│   │           │   │   ├── unicode.py
│   │           │   │   └── util.py
│   │           │   ├── misc/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── arrayTools.cpython-311.pyc
│   │           │   │   │   ├── bezierTools.cpython-311.pyc
│   │           │   │   │   ├── classifyTools.cpython-311.pyc
│   │           │   │   │   ├── cliTools.cpython-311.pyc
│   │           │   │   │   ├── configTools.cpython-311.pyc
│   │           │   │   │   ├── cython.cpython-311.pyc
│   │           │   │   │   ├── dictTools.cpython-311.pyc
│   │           │   │   │   ├── eexec.cpython-311.pyc
│   │           │   │   │   ├── encodingTools.cpython-311.pyc
│   │           │   │   │   ├── enumTools.cpython-311.pyc
│   │           │   │   │   ├── etree.cpython-311.pyc
│   │           │   │   │   ├── filenames.cpython-311.pyc
│   │           │   │   │   ├── fixedTools.cpython-311.pyc
│   │           │   │   │   ├── intTools.cpython-311.pyc
│   │           │   │   │   ├── iterTools.cpython-311.pyc
│   │           │   │   │   ├── lazyTools.cpython-311.pyc
│   │           │   │   │   ├── loggingTools.cpython-311.pyc
│   │           │   │   │   ├── macCreatorType.cpython-311.pyc
│   │           │   │   │   ├── macRes.cpython-311.pyc
│   │           │   │   │   ├── psCharStrings.cpython-311.pyc
│   │           │   │   │   ├── psLib.cpython-311.pyc
│   │           │   │   │   ├── psOperators.cpython-311.pyc
│   │           │   │   │   ├── py23.cpython-311.pyc
│   │           │   │   │   ├── roundTools.cpython-311.pyc
│   │           │   │   │   ├── sstruct.cpython-311.pyc
│   │           │   │   │   ├── symfont.cpython-311.pyc
│   │           │   │   │   ├── testTools.cpython-311.pyc
│   │           │   │   │   ├── textTools.cpython-311.pyc
│   │           │   │   │   ├── timeTools.cpython-311.pyc
│   │           │   │   │   ├── transform.cpython-311.pyc
│   │           │   │   │   ├── treeTools.cpython-311.pyc
│   │           │   │   │   ├── vector.cpython-311.pyc
│   │           │   │   │   ├── visitor.cpython-311.pyc
│   │           │   │   │   ├── xmlReader.cpython-311.pyc
│   │           │   │   │   └── xmlWriter.cpython-311.pyc
│   │           │   │   ├── arrayTools.py
│   │           │   │   ├── bezierTools.py
│   │           │   │   ├── classifyTools.py
│   │           │   │   ├── cliTools.py
│   │           │   │   ├── configTools.py
│   │           │   │   ├── cython.py
│   │           │   │   ├── dictTools.py
│   │           │   │   ├── eexec.py
│   │           │   │   ├── encodingTools.py
│   │           │   │   ├── enumTools.py
│   │           │   │   ├── etree.py
│   │           │   │   ├── filenames.py
│   │           │   │   ├── filesystem/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _base.cpython-311.pyc
│   │           │   │   │   │   ├── _copy.cpython-311.pyc
│   │           │   │   │   │   ├── _errors.cpython-311.pyc
│   │           │   │   │   │   ├── _info.cpython-311.pyc
│   │           │   │   │   │   ├── _osfs.cpython-311.pyc
│   │           │   │   │   │   ├── _path.cpython-311.pyc
│   │           │   │   │   │   ├── _subfs.cpython-311.pyc
│   │           │   │   │   │   ├── _tempfs.cpython-311.pyc
│   │           │   │   │   │   ├── _tools.cpython-311.pyc
│   │           │   │   │   │   ├── _walk.cpython-311.pyc
│   │           │   │   │   │   └── _zipfs.cpython-311.pyc
│   │           │   │   │   ├── _base.py
│   │           │   │   │   ├── _copy.py
│   │           │   │   │   ├── _errors.py
│   │           │   │   │   ├── _info.py
│   │           │   │   │   ├── _osfs.py
│   │           │   │   │   ├── _path.py
│   │           │   │   │   ├── _subfs.py
│   │           │   │   │   ├── _tempfs.py
│   │           │   │   │   ├── _tools.py
│   │           │   │   │   ├── _walk.py
│   │           │   │   │   └── _zipfs.py
│   │           │   │   ├── fixedTools.py
│   │           │   │   ├── intTools.py
│   │           │   │   ├── iterTools.py
│   │           │   │   ├── lazyTools.py
│   │           │   │   ├── loggingTools.py
│   │           │   │   ├── macCreatorType.py
│   │           │   │   ├── macRes.py
│   │           │   │   ├── plistlib/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   └── __init__.cpython-311.pyc
│   │           │   │   │   └── py.typed
│   │           │   │   ├── psCharStrings.py
│   │           │   │   ├── psLib.py
│   │           │   │   ├── psOperators.py
│   │           │   │   ├── py23.py
│   │           │   │   ├── roundTools.py
│   │           │   │   ├── sstruct.py
│   │           │   │   ├── symfont.py
│   │           │   │   ├── testTools.py
│   │           │   │   ├── textTools.py
│   │           │   │   ├── timeTools.py
│   │           │   │   ├── transform.py
│   │           │   │   ├── treeTools.py
│   │           │   │   ├── vector.py
│   │           │   │   ├── visitor.py
│   │           │   │   ├── xmlReader.py
│   │           │   │   └── xmlWriter.py
│   │           │   ├── mtiLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   └── __pycache__/
│   │           │   │       ├── __init__.cpython-311.pyc
│   │           │   │       └── __main__.cpython-311.pyc
│   │           │   ├── otlLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── builder.cpython-311.pyc
│   │           │   │   │   ├── error.cpython-311.pyc
│   │           │   │   │   └── maxContextCalc.cpython-311.pyc
│   │           │   │   ├── builder.py
│   │           │   │   ├── error.py
│   │           │   │   ├── maxContextCalc.py
│   │           │   │   └── optimize/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __main__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── __main__.cpython-311.pyc
│   │           │   │       │   └── gpos.cpython-311.pyc
│   │           │   │       └── gpos.py
│   │           │   ├── pens/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── areaPen.cpython-311.pyc
│   │           │   │   │   ├── basePen.cpython-311.pyc
│   │           │   │   │   ├── boundsPen.cpython-311.pyc
│   │           │   │   │   ├── cairoPen.cpython-311.pyc
│   │           │   │   │   ├── cocoaPen.cpython-311.pyc
│   │           │   │   │   ├── cu2quPen.cpython-311.pyc
│   │           │   │   │   ├── explicitClosingLinePen.cpython-311.pyc
│   │           │   │   │   ├── filterPen.cpython-311.pyc
│   │           │   │   │   ├── freetypePen.cpython-311.pyc
│   │           │   │   │   ├── hashPointPen.cpython-311.pyc
│   │           │   │   │   ├── momentsPen.cpython-311.pyc
│   │           │   │   │   ├── perimeterPen.cpython-311.pyc
│   │           │   │   │   ├── pointInsidePen.cpython-311.pyc
│   │           │   │   │   ├── pointPen.cpython-311.pyc
│   │           │   │   │   ├── qtPen.cpython-311.pyc
│   │           │   │   │   ├── qu2cuPen.cpython-311.pyc
│   │           │   │   │   ├── quartzPen.cpython-311.pyc
│   │           │   │   │   ├── recordingPen.cpython-311.pyc
│   │           │   │   │   ├── reportLabPen.cpython-311.pyc
│   │           │   │   │   ├── reverseContourPen.cpython-311.pyc
│   │           │   │   │   ├── roundingPen.cpython-311.pyc
│   │           │   │   │   ├── statisticsPen.cpython-311.pyc
│   │           │   │   │   ├── svgPathPen.cpython-311.pyc
│   │           │   │   │   ├── t2CharStringPen.cpython-311.pyc
│   │           │   │   │   ├── teePen.cpython-311.pyc
│   │           │   │   │   ├── transformPen.cpython-311.pyc
│   │           │   │   │   ├── ttGlyphPen.cpython-311.pyc
│   │           │   │   │   └── wxPen.cpython-311.pyc
│   │           │   │   ├── areaPen.py
│   │           │   │   ├── basePen.py
│   │           │   │   ├── boundsPen.py
│   │           │   │   ├── cairoPen.py
│   │           │   │   ├── cocoaPen.py
│   │           │   │   ├── cu2quPen.py
│   │           │   │   ├── explicitClosingLinePen.py
│   │           │   │   ├── filterPen.py
│   │           │   │   ├── freetypePen.py
│   │           │   │   ├── hashPointPen.py
│   │           │   │   ├── momentsPen.py
│   │           │   │   ├── perimeterPen.py
│   │           │   │   ├── pointInsidePen.py
│   │           │   │   ├── pointPen.py
│   │           │   │   ├── qtPen.py
│   │           │   │   ├── qu2cuPen.py
│   │           │   │   ├── quartzPen.py
│   │           │   │   ├── recordingPen.py
│   │           │   │   ├── reportLabPen.py
│   │           │   │   ├── reverseContourPen.py
│   │           │   │   ├── roundingPen.py
│   │           │   │   ├── statisticsPen.py
│   │           │   │   ├── svgPathPen.py
│   │           │   │   ├── t2CharStringPen.py
│   │           │   │   ├── teePen.py
│   │           │   │   ├── transformPen.py
│   │           │   │   ├── ttGlyphPen.py
│   │           │   │   └── wxPen.py
│   │           │   ├── qu2cu/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── benchmark.cpython-311.pyc
│   │           │   │   │   ├── cli.cpython-311.pyc
│   │           │   │   │   └── qu2cu.cpython-311.pyc
│   │           │   │   ├── benchmark.py
│   │           │   │   ├── cli.py
│   │           │   │   └── qu2cu.py
│   │           │   ├── subset
│   │           │   ├── subset/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── cff.cpython-311.pyc
│   │           │   │   │   ├── svg.cpython-311.pyc
│   │           │   │   │   └── util.cpython-311.pyc
│   │           │   │   ├── cff.py
│   │           │   │   ├── svg.py
│   │           │   │   └── util.py
│   │           │   ├── svgLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   └── __init__.cpython-311.pyc
│   │           │   │   └── path/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── arc.cpython-311.pyc
│   │           │   │       │   ├── parser.cpython-311.pyc
│   │           │   │       │   └── shapes.cpython-311.pyc
│   │           │   │       ├── arc.py
│   │           │   │       ├── parser.py
│   │           │   │       └── shapes.py
│   │           │   ├── t1Lib/
│   │           │   │   ├── __init__.py
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── tfmLib.py
│   │           │   ├── ttLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── macUtils.cpython-311.pyc
│   │           │   │   │   ├── removeOverlaps.cpython-311.pyc
│   │           │   │   │   ├── reorderGlyphs.cpython-311.pyc
│   │           │   │   │   ├── scaleUpem.cpython-311.pyc
│   │           │   │   │   ├── sfnt.cpython-311.pyc
│   │           │   │   │   ├── standardGlyphOrder.cpython-311.pyc
│   │           │   │   │   ├── ttCollection.cpython-311.pyc
│   │           │   │   │   ├── ttFont.cpython-311.pyc
│   │           │   │   │   ├── ttGlyphSet.cpython-311.pyc
│   │           │   │   │   ├── ttVisitor.cpython-311.pyc
│   │           │   │   │   └── woff2.cpython-311.pyc
│   │           │   │   ├── macUtils.py
│   │           │   │   ├── removeOverlaps.py
│   │           │   │   ├── reorderGlyphs.py
│   │           │   │   ├── scaleUpem.py
│   │           │   │   ├── sfnt.py
│   │           │   │   ├── standardGlyphOrder.py
│   │           │   │   ├── tables/
│   │           │   │   │   ├── B_A_S_E_.py
│   │           │   │   │   ├── BitmapGlyphMetrics.py
│   │           │   │   │   ├── C_B_D_T_.py
│   │           │   │   │   ├── C_B_L_C_.py
│   │           │   │   │   ├── C_F_F_.py
│   │           │   │   │   ├── C_F_F__2.py
│   │           │   │   │   ├── C_O_L_R_.py
│   │           │   │   │   ├── C_P_A_L_.py
│   │           │   │   │   ├── D_S_I_G_.py
│   │           │   │   │   ├── D__e_b_g.py
│   │           │   │   │   ├── DefaultTable.py
│   │           │   │   │   ├── E_B_D_T_.py
│   │           │   │   │   ├── E_B_L_C_.py
│   │           │   │   │   ├── F_F_T_M_.py
│   │           │   │   │   ├── F__e_a_t.py
│   │           │   │   │   ├── G_D_E_F_.py
│   │           │   │   │   ├── G_M_A_P_.py
│   │           │   │   │   ├── G_P_K_G_.py
│   │           │   │   │   ├── G_P_O_S_.py
│   │           │   │   │   ├── G_S_U_B_.py
│   │           │   │   │   ├── G_V_A_R_.py
│   │           │   │   │   ├── G__l_a_t.py
│   │           │   │   │   ├── G__l_o_c.py
│   │           │   │   │   ├── H_V_A_R_.py
│   │           │   │   │   ├── J_S_T_F_.py
│   │           │   │   │   ├── L_T_S_H_.py
│   │           │   │   │   ├── M_A_T_H_.py
│   │           │   │   │   ├── M_E_T_A_.py
│   │           │   │   │   ├── M_V_A_R_.py
│   │           │   │   │   ├── O_S_2f_2.py
│   │           │   │   │   ├── S_I_N_G_.py
│   │           │   │   │   ├── S_T_A_T_.py
│   │           │   │   │   ├── S_V_G_.py
│   │           │   │   │   ├── S__i_l_f.py
│   │           │   │   │   ├── S__i_l_l.py
│   │           │   │   │   ├── T_S_I_B_.py
│   │           │   │   │   ├── T_S_I_C_.py
│   │           │   │   │   ├── T_S_I_D_.py
│   │           │   │   │   ├── T_S_I_J_.py
│   │           │   │   │   ├── T_S_I_P_.py
│   │           │   │   │   ├── T_S_I_S_.py
│   │           │   │   │   ├── T_S_I_V_.py
│   │           │   │   │   ├── T_S_I__0.py
│   │           │   │   │   ├── T_S_I__1.py
│   │           │   │   │   ├── T_S_I__2.py
│   │           │   │   │   ├── T_S_I__3.py
│   │           │   │   │   ├── T_S_I__5.py
│   │           │   │   │   ├── T_T_F_A_.py
│   │           │   │   │   ├── TupleVariation.py
│   │           │   │   │   ├── V_A_R_C_.py
│   │           │   │   │   ├── V_D_M_X_.py
│   │           │   │   │   ├── V_O_R_G_.py
│   │           │   │   │   ├── V_V_A_R_.py
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── B_A_S_E_.cpython-311.pyc
│   │           │   │   │   │   ├── BitmapGlyphMetrics.cpython-311.pyc
│   │           │   │   │   │   ├── C_B_D_T_.cpython-311.pyc
│   │           │   │   │   │   ├── C_B_L_C_.cpython-311.pyc
│   │           │   │   │   │   ├── C_F_F_.cpython-311.pyc
│   │           │   │   │   │   ├── C_F_F__2.cpython-311.pyc
│   │           │   │   │   │   ├── C_O_L_R_.cpython-311.pyc
│   │           │   │   │   │   ├── C_P_A_L_.cpython-311.pyc
│   │           │   │   │   │   ├── D_S_I_G_.cpython-311.pyc
│   │           │   │   │   │   ├── D__e_b_g.cpython-311.pyc
│   │           │   │   │   │   ├── DefaultTable.cpython-311.pyc
│   │           │   │   │   │   ├── E_B_D_T_.cpython-311.pyc
│   │           │   │   │   │   ├── E_B_L_C_.cpython-311.pyc
│   │           │   │   │   │   ├── F_F_T_M_.cpython-311.pyc
│   │           │   │   │   │   ├── F__e_a_t.cpython-311.pyc
│   │           │   │   │   │   ├── G_D_E_F_.cpython-311.pyc
│   │           │   │   │   │   ├── G_M_A_P_.cpython-311.pyc
│   │           │   │   │   │   ├── G_P_K_G_.cpython-311.pyc
│   │           │   │   │   │   ├── G_P_O_S_.cpython-311.pyc
│   │           │   │   │   │   ├── G_S_U_B_.cpython-311.pyc
│   │           │   │   │   │   ├── G_V_A_R_.cpython-311.pyc
│   │           │   │   │   │   ├── G__l_a_t.cpython-311.pyc
│   │           │   │   │   │   ├── G__l_o_c.cpython-311.pyc
│   │           │   │   │   │   ├── H_V_A_R_.cpython-311.pyc
│   │           │   │   │   │   ├── J_S_T_F_.cpython-311.pyc
│   │           │   │   │   │   ├── L_T_S_H_.cpython-311.pyc
│   │           │   │   │   │   ├── M_A_T_H_.cpython-311.pyc
│   │           │   │   │   │   ├── M_E_T_A_.cpython-311.pyc
│   │           │   │   │   │   ├── M_V_A_R_.cpython-311.pyc
│   │           │   │   │   │   ├── O_S_2f_2.cpython-311.pyc
│   │           │   │   │   │   ├── S_I_N_G_.cpython-311.pyc
│   │           │   │   │   │   ├── S_T_A_T_.cpython-311.pyc
│   │           │   │   │   │   ├── S_V_G_.cpython-311.pyc
│   │           │   │   │   │   ├── S__i_l_f.cpython-311.pyc
│   │           │   │   │   │   ├── S__i_l_l.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_B_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_C_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_D_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_J_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_P_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_S_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I_V_.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I__0.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I__1.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I__2.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I__3.cpython-311.pyc
│   │           │   │   │   │   ├── T_S_I__5.cpython-311.pyc
│   │           │   │   │   │   ├── T_T_F_A_.cpython-311.pyc
│   │           │   │   │   │   ├── TupleVariation.cpython-311.pyc
│   │           │   │   │   │   ├── V_A_R_C_.cpython-311.pyc
│   │           │   │   │   │   ├── V_D_M_X_.cpython-311.pyc
│   │           │   │   │   │   ├── V_O_R_G_.cpython-311.pyc
│   │           │   │   │   │   ├── V_V_A_R_.cpython-311.pyc
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _a_n_k_r.cpython-311.pyc
│   │           │   │   │   │   ├── _a_v_a_r.cpython-311.pyc
│   │           │   │   │   │   ├── _b_s_l_n.cpython-311.pyc
│   │           │   │   │   │   ├── _c_i_d_g.cpython-311.pyc
│   │           │   │   │   │   ├── _c_m_a_p.cpython-311.pyc
│   │           │   │   │   │   ├── _c_v_a_r.cpython-311.pyc
│   │           │   │   │   │   ├── _c_v_t.cpython-311.pyc
│   │           │   │   │   │   ├── _f_e_a_t.cpython-311.pyc
│   │           │   │   │   │   ├── _f_p_g_m.cpython-311.pyc
│   │           │   │   │   │   ├── _f_v_a_r.cpython-311.pyc
│   │           │   │   │   │   ├── _g_a_s_p.cpython-311.pyc
│   │           │   │   │   │   ├── _g_c_i_d.cpython-311.pyc
│   │           │   │   │   │   ├── _g_l_y_f.cpython-311.pyc
│   │           │   │   │   │   ├── _g_v_a_r.cpython-311.pyc
│   │           │   │   │   │   ├── _h_d_m_x.cpython-311.pyc
│   │           │   │   │   │   ├── _h_e_a_d.cpython-311.pyc
│   │           │   │   │   │   ├── _h_h_e_a.cpython-311.pyc
│   │           │   │   │   │   ├── _h_m_t_x.cpython-311.pyc
│   │           │   │   │   │   ├── _k_e_r_n.cpython-311.pyc
│   │           │   │   │   │   ├── _l_c_a_r.cpython-311.pyc
│   │           │   │   │   │   ├── _l_o_c_a.cpython-311.pyc
│   │           │   │   │   │   ├── _l_t_a_g.cpython-311.pyc
│   │           │   │   │   │   ├── _m_a_x_p.cpython-311.pyc
│   │           │   │   │   │   ├── _m_e_t_a.cpython-311.pyc
│   │           │   │   │   │   ├── _m_o_r_t.cpython-311.pyc
│   │           │   │   │   │   ├── _m_o_r_x.cpython-311.pyc
│   │           │   │   │   │   ├── _n_a_m_e.cpython-311.pyc
│   │           │   │   │   │   ├── _o_p_b_d.cpython-311.pyc
│   │           │   │   │   │   ├── _p_o_s_t.cpython-311.pyc
│   │           │   │   │   │   ├── _p_r_e_p.cpython-311.pyc
│   │           │   │   │   │   ├── _p_r_o_p.cpython-311.pyc
│   │           │   │   │   │   ├── _s_b_i_x.cpython-311.pyc
│   │           │   │   │   │   ├── _t_r_a_k.cpython-311.pyc
│   │           │   │   │   │   ├── _v_h_e_a.cpython-311.pyc
│   │           │   │   │   │   ├── _v_m_t_x.cpython-311.pyc
│   │           │   │   │   │   ├── asciiTable.cpython-311.pyc
│   │           │   │   │   │   ├── grUtils.cpython-311.pyc
│   │           │   │   │   │   ├── otBase.cpython-311.pyc
│   │           │   │   │   │   ├── otConverters.cpython-311.pyc
│   │           │   │   │   │   ├── otData.cpython-311.pyc
│   │           │   │   │   │   ├── otTables.cpython-311.pyc
│   │           │   │   │   │   ├── otTraverse.cpython-311.pyc
│   │           │   │   │   │   ├── sbixGlyph.cpython-311.pyc
│   │           │   │   │   │   ├── sbixStrike.cpython-311.pyc
│   │           │   │   │   │   └── ttProgram.cpython-311.pyc
│   │           │   │   │   ├── _a_n_k_r.py
│   │           │   │   │   ├── _a_v_a_r.py
│   │           │   │   │   ├── _b_s_l_n.py
│   │           │   │   │   ├── _c_i_d_g.py
│   │           │   │   │   ├── _c_m_a_p.py
│   │           │   │   │   ├── _c_v_a_r.py
│   │           │   │   │   ├── _c_v_t.py
│   │           │   │   │   ├── _f_e_a_t.py
│   │           │   │   │   ├── _f_p_g_m.py
│   │           │   │   │   ├── _f_v_a_r.py
│   │           │   │   │   ├── _g_a_s_p.py
│   │           │   │   │   ├── _g_c_i_d.py
│   │           │   │   │   ├── _g_l_y_f.py
│   │           │   │   │   ├── _g_v_a_r.py
│   │           │   │   │   ├── _h_d_m_x.py
│   │           │   │   │   ├── _h_e_a_d.py
│   │           │   │   │   ├── _h_h_e_a.py
│   │           │   │   │   ├── _h_m_t_x.py
│   │           │   │   │   ├── _k_e_r_n.py
│   │           │   │   │   ├── _l_c_a_r.py
│   │           │   │   │   ├── _l_o_c_a.py
│   │           │   │   │   ├── _l_t_a_g.py
│   │           │   │   │   ├── _m_a_x_p.py
│   │           │   │   │   ├── _m_e_t_a.py
│   │           │   │   │   ├── _m_o_r_t.py
│   │           │   │   │   ├── _m_o_r_x.py
│   │           │   │   │   ├── _n_a_m_e.py
│   │           │   │   │   ├── _o_p_b_d.py
│   │           │   │   │   ├── _p_o_s_t.py
│   │           │   │   │   ├── _p_r_e_p.py
│   │           │   │   │   ├── _p_r_o_p.py
│   │           │   │   │   ├── _s_b_i_x.py
│   │           │   │   │   ├── _t_r_a_k.py
│   │           │   │   │   ├── _v_h_e_a.py
│   │           │   │   │   ├── _v_m_t_x.py
│   │           │   │   │   ├── asciiTable.py
│   │           │   │   │   ├── grUtils.py
│   │           │   │   │   ├── otBase.py
│   │           │   │   │   ├── otConverters.py
│   │           │   │   │   ├── otData.py
│   │           │   │   │   ├── otTables.py
│   │           │   │   │   ├── otTraverse.py
│   │           │   │   │   ├── sbixGlyph.py
│   │           │   │   │   ├── sbixStrike.py
│   │           │   │   │   ├── table_API_readme.txt
│   │           │   │   │   └── ttProgram.py
│   │           │   │   ├── ttCollection.py
│   │           │   │   ├── ttFont.py
│   │           │   │   ├── ttGlyphSet.py
│   │           │   │   ├── ttVisitor.py
│   │           │   │   └── woff2.py
│   │           │   ├── ttx.py
│   │           │   ├── ufoLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── converters.cpython-311.pyc
│   │           │   │   │   ├── errors.cpython-311.pyc
│   │           │   │   │   ├── etree.cpython-311.pyc
│   │           │   │   │   ├── filenames.cpython-311.pyc
│   │           │   │   │   ├── glifLib.cpython-311.pyc
│   │           │   │   │   ├── kerning.cpython-311.pyc
│   │           │   │   │   ├── plistlib.cpython-311.pyc
│   │           │   │   │   ├── pointPen.cpython-311.pyc
│   │           │   │   │   ├── utils.cpython-311.pyc
│   │           │   │   │   └── validators.cpython-311.pyc
│   │           │   │   ├── converters.py
│   │           │   │   ├── errors.py
│   │           │   │   ├── etree.py
│   │           │   │   ├── filenames.py
│   │           │   │   ├── glifLib.py
│   │           │   │   ├── kerning.py
│   │           │   │   ├── plistlib.py
│   │           │   │   ├── pointPen.py
│   │           │   │   ├── utils.py
│   │           │   │   └── validators.py
│   │           │   ├── unicode.py
│   │           │   ├── unicodedata/
│   │           │   │   ├── Blocks.py
│   │           │   │   ├── Mirrored.py
│   │           │   │   ├── OTTags.py
│   │           │   │   ├── ScriptExtensions.py
│   │           │   │   ├── Scripts.py
│   │           │   │   ├── __init__.py
│   │           │   │   └── __pycache__/
│   │           │   │       ├── Blocks.cpython-311.pyc
│   │           │   │       ├── Mirrored.cpython-311.pyc
│   │           │   │       ├── OTTags.cpython-311.pyc
│   │           │   │       ├── ScriptExtensions.cpython-311.pyc
│   │           │   │       ├── Scripts.cpython-311.pyc
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── varLib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── avarPlanner.cpython-311.pyc
│   │           │   │   │   ├── builder.cpython-311.pyc
│   │           │   │   │   ├── cff.cpython-311.pyc
│   │           │   │   │   ├── errors.cpython-311.pyc
│   │           │   │   │   ├── featureVars.cpython-311.pyc
│   │           │   │   │   ├── hvar.cpython-311.pyc
│   │           │   │   │   ├── interpolatable.cpython-311.pyc
│   │           │   │   │   ├── interpolatableHelpers.cpython-311.pyc
│   │           │   │   │   ├── interpolatablePlot.cpython-311.pyc
│   │           │   │   │   ├── interpolatableTestContourOrder.cpython-311.pyc
│   │           │   │   │   ├── interpolatableTestStartingPoint.cpython-311.pyc
│   │           │   │   │   ├── interpolate_layout.cpython-311.pyc
│   │           │   │   │   ├── iup.cpython-311.pyc
│   │           │   │   │   ├── merger.cpython-311.pyc
│   │           │   │   │   ├── models.cpython-311.pyc
│   │           │   │   │   ├── multiVarStore.cpython-311.pyc
│   │           │   │   │   ├── mutator.cpython-311.pyc
│   │           │   │   │   ├── mvar.cpython-311.pyc
│   │           │   │   │   ├── plot.cpython-311.pyc
│   │           │   │   │   ├── stat.cpython-311.pyc
│   │           │   │   │   └── varStore.cpython-311.pyc
│   │           │   │   ├── avar/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   ├── build.cpython-311.pyc
│   │           │   │   │   │   ├── map.cpython-311.pyc
│   │           │   │   │   │   ├── plan.cpython-311.pyc
│   │           │   │   │   │   └── unbuild.cpython-311.pyc
│   │           │   │   │   ├── build.py
│   │           │   │   │   ├── map.py
│   │           │   │   │   ├── plan.py
│   │           │   │   │   └── unbuild.py
│   │           │   │   ├── avarPlanner.py
│   │           │   │   ├── builder.py
│   │           │   │   ├── cff.py
│   │           │   │   ├── errors.py
│   │           │   │   ├── featureVars.py
│   │           │   │   ├── hvar.py
│   │           │   │   ├── instancer/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   ├── featureVars.cpython-311.pyc
│   │           │   │   │   │   ├── names.cpython-311.pyc
│   │           │   │   │   │   └── solver.cpython-311.pyc
│   │           │   │   │   ├── featureVars.py
│   │           │   │   │   ├── names.py
│   │           │   │   │   └── solver.py
│   │           │   │   ├── interpolatable.py
│   │           │   │   ├── interpolatableHelpers.py
│   │           │   │   ├── interpolatablePlot.py
│   │           │   │   ├── interpolatableTestContourOrder.py
│   │           │   │   ├── interpolatableTestStartingPoint.py
│   │           │   │   ├── interpolate_layout.py
│   │           │   │   ├── iup.py
│   │           │   │   ├── merger.py
│   │           │   │   ├── models.py
│   │           │   │   ├── multiVarStore.py
│   │           │   │   ├── mutator.py
│   │           │   │   ├── mvar.py
│   │           │   │   ├── plot.py
│   │           │   │   ├── stat.py
│   │           │   │   └── varStore.py
│   │           │   └── voltLib/
│   │           │       ├── __init__.py
│   │           │       ├── __main__.py
│   │           │       ├── __pycache__/
│   │           │       │   ├── __init__.cpython-311.pyc
│   │           │       │   ├── __main__.cpython-311.pyc
│   │           │       │   ├── ast.cpython-311.pyc
│   │           │       │   ├── error.cpython-311.pyc
│   │           │       │   ├── lexer.cpython-311.pyc
│   │           │       │   ├── parser.cpython-311.pyc
│   │           │       │   └── voltToFea.cpython-311.pyc
│   │           │       ├── ast.py
│   │           │       ├── error.py
│   │           │       ├── lexer.py
│   │           │       ├── parser.py
│   │           │       └── voltToFea.py
│   │           ├── fonttools-4.60.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   ├── entry_points.txt
│   │           │   ├── licenses/
│   │           │   │   ├── LICENSE
│   │           │   │   └── LICENSE.external
│   │           │   └── top_level.txt
│   │           ├── gpiozero-2.0.1.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.rst
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   ├── entry_points.txt
│   │           │   └── top_level.txt
│   │           ├── gpiozero/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── boards.cpython-311.pyc
│   │           │   │   ├── compat.cpython-311.pyc
│   │           │   │   ├── devices.cpython-311.pyc
│   │           │   │   ├── exc.cpython-311.pyc
│   │           │   │   ├── input_devices.cpython-311.pyc
│   │           │   │   ├── internal_devices.cpython-311.pyc
│   │           │   │   ├── mixins.cpython-311.pyc
│   │           │   │   ├── output_devices.cpython-311.pyc
│   │           │   │   ├── spi_devices.cpython-311.pyc
│   │           │   │   ├── threads.cpython-311.pyc
│   │           │   │   ├── tones.cpython-311.pyc
│   │           │   │   └── tools.cpython-311.pyc
│   │           │   ├── boards.py
│   │           │   ├── compat.py
│   │           │   ├── devices.py
│   │           │   ├── exc.py
│   │           │   ├── fonts/
│   │           │   │   ├── 14seg.txt
│   │           │   │   ├── 7seg.txt
│   │           │   │   ├── __init__.py
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── input_devices.py
│   │           │   ├── internal_devices.py
│   │           │   ├── mixins.py
│   │           │   ├── output_devices.py
│   │           │   ├── pins/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── data.cpython-311.pyc
│   │           │   │   │   ├── lgpio.cpython-311.pyc
│   │           │   │   │   ├── local.cpython-311.pyc
│   │           │   │   │   ├── mock.cpython-311.pyc
│   │           │   │   │   ├── native.cpython-311.pyc
│   │           │   │   │   ├── pi.cpython-311.pyc
│   │           │   │   │   ├── pigpio.cpython-311.pyc
│   │           │   │   │   ├── rpigpio.cpython-311.pyc
│   │           │   │   │   ├── spi.cpython-311.pyc
│   │           │   │   │   └── style.cpython-311.pyc
│   │           │   │   ├── data.py
│   │           │   │   ├── lgpio.py
│   │           │   │   ├── local.py
│   │           │   │   ├── mock.py
│   │           │   │   ├── native.py
│   │           │   │   ├── pi.py
│   │           │   │   ├── pigpio.py
│   │           │   │   ├── rpigpio.py
│   │           │   │   ├── spi.py
│   │           │   │   └── style.py
│   │           │   ├── spi_devices.py
│   │           │   ├── threads.py
│   │           │   ├── tones.py
│   │           │   └── tools.py
│   │           ├── gpiozerocli/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── pinout.cpython-311.pyc
│   │           │   │   └── pintest.cpython-311.pyc
│   │           │   ├── pinout.py
│   │           │   └── pintest.py
│   │           ├── itsdangerous-2.2.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.txt
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   └── WHEEL
│   │           ├── itsdangerous/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _json.cpython-311.pyc
│   │           │   │   ├── encoding.cpython-311.pyc
│   │           │   │   ├── exc.cpython-311.pyc
│   │           │   │   ├── serializer.cpython-311.pyc
│   │           │   │   ├── signer.cpython-311.pyc
│   │           │   │   ├── timed.cpython-311.pyc
│   │           │   │   └── url_safe.cpython-311.pyc
│   │           │   ├── _json.py
│   │           │   ├── encoding.py
│   │           │   ├── exc.py
│   │           │   ├── py.typed
│   │           │   ├── serializer.py
│   │           │   ├── signer.py
│   │           │   ├── timed.py
│   │           │   └── url_safe.py
│   │           ├── jinja2-3.1.6.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   ├── entry_points.txt
│   │           │   └── licenses/
│   │           │       └── LICENSE.txt
│   │           ├── jinja2/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _identifier.cpython-311.pyc
│   │           │   │   ├── async_utils.cpython-311.pyc
│   │           │   │   ├── bccache.cpython-311.pyc
│   │           │   │   ├── compiler.cpython-311.pyc
│   │           │   │   ├── constants.cpython-311.pyc
│   │           │   │   ├── debug.cpython-311.pyc
│   │           │   │   ├── defaults.cpython-311.pyc
│   │           │   │   ├── environment.cpython-311.pyc
│   │           │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   ├── ext.cpython-311.pyc
│   │           │   │   ├── filters.cpython-311.pyc
│   │           │   │   ├── idtracking.cpython-311.pyc
│   │           │   │   ├── lexer.cpython-311.pyc
│   │           │   │   ├── loaders.cpython-311.pyc
│   │           │   │   ├── meta.cpython-311.pyc
│   │           │   │   ├── nativetypes.cpython-311.pyc
│   │           │   │   ├── nodes.cpython-311.pyc
│   │           │   │   ├── optimizer.cpython-311.pyc
│   │           │   │   ├── parser.cpython-311.pyc
│   │           │   │   ├── runtime.cpython-311.pyc
│   │           │   │   ├── sandbox.cpython-311.pyc
│   │           │   │   ├── tests.cpython-311.pyc
│   │           │   │   ├── utils.cpython-311.pyc
│   │           │   │   └── visitor.cpython-311.pyc
│   │           │   ├── _identifier.py
│   │           │   ├── async_utils.py
│   │           │   ├── bccache.py
│   │           │   ├── compiler.py
│   │           │   ├── constants.py
│   │           │   ├── debug.py
│   │           │   ├── defaults.py
│   │           │   ├── environment.py
│   │           │   ├── exceptions.py
│   │           │   ├── ext.py
│   │           │   ├── filters.py
│   │           │   ├── idtracking.py
│   │           │   ├── lexer.py
│   │           │   ├── loaders.py
│   │           │   ├── meta.py
│   │           │   ├── nativetypes.py
│   │           │   ├── nodes.py
│   │           │   ├── optimizer.py
│   │           │   ├── parser.py
│   │           │   ├── py.typed
│   │           │   ├── runtime.py
│   │           │   ├── sandbox.py
│   │           │   ├── tests.py
│   │           │   ├── utils.py
│   │           │   └── visitor.py
│   │           ├── kiwisolver-1.4.9.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   ├── licenses/
│   │           │   │   └── LICENSE
│   │           │   └── top_level.txt
│   │           ├── kiwisolver/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   └── exceptions.cpython-311.pyc
│   │           │   ├── _cext.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _cext.pyi
│   │           │   ├── exceptions.py
│   │           │   └── py.typed
│   │           ├── lgpio-0.2.2.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   └── top_level.txt
│   │           ├── lgpio.py
│   │           ├── markupsafe-3.0.3.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   ├── licenses/
│   │           │   │   └── LICENSE.txt
│   │           │   └── top_level.txt
│   │           ├── markupsafe/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   └── _native.cpython-311.pyc
│   │           │   ├── _native.py
│   │           │   ├── _speedups.c
│   │           │   ├── _speedups.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _speedups.pyi
│   │           │   └── py.typed
│   │           ├── matplotlib-3.10.6.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   └── WHEEL
│   │           ├── matplotlib/
│   │           │   ├── __init__.py
│   │           │   ├── __init__.pyi
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _afm.cpython-311.pyc
│   │           │   │   ├── _animation_data.cpython-311.pyc
│   │           │   │   ├── _blocking_input.cpython-311.pyc
│   │           │   │   ├── _cm.cpython-311.pyc
│   │           │   │   ├── _cm_bivar.cpython-311.pyc
│   │           │   │   ├── _cm_listed.cpython-311.pyc
│   │           │   │   ├── _cm_multivar.cpython-311.pyc
│   │           │   │   ├── _color_data.cpython-311.pyc
│   │           │   │   ├── _constrained_layout.cpython-311.pyc
│   │           │   │   ├── _docstring.cpython-311.pyc
│   │           │   │   ├── _enums.cpython-311.pyc
│   │           │   │   ├── _fontconfig_pattern.cpython-311.pyc
│   │           │   │   ├── _internal_utils.cpython-311.pyc
│   │           │   │   ├── _layoutgrid.cpython-311.pyc
│   │           │   │   ├── _mathtext.cpython-311.pyc
│   │           │   │   ├── _mathtext_data.cpython-311.pyc
│   │           │   │   ├── _pylab_helpers.cpython-311.pyc
│   │           │   │   ├── _text_helpers.cpython-311.pyc
│   │           │   │   ├── _tight_bbox.cpython-311.pyc
│   │           │   │   ├── _tight_layout.cpython-311.pyc
│   │           │   │   ├── _type1font.cpython-311.pyc
│   │           │   │   ├── _version.cpython-311.pyc
│   │           │   │   ├── animation.cpython-311.pyc
│   │           │   │   ├── artist.cpython-311.pyc
│   │           │   │   ├── axis.cpython-311.pyc
│   │           │   │   ├── backend_bases.cpython-311.pyc
│   │           │   │   ├── backend_managers.cpython-311.pyc
│   │           │   │   ├── backend_tools.cpython-311.pyc
│   │           │   │   ├── bezier.cpython-311.pyc
│   │           │   │   ├── category.cpython-311.pyc
│   │           │   │   ├── cbook.cpython-311.pyc
│   │           │   │   ├── cm.cpython-311.pyc
│   │           │   │   ├── collections.cpython-311.pyc
│   │           │   │   ├── colorbar.cpython-311.pyc
│   │           │   │   ├── colorizer.cpython-311.pyc
│   │           │   │   ├── colors.cpython-311.pyc
│   │           │   │   ├── container.cpython-311.pyc
│   │           │   │   ├── contour.cpython-311.pyc
│   │           │   │   ├── dates.cpython-311.pyc
│   │           │   │   ├── dviread.cpython-311.pyc
│   │           │   │   ├── figure.cpython-311.pyc
│   │           │   │   ├── font_manager.cpython-311.pyc
│   │           │   │   ├── gridspec.cpython-311.pyc
│   │           │   │   ├── hatch.cpython-311.pyc
│   │           │   │   ├── image.cpython-311.pyc
│   │           │   │   ├── inset.cpython-311.pyc
│   │           │   │   ├── layout_engine.cpython-311.pyc
│   │           │   │   ├── legend.cpython-311.pyc
│   │           │   │   ├── legend_handler.cpython-311.pyc
│   │           │   │   ├── lines.cpython-311.pyc
│   │           │   │   ├── markers.cpython-311.pyc
│   │           │   │   ├── mathtext.cpython-311.pyc
│   │           │   │   ├── mlab.cpython-311.pyc
│   │           │   │   ├── offsetbox.cpython-311.pyc
│   │           │   │   ├── patches.cpython-311.pyc
│   │           │   │   ├── path.cpython-311.pyc
│   │           │   │   ├── patheffects.cpython-311.pyc
│   │           │   │   ├── pylab.cpython-311.pyc
│   │           │   │   ├── pyplot.cpython-311.pyc
│   │           │   │   ├── quiver.cpython-311.pyc
│   │           │   │   ├── rcsetup.cpython-311.pyc
│   │           │   │   ├── sankey.cpython-311.pyc
│   │           │   │   ├── scale.cpython-311.pyc
│   │           │   │   ├── spines.cpython-311.pyc
│   │           │   │   ├── stackplot.cpython-311.pyc
│   │           │   │   ├── streamplot.cpython-311.pyc
│   │           │   │   ├── table.cpython-311.pyc
│   │           │   │   ├── texmanager.cpython-311.pyc
│   │           │   │   ├── text.cpython-311.pyc
│   │           │   │   ├── textpath.cpython-311.pyc
│   │           │   │   ├── ticker.cpython-311.pyc
│   │           │   │   ├── transforms.cpython-311.pyc
│   │           │   │   ├── typing.cpython-311.pyc
│   │           │   │   ├── units.cpython-311.pyc
│   │           │   │   └── widgets.cpython-311.pyc
│   │           │   ├── _afm.py
│   │           │   ├── _animation_data.py
│   │           │   ├── _api/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── deprecation.cpython-311.pyc
│   │           │   │   ├── deprecation.py
│   │           │   │   └── deprecation.pyi
│   │           │   ├── _blocking_input.py
│   │           │   ├── _c_internal_utils.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _c_internal_utils.pyi
│   │           │   ├── _cm.py
│   │           │   ├── _cm_bivar.py
│   │           │   ├── _cm_listed.py
│   │           │   ├── _cm_multivar.py
│   │           │   ├── _color_data.py
│   │           │   ├── _color_data.pyi
│   │           │   ├── _constrained_layout.py
│   │           │   ├── _docstring.py
│   │           │   ├── _docstring.pyi
│   │           │   ├── _enums.py
│   │           │   ├── _enums.pyi
│   │           │   ├── _fontconfig_pattern.py
│   │           │   ├── _image.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _image.pyi
│   │           │   ├── _internal_utils.py
│   │           │   ├── _layoutgrid.py
│   │           │   ├── _mathtext.py
│   │           │   ├── _mathtext_data.py
│   │           │   ├── _path.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _path.pyi
│   │           │   ├── _pylab_helpers.py
│   │           │   ├── _pylab_helpers.pyi
│   │           │   ├── _qhull.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _qhull.pyi
│   │           │   ├── _text_helpers.py
│   │           │   ├── _tight_bbox.py
│   │           │   ├── _tight_layout.py
│   │           │   ├── _tri.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── _tri.pyi
│   │           │   ├── _type1font.py
│   │           │   ├── _version.py
│   │           │   ├── animation.py
│   │           │   ├── animation.pyi
│   │           │   ├── artist.py
│   │           │   ├── artist.pyi
│   │           │   ├── axes/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _axes.cpython-311.pyc
│   │           │   │   │   ├── _base.cpython-311.pyc
│   │           │   │   │   └── _secondary_axes.cpython-311.pyc
│   │           │   │   ├── _axes.py
│   │           │   │   ├── _axes.pyi
│   │           │   │   ├── _base.py
│   │           │   │   ├── _base.pyi
│   │           │   │   ├── _secondary_axes.py
│   │           │   │   └── _secondary_axes.pyi
│   │           │   ├── axis.py
│   │           │   ├── axis.pyi
│   │           │   ├── backend_bases.py
│   │           │   ├── backend_bases.pyi
│   │           │   ├── backend_managers.py
│   │           │   ├── backend_managers.pyi
│   │           │   ├── backend_tools.py
│   │           │   ├── backend_tools.pyi
│   │           │   ├── backends/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _backend_gtk.cpython-311.pyc
│   │           │   │   │   ├── _backend_pdf_ps.cpython-311.pyc
│   │           │   │   │   ├── _backend_tk.cpython-311.pyc
│   │           │   │   │   ├── backend_agg.cpython-311.pyc
│   │           │   │   │   ├── backend_cairo.cpython-311.pyc
│   │           │   │   │   ├── backend_gtk3.cpython-311.pyc
│   │           │   │   │   ├── backend_gtk3agg.cpython-311.pyc
│   │           │   │   │   ├── backend_gtk3cairo.cpython-311.pyc
│   │           │   │   │   ├── backend_gtk4.cpython-311.pyc
│   │           │   │   │   ├── backend_gtk4agg.cpython-311.pyc
│   │           │   │   │   ├── backend_gtk4cairo.cpython-311.pyc
│   │           │   │   │   ├── backend_macosx.cpython-311.pyc
│   │           │   │   │   ├── backend_mixed.cpython-311.pyc
│   │           │   │   │   ├── backend_nbagg.cpython-311.pyc
│   │           │   │   │   ├── backend_pdf.cpython-311.pyc
│   │           │   │   │   ├── backend_pgf.cpython-311.pyc
│   │           │   │   │   ├── backend_ps.cpython-311.pyc
│   │           │   │   │   ├── backend_qt.cpython-311.pyc
│   │           │   │   │   ├── backend_qt5.cpython-311.pyc
│   │           │   │   │   ├── backend_qt5agg.cpython-311.pyc
│   │           │   │   │   ├── backend_qt5cairo.cpython-311.pyc
│   │           │   │   │   ├── backend_qtagg.cpython-311.pyc
│   │           │   │   │   ├── backend_qtcairo.cpython-311.pyc
│   │           │   │   │   ├── backend_svg.cpython-311.pyc
│   │           │   │   │   ├── backend_template.cpython-311.pyc
│   │           │   │   │   ├── backend_tkagg.cpython-311.pyc
│   │           │   │   │   ├── backend_tkcairo.cpython-311.pyc
│   │           │   │   │   ├── backend_webagg.cpython-311.pyc
│   │           │   │   │   ├── backend_webagg_core.cpython-311.pyc
│   │           │   │   │   ├── backend_wx.cpython-311.pyc
│   │           │   │   │   ├── backend_wxagg.cpython-311.pyc
│   │           │   │   │   ├── backend_wxcairo.cpython-311.pyc
│   │           │   │   │   ├── qt_compat.cpython-311.pyc
│   │           │   │   │   └── registry.cpython-311.pyc
│   │           │   │   ├── _backend_agg.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _backend_agg.pyi
│   │           │   │   ├── _backend_gtk.py
│   │           │   │   ├── _backend_pdf_ps.py
│   │           │   │   ├── _backend_tk.py
│   │           │   │   ├── _macosx.pyi
│   │           │   │   ├── _tkagg.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _tkagg.pyi
│   │           │   │   ├── backend_agg.py
│   │           │   │   ├── backend_cairo.py
│   │           │   │   ├── backend_gtk3.py
│   │           │   │   ├── backend_gtk3agg.py
│   │           │   │   ├── backend_gtk3cairo.py
│   │           │   │   ├── backend_gtk4.py
│   │           │   │   ├── backend_gtk4agg.py
│   │           │   │   ├── backend_gtk4cairo.py
│   │           │   │   ├── backend_macosx.py
│   │           │   │   ├── backend_mixed.py
│   │           │   │   ├── backend_nbagg.py
│   │           │   │   ├── backend_pdf.py
│   │           │   │   ├── backend_pgf.py
│   │           │   │   ├── backend_ps.py
│   │           │   │   ├── backend_qt.py
│   │           │   │   ├── backend_qt5.py
│   │           │   │   ├── backend_qt5agg.py
│   │           │   │   ├── backend_qt5cairo.py
│   │           │   │   ├── backend_qtagg.py
│   │           │   │   ├── backend_qtcairo.py
│   │           │   │   ├── backend_svg.py
│   │           │   │   ├── backend_template.py
│   │           │   │   ├── backend_tkagg.py
│   │           │   │   ├── backend_tkcairo.py
│   │           │   │   ├── backend_webagg.py
│   │           │   │   ├── backend_webagg_core.py
│   │           │   │   ├── backend_wx.py
│   │           │   │   ├── backend_wxagg.py
│   │           │   │   ├── backend_wxcairo.py
│   │           │   │   ├── qt_compat.py
│   │           │   │   ├── qt_editor/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _formlayout.cpython-311.pyc
│   │           │   │   │   │   └── figureoptions.cpython-311.pyc
│   │           │   │   │   ├── _formlayout.py
│   │           │   │   │   └── figureoptions.py
│   │           │   │   ├── registry.py
│   │           │   │   └── web_backend/
│   │           │   │       ├── all_figures.html
│   │           │   │       ├── css/
│   │           │   │       │   ├── boilerplate.css
│   │           │   │       │   ├── fbm.css
│   │           │   │       │   ├── mpl.css
│   │           │   │       │   └── page.css
│   │           │   │       ├── ipython_inline_figure.html
│   │           │   │       ├── js/
│   │           │   │       │   ├── mpl.js
│   │           │   │       │   ├── mpl_tornado.js
│   │           │   │       │   └── nbagg_mpl.js
│   │           │   │       └── single_figure.html
│   │           │   ├── bezier.py
│   │           │   ├── bezier.pyi
│   │           │   ├── category.py
│   │           │   ├── cbook.py
│   │           │   ├── cbook.pyi
│   │           │   ├── cm.py
│   │           │   ├── cm.pyi
│   │           │   ├── collections.py
│   │           │   ├── collections.pyi
│   │           │   ├── colorbar.py
│   │           │   ├── colorbar.pyi
│   │           │   ├── colorizer.py
│   │           │   ├── colorizer.pyi
│   │           │   ├── colors.py
│   │           │   ├── colors.pyi
│   │           │   ├── container.py
│   │           │   ├── container.pyi
│   │           │   ├── contour.py
│   │           │   ├── contour.pyi
│   │           │   ├── dates.py
│   │           │   ├── dviread.py
│   │           │   ├── dviread.pyi
│   │           │   ├── figure.py
│   │           │   ├── figure.pyi
│   │           │   ├── font_manager.py
│   │           │   ├── font_manager.pyi
│   │           │   ├── ft2font.cpython-311-arm-linux-gnueabihf.so
│   │           │   ├── ft2font.pyi
│   │           │   ├── gridspec.py
│   │           │   ├── gridspec.pyi
│   │           │   ├── hatch.py
│   │           │   ├── hatch.pyi
│   │           │   ├── image.py
│   │           │   ├── image.pyi
│   │           │   ├── inset.py
│   │           │   ├── inset.pyi
│   │           │   ├── layout_engine.py
│   │           │   ├── layout_engine.pyi
│   │           │   ├── legend.py
│   │           │   ├── legend.pyi
│   │           │   ├── legend_handler.py
│   │           │   ├── legend_handler.pyi
│   │           │   ├── lines.py
│   │           │   ├── lines.pyi
│   │           │   ├── markers.py
│   │           │   ├── markers.pyi
│   │           │   ├── mathtext.py
│   │           │   ├── mathtext.pyi
│   │           │   ├── mlab.py
│   │           │   ├── mlab.pyi
│   │           │   ├── mpl-data/
│   │           │   │   ├── fonts/
│   │           │   │   │   ├── afm/
│   │           │   │   │   │   ├── cmex10.afm
│   │           │   │   │   │   ├── cmmi10.afm
│   │           │   │   │   │   ├── cmr10.afm
│   │           │   │   │   │   ├── cmsy10.afm
│   │           │   │   │   │   ├── cmtt10.afm
│   │           │   │   │   │   ├── pagd8a.afm
│   │           │   │   │   │   ├── pagdo8a.afm
│   │           │   │   │   │   ├── pagk8a.afm
│   │           │   │   │   │   ├── pagko8a.afm
│   │           │   │   │   │   ├── pbkd8a.afm
│   │           │   │   │   │   ├── pbkdi8a.afm
│   │           │   │   │   │   ├── pbkl8a.afm
│   │           │   │   │   │   ├── pbkli8a.afm
│   │           │   │   │   │   ├── pcrb8a.afm
│   │           │   │   │   │   ├── pcrbo8a.afm
│   │           │   │   │   │   ├── pcrr8a.afm
│   │           │   │   │   │   ├── pcrro8a.afm
│   │           │   │   │   │   ├── phvb8a.afm
│   │           │   │   │   │   ├── phvb8an.afm
│   │           │   │   │   │   ├── phvbo8a.afm
│   │           │   │   │   │   ├── phvbo8an.afm
│   │           │   │   │   │   ├── phvl8a.afm
│   │           │   │   │   │   ├── phvlo8a.afm
│   │           │   │   │   │   ├── phvr8a.afm
│   │           │   │   │   │   ├── phvr8an.afm
│   │           │   │   │   │   ├── phvro8a.afm
│   │           │   │   │   │   ├── phvro8an.afm
│   │           │   │   │   │   ├── pncb8a.afm
│   │           │   │   │   │   ├── pncbi8a.afm
│   │           │   │   │   │   ├── pncr8a.afm
│   │           │   │   │   │   ├── pncri8a.afm
│   │           │   │   │   │   ├── pplb8a.afm
│   │           │   │   │   │   ├── pplbi8a.afm
│   │           │   │   │   │   ├── pplr8a.afm
│   │           │   │   │   │   ├── pplri8a.afm
│   │           │   │   │   │   ├── psyr.afm
│   │           │   │   │   │   ├── ptmb8a.afm
│   │           │   │   │   │   ├── ptmbi8a.afm
│   │           │   │   │   │   ├── ptmr8a.afm
│   │           │   │   │   │   ├── ptmri8a.afm
│   │           │   │   │   │   ├── putb8a.afm
│   │           │   │   │   │   ├── putbi8a.afm
│   │           │   │   │   │   ├── putr8a.afm
│   │           │   │   │   │   ├── putri8a.afm
│   │           │   │   │   │   ├── pzcmi8a.afm
│   │           │   │   │   │   └── pzdr.afm
│   │           │   │   │   ├── pdfcorefonts/
│   │           │   │   │   │   ├── Courier-Bold.afm
│   │           │   │   │   │   ├── Courier-BoldOblique.afm
│   │           │   │   │   │   ├── Courier-Oblique.afm
│   │           │   │   │   │   ├── Courier.afm
│   │           │   │   │   │   ├── Helvetica-Bold.afm
│   │           │   │   │   │   ├── Helvetica-BoldOblique.afm
│   │           │   │   │   │   ├── Helvetica-Oblique.afm
│   │           │   │   │   │   ├── Helvetica.afm
│   │           │   │   │   │   ├── Symbol.afm
│   │           │   │   │   │   ├── Times-Bold.afm
│   │           │   │   │   │   ├── Times-BoldItalic.afm
│   │           │   │   │   │   ├── Times-Italic.afm
│   │           │   │   │   │   ├── Times-Roman.afm
│   │           │   │   │   │   ├── ZapfDingbats.afm
│   │           │   │   │   │   └── readme.txt
│   │           │   │   │   └── ttf/
│   │           │   │   │       ├── DejaVuSans-Bold.ttf
│   │           │   │   │       ├── DejaVuSans-BoldOblique.ttf
│   │           │   │   │       ├── DejaVuSans-Oblique.ttf
│   │           │   │   │       ├── DejaVuSans.ttf
│   │           │   │   │       ├── DejaVuSansDisplay.ttf
│   │           │   │   │       ├── DejaVuSansMono-Bold.ttf
│   │           │   │   │       ├── DejaVuSansMono-BoldOblique.ttf
│   │           │   │   │       ├── DejaVuSansMono-Oblique.ttf
│   │           │   │   │       ├── DejaVuSansMono.ttf
│   │           │   │   │       ├── DejaVuSerif-Bold.ttf
│   │           │   │   │       ├── DejaVuSerif-BoldItalic.ttf
│   │           │   │   │       ├── DejaVuSerif-Italic.ttf
│   │           │   │   │       ├── DejaVuSerif.ttf
│   │           │   │   │       ├── DejaVuSerifDisplay.ttf
│   │           │   │   │       ├── LICENSE_DEJAVU
│   │           │   │   │       ├── LICENSE_STIX
│   │           │   │   │       ├── STIXGeneral.ttf
│   │           │   │   │       ├── STIXGeneralBol.ttf
│   │           │   │   │       ├── STIXGeneralBolIta.ttf
│   │           │   │   │       ├── STIXGeneralItalic.ttf
│   │           │   │   │       ├── STIXNonUni.ttf
│   │           │   │   │       ├── STIXNonUniBol.ttf
│   │           │   │   │       ├── STIXNonUniBolIta.ttf
│   │           │   │   │       ├── STIXNonUniIta.ttf
│   │           │   │   │       ├── STIXSizFiveSymReg.ttf
│   │           │   │   │       ├── STIXSizFourSymBol.ttf
│   │           │   │   │       ├── STIXSizFourSymReg.ttf
│   │           │   │   │       ├── STIXSizOneSymBol.ttf
│   │           │   │   │       ├── STIXSizOneSymReg.ttf
│   │           │   │   │       ├── STIXSizThreeSymBol.ttf
│   │           │   │   │       ├── STIXSizThreeSymReg.ttf
│   │           │   │   │       ├── STIXSizTwoSymBol.ttf
│   │           │   │   │       ├── STIXSizTwoSymReg.ttf
│   │           │   │   │       ├── cmb10.ttf
│   │           │   │   │       ├── cmex10.ttf
│   │           │   │   │       ├── cmmi10.ttf
│   │           │   │   │       ├── cmr10.ttf
│   │           │   │   │       ├── cmss10.ttf
│   │           │   │   │       ├── cmsy10.ttf
│   │           │   │   │       └── cmtt10.ttf
│   │           │   │   ├── images/
│   │           │   │   │   ├── back-symbolic.svg
│   │           │   │   │   ├── back.pdf
│   │           │   │   │   ├── back.png
│   │           │   │   │   ├── back.svg
│   │           │   │   │   ├── back_large.png
│   │           │   │   │   ├── filesave-symbolic.svg
│   │           │   │   │   ├── filesave.pdf
│   │           │   │   │   ├── filesave.png
│   │           │   │   │   ├── filesave.svg
│   │           │   │   │   ├── filesave_large.png
│   │           │   │   │   ├── forward-symbolic.svg
│   │           │   │   │   ├── forward.pdf
│   │           │   │   │   ├── forward.png
│   │           │   │   │   ├── forward.svg
│   │           │   │   │   ├── forward_large.png
│   │           │   │   │   ├── hand.pdf
│   │           │   │   │   ├── hand.png
│   │           │   │   │   ├── hand.svg
│   │           │   │   │   ├── help-symbolic.svg
│   │           │   │   │   ├── help.pdf
│   │           │   │   │   ├── help.png
│   │           │   │   │   ├── help.svg
│   │           │   │   │   ├── help_large.png
│   │           │   │   │   ├── home-symbolic.svg
│   │           │   │   │   ├── home.pdf
│   │           │   │   │   ├── home.png
│   │           │   │   │   ├── home.svg
│   │           │   │   │   ├── home_large.png
│   │           │   │   │   ├── matplotlib.pdf
│   │           │   │   │   ├── matplotlib.png
│   │           │   │   │   ├── matplotlib.svg
│   │           │   │   │   ├── matplotlib_large.png
│   │           │   │   │   ├── move-symbolic.svg
│   │           │   │   │   ├── move.pdf
│   │           │   │   │   ├── move.png
│   │           │   │   │   ├── move.svg
│   │           │   │   │   ├── move_large.png
│   │           │   │   │   ├── qt4_editor_options.pdf
│   │           │   │   │   ├── qt4_editor_options.png
│   │           │   │   │   ├── qt4_editor_options.svg
│   │           │   │   │   ├── qt4_editor_options_large.png
│   │           │   │   │   ├── subplots-symbolic.svg
│   │           │   │   │   ├── subplots.pdf
│   │           │   │   │   ├── subplots.png
│   │           │   │   │   ├── subplots.svg
│   │           │   │   │   ├── subplots_large.png
│   │           │   │   │   ├── zoom_to_rect-symbolic.svg
│   │           │   │   │   ├── zoom_to_rect.pdf
│   │           │   │   │   ├── zoom_to_rect.png
│   │           │   │   │   ├── zoom_to_rect.svg
│   │           │   │   │   └── zoom_to_rect_large.png
│   │           │   │   ├── kpsewhich.lua
│   │           │   │   ├── matplotlibrc
│   │           │   │   ├── plot_directive/
│   │           │   │   │   └── plot_directive.css
│   │           │   │   ├── sample_data/
│   │           │   │   │   ├── Minduka_Present_Blue_Pack.png
│   │           │   │   │   ├── README.txt
│   │           │   │   │   ├── Stocks.csv
│   │           │   │   │   ├── axes_grid/
│   │           │   │   │   │   └── bivariate_normal.npy
│   │           │   │   │   ├── data_x_x2_x3.csv
│   │           │   │   │   ├── eeg.dat
│   │           │   │   │   ├── embedding_in_wx3.xrc
│   │           │   │   │   ├── goog.npz
│   │           │   │   │   ├── grace_hopper.jpg
│   │           │   │   │   ├── jacksboro_fault_dem.npz
│   │           │   │   │   ├── logo2.png
│   │           │   │   │   ├── membrane.dat
│   │           │   │   │   ├── msft.csv
│   │           │   │   │   ├── s1045.ima.gz
│   │           │   │   │   └── topobathy.npz
│   │           │   │   └── stylelib/
│   │           │   │       ├── _classic_test_patch.mplstyle
│   │           │   │       ├── _mpl-gallery-nogrid.mplstyle
│   │           │   │       ├── _mpl-gallery.mplstyle
│   │           │   │       ├── bmh.mplstyle
│   │           │   │       ├── classic.mplstyle
│   │           │   │       ├── dark_background.mplstyle
│   │           │   │       ├── fast.mplstyle
│   │           │   │       ├── fivethirtyeight.mplstyle
│   │           │   │       ├── ggplot.mplstyle
│   │           │   │       ├── grayscale.mplstyle
│   │           │   │       ├── petroff10.mplstyle
│   │           │   │       ├── seaborn-v0_8-bright.mplstyle
│   │           │   │       ├── seaborn-v0_8-colorblind.mplstyle
│   │           │   │       ├── seaborn-v0_8-dark-palette.mplstyle
│   │           │   │       ├── seaborn-v0_8-dark.mplstyle
│   │           │   │       ├── seaborn-v0_8-darkgrid.mplstyle
│   │           │   │       ├── seaborn-v0_8-deep.mplstyle
│   │           │   │       ├── seaborn-v0_8-muted.mplstyle
│   │           │   │       ├── seaborn-v0_8-notebook.mplstyle
│   │           │   │       ├── seaborn-v0_8-paper.mplstyle
│   │           │   │       ├── seaborn-v0_8-pastel.mplstyle
│   │           │   │       ├── seaborn-v0_8-poster.mplstyle
│   │           │   │       ├── seaborn-v0_8-talk.mplstyle
│   │           │   │       ├── seaborn-v0_8-ticks.mplstyle
│   │           │   │       ├── seaborn-v0_8-white.mplstyle
│   │           │   │       ├── seaborn-v0_8-whitegrid.mplstyle
│   │           │   │       ├── seaborn-v0_8.mplstyle
│   │           │   │       └── tableau-colorblind10.mplstyle
│   │           │   ├── offsetbox.py
│   │           │   ├── offsetbox.pyi
│   │           │   ├── patches.py
│   │           │   ├── patches.pyi
│   │           │   ├── path.py
│   │           │   ├── path.pyi
│   │           │   ├── patheffects.py
│   │           │   ├── patheffects.pyi
│   │           │   ├── projections/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── geo.cpython-311.pyc
│   │           │   │   │   └── polar.cpython-311.pyc
│   │           │   │   ├── geo.py
│   │           │   │   ├── geo.pyi
│   │           │   │   ├── polar.py
│   │           │   │   └── polar.pyi
│   │           │   ├── py.typed
│   │           │   ├── pylab.py
│   │           │   ├── pyplot.py
│   │           │   ├── quiver.py
│   │           │   ├── quiver.pyi
│   │           │   ├── rcsetup.py
│   │           │   ├── rcsetup.pyi
│   │           │   ├── sankey.py
│   │           │   ├── sankey.pyi
│   │           │   ├── scale.py
│   │           │   ├── scale.pyi
│   │           │   ├── sphinxext/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── figmpl_directive.cpython-311.pyc
│   │           │   │   │   ├── mathmpl.cpython-311.pyc
│   │           │   │   │   ├── plot_directive.cpython-311.pyc
│   │           │   │   │   └── roles.cpython-311.pyc
│   │           │   │   ├── figmpl_directive.py
│   │           │   │   ├── mathmpl.py
│   │           │   │   ├── plot_directive.py
│   │           │   │   └── roles.py
│   │           │   ├── spines.py
│   │           │   ├── spines.pyi
│   │           │   ├── stackplot.py
│   │           │   ├── stackplot.pyi
│   │           │   ├── streamplot.py
│   │           │   ├── streamplot.pyi
│   │           │   ├── style
│   │           │   ├── style/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── core.cpython-311.pyc
│   │           │   │   ├── core.py
│   │           │   │   └── core.pyi
│   │           │   ├── table.py
│   │           │   ├── table.pyi
│   │           │   ├── testing/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _markers.cpython-311.pyc
│   │           │   │   │   ├── compare.cpython-311.pyc
│   │           │   │   │   ├── conftest.cpython-311.pyc
│   │           │   │   │   ├── decorators.cpython-311.pyc
│   │           │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   └── widgets.cpython-311.pyc
│   │           │   │   ├── _markers.py
│   │           │   │   ├── compare.py
│   │           │   │   ├── compare.pyi
│   │           │   │   ├── conftest.py
│   │           │   │   ├── conftest.pyi
│   │           │   │   ├── decorators.py
│   │           │   │   ├── decorators.pyi
│   │           │   │   ├── exceptions.py
│   │           │   │   ├── jpl_units/
│   │           │   │   │   ├── Duration.py
│   │           │   │   │   ├── Epoch.py
│   │           │   │   │   ├── EpochConverter.py
│   │           │   │   │   ├── StrConverter.py
│   │           │   │   │   ├── UnitDbl.py
│   │           │   │   │   ├── UnitDblConverter.py
│   │           │   │   │   ├── UnitDblFormatter.py
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   └── __pycache__/
│   │           │   │   │       ├── Duration.cpython-311.pyc
│   │           │   │   │       ├── Epoch.cpython-311.pyc
│   │           │   │   │       ├── EpochConverter.cpython-311.pyc
│   │           │   │   │       ├── StrConverter.cpython-311.pyc
│   │           │   │   │       ├── UnitDbl.cpython-311.pyc
│   │           │   │   │       ├── UnitDblConverter.cpython-311.pyc
│   │           │   │   │       ├── UnitDblFormatter.cpython-311.pyc
│   │           │   │   │       └── __init__.cpython-311.pyc
│   │           │   │   ├── widgets.py
│   │           │   │   └── widgets.pyi
│   │           │   ├── tests/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── conftest.cpython-311.pyc
│   │           │   │   │   ├── test_afm.cpython-311.pyc
│   │           │   │   │   ├── test_agg.cpython-311.pyc
│   │           │   │   │   ├── test_agg_filter.cpython-311.pyc
│   │           │   │   │   ├── test_animation.cpython-311.pyc
│   │           │   │   │   ├── test_api.cpython-311.pyc
│   │           │   │   │   ├── test_arrow_patches.cpython-311.pyc
│   │           │   │   │   ├── test_artist.cpython-311.pyc
│   │           │   │   │   ├── test_axes.cpython-311.pyc
│   │           │   │   │   ├── test_axis.cpython-311.pyc
│   │           │   │   │   ├── test_backend_bases.cpython-311.pyc
│   │           │   │   │   ├── test_backend_cairo.cpython-311.pyc
│   │           │   │   │   ├── test_backend_gtk3.cpython-311.pyc
│   │           │   │   │   ├── test_backend_inline.cpython-311.pyc
│   │           │   │   │   ├── test_backend_macosx.cpython-311.pyc
│   │           │   │   │   ├── test_backend_nbagg.cpython-311.pyc
│   │           │   │   │   ├── test_backend_pdf.cpython-311.pyc
│   │           │   │   │   ├── test_backend_pgf.cpython-311.pyc
│   │           │   │   │   ├── test_backend_ps.cpython-311.pyc
│   │           │   │   │   ├── test_backend_qt.cpython-311.pyc
│   │           │   │   │   ├── test_backend_registry.cpython-311.pyc
│   │           │   │   │   ├── test_backend_svg.cpython-311.pyc
│   │           │   │   │   ├── test_backend_template.cpython-311.pyc
│   │           │   │   │   ├── test_backend_tk.cpython-311.pyc
│   │           │   │   │   ├── test_backend_tools.cpython-311.pyc
│   │           │   │   │   ├── test_backend_webagg.cpython-311.pyc
│   │           │   │   │   ├── test_backends_interactive.cpython-311.pyc
│   │           │   │   │   ├── test_basic.cpython-311.pyc
│   │           │   │   │   ├── test_bbox_tight.cpython-311.pyc
│   │           │   │   │   ├── test_bezier.cpython-311.pyc
│   │           │   │   │   ├── test_category.cpython-311.pyc
│   │           │   │   │   ├── test_cbook.cpython-311.pyc
│   │           │   │   │   ├── test_collections.cpython-311.pyc
│   │           │   │   │   ├── test_colorbar.cpython-311.pyc
│   │           │   │   │   ├── test_colors.cpython-311.pyc
│   │           │   │   │   ├── test_compare_images.cpython-311.pyc
│   │           │   │   │   ├── test_constrainedlayout.cpython-311.pyc
│   │           │   │   │   ├── test_container.cpython-311.pyc
│   │           │   │   │   ├── test_contour.cpython-311.pyc
│   │           │   │   │   ├── test_cycles.cpython-311.pyc
│   │           │   │   │   ├── test_dates.cpython-311.pyc
│   │           │   │   │   ├── test_datetime.cpython-311.pyc
│   │           │   │   │   ├── test_determinism.cpython-311.pyc
│   │           │   │   │   ├── test_doc.cpython-311.pyc
│   │           │   │   │   ├── test_dviread.cpython-311.pyc
│   │           │   │   │   ├── test_figure.cpython-311.pyc
│   │           │   │   │   ├── test_font_manager.cpython-311.pyc
│   │           │   │   │   ├── test_fontconfig_pattern.cpython-311.pyc
│   │           │   │   │   ├── test_ft2font.cpython-311.pyc
│   │           │   │   │   ├── test_getattr.cpython-311.pyc
│   │           │   │   │   ├── test_gridspec.cpython-311.pyc
│   │           │   │   │   ├── test_image.cpython-311.pyc
│   │           │   │   │   ├── test_legend.cpython-311.pyc
│   │           │   │   │   ├── test_lines.cpython-311.pyc
│   │           │   │   │   ├── test_marker.cpython-311.pyc
│   │           │   │   │   ├── test_mathtext.cpython-311.pyc
│   │           │   │   │   ├── test_matplotlib.cpython-311.pyc
│   │           │   │   │   ├── test_mlab.cpython-311.pyc
│   │           │   │   │   ├── test_multivariate_colormaps.cpython-311.pyc
│   │           │   │   │   ├── test_offsetbox.cpython-311.pyc
│   │           │   │   │   ├── test_patches.cpython-311.pyc
│   │           │   │   │   ├── test_path.cpython-311.pyc
│   │           │   │   │   ├── test_patheffects.cpython-311.pyc
│   │           │   │   │   ├── test_pickle.cpython-311.pyc
│   │           │   │   │   ├── test_png.cpython-311.pyc
│   │           │   │   │   ├── test_polar.cpython-311.pyc
│   │           │   │   │   ├── test_preprocess_data.cpython-311.pyc
│   │           │   │   │   ├── test_pyplot.cpython-311.pyc
│   │           │   │   │   ├── test_quiver.cpython-311.pyc
│   │           │   │   │   ├── test_rcparams.cpython-311.pyc
│   │           │   │   │   ├── test_sankey.cpython-311.pyc
│   │           │   │   │   ├── test_scale.cpython-311.pyc
│   │           │   │   │   ├── test_simplification.cpython-311.pyc
│   │           │   │   │   ├── test_skew.cpython-311.pyc
│   │           │   │   │   ├── test_sphinxext.cpython-311.pyc
│   │           │   │   │   ├── test_spines.cpython-311.pyc
│   │           │   │   │   ├── test_streamplot.cpython-311.pyc
│   │           │   │   │   ├── test_style.cpython-311.pyc
│   │           │   │   │   ├── test_subplots.cpython-311.pyc
│   │           │   │   │   ├── test_table.cpython-311.pyc
│   │           │   │   │   ├── test_testing.cpython-311.pyc
│   │           │   │   │   ├── test_texmanager.cpython-311.pyc
│   │           │   │   │   ├── test_text.cpython-311.pyc
│   │           │   │   │   ├── test_textpath.cpython-311.pyc
│   │           │   │   │   ├── test_ticker.cpython-311.pyc
│   │           │   │   │   ├── test_tightlayout.cpython-311.pyc
│   │           │   │   │   ├── test_transforms.cpython-311.pyc
│   │           │   │   │   ├── test_triangulation.cpython-311.pyc
│   │           │   │   │   ├── test_type1font.cpython-311.pyc
│   │           │   │   │   ├── test_units.cpython-311.pyc
│   │           │   │   │   ├── test_usetex.cpython-311.pyc
│   │           │   │   │   └── test_widgets.cpython-311.pyc
│   │           │   │   ├── conftest.py
│   │           │   │   ├── test_afm.py
│   │           │   │   ├── test_agg.py
│   │           │   │   ├── test_agg_filter.py
│   │           │   │   ├── test_animation.py
│   │           │   │   ├── test_api.py
│   │           │   │   ├── test_arrow_patches.py
│   │           │   │   ├── test_artist.py
│   │           │   │   ├── test_axes.py
│   │           │   │   ├── test_axis.py
│   │           │   │   ├── test_backend_bases.py
│   │           │   │   ├── test_backend_cairo.py
│   │           │   │   ├── test_backend_gtk3.py
│   │           │   │   ├── test_backend_inline.py
│   │           │   │   ├── test_backend_macosx.py
│   │           │   │   ├── test_backend_nbagg.py
│   │           │   │   ├── test_backend_pdf.py
│   │           │   │   ├── test_backend_pgf.py
│   │           │   │   ├── test_backend_ps.py
│   │           │   │   ├── test_backend_qt.py
│   │           │   │   ├── test_backend_registry.py
│   │           │   │   ├── test_backend_svg.py
│   │           │   │   ├── test_backend_template.py
│   │           │   │   ├── test_backend_tk.py
│   │           │   │   ├── test_backend_tools.py
│   │           │   │   ├── test_backend_webagg.py
│   │           │   │   ├── test_backends_interactive.py
│   │           │   │   ├── test_basic.py
│   │           │   │   ├── test_bbox_tight.py
│   │           │   │   ├── test_bezier.py
│   │           │   │   ├── test_category.py
│   │           │   │   ├── test_cbook.py
│   │           │   │   ├── test_collections.py
│   │           │   │   ├── test_colorbar.py
│   │           │   │   ├── test_colors.py
│   │           │   │   ├── test_compare_images.py
│   │           │   │   ├── test_constrainedlayout.py
│   │           │   │   ├── test_container.py
│   │           │   │   ├── test_contour.py
│   │           │   │   ├── test_cycles.py
│   │           │   │   ├── test_dates.py
│   │           │   │   ├── test_datetime.py
│   │           │   │   ├── test_determinism.py
│   │           │   │   ├── test_doc.py
│   │           │   │   ├── test_dviread.py
│   │           │   │   ├── test_figure.py
│   │           │   │   ├── test_font_manager.py
│   │           │   │   ├── test_fontconfig_pattern.py
│   │           │   │   ├── test_ft2font.py
│   │           │   │   ├── test_getattr.py
│   │           │   │   ├── test_gridspec.py
│   │           │   │   ├── test_image.py
│   │           │   │   ├── test_legend.py
│   │           │   │   ├── test_lines.py
│   │           │   │   ├── test_marker.py
│   │           │   │   ├── test_mathtext.py
│   │           │   │   ├── test_matplotlib.py
│   │           │   │   ├── test_mlab.py
│   │           │   │   ├── test_multivariate_colormaps.py
│   │           │   │   ├── test_offsetbox.py
│   │           │   │   ├── test_patches.py
│   │           │   │   ├── test_path.py
│   │           │   │   ├── test_patheffects.py
│   │           │   │   ├── test_pickle.py
│   │           │   │   ├── test_png.py
│   │           │   │   ├── test_polar.py
│   │           │   │   ├── test_preprocess_data.py
│   │           │   │   ├── test_pyplot.py
│   │           │   │   ├── test_quiver.py
│   │           │   │   ├── test_rcparams.py
│   │           │   │   ├── test_sankey.py
│   │           │   │   ├── test_scale.py
│   │           │   │   ├── test_simplification.py
│   │           │   │   ├── test_skew.py
│   │           │   │   ├── test_sphinxext.py
│   │           │   │   ├── test_spines.py
│   │           │   │   ├── test_streamplot.py
│   │           │   │   ├── test_style.py
│   │           │   │   ├── test_subplots.py
│   │           │   │   ├── test_table.py
│   │           │   │   ├── test_testing.py
│   │           │   │   ├── test_texmanager.py
│   │           │   │   ├── test_text.py
│   │           │   │   ├── test_textpath.py
│   │           │   │   ├── test_ticker.py
│   │           │   │   ├── test_tightlayout.py
│   │           │   │   ├── test_transforms.py
│   │           │   │   ├── test_triangulation.py
│   │           │   │   ├── test_type1font.py
│   │           │   │   ├── test_units.py
│   │           │   │   ├── test_usetex.py
│   │           │   │   └── test_widgets.py
│   │           │   ├── texmanager.py
│   │           │   ├── texmanager.pyi
│   │           │   ├── text.py
│   │           │   ├── text.pyi
│   │           │   ├── textpath.py
│   │           │   ├── textpath.pyi
│   │           │   ├── ticker.py
│   │           │   ├── ticker.pyi
│   │           │   ├── transforms.py
│   │           │   ├── transforms.pyi
│   │           │   ├── tri/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _triangulation.cpython-311.pyc
│   │           │   │   │   ├── _tricontour.cpython-311.pyc
│   │           │   │   │   ├── _trifinder.cpython-311.pyc
│   │           │   │   │   ├── _triinterpolate.cpython-311.pyc
│   │           │   │   │   ├── _tripcolor.cpython-311.pyc
│   │           │   │   │   ├── _triplot.cpython-311.pyc
│   │           │   │   │   ├── _trirefine.cpython-311.pyc
│   │           │   │   │   └── _tritools.cpython-311.pyc
│   │           │   │   ├── _triangulation.py
│   │           │   │   ├── _triangulation.pyi
│   │           │   │   ├── _tricontour.py
│   │           │   │   ├── _tricontour.pyi
│   │           │   │   ├── _trifinder.py
│   │           │   │   ├── _trifinder.pyi
│   │           │   │   ├── _triinterpolate.py
│   │           │   │   ├── _triinterpolate.pyi
│   │           │   │   ├── _tripcolor.py
│   │           │   │   ├── _tripcolor.pyi
│   │           │   │   ├── _triplot.py
│   │           │   │   ├── _triplot.pyi
│   │           │   │   ├── _trirefine.py
│   │           │   │   ├── _trirefine.pyi
│   │           │   │   ├── _tritools.py
│   │           │   │   └── _tritools.pyi
│   │           │   ├── typing.py
│   │           │   ├── units.py
│   │           │   ├── widgets.py
│   │           │   └── widgets.pyi
│   │           ├── mpl_toolkits/
│   │           │   ├── axes_grid1/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── anchored_artists.cpython-311.pyc
│   │           │   │   │   ├── axes_divider.cpython-311.pyc
│   │           │   │   │   ├── axes_grid.cpython-311.pyc
│   │           │   │   │   ├── axes_rgb.cpython-311.pyc
│   │           │   │   │   ├── axes_size.cpython-311.pyc
│   │           │   │   │   ├── inset_locator.cpython-311.pyc
│   │           │   │   │   ├── mpl_axes.cpython-311.pyc
│   │           │   │   │   └── parasite_axes.cpython-311.pyc
│   │           │   │   ├── anchored_artists.py
│   │           │   │   ├── axes_divider.py
│   │           │   │   ├── axes_grid.py
│   │           │   │   ├── axes_rgb.py
│   │           │   │   ├── axes_size.py
│   │           │   │   ├── inset_locator.py
│   │           │   │   ├── mpl_axes.py
│   │           │   │   ├── parasite_axes.py
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── conftest.cpython-311.pyc
│   │           │   │       │   └── test_axes_grid1.cpython-311.pyc
│   │           │   │       ├── conftest.py
│   │           │   │       └── test_axes_grid1.py
│   │           │   ├── axisartist/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── angle_helper.cpython-311.pyc
│   │           │   │   │   ├── axes_divider.cpython-311.pyc
│   │           │   │   │   ├── axis_artist.cpython-311.pyc
│   │           │   │   │   ├── axisline_style.cpython-311.pyc
│   │           │   │   │   ├── axislines.cpython-311.pyc
│   │           │   │   │   ├── floating_axes.cpython-311.pyc
│   │           │   │   │   ├── grid_finder.cpython-311.pyc
│   │           │   │   │   ├── grid_helper_curvelinear.cpython-311.pyc
│   │           │   │   │   └── parasite_axes.cpython-311.pyc
│   │           │   │   ├── angle_helper.py
│   │           │   │   ├── axes_divider.py
│   │           │   │   ├── axis_artist.py
│   │           │   │   ├── axisline_style.py
│   │           │   │   ├── axislines.py
│   │           │   │   ├── floating_axes.py
│   │           │   │   ├── grid_finder.py
│   │           │   │   ├── grid_helper_curvelinear.py
│   │           │   │   ├── parasite_axes.py
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── conftest.cpython-311.pyc
│   │           │   │       │   ├── test_angle_helper.cpython-311.pyc
│   │           │   │       │   ├── test_axis_artist.cpython-311.pyc
│   │           │   │       │   ├── test_axislines.cpython-311.pyc
│   │           │   │       │   ├── test_floating_axes.cpython-311.pyc
│   │           │   │       │   ├── test_grid_finder.cpython-311.pyc
│   │           │   │       │   └── test_grid_helper_curvelinear.cpython-311.pyc
│   │           │   │       ├── conftest.py
│   │           │   │       ├── test_angle_helper.py
│   │           │   │       ├── test_axis_artist.py
│   │           │   │       ├── test_axislines.py
│   │           │   │       ├── test_floating_axes.py
│   │           │   │       ├── test_grid_finder.py
│   │           │   │       └── test_grid_helper_curvelinear.py
│   │           │   └── mplot3d/
│   │           │       ├── __init__.py
│   │           │       ├── __pycache__/
│   │           │       │   ├── __init__.cpython-311.pyc
│   │           │       │   ├── art3d.cpython-311.pyc
│   │           │       │   ├── axes3d.cpython-311.pyc
│   │           │       │   ├── axis3d.cpython-311.pyc
│   │           │       │   └── proj3d.cpython-311.pyc
│   │           │       ├── art3d.py
│   │           │       ├── axes3d.py
│   │           │       ├── axis3d.py
│   │           │       ├── proj3d.py
│   │           │       └── tests/
│   │           │           ├── __init__.py
│   │           │           ├── __pycache__/
│   │           │           │   ├── __init__.cpython-311.pyc
│   │           │           │   ├── conftest.cpython-311.pyc
│   │           │           │   ├── test_art3d.cpython-311.pyc
│   │           │           │   ├── test_axes3d.cpython-311.pyc
│   │           │           │   └── test_legend3d.cpython-311.pyc
│   │           │           ├── conftest.py
│   │           │           ├── test_art3d.py
│   │           │           ├── test_axes3d.py
│   │           │           └── test_legend3d.py
│   │           ├── numpy-2.3.3.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.txt
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   └── entry_points.txt
│   │           ├── numpy/
│   │           │   ├── __config__.py
│   │           │   ├── __config__.pyi
│   │           │   ├── __init__.cython-30.pxd
│   │           │   ├── __init__.pxd
│   │           │   ├── __init__.py
│   │           │   ├── __init__.pyi
│   │           │   ├── __pycache__/
│   │           │   │   ├── __config__.cpython-311.pyc
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _array_api_info.cpython-311.pyc
│   │           │   │   ├── _configtool.cpython-311.pyc
│   │           │   │   ├── _distributor_init.cpython-311.pyc
│   │           │   │   ├── _expired_attrs_2_0.cpython-311.pyc
│   │           │   │   ├── _globals.cpython-311.pyc
│   │           │   │   ├── _pytesttester.cpython-311.pyc
│   │           │   │   ├── conftest.cpython-311.pyc
│   │           │   │   ├── dtypes.cpython-311.pyc
│   │           │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   ├── matlib.cpython-311.pyc
│   │           │   │   └── version.cpython-311.pyc
│   │           │   ├── _array_api_info.py
│   │           │   ├── _array_api_info.pyi
│   │           │   ├── _configtool.py
│   │           │   ├── _configtool.pyi
│   │           │   ├── _core/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _add_newdocs.cpython-311.pyc
│   │           │   │   │   ├── _add_newdocs_scalars.cpython-311.pyc
│   │           │   │   │   ├── _asarray.cpython-311.pyc
│   │           │   │   │   ├── _dtype.cpython-311.pyc
│   │           │   │   │   ├── _dtype_ctypes.cpython-311.pyc
│   │           │   │   │   ├── _exceptions.cpython-311.pyc
│   │           │   │   │   ├── _internal.cpython-311.pyc
│   │           │   │   │   ├── _machar.cpython-311.pyc
│   │           │   │   │   ├── _methods.cpython-311.pyc
│   │           │   │   │   ├── _string_helpers.cpython-311.pyc
│   │           │   │   │   ├── _type_aliases.cpython-311.pyc
│   │           │   │   │   ├── _ufunc_config.cpython-311.pyc
│   │           │   │   │   ├── arrayprint.cpython-311.pyc
│   │           │   │   │   ├── cversions.cpython-311.pyc
│   │           │   │   │   ├── defchararray.cpython-311.pyc
│   │           │   │   │   ├── einsumfunc.cpython-311.pyc
│   │           │   │   │   ├── fromnumeric.cpython-311.pyc
│   │           │   │   │   ├── function_base.cpython-311.pyc
│   │           │   │   │   ├── getlimits.cpython-311.pyc
│   │           │   │   │   ├── memmap.cpython-311.pyc
│   │           │   │   │   ├── multiarray.cpython-311.pyc
│   │           │   │   │   ├── numeric.cpython-311.pyc
│   │           │   │   │   ├── numerictypes.cpython-311.pyc
│   │           │   │   │   ├── overrides.cpython-311.pyc
│   │           │   │   │   ├── printoptions.cpython-311.pyc
│   │           │   │   │   ├── records.cpython-311.pyc
│   │           │   │   │   ├── shape_base.cpython-311.pyc
│   │           │   │   │   ├── strings.cpython-311.pyc
│   │           │   │   │   └── umath.cpython-311.pyc
│   │           │   │   ├── _add_newdocs.py
│   │           │   │   ├── _add_newdocs.pyi
│   │           │   │   ├── _add_newdocs_scalars.py
│   │           │   │   ├── _add_newdocs_scalars.pyi
│   │           │   │   ├── _asarray.py
│   │           │   │   ├── _asarray.pyi
│   │           │   │   ├── _dtype.py
│   │           │   │   ├── _dtype.pyi
│   │           │   │   ├── _dtype_ctypes.py
│   │           │   │   ├── _dtype_ctypes.pyi
│   │           │   │   ├── _exceptions.py
│   │           │   │   ├── _exceptions.pyi
│   │           │   │   ├── _internal.py
│   │           │   │   ├── _internal.pyi
│   │           │   │   ├── _machar.py
│   │           │   │   ├── _machar.pyi
│   │           │   │   ├── _methods.py
│   │           │   │   ├── _methods.pyi
│   │           │   │   ├── _multiarray_tests.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _multiarray_umath.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _operand_flag_tests.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _rational_tests.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _simd.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _simd.pyi
│   │           │   │   ├── _string_helpers.py
│   │           │   │   ├── _string_helpers.pyi
│   │           │   │   ├── _struct_ufunc_tests.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _type_aliases.py
│   │           │   │   ├── _type_aliases.pyi
│   │           │   │   ├── _ufunc_config.py
│   │           │   │   ├── _ufunc_config.pyi
│   │           │   │   ├── _umath_tests.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── arrayprint.py
│   │           │   │   ├── arrayprint.pyi
│   │           │   │   ├── cversions.py
│   │           │   │   ├── defchararray.py
│   │           │   │   ├── defchararray.pyi
│   │           │   │   ├── einsumfunc.py
│   │           │   │   ├── einsumfunc.pyi
│   │           │   │   ├── fromnumeric.py
│   │           │   │   ├── fromnumeric.pyi
│   │           │   │   ├── function_base.py
│   │           │   │   ├── function_base.pyi
│   │           │   │   ├── getlimits.py
│   │           │   │   ├── getlimits.pyi
│   │           │   │   ├── include/
│   │           │   │   │   └── numpy/
│   │           │   │   │       ├── __multiarray_api.c
│   │           │   │   │       ├── __multiarray_api.h
│   │           │   │   │       ├── __ufunc_api.c
│   │           │   │   │       ├── __ufunc_api.h
│   │           │   │   │       ├── _neighborhood_iterator_imp.h
│   │           │   │   │       ├── _numpyconfig.h
│   │           │   │   │       ├── _public_dtype_api_table.h
│   │           │   │   │       ├── arrayobject.h
│   │           │   │   │       ├── arrayscalars.h
│   │           │   │   │       ├── dtype_api.h
│   │           │   │   │       ├── halffloat.h
│   │           │   │   │       ├── ndarrayobject.h
│   │           │   │   │       ├── ndarraytypes.h
│   │           │   │   │       ├── npy_2_compat.h
│   │           │   │   │       ├── npy_2_complexcompat.h
│   │           │   │   │       ├── npy_3kcompat.h
│   │           │   │   │       ├── npy_common.h
│   │           │   │   │       ├── npy_cpu.h
│   │           │   │   │       ├── npy_endian.h
│   │           │   │   │       ├── npy_math.h
│   │           │   │   │       ├── npy_no_deprecated_api.h
│   │           │   │   │       ├── npy_os.h
│   │           │   │   │       ├── numpyconfig.h
│   │           │   │   │       ├── random/
│   │           │   │   │       │   ├── LICENSE.txt
│   │           │   │   │       │   ├── bitgen.h
│   │           │   │   │       │   ├── distributions.h
│   │           │   │   │       │   └── libdivide.h
│   │           │   │   │       ├── ufuncobject.h
│   │           │   │   │       └── utils.h
│   │           │   │   ├── lib/
│   │           │   │   │   ├── libnpymath.a
│   │           │   │   │   ├── npy-pkg-config/
│   │           │   │   │   │   ├── mlib.ini
│   │           │   │   │   │   └── npymath.ini
│   │           │   │   │   └── pkgconfig/
│   │           │   │   │       └── numpy.pc
│   │           │   │   ├── memmap.py
│   │           │   │   ├── memmap.pyi
│   │           │   │   ├── multiarray.py
│   │           │   │   ├── multiarray.pyi
│   │           │   │   ├── numeric.py
│   │           │   │   ├── numeric.pyi
│   │           │   │   ├── numerictypes.py
│   │           │   │   ├── numerictypes.pyi
│   │           │   │   ├── overrides.py
│   │           │   │   ├── overrides.pyi
│   │           │   │   ├── printoptions.py
│   │           │   │   ├── printoptions.pyi
│   │           │   │   ├── records.py
│   │           │   │   ├── records.pyi
│   │           │   │   ├── shape_base.py
│   │           │   │   ├── shape_base.pyi
│   │           │   │   ├── strings.py
│   │           │   │   ├── strings.pyi
│   │           │   │   ├── tests/
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── _locales.cpython-311.pyc
│   │           │   │   │   │   ├── _natype.cpython-311.pyc
│   │           │   │   │   │   ├── test__exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── test_abc.cpython-311.pyc
│   │           │   │   │   │   ├── test_api.cpython-311.pyc
│   │           │   │   │   │   ├── test_argparse.cpython-311.pyc
│   │           │   │   │   │   ├── test_array_api_info.cpython-311.pyc
│   │           │   │   │   │   ├── test_array_coercion.cpython-311.pyc
│   │           │   │   │   │   ├── test_array_interface.cpython-311.pyc
│   │           │   │   │   │   ├── test_arraymethod.cpython-311.pyc
│   │           │   │   │   │   ├── test_arrayobject.cpython-311.pyc
│   │           │   │   │   │   ├── test_arrayprint.cpython-311.pyc
│   │           │   │   │   │   ├── test_casting_floatingpoint_errors.cpython-311.pyc
│   │           │   │   │   │   ├── test_casting_unittests.cpython-311.pyc
│   │           │   │   │   │   ├── test_conversion_utils.cpython-311.pyc
│   │           │   │   │   │   ├── test_cpu_dispatcher.cpython-311.pyc
│   │           │   │   │   │   ├── test_cpu_features.cpython-311.pyc
│   │           │   │   │   │   ├── test_custom_dtypes.cpython-311.pyc
│   │           │   │   │   │   ├── test_cython.cpython-311.pyc
│   │           │   │   │   │   ├── test_datetime.cpython-311.pyc
│   │           │   │   │   │   ├── test_defchararray.cpython-311.pyc
│   │           │   │   │   │   ├── test_deprecations.cpython-311.pyc
│   │           │   │   │   │   ├── test_dlpack.cpython-311.pyc
│   │           │   │   │   │   ├── test_dtype.cpython-311.pyc
│   │           │   │   │   │   ├── test_einsum.cpython-311.pyc
│   │           │   │   │   │   ├── test_errstate.cpython-311.pyc
│   │           │   │   │   │   ├── test_extint128.cpython-311.pyc
│   │           │   │   │   │   ├── test_function_base.cpython-311.pyc
│   │           │   │   │   │   ├── test_getlimits.cpython-311.pyc
│   │           │   │   │   │   ├── test_half.cpython-311.pyc
│   │           │   │   │   │   ├── test_hashtable.cpython-311.pyc
│   │           │   │   │   │   ├── test_indexerrors.cpython-311.pyc
│   │           │   │   │   │   ├── test_indexing.cpython-311.pyc
│   │           │   │   │   │   ├── test_item_selection.cpython-311.pyc
│   │           │   │   │   │   ├── test_limited_api.cpython-311.pyc
│   │           │   │   │   │   ├── test_longdouble.cpython-311.pyc
│   │           │   │   │   │   ├── test_machar.cpython-311.pyc
│   │           │   │   │   │   ├── test_mem_overlap.cpython-311.pyc
│   │           │   │   │   │   ├── test_mem_policy.cpython-311.pyc
│   │           │   │   │   │   ├── test_memmap.cpython-311.pyc
│   │           │   │   │   │   ├── test_multiarray.cpython-311.pyc
│   │           │   │   │   │   ├── test_multithreading.cpython-311.pyc
│   │           │   │   │   │   ├── test_nditer.cpython-311.pyc
│   │           │   │   │   │   ├── test_nep50_promotions.cpython-311.pyc
│   │           │   │   │   │   ├── test_numeric.cpython-311.pyc
│   │           │   │   │   │   ├── test_numerictypes.cpython-311.pyc
│   │           │   │   │   │   ├── test_overrides.cpython-311.pyc
│   │           │   │   │   │   ├── test_print.cpython-311.pyc
│   │           │   │   │   │   ├── test_protocols.cpython-311.pyc
│   │           │   │   │   │   ├── test_records.cpython-311.pyc
│   │           │   │   │   │   ├── test_regression.cpython-311.pyc
│   │           │   │   │   │   ├── test_scalar_ctors.cpython-311.pyc
│   │           │   │   │   │   ├── test_scalar_methods.cpython-311.pyc
│   │           │   │   │   │   ├── test_scalarbuffer.cpython-311.pyc
│   │           │   │   │   │   ├── test_scalarinherit.cpython-311.pyc
│   │           │   │   │   │   ├── test_scalarmath.cpython-311.pyc
│   │           │   │   │   │   ├── test_scalarprint.cpython-311.pyc
│   │           │   │   │   │   ├── test_shape_base.cpython-311.pyc
│   │           │   │   │   │   ├── test_simd.cpython-311.pyc
│   │           │   │   │   │   ├── test_simd_module.cpython-311.pyc
│   │           │   │   │   │   ├── test_stringdtype.cpython-311.pyc
│   │           │   │   │   │   ├── test_strings.cpython-311.pyc
│   │           │   │   │   │   ├── test_ufunc.cpython-311.pyc
│   │           │   │   │   │   ├── test_umath.cpython-311.pyc
│   │           │   │   │   │   ├── test_umath_accuracy.cpython-311.pyc
│   │           │   │   │   │   ├── test_umath_complex.cpython-311.pyc
│   │           │   │   │   │   └── test_unicode.cpython-311.pyc
│   │           │   │   │   ├── _locales.py
│   │           │   │   │   ├── _natype.py
│   │           │   │   │   ├── data/
│   │           │   │   │   │   ├── astype_copy.pkl
│   │           │   │   │   │   ├── generate_umath_validation_data.cpp
│   │           │   │   │   │   ├── recarray_from_file.fits
│   │           │   │   │   │   ├── umath-validation-set-README.txt
│   │           │   │   │   │   ├── umath-validation-set-arccos.csv
│   │           │   │   │   │   ├── umath-validation-set-arccosh.csv
│   │           │   │   │   │   ├── umath-validation-set-arcsin.csv
│   │           │   │   │   │   ├── umath-validation-set-arcsinh.csv
│   │           │   │   │   │   ├── umath-validation-set-arctan.csv
│   │           │   │   │   │   ├── umath-validation-set-arctanh.csv
│   │           │   │   │   │   ├── umath-validation-set-cbrt.csv
│   │           │   │   │   │   ├── umath-validation-set-cos.csv
│   │           │   │   │   │   ├── umath-validation-set-cosh.csv
│   │           │   │   │   │   ├── umath-validation-set-exp.csv
│   │           │   │   │   │   ├── umath-validation-set-exp2.csv
│   │           │   │   │   │   ├── umath-validation-set-expm1.csv
│   │           │   │   │   │   ├── umath-validation-set-log.csv
│   │           │   │   │   │   ├── umath-validation-set-log10.csv
│   │           │   │   │   │   ├── umath-validation-set-log1p.csv
│   │           │   │   │   │   ├── umath-validation-set-log2.csv
│   │           │   │   │   │   ├── umath-validation-set-sin.csv
│   │           │   │   │   │   ├── umath-validation-set-sinh.csv
│   │           │   │   │   │   ├── umath-validation-set-tan.csv
│   │           │   │   │   │   └── umath-validation-set-tanh.csv
│   │           │   │   │   ├── examples/
│   │           │   │   │   │   ├── cython/
│   │           │   │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   │   └── setup.cpython-311.pyc
│   │           │   │   │   │   │   ├── checks.pyx
│   │           │   │   │   │   │   └── setup.py
│   │           │   │   │   │   └── limited_api/
│   │           │   │   │   │       ├── __pycache__/
│   │           │   │   │   │       │   └── setup.cpython-311.pyc
│   │           │   │   │   │       ├── limited_api1.c
│   │           │   │   │   │       ├── limited_api2.pyx
│   │           │   │   │   │       ├── limited_api_latest.c
│   │           │   │   │   │       ├── meson.build
│   │           │   │   │   │       └── setup.py
│   │           │   │   │   ├── test__exceptions.py
│   │           │   │   │   ├── test_abc.py
│   │           │   │   │   ├── test_api.py
│   │           │   │   │   ├── test_argparse.py
│   │           │   │   │   ├── test_array_api_info.py
│   │           │   │   │   ├── test_array_coercion.py
│   │           │   │   │   ├── test_array_interface.py
│   │           │   │   │   ├── test_arraymethod.py
│   │           │   │   │   ├── test_arrayobject.py
│   │           │   │   │   ├── test_arrayprint.py
│   │           │   │   │   ├── test_casting_floatingpoint_errors.py
│   │           │   │   │   ├── test_casting_unittests.py
│   │           │   │   │   ├── test_conversion_utils.py
│   │           │   │   │   ├── test_cpu_dispatcher.py
│   │           │   │   │   ├── test_cpu_features.py
│   │           │   │   │   ├── test_custom_dtypes.py
│   │           │   │   │   ├── test_cython.py
│   │           │   │   │   ├── test_datetime.py
│   │           │   │   │   ├── test_defchararray.py
│   │           │   │   │   ├── test_deprecations.py
│   │           │   │   │   ├── test_dlpack.py
│   │           │   │   │   ├── test_dtype.py
│   │           │   │   │   ├── test_einsum.py
│   │           │   │   │   ├── test_errstate.py
│   │           │   │   │   ├── test_extint128.py
│   │           │   │   │   ├── test_function_base.py
│   │           │   │   │   ├── test_getlimits.py
│   │           │   │   │   ├── test_half.py
│   │           │   │   │   ├── test_hashtable.py
│   │           │   │   │   ├── test_indexerrors.py
│   │           │   │   │   ├── test_indexing.py
│   │           │   │   │   ├── test_item_selection.py
│   │           │   │   │   ├── test_limited_api.py
│   │           │   │   │   ├── test_longdouble.py
│   │           │   │   │   ├── test_machar.py
│   │           │   │   │   ├── test_mem_overlap.py
│   │           │   │   │   ├── test_mem_policy.py
│   │           │   │   │   ├── test_memmap.py
│   │           │   │   │   ├── test_multiarray.py
│   │           │   │   │   ├── test_multithreading.py
│   │           │   │   │   ├── test_nditer.py
│   │           │   │   │   ├── test_nep50_promotions.py
│   │           │   │   │   ├── test_numeric.py
│   │           │   │   │   ├── test_numerictypes.py
│   │           │   │   │   ├── test_overrides.py
│   │           │   │   │   ├── test_print.py
│   │           │   │   │   ├── test_protocols.py
│   │           │   │   │   ├── test_records.py
│   │           │   │   │   ├── test_regression.py
│   │           │   │   │   ├── test_scalar_ctors.py
│   │           │   │   │   ├── test_scalar_methods.py
│   │           │   │   │   ├── test_scalarbuffer.py
│   │           │   │   │   ├── test_scalarinherit.py
│   │           │   │   │   ├── test_scalarmath.py
│   │           │   │   │   ├── test_scalarprint.py
│   │           │   │   │   ├── test_shape_base.py
│   │           │   │   │   ├── test_simd.py
│   │           │   │   │   ├── test_simd_module.py
│   │           │   │   │   ├── test_stringdtype.py
│   │           │   │   │   ├── test_strings.py
│   │           │   │   │   ├── test_ufunc.py
│   │           │   │   │   ├── test_umath.py
│   │           │   │   │   ├── test_umath_accuracy.py
│   │           │   │   │   ├── test_umath_complex.py
│   │           │   │   │   └── test_unicode.py
│   │           │   │   ├── umath.py
│   │           │   │   └── umath.pyi
│   │           │   ├── _distributor_init.py
│   │           │   ├── _distributor_init.pyi
│   │           │   ├── _expired_attrs_2_0.py
│   │           │   ├── _expired_attrs_2_0.pyi
│   │           │   ├── _globals.py
│   │           │   ├── _globals.pyi
│   │           │   ├── _pyinstaller/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── hook-numpy.cpython-311.pyc
│   │           │   │   ├── hook-numpy.py
│   │           │   │   ├── hook-numpy.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── pyinstaller-smoke.cpython-311.pyc
│   │           │   │       │   └── test_pyinstaller.cpython-311.pyc
│   │           │   │       ├── pyinstaller-smoke.py
│   │           │   │       └── test_pyinstaller.py
│   │           │   ├── _pytesttester.py
│   │           │   ├── _pytesttester.pyi
│   │           │   ├── _typing/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _add_docstring.cpython-311.pyc
│   │           │   │   │   ├── _array_like.cpython-311.pyc
│   │           │   │   │   ├── _char_codes.cpython-311.pyc
│   │           │   │   │   ├── _dtype_like.cpython-311.pyc
│   │           │   │   │   ├── _extended_precision.cpython-311.pyc
│   │           │   │   │   ├── _nbit.cpython-311.pyc
│   │           │   │   │   ├── _nbit_base.cpython-311.pyc
│   │           │   │   │   ├── _nested_sequence.cpython-311.pyc
│   │           │   │   │   ├── _scalars.cpython-311.pyc
│   │           │   │   │   ├── _shape.cpython-311.pyc
│   │           │   │   │   └── _ufunc.cpython-311.pyc
│   │           │   │   ├── _add_docstring.py
│   │           │   │   ├── _array_like.py
│   │           │   │   ├── _callable.pyi
│   │           │   │   ├── _char_codes.py
│   │           │   │   ├── _dtype_like.py
│   │           │   │   ├── _extended_precision.py
│   │           │   │   ├── _nbit.py
│   │           │   │   ├── _nbit_base.py
│   │           │   │   ├── _nbit_base.pyi
│   │           │   │   ├── _nested_sequence.py
│   │           │   │   ├── _scalars.py
│   │           │   │   ├── _shape.py
│   │           │   │   ├── _ufunc.py
│   │           │   │   └── _ufunc.pyi
│   │           │   ├── _utils/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _convertions.cpython-311.pyc
│   │           │   │   │   ├── _inspect.cpython-311.pyc
│   │           │   │   │   └── _pep440.cpython-311.pyc
│   │           │   │   ├── _convertions.py
│   │           │   │   ├── _convertions.pyi
│   │           │   │   ├── _inspect.py
│   │           │   │   ├── _inspect.pyi
│   │           │   │   ├── _pep440.py
│   │           │   │   └── _pep440.pyi
│   │           │   ├── char/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── conftest.py
│   │           │   ├── core/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _dtype.cpython-311.pyc
│   │           │   │   │   ├── _dtype_ctypes.cpython-311.pyc
│   │           │   │   │   ├── _internal.cpython-311.pyc
│   │           │   │   │   ├── _multiarray_umath.cpython-311.pyc
│   │           │   │   │   ├── _utils.cpython-311.pyc
│   │           │   │   │   ├── arrayprint.cpython-311.pyc
│   │           │   │   │   ├── defchararray.cpython-311.pyc
│   │           │   │   │   ├── einsumfunc.cpython-311.pyc
│   │           │   │   │   ├── fromnumeric.cpython-311.pyc
│   │           │   │   │   ├── function_base.cpython-311.pyc
│   │           │   │   │   ├── getlimits.cpython-311.pyc
│   │           │   │   │   ├── multiarray.cpython-311.pyc
│   │           │   │   │   ├── numeric.cpython-311.pyc
│   │           │   │   │   ├── numerictypes.cpython-311.pyc
│   │           │   │   │   ├── overrides.cpython-311.pyc
│   │           │   │   │   ├── records.cpython-311.pyc
│   │           │   │   │   ├── shape_base.cpython-311.pyc
│   │           │   │   │   └── umath.cpython-311.pyc
│   │           │   │   ├── _dtype.py
│   │           │   │   ├── _dtype.pyi
│   │           │   │   ├── _dtype_ctypes.py
│   │           │   │   ├── _dtype_ctypes.pyi
│   │           │   │   ├── _internal.py
│   │           │   │   ├── _multiarray_umath.py
│   │           │   │   ├── _utils.py
│   │           │   │   ├── arrayprint.py
│   │           │   │   ├── defchararray.py
│   │           │   │   ├── einsumfunc.py
│   │           │   │   ├── fromnumeric.py
│   │           │   │   ├── function_base.py
│   │           │   │   ├── getlimits.py
│   │           │   │   ├── multiarray.py
│   │           │   │   ├── numeric.py
│   │           │   │   ├── numerictypes.py
│   │           │   │   ├── overrides.py
│   │           │   │   ├── overrides.pyi
│   │           │   │   ├── records.py
│   │           │   │   ├── shape_base.py
│   │           │   │   └── umath.py
│   │           │   ├── ctypeslib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── _ctypeslib.cpython-311.pyc
│   │           │   │   ├── _ctypeslib.py
│   │           │   │   └── _ctypeslib.pyi
│   │           │   ├── distutils/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _shell_utils.cpython-311.pyc
│   │           │   │   │   ├── armccompiler.cpython-311.pyc
│   │           │   │   │   ├── ccompiler.cpython-311.pyc
│   │           │   │   │   ├── ccompiler_opt.cpython-311.pyc
│   │           │   │   │   ├── conv_template.cpython-311.pyc
│   │           │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   ├── cpuinfo.cpython-311.pyc
│   │           │   │   │   ├── exec_command.cpython-311.pyc
│   │           │   │   │   ├── extension.cpython-311.pyc
│   │           │   │   │   ├── from_template.cpython-311.pyc
│   │           │   │   │   ├── fujitsuccompiler.cpython-311.pyc
│   │           │   │   │   ├── intelccompiler.cpython-311.pyc
│   │           │   │   │   ├── lib2def.cpython-311.pyc
│   │           │   │   │   ├── line_endings.cpython-311.pyc
│   │           │   │   │   ├── log.cpython-311.pyc
│   │           │   │   │   ├── mingw32ccompiler.cpython-311.pyc
│   │           │   │   │   ├── misc_util.cpython-311.pyc
│   │           │   │   │   ├── msvc9compiler.cpython-311.pyc
│   │           │   │   │   ├── msvccompiler.cpython-311.pyc
│   │           │   │   │   ├── npy_pkg_config.cpython-311.pyc
│   │           │   │   │   ├── numpy_distribution.cpython-311.pyc
│   │           │   │   │   ├── pathccompiler.cpython-311.pyc
│   │           │   │   │   ├── system_info.cpython-311.pyc
│   │           │   │   │   └── unixccompiler.cpython-311.pyc
│   │           │   │   ├── _shell_utils.py
│   │           │   │   ├── armccompiler.py
│   │           │   │   ├── ccompiler.py
│   │           │   │   ├── ccompiler_opt.py
│   │           │   │   ├── checks/
│   │           │   │   │   ├── cpu_asimd.c
│   │           │   │   │   ├── cpu_asimddp.c
│   │           │   │   │   ├── cpu_asimdfhm.c
│   │           │   │   │   ├── cpu_asimdhp.c
│   │           │   │   │   ├── cpu_avx.c
│   │           │   │   │   ├── cpu_avx2.c
│   │           │   │   │   ├── cpu_avx512_clx.c
│   │           │   │   │   ├── cpu_avx512_cnl.c
│   │           │   │   │   ├── cpu_avx512_icl.c
│   │           │   │   │   ├── cpu_avx512_knl.c
│   │           │   │   │   ├── cpu_avx512_knm.c
│   │           │   │   │   ├── cpu_avx512_skx.c
│   │           │   │   │   ├── cpu_avx512_spr.c
│   │           │   │   │   ├── cpu_avx512cd.c
│   │           │   │   │   ├── cpu_avx512f.c
│   │           │   │   │   ├── cpu_f16c.c
│   │           │   │   │   ├── cpu_fma3.c
│   │           │   │   │   ├── cpu_fma4.c
│   │           │   │   │   ├── cpu_lsx.c
│   │           │   │   │   ├── cpu_neon.c
│   │           │   │   │   ├── cpu_neon_fp16.c
│   │           │   │   │   ├── cpu_neon_vfpv4.c
│   │           │   │   │   ├── cpu_popcnt.c
│   │           │   │   │   ├── cpu_rvv.c
│   │           │   │   │   ├── cpu_sse.c
│   │           │   │   │   ├── cpu_sse2.c
│   │           │   │   │   ├── cpu_sse3.c
│   │           │   │   │   ├── cpu_sse41.c
│   │           │   │   │   ├── cpu_sse42.c
│   │           │   │   │   ├── cpu_ssse3.c
│   │           │   │   │   ├── cpu_sve.c
│   │           │   │   │   ├── cpu_vsx.c
│   │           │   │   │   ├── cpu_vsx2.c
│   │           │   │   │   ├── cpu_vsx3.c
│   │           │   │   │   ├── cpu_vsx4.c
│   │           │   │   │   ├── cpu_vx.c
│   │           │   │   │   ├── cpu_vxe.c
│   │           │   │   │   ├── cpu_vxe2.c
│   │           │   │   │   ├── cpu_xop.c
│   │           │   │   │   ├── extra_avx512bw_mask.c
│   │           │   │   │   ├── extra_avx512dq_mask.c
│   │           │   │   │   ├── extra_avx512f_reduce.c
│   │           │   │   │   ├── extra_vsx3_half_double.c
│   │           │   │   │   ├── extra_vsx4_mma.c
│   │           │   │   │   ├── extra_vsx_asm.c
│   │           │   │   │   └── test_flags.c
│   │           │   │   ├── command/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── autodist.cpython-311.pyc
│   │           │   │   │   │   ├── bdist_rpm.cpython-311.pyc
│   │           │   │   │   │   ├── build.cpython-311.pyc
│   │           │   │   │   │   ├── build_clib.cpython-311.pyc
│   │           │   │   │   │   ├── build_ext.cpython-311.pyc
│   │           │   │   │   │   ├── build_py.cpython-311.pyc
│   │           │   │   │   │   ├── build_scripts.cpython-311.pyc
│   │           │   │   │   │   ├── build_src.cpython-311.pyc
│   │           │   │   │   │   ├── config.cpython-311.pyc
│   │           │   │   │   │   ├── config_compiler.cpython-311.pyc
│   │           │   │   │   │   ├── develop.cpython-311.pyc
│   │           │   │   │   │   ├── egg_info.cpython-311.pyc
│   │           │   │   │   │   ├── install.cpython-311.pyc
│   │           │   │   │   │   ├── install_clib.cpython-311.pyc
│   │           │   │   │   │   ├── install_data.cpython-311.pyc
│   │           │   │   │   │   ├── install_headers.cpython-311.pyc
│   │           │   │   │   │   └── sdist.cpython-311.pyc
│   │           │   │   │   ├── autodist.py
│   │           │   │   │   ├── bdist_rpm.py
│   │           │   │   │   ├── build.py
│   │           │   │   │   ├── build_clib.py
│   │           │   │   │   ├── build_ext.py
│   │           │   │   │   ├── build_py.py
│   │           │   │   │   ├── build_scripts.py
│   │           │   │   │   ├── build_src.py
│   │           │   │   │   ├── config.py
│   │           │   │   │   ├── config_compiler.py
│   │           │   │   │   ├── develop.py
│   │           │   │   │   ├── egg_info.py
│   │           │   │   │   ├── install.py
│   │           │   │   │   ├── install_clib.py
│   │           │   │   │   ├── install_data.py
│   │           │   │   │   ├── install_headers.py
│   │           │   │   │   └── sdist.py
│   │           │   │   ├── conv_template.py
│   │           │   │   ├── core.py
│   │           │   │   ├── cpuinfo.py
│   │           │   │   ├── exec_command.py
│   │           │   │   ├── extension.py
│   │           │   │   ├── fcompiler/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── absoft.cpython-311.pyc
│   │           │   │   │   │   ├── arm.cpython-311.pyc
│   │           │   │   │   │   ├── compaq.cpython-311.pyc
│   │           │   │   │   │   ├── environment.cpython-311.pyc
│   │           │   │   │   │   ├── fujitsu.cpython-311.pyc
│   │           │   │   │   │   ├── g95.cpython-311.pyc
│   │           │   │   │   │   ├── gnu.cpython-311.pyc
│   │           │   │   │   │   ├── hpux.cpython-311.pyc
│   │           │   │   │   │   ├── ibm.cpython-311.pyc
│   │           │   │   │   │   ├── intel.cpython-311.pyc
│   │           │   │   │   │   ├── lahey.cpython-311.pyc
│   │           │   │   │   │   ├── mips.cpython-311.pyc
│   │           │   │   │   │   ├── nag.cpython-311.pyc
│   │           │   │   │   │   ├── none.cpython-311.pyc
│   │           │   │   │   │   ├── nv.cpython-311.pyc
│   │           │   │   │   │   ├── pathf95.cpython-311.pyc
│   │           │   │   │   │   ├── pg.cpython-311.pyc
│   │           │   │   │   │   ├── sun.cpython-311.pyc
│   │           │   │   │   │   └── vast.cpython-311.pyc
│   │           │   │   │   ├── absoft.py
│   │           │   │   │   ├── arm.py
│   │           │   │   │   ├── compaq.py
│   │           │   │   │   ├── environment.py
│   │           │   │   │   ├── fujitsu.py
│   │           │   │   │   ├── g95.py
│   │           │   │   │   ├── gnu.py
│   │           │   │   │   ├── hpux.py
│   │           │   │   │   ├── ibm.py
│   │           │   │   │   ├── intel.py
│   │           │   │   │   ├── lahey.py
│   │           │   │   │   ├── mips.py
│   │           │   │   │   ├── nag.py
│   │           │   │   │   ├── none.py
│   │           │   │   │   ├── nv.py
│   │           │   │   │   ├── pathf95.py
│   │           │   │   │   ├── pg.py
│   │           │   │   │   ├── sun.py
│   │           │   │   │   └── vast.py
│   │           │   │   ├── from_template.py
│   │           │   │   ├── fujitsuccompiler.py
│   │           │   │   ├── intelccompiler.py
│   │           │   │   ├── lib2def.py
│   │           │   │   ├── line_endings.py
│   │           │   │   ├── log.py
│   │           │   │   ├── mingw/
│   │           │   │   │   └── gfortran_vs2003_hack.c
│   │           │   │   ├── mingw32ccompiler.py
│   │           │   │   ├── misc_util.py
│   │           │   │   ├── msvc9compiler.py
│   │           │   │   ├── msvccompiler.py
│   │           │   │   ├── npy_pkg_config.py
│   │           │   │   ├── numpy_distribution.py
│   │           │   │   ├── pathccompiler.py
│   │           │   │   ├── system_info.py
│   │           │   │   ├── tests/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── test_build_ext.cpython-311.pyc
│   │           │   │   │   │   ├── test_ccompiler_opt.cpython-311.pyc
│   │           │   │   │   │   ├── test_ccompiler_opt_conf.cpython-311.pyc
│   │           │   │   │   │   ├── test_exec_command.cpython-311.pyc
│   │           │   │   │   │   ├── test_fcompiler.cpython-311.pyc
│   │           │   │   │   │   ├── test_fcompiler_gnu.cpython-311.pyc
│   │           │   │   │   │   ├── test_fcompiler_intel.cpython-311.pyc
│   │           │   │   │   │   ├── test_fcompiler_nagfor.cpython-311.pyc
│   │           │   │   │   │   ├── test_from_template.cpython-311.pyc
│   │           │   │   │   │   ├── test_log.cpython-311.pyc
│   │           │   │   │   │   ├── test_mingw32ccompiler.cpython-311.pyc
│   │           │   │   │   │   ├── test_misc_util.cpython-311.pyc
│   │           │   │   │   │   ├── test_npy_pkg_config.cpython-311.pyc
│   │           │   │   │   │   ├── test_shell_utils.cpython-311.pyc
│   │           │   │   │   │   ├── test_system_info.cpython-311.pyc
│   │           │   │   │   │   └── utilities.cpython-311.pyc
│   │           │   │   │   ├── test_build_ext.py
│   │           │   │   │   ├── test_ccompiler_opt.py
│   │           │   │   │   ├── test_ccompiler_opt_conf.py
│   │           │   │   │   ├── test_exec_command.py
│   │           │   │   │   ├── test_fcompiler.py
│   │           │   │   │   ├── test_fcompiler_gnu.py
│   │           │   │   │   ├── test_fcompiler_intel.py
│   │           │   │   │   ├── test_fcompiler_nagfor.py
│   │           │   │   │   ├── test_from_template.py
│   │           │   │   │   ├── test_log.py
│   │           │   │   │   ├── test_mingw32ccompiler.py
│   │           │   │   │   ├── test_misc_util.py
│   │           │   │   │   ├── test_npy_pkg_config.py
│   │           │   │   │   ├── test_shell_utils.py
│   │           │   │   │   ├── test_system_info.py
│   │           │   │   │   └── utilities.py
│   │           │   │   └── unixccompiler.py
│   │           │   ├── doc/
│   │           │   │   ├── __pycache__/
│   │           │   │   │   └── ufuncs.cpython-311.pyc
│   │           │   │   └── ufuncs.py
│   │           │   ├── dtypes.py
│   │           │   ├── dtypes.pyi
│   │           │   ├── exceptions.py
│   │           │   ├── exceptions.pyi
│   │           │   ├── f2py
│   │           │   ├── f2py/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __main__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   ├── __version__.cpython-311.pyc
│   │           │   │   │   ├── _isocbind.cpython-311.pyc
│   │           │   │   │   ├── _src_pyf.cpython-311.pyc
│   │           │   │   │   ├── auxfuncs.cpython-311.pyc
│   │           │   │   │   ├── capi_maps.cpython-311.pyc
│   │           │   │   │   ├── cb_rules.cpython-311.pyc
│   │           │   │   │   ├── cfuncs.cpython-311.pyc
│   │           │   │   │   ├── common_rules.cpython-311.pyc
│   │           │   │   │   ├── crackfortran.cpython-311.pyc
│   │           │   │   │   ├── diagnose.cpython-311.pyc
│   │           │   │   │   ├── f2py2e.cpython-311.pyc
│   │           │   │   │   ├── f90mod_rules.cpython-311.pyc
│   │           │   │   │   ├── func2subr.cpython-311.pyc
│   │           │   │   │   ├── rules.cpython-311.pyc
│   │           │   │   │   ├── symbolic.cpython-311.pyc
│   │           │   │   │   └── use_rules.cpython-311.pyc
│   │           │   │   ├── __version__.py
│   │           │   │   ├── __version__.pyi
│   │           │   │   ├── _backends/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __init__.pyi
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _backend.cpython-311.pyc
│   │           │   │   │   │   ├── _distutils.cpython-311.pyc
│   │           │   │   │   │   └── _meson.cpython-311.pyc
│   │           │   │   │   ├── _backend.py
│   │           │   │   │   ├── _backend.pyi
│   │           │   │   │   ├── _distutils.py
│   │           │   │   │   ├── _distutils.pyi
│   │           │   │   │   ├── _meson.py
│   │           │   │   │   ├── _meson.pyi
│   │           │   │   │   └── meson.build.template
│   │           │   │   ├── _isocbind.py
│   │           │   │   ├── _isocbind.pyi
│   │           │   │   ├── _src_pyf.py
│   │           │   │   ├── _src_pyf.pyi
│   │           │   │   ├── auxfuncs.py
│   │           │   │   ├── auxfuncs.pyi
│   │           │   │   ├── capi_maps.py
│   │           │   │   ├── capi_maps.pyi
│   │           │   │   ├── cb_rules.py
│   │           │   │   ├── cb_rules.pyi
│   │           │   │   ├── cfuncs.py
│   │           │   │   ├── cfuncs.pyi
│   │           │   │   ├── common_rules.py
│   │           │   │   ├── common_rules.pyi
│   │           │   │   ├── crackfortran.py
│   │           │   │   ├── crackfortran.pyi
│   │           │   │   ├── diagnose.py
│   │           │   │   ├── diagnose.pyi
│   │           │   │   ├── f2py2e.py
│   │           │   │   ├── f2py2e.pyi
│   │           │   │   ├── f90mod_rules.py
│   │           │   │   ├── f90mod_rules.pyi
│   │           │   │   ├── func2subr.py
│   │           │   │   ├── func2subr.pyi
│   │           │   │   ├── rules.py
│   │           │   │   ├── rules.pyi
│   │           │   │   ├── setup.cfg
│   │           │   │   ├── src/
│   │           │   │   │   ├── fortranobject.c
│   │           │   │   │   └── fortranobject.h
│   │           │   │   ├── symbolic.py
│   │           │   │   ├── symbolic.pyi
│   │           │   │   ├── tests/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── test_abstract_interface.cpython-311.pyc
│   │           │   │   │   │   ├── test_array_from_pyobj.cpython-311.pyc
│   │           │   │   │   │   ├── test_assumed_shape.cpython-311.pyc
│   │           │   │   │   │   ├── test_block_docstring.cpython-311.pyc
│   │           │   │   │   │   ├── test_callback.cpython-311.pyc
│   │           │   │   │   │   ├── test_character.cpython-311.pyc
│   │           │   │   │   │   ├── test_common.cpython-311.pyc
│   │           │   │   │   │   ├── test_crackfortran.cpython-311.pyc
│   │           │   │   │   │   ├── test_data.cpython-311.pyc
│   │           │   │   │   │   ├── test_docs.cpython-311.pyc
│   │           │   │   │   │   ├── test_f2cmap.cpython-311.pyc
│   │           │   │   │   │   ├── test_f2py2e.cpython-311.pyc
│   │           │   │   │   │   ├── test_isoc.cpython-311.pyc
│   │           │   │   │   │   ├── test_kind.cpython-311.pyc
│   │           │   │   │   │   ├── test_mixed.cpython-311.pyc
│   │           │   │   │   │   ├── test_modules.cpython-311.pyc
│   │           │   │   │   │   ├── test_parameter.cpython-311.pyc
│   │           │   │   │   │   ├── test_pyf_src.cpython-311.pyc
│   │           │   │   │   │   ├── test_quoted_character.cpython-311.pyc
│   │           │   │   │   │   ├── test_regression.cpython-311.pyc
│   │           │   │   │   │   ├── test_return_character.cpython-311.pyc
│   │           │   │   │   │   ├── test_return_complex.cpython-311.pyc
│   │           │   │   │   │   ├── test_return_integer.cpython-311.pyc
│   │           │   │   │   │   ├── test_return_logical.cpython-311.pyc
│   │           │   │   │   │   ├── test_return_real.cpython-311.pyc
│   │           │   │   │   │   ├── test_routines.cpython-311.pyc
│   │           │   │   │   │   ├── test_semicolon_split.cpython-311.pyc
│   │           │   │   │   │   ├── test_size.cpython-311.pyc
│   │           │   │   │   │   ├── test_string.cpython-311.pyc
│   │           │   │   │   │   ├── test_symbolic.cpython-311.pyc
│   │           │   │   │   │   ├── test_value_attrspec.cpython-311.pyc
│   │           │   │   │   │   └── util.cpython-311.pyc
│   │           │   │   │   ├── src/
│   │           │   │   │   │   ├── abstract_interface/
│   │           │   │   │   │   │   ├── foo.f90
│   │           │   │   │   │   │   └── gh18403_mod.f90
│   │           │   │   │   │   ├── array_from_pyobj/
│   │           │   │   │   │   │   └── wrapmodule.c
│   │           │   │   │   │   ├── assumed_shape/
│   │           │   │   │   │   │   ├── foo_free.f90
│   │           │   │   │   │   │   ├── foo_mod.f90
│   │           │   │   │   │   │   ├── foo_use.f90
│   │           │   │   │   │   │   └── precision.f90
│   │           │   │   │   │   ├── block_docstring/
│   │           │   │   │   │   │   └── foo.f
│   │           │   │   │   │   ├── callback/
│   │           │   │   │   │   │   ├── foo.f
│   │           │   │   │   │   │   ├── gh17797.f90
│   │           │   │   │   │   │   ├── gh18335.f90
│   │           │   │   │   │   │   ├── gh25211.f
│   │           │   │   │   │   │   ├── gh25211.pyf
│   │           │   │   │   │   │   └── gh26681.f90
│   │           │   │   │   │   ├── cli/
│   │           │   │   │   │   │   ├── gh_22819.pyf
│   │           │   │   │   │   │   ├── hi77.f
│   │           │   │   │   │   │   └── hiworld.f90
│   │           │   │   │   │   ├── common/
│   │           │   │   │   │   │   ├── block.f
│   │           │   │   │   │   │   └── gh19161.f90
│   │           │   │   │   │   ├── crackfortran/
│   │           │   │   │   │   │   ├── accesstype.f90
│   │           │   │   │   │   │   ├── common_with_division.f
│   │           │   │   │   │   │   ├── data_common.f
│   │           │   │   │   │   │   ├── data_multiplier.f
│   │           │   │   │   │   │   ├── data_stmts.f90
│   │           │   │   │   │   │   ├── data_with_comments.f
│   │           │   │   │   │   │   ├── foo_deps.f90
│   │           │   │   │   │   │   ├── gh15035.f
│   │           │   │   │   │   │   ├── gh17859.f
│   │           │   │   │   │   │   ├── gh22648.pyf
│   │           │   │   │   │   │   ├── gh23533.f
│   │           │   │   │   │   │   ├── gh23598.f90
│   │           │   │   │   │   │   ├── gh23598Warn.f90
│   │           │   │   │   │   │   ├── gh23879.f90
│   │           │   │   │   │   │   ├── gh27697.f90
│   │           │   │   │   │   │   ├── gh2848.f90
│   │           │   │   │   │   │   ├── operators.f90
│   │           │   │   │   │   │   ├── privatemod.f90
│   │           │   │   │   │   │   ├── publicmod.f90
│   │           │   │   │   │   │   ├── pubprivmod.f90
│   │           │   │   │   │   │   └── unicode_comment.f90
│   │           │   │   │   │   ├── f2cmap
│   │           │   │   │   │   ├── f2cmap/
│   │           │   │   │   │   │   ├── .f2py_f2cmap
│   │           │   │   │   │   │   └── isoFortranEnvMap.f90
│   │           │   │   │   │   ├── isocintrin/
│   │           │   │   │   │   │   └── isoCtests.f90
│   │           │   │   │   │   ├── kind/
│   │           │   │   │   │   │   └── foo.f90
│   │           │   │   │   │   ├── mixed/
│   │           │   │   │   │   │   ├── foo.f
│   │           │   │   │   │   │   ├── foo_fixed.f90
│   │           │   │   │   │   │   └── foo_free.f90
│   │           │   │   │   │   ├── modules/
│   │           │   │   │   │   │   ├── gh25337/
│   │           │   │   │   │   │   │   ├── data.f90
│   │           │   │   │   │   │   │   └── use_data.f90
│   │           │   │   │   │   │   ├── gh26920/
│   │           │   │   │   │   │   │   ├── two_mods_with_no_public_entities.f90
│   │           │   │   │   │   │   │   └── two_mods_with_one_public_routine.f90
│   │           │   │   │   │   │   ├── module_data_docstring.f90
│   │           │   │   │   │   │   └── use_modules.f90
│   │           │   │   │   │   ├── negative_bounds/
│   │           │   │   │   │   │   └── issue_20853.f90
│   │           │   │   │   │   ├── parameter/
│   │           │   │   │   │   │   ├── constant_array.f90
│   │           │   │   │   │   │   ├── constant_both.f90
│   │           │   │   │   │   │   ├── constant_compound.f90
│   │           │   │   │   │   │   ├── constant_integer.f90
│   │           │   │   │   │   │   ├── constant_non_compound.f90
│   │           │   │   │   │   │   └── constant_real.f90
│   │           │   │   │   │   ├── quoted_character/
│   │           │   │   │   │   │   └── foo.f
│   │           │   │   │   │   ├── regression/
│   │           │   │   │   │   │   ├── AB.inc
│   │           │   │   │   │   │   ├── assignOnlyModule.f90
│   │           │   │   │   │   │   ├── datonly.f90
│   │           │   │   │   │   │   ├── f77comments.f
│   │           │   │   │   │   │   ├── f77fixedform.f95
│   │           │   │   │   │   │   ├── f90continuation.f90
│   │           │   │   │   │   │   ├── incfile.f90
│   │           │   │   │   │   │   ├── inout.f90
│   │           │   │   │   │   │   ├── lower_f2py_fortran.f90
│   │           │   │   │   │   │   └── mod_derived_types.f90
│   │           │   │   │   │   ├── return_character/
│   │           │   │   │   │   │   ├── foo77.f
│   │           │   │   │   │   │   └── foo90.f90
│   │           │   │   │   │   ├── return_complex/
│   │           │   │   │   │   │   ├── foo77.f
│   │           │   │   │   │   │   └── foo90.f90
│   │           │   │   │   │   ├── return_integer/
│   │           │   │   │   │   │   ├── foo77.f
│   │           │   │   │   │   │   └── foo90.f90
│   │           │   │   │   │   ├── return_logical/
│   │           │   │   │   │   │   ├── foo77.f
│   │           │   │   │   │   │   └── foo90.f90
│   │           │   │   │   │   ├── return_real/
│   │           │   │   │   │   │   ├── foo77.f
│   │           │   │   │   │   │   └── foo90.f90
│   │           │   │   │   │   ├── routines/
│   │           │   │   │   │   │   ├── funcfortranname.f
│   │           │   │   │   │   │   ├── funcfortranname.pyf
│   │           │   │   │   │   │   ├── subrout.f
│   │           │   │   │   │   │   └── subrout.pyf
│   │           │   │   │   │   ├── size/
│   │           │   │   │   │   │   └── foo.f90
│   │           │   │   │   │   ├── string/
│   │           │   │   │   │   │   ├── char.f90
│   │           │   │   │   │   │   ├── fixed_string.f90
│   │           │   │   │   │   │   ├── gh24008.f
│   │           │   │   │   │   │   ├── gh24662.f90
│   │           │   │   │   │   │   ├── gh25286.f90
│   │           │   │   │   │   │   ├── gh25286.pyf
│   │           │   │   │   │   │   ├── gh25286_bc.pyf
│   │           │   │   │   │   │   ├── scalar_string.f90
│   │           │   │   │   │   │   └── string.f
│   │           │   │   │   │   └── value_attrspec/
│   │           │   │   │   │       └── gh21665.f90
│   │           │   │   │   ├── test_abstract_interface.py
│   │           │   │   │   ├── test_array_from_pyobj.py
│   │           │   │   │   ├── test_assumed_shape.py
│   │           │   │   │   ├── test_block_docstring.py
│   │           │   │   │   ├── test_callback.py
│   │           │   │   │   ├── test_character.py
│   │           │   │   │   ├── test_common.py
│   │           │   │   │   ├── test_crackfortran.py
│   │           │   │   │   ├── test_data.py
│   │           │   │   │   ├── test_docs.py
│   │           │   │   │   ├── test_f2cmap.py
│   │           │   │   │   ├── test_f2py2e.py
│   │           │   │   │   ├── test_isoc.py
│   │           │   │   │   ├── test_kind.py
│   │           │   │   │   ├── test_mixed.py
│   │           │   │   │   ├── test_modules.py
│   │           │   │   │   ├── test_parameter.py
│   │           │   │   │   ├── test_pyf_src.py
│   │           │   │   │   ├── test_quoted_character.py
│   │           │   │   │   ├── test_regression.py
│   │           │   │   │   ├── test_return_character.py
│   │           │   │   │   ├── test_return_complex.py
│   │           │   │   │   ├── test_return_integer.py
│   │           │   │   │   ├── test_return_logical.py
│   │           │   │   │   ├── test_return_real.py
│   │           │   │   │   ├── test_routines.py
│   │           │   │   │   ├── test_semicolon_split.py
│   │           │   │   │   ├── test_size.py
│   │           │   │   │   ├── test_string.py
│   │           │   │   │   ├── test_symbolic.py
│   │           │   │   │   ├── test_value_attrspec.py
│   │           │   │   │   └── util.py
│   │           │   │   ├── use_rules.py
│   │           │   │   └── use_rules.pyi
│   │           │   ├── fft/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _helper.cpython-311.pyc
│   │           │   │   │   ├── _pocketfft.cpython-311.pyc
│   │           │   │   │   └── helper.cpython-311.pyc
│   │           │   │   ├── _helper.py
│   │           │   │   ├── _helper.pyi
│   │           │   │   ├── _pocketfft.py
│   │           │   │   ├── _pocketfft.pyi
│   │           │   │   ├── _pocketfft_umath.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── helper.py
│   │           │   │   ├── helper.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── test_helper.cpython-311.pyc
│   │           │   │       │   └── test_pocketfft.cpython-311.pyc
│   │           │   │       ├── test_helper.py
│   │           │   │       └── test_pocketfft.py
│   │           │   ├── lib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _array_utils_impl.cpython-311.pyc
│   │           │   │   │   ├── _arraypad_impl.cpython-311.pyc
│   │           │   │   │   ├── _arraysetops_impl.cpython-311.pyc
│   │           │   │   │   ├── _arrayterator_impl.cpython-311.pyc
│   │           │   │   │   ├── _datasource.cpython-311.pyc
│   │           │   │   │   ├── _format_impl.cpython-311.pyc
│   │           │   │   │   ├── _function_base_impl.cpython-311.pyc
│   │           │   │   │   ├── _histograms_impl.cpython-311.pyc
│   │           │   │   │   ├── _index_tricks_impl.cpython-311.pyc
│   │           │   │   │   ├── _iotools.cpython-311.pyc
│   │           │   │   │   ├── _nanfunctions_impl.cpython-311.pyc
│   │           │   │   │   ├── _npyio_impl.cpython-311.pyc
│   │           │   │   │   ├── _polynomial_impl.cpython-311.pyc
│   │           │   │   │   ├── _scimath_impl.cpython-311.pyc
│   │           │   │   │   ├── _shape_base_impl.cpython-311.pyc
│   │           │   │   │   ├── _stride_tricks_impl.cpython-311.pyc
│   │           │   │   │   ├── _twodim_base_impl.cpython-311.pyc
│   │           │   │   │   ├── _type_check_impl.cpython-311.pyc
│   │           │   │   │   ├── _ufunclike_impl.cpython-311.pyc
│   │           │   │   │   ├── _user_array_impl.cpython-311.pyc
│   │           │   │   │   ├── _utils_impl.cpython-311.pyc
│   │           │   │   │   ├── _version.cpython-311.pyc
│   │           │   │   │   ├── array_utils.cpython-311.pyc
│   │           │   │   │   ├── format.cpython-311.pyc
│   │           │   │   │   ├── introspect.cpython-311.pyc
│   │           │   │   │   ├── mixins.cpython-311.pyc
│   │           │   │   │   ├── npyio.cpython-311.pyc
│   │           │   │   │   ├── recfunctions.cpython-311.pyc
│   │           │   │   │   ├── scimath.cpython-311.pyc
│   │           │   │   │   ├── stride_tricks.cpython-311.pyc
│   │           │   │   │   └── user_array.cpython-311.pyc
│   │           │   │   ├── _array_utils_impl.py
│   │           │   │   ├── _array_utils_impl.pyi
│   │           │   │   ├── _arraypad_impl.py
│   │           │   │   ├── _arraypad_impl.pyi
│   │           │   │   ├── _arraysetops_impl.py
│   │           │   │   ├── _arraysetops_impl.pyi
│   │           │   │   ├── _arrayterator_impl.py
│   │           │   │   ├── _arrayterator_impl.pyi
│   │           │   │   ├── _datasource.py
│   │           │   │   ├── _datasource.pyi
│   │           │   │   ├── _format_impl.py
│   │           │   │   ├── _format_impl.pyi
│   │           │   │   ├── _function_base_impl.py
│   │           │   │   ├── _function_base_impl.pyi
│   │           │   │   ├── _histograms_impl.py
│   │           │   │   ├── _histograms_impl.pyi
│   │           │   │   ├── _index_tricks_impl.py
│   │           │   │   ├── _index_tricks_impl.pyi
│   │           │   │   ├── _iotools.py
│   │           │   │   ├── _iotools.pyi
│   │           │   │   ├── _nanfunctions_impl.py
│   │           │   │   ├── _nanfunctions_impl.pyi
│   │           │   │   ├── _npyio_impl.py
│   │           │   │   ├── _npyio_impl.pyi
│   │           │   │   ├── _polynomial_impl.py
│   │           │   │   ├── _polynomial_impl.pyi
│   │           │   │   ├── _scimath_impl.py
│   │           │   │   ├── _scimath_impl.pyi
│   │           │   │   ├── _shape_base_impl.py
│   │           │   │   ├── _shape_base_impl.pyi
│   │           │   │   ├── _stride_tricks_impl.py
│   │           │   │   ├── _stride_tricks_impl.pyi
│   │           │   │   ├── _twodim_base_impl.py
│   │           │   │   ├── _twodim_base_impl.pyi
│   │           │   │   ├── _type_check_impl.py
│   │           │   │   ├── _type_check_impl.pyi
│   │           │   │   ├── _ufunclike_impl.py
│   │           │   │   ├── _ufunclike_impl.pyi
│   │           │   │   ├── _user_array_impl.py
│   │           │   │   ├── _user_array_impl.pyi
│   │           │   │   ├── _utils_impl.py
│   │           │   │   ├── _utils_impl.pyi
│   │           │   │   ├── _version.py
│   │           │   │   ├── _version.pyi
│   │           │   │   ├── array_utils.py
│   │           │   │   ├── array_utils.pyi
│   │           │   │   ├── format.py
│   │           │   │   ├── format.pyi
│   │           │   │   ├── introspect.py
│   │           │   │   ├── introspect.pyi
│   │           │   │   ├── mixins.py
│   │           │   │   ├── mixins.pyi
│   │           │   │   ├── npyio.py
│   │           │   │   ├── npyio.pyi
│   │           │   │   ├── recfunctions.py
│   │           │   │   ├── recfunctions.pyi
│   │           │   │   ├── scimath.py
│   │           │   │   ├── scimath.pyi
│   │           │   │   ├── stride_tricks.py
│   │           │   │   ├── stride_tricks.pyi
│   │           │   │   ├── tests/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── test__datasource.cpython-311.pyc
│   │           │   │   │   │   ├── test__iotools.cpython-311.pyc
│   │           │   │   │   │   ├── test__version.cpython-311.pyc
│   │           │   │   │   │   ├── test_array_utils.cpython-311.pyc
│   │           │   │   │   │   ├── test_arraypad.cpython-311.pyc
│   │           │   │   │   │   ├── test_arraysetops.cpython-311.pyc
│   │           │   │   │   │   ├── test_arrayterator.cpython-311.pyc
│   │           │   │   │   │   ├── test_format.cpython-311.pyc
│   │           │   │   │   │   ├── test_function_base.cpython-311.pyc
│   │           │   │   │   │   ├── test_histograms.cpython-311.pyc
│   │           │   │   │   │   ├── test_index_tricks.cpython-311.pyc
│   │           │   │   │   │   ├── test_io.cpython-311.pyc
│   │           │   │   │   │   ├── test_loadtxt.cpython-311.pyc
│   │           │   │   │   │   ├── test_mixins.cpython-311.pyc
│   │           │   │   │   │   ├── test_nanfunctions.cpython-311.pyc
│   │           │   │   │   │   ├── test_packbits.cpython-311.pyc
│   │           │   │   │   │   ├── test_polynomial.cpython-311.pyc
│   │           │   │   │   │   ├── test_recfunctions.cpython-311.pyc
│   │           │   │   │   │   ├── test_regression.cpython-311.pyc
│   │           │   │   │   │   ├── test_shape_base.cpython-311.pyc
│   │           │   │   │   │   ├── test_stride_tricks.cpython-311.pyc
│   │           │   │   │   │   ├── test_twodim_base.cpython-311.pyc
│   │           │   │   │   │   ├── test_type_check.cpython-311.pyc
│   │           │   │   │   │   ├── test_ufunclike.cpython-311.pyc
│   │           │   │   │   │   └── test_utils.cpython-311.pyc
│   │           │   │   │   ├── data/
│   │           │   │   │   │   ├── py2-np0-objarr.npy
│   │           │   │   │   │   ├── py2-objarr.npy
│   │           │   │   │   │   ├── py2-objarr.npz
│   │           │   │   │   │   ├── py3-objarr.npy
│   │           │   │   │   │   ├── py3-objarr.npz
│   │           │   │   │   │   ├── python3.npy
│   │           │   │   │   │   └── win64python2.npy
│   │           │   │   │   ├── test__datasource.py
│   │           │   │   │   ├── test__iotools.py
│   │           │   │   │   ├── test__version.py
│   │           │   │   │   ├── test_array_utils.py
│   │           │   │   │   ├── test_arraypad.py
│   │           │   │   │   ├── test_arraysetops.py
│   │           │   │   │   ├── test_arrayterator.py
│   │           │   │   │   ├── test_format.py
│   │           │   │   │   ├── test_function_base.py
│   │           │   │   │   ├── test_histograms.py
│   │           │   │   │   ├── test_index_tricks.py
│   │           │   │   │   ├── test_io.py
│   │           │   │   │   ├── test_loadtxt.py
│   │           │   │   │   ├── test_mixins.py
│   │           │   │   │   ├── test_nanfunctions.py
│   │           │   │   │   ├── test_packbits.py
│   │           │   │   │   ├── test_polynomial.py
│   │           │   │   │   ├── test_recfunctions.py
│   │           │   │   │   ├── test_regression.py
│   │           │   │   │   ├── test_shape_base.py
│   │           │   │   │   ├── test_stride_tricks.py
│   │           │   │   │   ├── test_twodim_base.py
│   │           │   │   │   ├── test_type_check.py
│   │           │   │   │   ├── test_ufunclike.py
│   │           │   │   │   └── test_utils.py
│   │           │   │   ├── user_array.py
│   │           │   │   └── user_array.pyi
│   │           │   ├── linalg/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _linalg.cpython-311.pyc
│   │           │   │   │   └── linalg.cpython-311.pyc
│   │           │   │   ├── _linalg.py
│   │           │   │   ├── _linalg.pyi
│   │           │   │   ├── _umath_linalg.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _umath_linalg.pyi
│   │           │   │   ├── lapack_lite.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── lapack_lite.pyi
│   │           │   │   ├── linalg.py
│   │           │   │   ├── linalg.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── test_deprecations.cpython-311.pyc
│   │           │   │       │   ├── test_linalg.cpython-311.pyc
│   │           │   │       │   └── test_regression.cpython-311.pyc
│   │           │   │       ├── test_deprecations.py
│   │           │   │       ├── test_linalg.py
│   │           │   │       └── test_regression.py
│   │           │   ├── ma/
│   │           │   │   ├── API_CHANGES.txt
│   │           │   │   ├── LICENSE
│   │           │   │   ├── README.rst
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   ├── extras.cpython-311.pyc
│   │           │   │   │   ├── mrecords.cpython-311.pyc
│   │           │   │   │   └── testutils.cpython-311.pyc
│   │           │   │   ├── core.py
│   │           │   │   ├── core.pyi
│   │           │   │   ├── extras.py
│   │           │   │   ├── extras.pyi
│   │           │   │   ├── mrecords.py
│   │           │   │   ├── mrecords.pyi
│   │           │   │   ├── tests/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── test_arrayobject.cpython-311.pyc
│   │           │   │   │   │   ├── test_core.cpython-311.pyc
│   │           │   │   │   │   ├── test_deprecations.cpython-311.pyc
│   │           │   │   │   │   ├── test_extras.cpython-311.pyc
│   │           │   │   │   │   ├── test_mrecords.cpython-311.pyc
│   │           │   │   │   │   ├── test_old_ma.cpython-311.pyc
│   │           │   │   │   │   ├── test_regression.cpython-311.pyc
│   │           │   │   │   │   └── test_subclassing.cpython-311.pyc
│   │           │   │   │   ├── test_arrayobject.py
│   │           │   │   │   ├── test_core.py
│   │           │   │   │   ├── test_deprecations.py
│   │           │   │   │   ├── test_extras.py
│   │           │   │   │   ├── test_mrecords.py
│   │           │   │   │   ├── test_old_ma.py
│   │           │   │   │   ├── test_regression.py
│   │           │   │   │   └── test_subclassing.py
│   │           │   │   └── testutils.py
│   │           │   ├── matlib.py
│   │           │   ├── matlib.pyi
│   │           │   ├── matrixlib/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── defmatrix.cpython-311.pyc
│   │           │   │   ├── defmatrix.py
│   │           │   │   ├── defmatrix.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── test_defmatrix.cpython-311.pyc
│   │           │   │       │   ├── test_interaction.cpython-311.pyc
│   │           │   │       │   ├── test_masked_matrix.cpython-311.pyc
│   │           │   │       │   ├── test_matrix_linalg.cpython-311.pyc
│   │           │   │       │   ├── test_multiarray.cpython-311.pyc
│   │           │   │       │   ├── test_numeric.cpython-311.pyc
│   │           │   │       │   └── test_regression.cpython-311.pyc
│   │           │   │       ├── test_defmatrix.py
│   │           │   │       ├── test_interaction.py
│   │           │   │       ├── test_masked_matrix.py
│   │           │   │       ├── test_matrix_linalg.py
│   │           │   │       ├── test_multiarray.py
│   │           │   │       ├── test_numeric.py
│   │           │   │       └── test_regression.py
│   │           │   ├── polynomial/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _polybase.cpython-311.pyc
│   │           │   │   │   ├── chebyshev.cpython-311.pyc
│   │           │   │   │   ├── hermite.cpython-311.pyc
│   │           │   │   │   ├── hermite_e.cpython-311.pyc
│   │           │   │   │   ├── laguerre.cpython-311.pyc
│   │           │   │   │   ├── legendre.cpython-311.pyc
│   │           │   │   │   ├── polynomial.cpython-311.pyc
│   │           │   │   │   └── polyutils.cpython-311.pyc
│   │           │   │   ├── _polybase.py
│   │           │   │   ├── _polybase.pyi
│   │           │   │   ├── _polytypes.pyi
│   │           │   │   ├── chebyshev.py
│   │           │   │   ├── chebyshev.pyi
│   │           │   │   ├── hermite.py
│   │           │   │   ├── hermite.pyi
│   │           │   │   ├── hermite_e.py
│   │           │   │   ├── hermite_e.pyi
│   │           │   │   ├── laguerre.py
│   │           │   │   ├── laguerre.pyi
│   │           │   │   ├── legendre.py
│   │           │   │   ├── legendre.pyi
│   │           │   │   ├── polynomial.py
│   │           │   │   ├── polynomial.pyi
│   │           │   │   ├── polyutils.py
│   │           │   │   ├── polyutils.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── test_chebyshev.cpython-311.pyc
│   │           │   │       │   ├── test_classes.cpython-311.pyc
│   │           │   │       │   ├── test_hermite.cpython-311.pyc
│   │           │   │       │   ├── test_hermite_e.cpython-311.pyc
│   │           │   │       │   ├── test_laguerre.cpython-311.pyc
│   │           │   │       │   ├── test_legendre.cpython-311.pyc
│   │           │   │       │   ├── test_polynomial.cpython-311.pyc
│   │           │   │       │   ├── test_polyutils.cpython-311.pyc
│   │           │   │       │   ├── test_printing.cpython-311.pyc
│   │           │   │       │   └── test_symbol.cpython-311.pyc
│   │           │   │       ├── test_chebyshev.py
│   │           │   │       ├── test_classes.py
│   │           │   │       ├── test_hermite.py
│   │           │   │       ├── test_hermite_e.py
│   │           │   │       ├── test_laguerre.py
│   │           │   │       ├── test_legendre.py
│   │           │   │       ├── test_polynomial.py
│   │           │   │       ├── test_polyutils.py
│   │           │   │       ├── test_printing.py
│   │           │   │       └── test_symbol.py
│   │           │   ├── py.typed
│   │           │   ├── random/
│   │           │   │   ├── LICENSE.md
│   │           │   │   ├── __init__.pxd
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── _pickle.cpython-311.pyc
│   │           │   │   ├── _bounded_integers.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _bounded_integers.pxd
│   │           │   │   ├── _bounded_integers.pyi
│   │           │   │   ├── _common.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _common.pxd
│   │           │   │   ├── _common.pyi
│   │           │   │   ├── _examples/
│   │           │   │   │   ├── cffi/
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── extending.cpython-311.pyc
│   │           │   │   │   │   │   └── parse.cpython-311.pyc
│   │           │   │   │   │   ├── extending.py
│   │           │   │   │   │   └── parse.py
│   │           │   │   │   ├── cython/
│   │           │   │   │   │   ├── extending.pyx
│   │           │   │   │   │   ├── extending_distributions.pyx
│   │           │   │   │   │   └── meson.build
│   │           │   │   │   └── numba/
│   │           │   │   │       ├── __pycache__/
│   │           │   │   │       │   ├── extending.cpython-311.pyc
│   │           │   │   │       │   └── extending_distributions.cpython-311.pyc
│   │           │   │   │       ├── extending.py
│   │           │   │   │       └── extending_distributions.py
│   │           │   │   ├── _generator.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _generator.pyi
│   │           │   │   ├── _mt19937.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _mt19937.pyi
│   │           │   │   ├── _pcg64.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _pcg64.pyi
│   │           │   │   ├── _philox.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _philox.pyi
│   │           │   │   ├── _pickle.py
│   │           │   │   ├── _pickle.pyi
│   │           │   │   ├── _sfc64.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── _sfc64.pyi
│   │           │   │   ├── bit_generator.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── bit_generator.pxd
│   │           │   │   ├── bit_generator.pyi
│   │           │   │   ├── c_distributions.pxd
│   │           │   │   ├── lib/
│   │           │   │   │   └── libnpyrandom.a
│   │           │   │   ├── mtrand.cpython-311-arm-linux-gnueabihf.so
│   │           │   │   ├── mtrand.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── test_direct.cpython-311.pyc
│   │           │   │       │   ├── test_extending.cpython-311.pyc
│   │           │   │       │   ├── test_generator_mt19937.cpython-311.pyc
│   │           │   │       │   ├── test_generator_mt19937_regressions.cpython-311.pyc
│   │           │   │       │   ├── test_random.cpython-311.pyc
│   │           │   │       │   ├── test_randomstate.cpython-311.pyc
│   │           │   │       │   ├── test_randomstate_regression.cpython-311.pyc
│   │           │   │       │   ├── test_regression.cpython-311.pyc
│   │           │   │       │   ├── test_seed_sequence.cpython-311.pyc
│   │           │   │       │   └── test_smoke.cpython-311.pyc
│   │           │   │       ├── data/
│   │           │   │       │   ├── __init__.py
│   │           │   │       │   ├── __pycache__/
│   │           │   │       │   │   └── __init__.cpython-311.pyc
│   │           │   │       │   ├── generator_pcg64_np121.pkl.gz
│   │           │   │       │   ├── generator_pcg64_np126.pkl.gz
│   │           │   │       │   ├── mt19937-testset-1.csv
│   │           │   │       │   ├── mt19937-testset-2.csv
│   │           │   │       │   ├── pcg64-testset-1.csv
│   │           │   │       │   ├── pcg64-testset-2.csv
│   │           │   │       │   ├── pcg64dxsm-testset-1.csv
│   │           │   │       │   ├── pcg64dxsm-testset-2.csv
│   │           │   │       │   ├── philox-testset-1.csv
│   │           │   │       │   ├── philox-testset-2.csv
│   │           │   │       │   ├── sfc64-testset-1.csv
│   │           │   │       │   ├── sfc64-testset-2.csv
│   │           │   │       │   └── sfc64_np126.pkl.gz
│   │           │   │       ├── test_direct.py
│   │           │   │       ├── test_extending.py
│   │           │   │       ├── test_generator_mt19937.py
│   │           │   │       ├── test_generator_mt19937_regressions.py
│   │           │   │       ├── test_random.py
│   │           │   │       ├── test_randomstate.py
│   │           │   │       ├── test_randomstate_regression.py
│   │           │   │       ├── test_regression.py
│   │           │   │       ├── test_seed_sequence.py
│   │           │   │       └── test_smoke.py
│   │           │   ├── rec/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── strings/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── testing/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __init__.pyi
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── overrides.cpython-311.pyc
│   │           │   │   │   └── print_coercion_tables.cpython-311.pyc
│   │           │   │   ├── _private/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __init__.pyi
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── extbuild.cpython-311.pyc
│   │           │   │   │   │   └── utils.cpython-311.pyc
│   │           │   │   │   ├── extbuild.py
│   │           │   │   │   ├── extbuild.pyi
│   │           │   │   │   ├── utils.py
│   │           │   │   │   └── utils.pyi
│   │           │   │   ├── overrides.py
│   │           │   │   ├── overrides.pyi
│   │           │   │   ├── print_coercion_tables.py
│   │           │   │   ├── print_coercion_tables.pyi
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   └── test_utils.cpython-311.pyc
│   │           │   │       └── test_utils.py
│   │           │   ├── tests/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── test__all__.cpython-311.pyc
│   │           │   │   │   ├── test_configtool.cpython-311.pyc
│   │           │   │   │   ├── test_ctypeslib.cpython-311.pyc
│   │           │   │   │   ├── test_lazyloading.cpython-311.pyc
│   │           │   │   │   ├── test_matlib.cpython-311.pyc
│   │           │   │   │   ├── test_numpy_config.cpython-311.pyc
│   │           │   │   │   ├── test_numpy_version.cpython-311.pyc
│   │           │   │   │   ├── test_public_api.cpython-311.pyc
│   │           │   │   │   ├── test_reloading.cpython-311.pyc
│   │           │   │   │   ├── test_scripts.cpython-311.pyc
│   │           │   │   │   └── test_warnings.cpython-311.pyc
│   │           │   │   ├── test__all__.py
│   │           │   │   ├── test_configtool.py
│   │           │   │   ├── test_ctypeslib.py
│   │           │   │   ├── test_lazyloading.py
│   │           │   │   ├── test_matlib.py
│   │           │   │   ├── test_numpy_config.py
│   │           │   │   ├── test_numpy_version.py
│   │           │   │   ├── test_public_api.py
│   │           │   │   ├── test_reloading.py
│   │           │   │   ├── test_scripts.py
│   │           │   │   └── test_warnings.py
│   │           │   ├── typing/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── mypy_plugin.cpython-311.pyc
│   │           │   │   ├── mypy_plugin.py
│   │           │   │   └── tests/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── test_isfile.cpython-311.pyc
│   │           │   │       │   ├── test_runtime.cpython-311.pyc
│   │           │   │       │   └── test_typing.cpython-311.pyc
│   │           │   │       ├── data/
│   │           │   │       │   ├── fail/
│   │           │   │       │   │   ├── arithmetic.pyi
│   │           │   │       │   │   ├── array_constructors.pyi
│   │           │   │       │   │   ├── array_like.pyi
│   │           │   │       │   │   ├── array_pad.pyi
│   │           │   │       │   │   ├── arrayprint.pyi
│   │           │   │       │   │   ├── arrayterator.pyi
│   │           │   │       │   │   ├── bitwise_ops.pyi
│   │           │   │       │   │   ├── char.pyi
│   │           │   │       │   │   ├── chararray.pyi
│   │           │   │       │   │   ├── comparisons.pyi
│   │           │   │       │   │   ├── constants.pyi
│   │           │   │       │   │   ├── datasource.pyi
│   │           │   │       │   │   ├── dtype.pyi
│   │           │   │       │   │   ├── einsumfunc.pyi
│   │           │   │       │   │   ├── flatiter.pyi
│   │           │   │       │   │   ├── fromnumeric.pyi
│   │           │   │       │   │   ├── histograms.pyi
│   │           │   │       │   │   ├── index_tricks.pyi
│   │           │   │       │   │   ├── lib_function_base.pyi
│   │           │   │       │   │   ├── lib_polynomial.pyi
│   │           │   │       │   │   ├── lib_utils.pyi
│   │           │   │       │   │   ├── lib_version.pyi
│   │           │   │       │   │   ├── linalg.pyi
│   │           │   │       │   │   ├── ma.pyi
│   │           │   │       │   │   ├── memmap.pyi
│   │           │   │       │   │   ├── modules.pyi
│   │           │   │       │   │   ├── multiarray.pyi
│   │           │   │       │   │   ├── ndarray.pyi
│   │           │   │       │   │   ├── ndarray_misc.pyi
│   │           │   │       │   │   ├── nditer.pyi
│   │           │   │       │   │   ├── nested_sequence.pyi
│   │           │   │       │   │   ├── npyio.pyi
│   │           │   │       │   │   ├── numerictypes.pyi
│   │           │   │       │   │   ├── random.pyi
│   │           │   │       │   │   ├── rec.pyi
│   │           │   │       │   │   ├── scalars.pyi
│   │           │   │       │   │   ├── shape.pyi
│   │           │   │       │   │   ├── shape_base.pyi
│   │           │   │       │   │   ├── stride_tricks.pyi
│   │           │   │       │   │   ├── strings.pyi
│   │           │   │       │   │   ├── testing.pyi
│   │           │   │       │   │   ├── twodim_base.pyi
│   │           │   │       │   │   ├── type_check.pyi
│   │           │   │       │   │   ├── ufunc_config.pyi
│   │           │   │       │   │   ├── ufunclike.pyi
│   │           │   │       │   │   ├── ufuncs.pyi
│   │           │   │       │   │   └── warnings_and_errors.pyi
│   │           │   │       │   ├── misc/
│   │           │   │       │   │   └── extended_precision.pyi
│   │           │   │       │   ├── mypy.ini
│   │           │   │       │   ├── pass/
│   │           │   │       │   │   ├── __pycache__/
│   │           │   │       │   │   │   ├── arithmetic.cpython-311.pyc
│   │           │   │       │   │   │   ├── array_constructors.cpython-311.pyc
│   │           │   │       │   │   │   ├── array_like.cpython-311.pyc
│   │           │   │       │   │   │   ├── arrayprint.cpython-311.pyc
│   │           │   │       │   │   │   ├── arrayterator.cpython-311.pyc
│   │           │   │       │   │   │   ├── bitwise_ops.cpython-311.pyc
│   │           │   │       │   │   │   ├── comparisons.cpython-311.pyc
│   │           │   │       │   │   │   ├── dtype.cpython-311.pyc
│   │           │   │       │   │   │   ├── einsumfunc.cpython-311.pyc
│   │           │   │       │   │   │   ├── flatiter.cpython-311.pyc
│   │           │   │       │   │   │   ├── fromnumeric.cpython-311.pyc
│   │           │   │       │   │   │   ├── index_tricks.cpython-311.pyc
│   │           │   │       │   │   │   ├── lib_user_array.cpython-311.pyc
│   │           │   │       │   │   │   ├── lib_utils.cpython-311.pyc
│   │           │   │       │   │   │   ├── lib_version.cpython-311.pyc
│   │           │   │       │   │   │   ├── literal.cpython-311.pyc
│   │           │   │       │   │   │   ├── ma.cpython-311.pyc
│   │           │   │       │   │   │   ├── mod.cpython-311.pyc
│   │           │   │       │   │   │   ├── modules.cpython-311.pyc
│   │           │   │       │   │   │   ├── multiarray.cpython-311.pyc
│   │           │   │       │   │   │   ├── ndarray_conversion.cpython-311.pyc
│   │           │   │       │   │   │   ├── ndarray_misc.cpython-311.pyc
│   │           │   │       │   │   │   ├── ndarray_shape_manipulation.cpython-311.pyc
│   │           │   │       │   │   │   ├── nditer.cpython-311.pyc
│   │           │   │       │   │   │   ├── numeric.cpython-311.pyc
│   │           │   │       │   │   │   ├── numerictypes.cpython-311.pyc
│   │           │   │       │   │   │   ├── random.cpython-311.pyc
│   │           │   │       │   │   │   ├── recfunctions.cpython-311.pyc
│   │           │   │       │   │   │   ├── scalars.cpython-311.pyc
│   │           │   │       │   │   │   ├── shape.cpython-311.pyc
│   │           │   │       │   │   │   ├── simple.cpython-311.pyc
│   │           │   │       │   │   │   ├── simple_py3.cpython-311.pyc
│   │           │   │       │   │   │   ├── ufunc_config.cpython-311.pyc
│   │           │   │       │   │   │   ├── ufunclike.cpython-311.pyc
│   │           │   │       │   │   │   ├── ufuncs.cpython-311.pyc
│   │           │   │       │   │   │   └── warnings_and_errors.cpython-311.pyc
│   │           │   │       │   │   ├── arithmetic.py
│   │           │   │       │   │   ├── array_constructors.py
│   │           │   │       │   │   ├── array_like.py
│   │           │   │       │   │   ├── arrayprint.py
│   │           │   │       │   │   ├── arrayterator.py
│   │           │   │       │   │   ├── bitwise_ops.py
│   │           │   │       │   │   ├── comparisons.py
│   │           │   │       │   │   ├── dtype.py
│   │           │   │       │   │   ├── einsumfunc.py
│   │           │   │       │   │   ├── flatiter.py
│   │           │   │       │   │   ├── fromnumeric.py
│   │           │   │       │   │   ├── index_tricks.py
│   │           │   │       │   │   ├── lib_user_array.py
│   │           │   │       │   │   ├── lib_utils.py
│   │           │   │       │   │   ├── lib_version.py
│   │           │   │       │   │   ├── literal.py
│   │           │   │       │   │   ├── ma.py
│   │           │   │       │   │   ├── mod.py
│   │           │   │       │   │   ├── modules.py
│   │           │   │       │   │   ├── multiarray.py
│   │           │   │       │   │   ├── ndarray_conversion.py
│   │           │   │       │   │   ├── ndarray_misc.py
│   │           │   │       │   │   ├── ndarray_shape_manipulation.py
│   │           │   │       │   │   ├── nditer.py
│   │           │   │       │   │   ├── numeric.py
│   │           │   │       │   │   ├── numerictypes.py
│   │           │   │       │   │   ├── random.py
│   │           │   │       │   │   ├── recfunctions.py
│   │           │   │       │   │   ├── scalars.py
│   │           │   │       │   │   ├── shape.py
│   │           │   │       │   │   ├── simple.py
│   │           │   │       │   │   ├── simple_py3.py
│   │           │   │       │   │   ├── ufunc_config.py
│   │           │   │       │   │   ├── ufunclike.py
│   │           │   │       │   │   ├── ufuncs.py
│   │           │   │       │   │   └── warnings_and_errors.py
│   │           │   │       │   └── reveal/
│   │           │   │       │       ├── arithmetic.pyi
│   │           │   │       │       ├── array_api_info.pyi
│   │           │   │       │       ├── array_constructors.pyi
│   │           │   │       │       ├── arraypad.pyi
│   │           │   │       │       ├── arrayprint.pyi
│   │           │   │       │       ├── arraysetops.pyi
│   │           │   │       │       ├── arrayterator.pyi
│   │           │   │       │       ├── bitwise_ops.pyi
│   │           │   │       │       ├── char.pyi
│   │           │   │       │       ├── chararray.pyi
│   │           │   │       │       ├── comparisons.pyi
│   │           │   │       │       ├── constants.pyi
│   │           │   │       │       ├── ctypeslib.pyi
│   │           │   │       │       ├── datasource.pyi
│   │           │   │       │       ├── dtype.pyi
│   │           │   │       │       ├── einsumfunc.pyi
│   │           │   │       │       ├── emath.pyi
│   │           │   │       │       ├── fft.pyi
│   │           │   │       │       ├── flatiter.pyi
│   │           │   │       │       ├── fromnumeric.pyi
│   │           │   │       │       ├── getlimits.pyi
│   │           │   │       │       ├── histograms.pyi
│   │           │   │       │       ├── index_tricks.pyi
│   │           │   │       │       ├── lib_function_base.pyi
│   │           │   │       │       ├── lib_polynomial.pyi
│   │           │   │       │       ├── lib_utils.pyi
│   │           │   │       │       ├── lib_version.pyi
│   │           │   │       │       ├── linalg.pyi
│   │           │   │       │       ├── ma.pyi
│   │           │   │       │       ├── matrix.pyi
│   │           │   │       │       ├── memmap.pyi
│   │           │   │       │       ├── mod.pyi
│   │           │   │       │       ├── modules.pyi
│   │           │   │       │       ├── multiarray.pyi
│   │           │   │       │       ├── nbit_base_example.pyi
│   │           │   │       │       ├── ndarray_assignability.pyi
│   │           │   │       │       ├── ndarray_conversion.pyi
│   │           │   │       │       ├── ndarray_misc.pyi
│   │           │   │       │       ├── ndarray_shape_manipulation.pyi
│   │           │   │       │       ├── nditer.pyi
│   │           │   │       │       ├── nested_sequence.pyi
│   │           │   │       │       ├── npyio.pyi
│   │           │   │       │       ├── numeric.pyi
│   │           │   │       │       ├── numerictypes.pyi
│   │           │   │       │       ├── polynomial_polybase.pyi
│   │           │   │       │       ├── polynomial_polyutils.pyi
│   │           │   │       │       ├── polynomial_series.pyi
│   │           │   │       │       ├── random.pyi
│   │           │   │       │       ├── rec.pyi
│   │           │   │       │       ├── scalars.pyi
│   │           │   │       │       ├── shape.pyi
│   │           │   │       │       ├── shape_base.pyi
│   │           │   │       │       ├── stride_tricks.pyi
│   │           │   │       │       ├── strings.pyi
│   │           │   │       │       ├── testing.pyi
│   │           │   │       │       ├── twodim_base.pyi
│   │           │   │       │       ├── type_check.pyi
│   │           │   │       │       ├── ufunc_config.pyi
│   │           │   │       │       ├── ufunclike.pyi
│   │           │   │       │       ├── ufuncs.pyi
│   │           │   │       │       └── warnings_and_errors.pyi
│   │           │   │       ├── test_isfile.py
│   │           │   │       ├── test_runtime.py
│   │           │   │       └── test_typing.py
│   │           │   ├── version.py
│   │           │   └── version.pyi
│   │           ├── packaging-25.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   └── licenses/
│   │           │       ├── LICENSE
│   │           │       ├── LICENSE.APACHE
│   │           │       └── LICENSE.BSD
│   │           ├── packaging/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _elffile.cpython-311.pyc
│   │           │   │   ├── _manylinux.cpython-311.pyc
│   │           │   │   ├── _musllinux.cpython-311.pyc
│   │           │   │   ├── _parser.cpython-311.pyc
│   │           │   │   ├── _structures.cpython-311.pyc
│   │           │   │   ├── _tokenizer.cpython-311.pyc
│   │           │   │   ├── markers.cpython-311.pyc
│   │           │   │   ├── metadata.cpython-311.pyc
│   │           │   │   ├── requirements.cpython-311.pyc
│   │           │   │   ├── specifiers.cpython-311.pyc
│   │           │   │   ├── tags.cpython-311.pyc
│   │           │   │   ├── utils.cpython-311.pyc
│   │           │   │   └── version.cpython-311.pyc
│   │           │   ├── _elffile.py
│   │           │   ├── _manylinux.py
│   │           │   ├── _musllinux.py
│   │           │   ├── _parser.py
│   │           │   ├── _structures.py
│   │           │   ├── _tokenizer.py
│   │           │   ├── licenses/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── _spdx.cpython-311.pyc
│   │           │   │   └── _spdx.py
│   │           │   ├── markers.py
│   │           │   ├── metadata.py
│   │           │   ├── py.typed
│   │           │   ├── requirements.py
│   │           │   ├── specifiers.py
│   │           │   ├── tags.py
│   │           │   ├── utils.py
│   │           │   └── version.py
│   │           ├── pillow-11.3.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   ├── licenses/
│   │           │   │   └── LICENSE
│   │           │   ├── top_level.txt
│   │           │   └── zip-safe
│   │           ├── pip-23.0.1.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.txt
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   ├── entry_points.txt
│   │           │   └── top_level.txt
│   │           ├── pip
│   │           ├── pip/
│   │           │   ├── __init__.py
│   │           │   ├── __main__.py
│   │           │   ├── __pip-runner__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── __main__.cpython-311.pyc
│   │           │   │   └── __pip-runner__.cpython-311.pyc
│   │           │   ├── _internal/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── build_env.cpython-311.pyc
│   │           │   │   │   ├── cache.cpython-311.pyc
│   │           │   │   │   ├── configuration.cpython-311.pyc
│   │           │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   ├── main.cpython-311.pyc
│   │           │   │   │   ├── pyproject.cpython-311.pyc
│   │           │   │   │   ├── self_outdated_check.cpython-311.pyc
│   │           │   │   │   └── wheel_builder.cpython-311.pyc
│   │           │   │   ├── build_env.py
│   │           │   │   ├── cache.py
│   │           │   │   ├── cli/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── autocompletion.cpython-311.pyc
│   │           │   │   │   │   ├── base_command.cpython-311.pyc
│   │           │   │   │   │   ├── cmdoptions.cpython-311.pyc
│   │           │   │   │   │   ├── command_context.cpython-311.pyc
│   │           │   │   │   │   ├── main.cpython-311.pyc
│   │           │   │   │   │   ├── main_parser.cpython-311.pyc
│   │           │   │   │   │   ├── parser.cpython-311.pyc
│   │           │   │   │   │   ├── progress_bars.cpython-311.pyc
│   │           │   │   │   │   ├── req_command.cpython-311.pyc
│   │           │   │   │   │   ├── spinners.cpython-311.pyc
│   │           │   │   │   │   └── status_codes.cpython-311.pyc
│   │           │   │   │   ├── autocompletion.py
│   │           │   │   │   ├── base_command.py
│   │           │   │   │   ├── cmdoptions.py
│   │           │   │   │   ├── command_context.py
│   │           │   │   │   ├── main.py
│   │           │   │   │   ├── main_parser.py
│   │           │   │   │   ├── parser.py
│   │           │   │   │   ├── progress_bars.py
│   │           │   │   │   ├── req_command.py
│   │           │   │   │   ├── spinners.py
│   │           │   │   │   └── status_codes.py
│   │           │   │   ├── commands/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── cache.cpython-311.pyc
│   │           │   │   │   │   ├── check.cpython-311.pyc
│   │           │   │   │   │   ├── completion.cpython-311.pyc
│   │           │   │   │   │   ├── configuration.cpython-311.pyc
│   │           │   │   │   │   ├── debug.cpython-311.pyc
│   │           │   │   │   │   ├── download.cpython-311.pyc
│   │           │   │   │   │   ├── freeze.cpython-311.pyc
│   │           │   │   │   │   ├── hash.cpython-311.pyc
│   │           │   │   │   │   ├── help.cpython-311.pyc
│   │           │   │   │   │   ├── index.cpython-311.pyc
│   │           │   │   │   │   ├── inspect.cpython-311.pyc
│   │           │   │   │   │   ├── install.cpython-311.pyc
│   │           │   │   │   │   ├── list.cpython-311.pyc
│   │           │   │   │   │   ├── search.cpython-311.pyc
│   │           │   │   │   │   ├── show.cpython-311.pyc
│   │           │   │   │   │   ├── uninstall.cpython-311.pyc
│   │           │   │   │   │   └── wheel.cpython-311.pyc
│   │           │   │   │   ├── cache.py
│   │           │   │   │   ├── check.py
│   │           │   │   │   ├── completion.py
│   │           │   │   │   ├── configuration.py
│   │           │   │   │   ├── debug.py
│   │           │   │   │   ├── download.py
│   │           │   │   │   ├── freeze.py
│   │           │   │   │   ├── hash.py
│   │           │   │   │   ├── help.py
│   │           │   │   │   ├── index.py
│   │           │   │   │   ├── inspect.py
│   │           │   │   │   ├── install.py
│   │           │   │   │   ├── list.py
│   │           │   │   │   ├── search.py
│   │           │   │   │   ├── show.py
│   │           │   │   │   ├── uninstall.py
│   │           │   │   │   └── wheel.py
│   │           │   │   ├── configuration.py
│   │           │   │   ├── distributions/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── base.cpython-311.pyc
│   │           │   │   │   │   ├── installed.cpython-311.pyc
│   │           │   │   │   │   ├── sdist.cpython-311.pyc
│   │           │   │   │   │   └── wheel.cpython-311.pyc
│   │           │   │   │   ├── base.py
│   │           │   │   │   ├── installed.py
│   │           │   │   │   ├── sdist.py
│   │           │   │   │   └── wheel.py
│   │           │   │   ├── exceptions.py
│   │           │   │   ├── index/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── collector.cpython-311.pyc
│   │           │   │   │   │   ├── package_finder.cpython-311.pyc
│   │           │   │   │   │   └── sources.cpython-311.pyc
│   │           │   │   │   ├── collector.py
│   │           │   │   │   ├── package_finder.py
│   │           │   │   │   └── sources.py
│   │           │   │   ├── locations/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _distutils.cpython-311.pyc
│   │           │   │   │   │   ├── _sysconfig.cpython-311.pyc
│   │           │   │   │   │   └── base.cpython-311.pyc
│   │           │   │   │   ├── _distutils.py
│   │           │   │   │   ├── _sysconfig.py
│   │           │   │   │   └── base.py
│   │           │   │   ├── main.py
│   │           │   │   ├── metadata/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _json.cpython-311.pyc
│   │           │   │   │   │   ├── base.cpython-311.pyc
│   │           │   │   │   │   └── pkg_resources.cpython-311.pyc
│   │           │   │   │   ├── _json.py
│   │           │   │   │   ├── base.py
│   │           │   │   │   ├── importlib/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── _compat.cpython-311.pyc
│   │           │   │   │   │   │   ├── _dists.cpython-311.pyc
│   │           │   │   │   │   │   └── _envs.cpython-311.pyc
│   │           │   │   │   │   ├── _compat.py
│   │           │   │   │   │   ├── _dists.py
│   │           │   │   │   │   └── _envs.py
│   │           │   │   │   └── pkg_resources.py
│   │           │   │   ├── models/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── candidate.cpython-311.pyc
│   │           │   │   │   │   ├── direct_url.cpython-311.pyc
│   │           │   │   │   │   ├── format_control.cpython-311.pyc
│   │           │   │   │   │   ├── index.cpython-311.pyc
│   │           │   │   │   │   ├── installation_report.cpython-311.pyc
│   │           │   │   │   │   ├── link.cpython-311.pyc
│   │           │   │   │   │   ├── scheme.cpython-311.pyc
│   │           │   │   │   │   ├── search_scope.cpython-311.pyc
│   │           │   │   │   │   ├── selection_prefs.cpython-311.pyc
│   │           │   │   │   │   ├── target_python.cpython-311.pyc
│   │           │   │   │   │   └── wheel.cpython-311.pyc
│   │           │   │   │   ├── candidate.py
│   │           │   │   │   ├── direct_url.py
│   │           │   │   │   ├── format_control.py
│   │           │   │   │   ├── index.py
│   │           │   │   │   ├── installation_report.py
│   │           │   │   │   ├── link.py
│   │           │   │   │   ├── scheme.py
│   │           │   │   │   ├── search_scope.py
│   │           │   │   │   ├── selection_prefs.py
│   │           │   │   │   ├── target_python.py
│   │           │   │   │   └── wheel.py
│   │           │   │   ├── network/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── auth.cpython-311.pyc
│   │           │   │   │   │   ├── cache.cpython-311.pyc
│   │           │   │   │   │   ├── download.cpython-311.pyc
│   │           │   │   │   │   ├── lazy_wheel.cpython-311.pyc
│   │           │   │   │   │   ├── session.cpython-311.pyc
│   │           │   │   │   │   ├── utils.cpython-311.pyc
│   │           │   │   │   │   └── xmlrpc.cpython-311.pyc
│   │           │   │   │   ├── auth.py
│   │           │   │   │   ├── cache.py
│   │           │   │   │   ├── download.py
│   │           │   │   │   ├── lazy_wheel.py
│   │           │   │   │   ├── session.py
│   │           │   │   │   ├── utils.py
│   │           │   │   │   └── xmlrpc.py
│   │           │   │   ├── operations/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── check.cpython-311.pyc
│   │           │   │   │   │   ├── freeze.cpython-311.pyc
│   │           │   │   │   │   └── prepare.cpython-311.pyc
│   │           │   │   │   ├── build
│   │           │   │   │   ├── build/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── build_tracker.cpython-311.pyc
│   │           │   │   │   │   │   ├── metadata.cpython-311.pyc
│   │           │   │   │   │   │   ├── metadata_editable.cpython-311.pyc
│   │           │   │   │   │   │   ├── metadata_legacy.cpython-311.pyc
│   │           │   │   │   │   │   ├── wheel.cpython-311.pyc
│   │           │   │   │   │   │   ├── wheel_editable.cpython-311.pyc
│   │           │   │   │   │   │   └── wheel_legacy.cpython-311.pyc
│   │           │   │   │   │   ├── build_tracker.py
│   │           │   │   │   │   ├── metadata.py
│   │           │   │   │   │   ├── metadata_editable.py
│   │           │   │   │   │   ├── metadata_legacy.py
│   │           │   │   │   │   ├── wheel.py
│   │           │   │   │   │   ├── wheel_editable.py
│   │           │   │   │   │   └── wheel_legacy.py
│   │           │   │   │   ├── check.py
│   │           │   │   │   ├── freeze.py
│   │           │   │   │   ├── install/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── editable_legacy.cpython-311.pyc
│   │           │   │   │   │   │   ├── legacy.cpython-311.pyc
│   │           │   │   │   │   │   └── wheel.cpython-311.pyc
│   │           │   │   │   │   ├── editable_legacy.py
│   │           │   │   │   │   ├── legacy.py
│   │           │   │   │   │   └── wheel.py
│   │           │   │   │   └── prepare.py
│   │           │   │   ├── pyproject.py
│   │           │   │   ├── req/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── constructors.cpython-311.pyc
│   │           │   │   │   │   ├── req_file.cpython-311.pyc
│   │           │   │   │   │   ├── req_install.cpython-311.pyc
│   │           │   │   │   │   ├── req_set.cpython-311.pyc
│   │           │   │   │   │   └── req_uninstall.cpython-311.pyc
│   │           │   │   │   ├── constructors.py
│   │           │   │   │   ├── req_file.py
│   │           │   │   │   ├── req_install.py
│   │           │   │   │   ├── req_set.py
│   │           │   │   │   └── req_uninstall.py
│   │           │   │   ├── resolution/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   └── base.cpython-311.pyc
│   │           │   │   │   ├── base.py
│   │           │   │   │   ├── legacy/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   └── resolver.cpython-311.pyc
│   │           │   │   │   │   └── resolver.py
│   │           │   │   │   └── resolvelib/
│   │           │   │   │       ├── __init__.py
│   │           │   │   │       ├── __pycache__/
│   │           │   │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │   │       │   ├── base.cpython-311.pyc
│   │           │   │   │       │   ├── candidates.cpython-311.pyc
│   │           │   │   │       │   ├── factory.cpython-311.pyc
│   │           │   │   │       │   ├── found_candidates.cpython-311.pyc
│   │           │   │   │       │   ├── provider.cpython-311.pyc
│   │           │   │   │       │   ├── reporter.cpython-311.pyc
│   │           │   │   │       │   ├── requirements.cpython-311.pyc
│   │           │   │   │       │   └── resolver.cpython-311.pyc
│   │           │   │   │       ├── base.py
│   │           │   │   │       ├── candidates.py
│   │           │   │   │       ├── factory.py
│   │           │   │   │       ├── found_candidates.py
│   │           │   │   │       ├── provider.py
│   │           │   │   │       ├── reporter.py
│   │           │   │   │       ├── requirements.py
│   │           │   │   │       └── resolver.py
│   │           │   │   ├── self_outdated_check.py
│   │           │   │   ├── utils/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _log.cpython-311.pyc
│   │           │   │   │   │   ├── appdirs.cpython-311.pyc
│   │           │   │   │   │   ├── compat.cpython-311.pyc
│   │           │   │   │   │   ├── compatibility_tags.cpython-311.pyc
│   │           │   │   │   │   ├── datetime.cpython-311.pyc
│   │           │   │   │   │   ├── deprecation.cpython-311.pyc
│   │           │   │   │   │   ├── direct_url_helpers.cpython-311.pyc
│   │           │   │   │   │   ├── distutils_args.cpython-311.pyc
│   │           │   │   │   │   ├── egg_link.cpython-311.pyc
│   │           │   │   │   │   ├── encoding.cpython-311.pyc
│   │           │   │   │   │   ├── entrypoints.cpython-311.pyc
│   │           │   │   │   │   ├── filesystem.cpython-311.pyc
│   │           │   │   │   │   ├── filetypes.cpython-311.pyc
│   │           │   │   │   │   ├── glibc.cpython-311.pyc
│   │           │   │   │   │   ├── hashes.cpython-311.pyc
│   │           │   │   │   │   ├── inject_securetransport.cpython-311.pyc
│   │           │   │   │   │   ├── logging.cpython-311.pyc
│   │           │   │   │   │   ├── misc.cpython-311.pyc
│   │           │   │   │   │   ├── models.cpython-311.pyc
│   │           │   │   │   │   ├── packaging.cpython-311.pyc
│   │           │   │   │   │   ├── setuptools_build.cpython-311.pyc
│   │           │   │   │   │   ├── subprocess.cpython-311.pyc
│   │           │   │   │   │   ├── temp_dir.cpython-311.pyc
│   │           │   │   │   │   ├── unpacking.cpython-311.pyc
│   │           │   │   │   │   ├── urls.cpython-311.pyc
│   │           │   │   │   │   ├── virtualenv.cpython-311.pyc
│   │           │   │   │   │   └── wheel.cpython-311.pyc
│   │           │   │   │   ├── _log.py
│   │           │   │   │   ├── appdirs.py
│   │           │   │   │   ├── compat.py
│   │           │   │   │   ├── compatibility_tags.py
│   │           │   │   │   ├── datetime.py
│   │           │   │   │   ├── deprecation.py
│   │           │   │   │   ├── direct_url_helpers.py
│   │           │   │   │   ├── distutils_args.py
│   │           │   │   │   ├── egg_link.py
│   │           │   │   │   ├── encoding.py
│   │           │   │   │   ├── entrypoints.py
│   │           │   │   │   ├── filesystem.py
│   │           │   │   │   ├── filetypes.py
│   │           │   │   │   ├── glibc.py
│   │           │   │   │   ├── hashes.py
│   │           │   │   │   ├── inject_securetransport.py
│   │           │   │   │   ├── logging.py
│   │           │   │   │   ├── misc.py
│   │           │   │   │   ├── models.py
│   │           │   │   │   ├── packaging.py
│   │           │   │   │   ├── setuptools_build.py
│   │           │   │   │   ├── subprocess.py
│   │           │   │   │   ├── temp_dir.py
│   │           │   │   │   ├── unpacking.py
│   │           │   │   │   ├── urls.py
│   │           │   │   │   ├── virtualenv.py
│   │           │   │   │   └── wheel.py
│   │           │   │   ├── vcs/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── bazaar.cpython-311.pyc
│   │           │   │   │   │   ├── git.cpython-311.pyc
│   │           │   │   │   │   ├── mercurial.cpython-311.pyc
│   │           │   │   │   │   ├── subversion.cpython-311.pyc
│   │           │   │   │   │   └── versioncontrol.cpython-311.pyc
│   │           │   │   │   ├── bazaar.py
│   │           │   │   │   ├── git.py
│   │           │   │   │   ├── mercurial.py
│   │           │   │   │   ├── subversion.py
│   │           │   │   │   └── versioncontrol.py
│   │           │   │   └── wheel_builder.py
│   │           │   ├── _vendor/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── six.cpython-311.pyc
│   │           │   │   │   └── typing_extensions.cpython-311.pyc
│   │           │   │   ├── cachecontrol/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _cmd.cpython-311.pyc
│   │           │   │   │   │   ├── adapter.cpython-311.pyc
│   │           │   │   │   │   ├── cache.cpython-311.pyc
│   │           │   │   │   │   ├── compat.cpython-311.pyc
│   │           │   │   │   │   ├── controller.cpython-311.pyc
│   │           │   │   │   │   ├── filewrapper.cpython-311.pyc
│   │           │   │   │   │   ├── heuristics.cpython-311.pyc
│   │           │   │   │   │   ├── serialize.cpython-311.pyc
│   │           │   │   │   │   └── wrapper.cpython-311.pyc
│   │           │   │   │   ├── _cmd.py
│   │           │   │   │   ├── adapter.py
│   │           │   │   │   ├── cache.py
│   │           │   │   │   ├── caches/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── file_cache.cpython-311.pyc
│   │           │   │   │   │   │   └── redis_cache.cpython-311.pyc
│   │           │   │   │   │   ├── file_cache.py
│   │           │   │   │   │   └── redis_cache.py
│   │           │   │   │   ├── compat.py
│   │           │   │   │   ├── controller.py
│   │           │   │   │   ├── filewrapper.py
│   │           │   │   │   ├── heuristics.py
│   │           │   │   │   ├── serialize.py
│   │           │   │   │   └── wrapper.py
│   │           │   │   ├── certifi/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   └── core.cpython-311.pyc
│   │           │   │   │   ├── cacert.pem
│   │           │   │   │   └── core.py
│   │           │   │   ├── chardet/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── big5freq.cpython-311.pyc
│   │           │   │   │   │   ├── big5prober.cpython-311.pyc
│   │           │   │   │   │   ├── chardistribution.cpython-311.pyc
│   │           │   │   │   │   ├── charsetgroupprober.cpython-311.pyc
│   │           │   │   │   │   ├── charsetprober.cpython-311.pyc
│   │           │   │   │   │   ├── codingstatemachine.cpython-311.pyc
│   │           │   │   │   │   ├── codingstatemachinedict.cpython-311.pyc
│   │           │   │   │   │   ├── cp949prober.cpython-311.pyc
│   │           │   │   │   │   ├── enums.cpython-311.pyc
│   │           │   │   │   │   ├── escprober.cpython-311.pyc
│   │           │   │   │   │   ├── escsm.cpython-311.pyc
│   │           │   │   │   │   ├── eucjpprober.cpython-311.pyc
│   │           │   │   │   │   ├── euckrfreq.cpython-311.pyc
│   │           │   │   │   │   ├── euckrprober.cpython-311.pyc
│   │           │   │   │   │   ├── euctwfreq.cpython-311.pyc
│   │           │   │   │   │   ├── euctwprober.cpython-311.pyc
│   │           │   │   │   │   ├── gb2312freq.cpython-311.pyc
│   │           │   │   │   │   ├── gb2312prober.cpython-311.pyc
│   │           │   │   │   │   ├── hebrewprober.cpython-311.pyc
│   │           │   │   │   │   ├── jisfreq.cpython-311.pyc
│   │           │   │   │   │   ├── johabfreq.cpython-311.pyc
│   │           │   │   │   │   ├── johabprober.cpython-311.pyc
│   │           │   │   │   │   ├── jpcntx.cpython-311.pyc
│   │           │   │   │   │   ├── langbulgarianmodel.cpython-311.pyc
│   │           │   │   │   │   ├── langgreekmodel.cpython-311.pyc
│   │           │   │   │   │   ├── langhebrewmodel.cpython-311.pyc
│   │           │   │   │   │   ├── langhungarianmodel.cpython-311.pyc
│   │           │   │   │   │   ├── langrussianmodel.cpython-311.pyc
│   │           │   │   │   │   ├── langthaimodel.cpython-311.pyc
│   │           │   │   │   │   ├── langturkishmodel.cpython-311.pyc
│   │           │   │   │   │   ├── latin1prober.cpython-311.pyc
│   │           │   │   │   │   ├── macromanprober.cpython-311.pyc
│   │           │   │   │   │   ├── mbcharsetprober.cpython-311.pyc
│   │           │   │   │   │   ├── mbcsgroupprober.cpython-311.pyc
│   │           │   │   │   │   ├── mbcssm.cpython-311.pyc
│   │           │   │   │   │   ├── resultdict.cpython-311.pyc
│   │           │   │   │   │   ├── sbcharsetprober.cpython-311.pyc
│   │           │   │   │   │   ├── sbcsgroupprober.cpython-311.pyc
│   │           │   │   │   │   ├── sjisprober.cpython-311.pyc
│   │           │   │   │   │   ├── universaldetector.cpython-311.pyc
│   │           │   │   │   │   ├── utf1632prober.cpython-311.pyc
│   │           │   │   │   │   ├── utf8prober.cpython-311.pyc
│   │           │   │   │   │   └── version.cpython-311.pyc
│   │           │   │   │   ├── big5freq.py
│   │           │   │   │   ├── big5prober.py
│   │           │   │   │   ├── chardistribution.py
│   │           │   │   │   ├── charsetgroupprober.py
│   │           │   │   │   ├── charsetprober.py
│   │           │   │   │   ├── cli/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   └── chardetect.cpython-311.pyc
│   │           │   │   │   │   └── chardetect.py
│   │           │   │   │   ├── codingstatemachine.py
│   │           │   │   │   ├── codingstatemachinedict.py
│   │           │   │   │   ├── cp949prober.py
│   │           │   │   │   ├── enums.py
│   │           │   │   │   ├── escprober.py
│   │           │   │   │   ├── escsm.py
│   │           │   │   │   ├── eucjpprober.py
│   │           │   │   │   ├── euckrfreq.py
│   │           │   │   │   ├── euckrprober.py
│   │           │   │   │   ├── euctwfreq.py
│   │           │   │   │   ├── euctwprober.py
│   │           │   │   │   ├── gb2312freq.py
│   │           │   │   │   ├── gb2312prober.py
│   │           │   │   │   ├── hebrewprober.py
│   │           │   │   │   ├── jisfreq.py
│   │           │   │   │   ├── johabfreq.py
│   │           │   │   │   ├── johabprober.py
│   │           │   │   │   ├── jpcntx.py
│   │           │   │   │   ├── langbulgarianmodel.py
│   │           │   │   │   ├── langgreekmodel.py
│   │           │   │   │   ├── langhebrewmodel.py
│   │           │   │   │   ├── langhungarianmodel.py
│   │           │   │   │   ├── langrussianmodel.py
│   │           │   │   │   ├── langthaimodel.py
│   │           │   │   │   ├── langturkishmodel.py
│   │           │   │   │   ├── latin1prober.py
│   │           │   │   │   ├── macromanprober.py
│   │           │   │   │   ├── mbcharsetprober.py
│   │           │   │   │   ├── mbcsgroupprober.py
│   │           │   │   │   ├── mbcssm.py
│   │           │   │   │   ├── metadata/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   └── languages.cpython-311.pyc
│   │           │   │   │   │   └── languages.py
│   │           │   │   │   ├── resultdict.py
│   │           │   │   │   ├── sbcharsetprober.py
│   │           │   │   │   ├── sbcsgroupprober.py
│   │           │   │   │   ├── sjisprober.py
│   │           │   │   │   ├── universaldetector.py
│   │           │   │   │   ├── utf1632prober.py
│   │           │   │   │   ├── utf8prober.py
│   │           │   │   │   └── version.py
│   │           │   │   ├── colorama/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── ansi.cpython-311.pyc
│   │           │   │   │   │   ├── ansitowin32.cpython-311.pyc
│   │           │   │   │   │   ├── initialise.cpython-311.pyc
│   │           │   │   │   │   ├── win32.cpython-311.pyc
│   │           │   │   │   │   └── winterm.cpython-311.pyc
│   │           │   │   │   ├── ansi.py
│   │           │   │   │   ├── ansitowin32.py
│   │           │   │   │   ├── initialise.py
│   │           │   │   │   ├── tests/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── ansi_test.cpython-311.pyc
│   │           │   │   │   │   │   ├── ansitowin32_test.cpython-311.pyc
│   │           │   │   │   │   │   ├── initialise_test.cpython-311.pyc
│   │           │   │   │   │   │   ├── isatty_test.cpython-311.pyc
│   │           │   │   │   │   │   ├── utils.cpython-311.pyc
│   │           │   │   │   │   │   └── winterm_test.cpython-311.pyc
│   │           │   │   │   │   ├── ansi_test.py
│   │           │   │   │   │   ├── ansitowin32_test.py
│   │           │   │   │   │   ├── initialise_test.py
│   │           │   │   │   │   ├── isatty_test.py
│   │           │   │   │   │   ├── utils.py
│   │           │   │   │   │   └── winterm_test.py
│   │           │   │   │   ├── win32.py
│   │           │   │   │   └── winterm.py
│   │           │   │   ├── distlib/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── compat.cpython-311.pyc
│   │           │   │   │   │   ├── database.cpython-311.pyc
│   │           │   │   │   │   ├── index.cpython-311.pyc
│   │           │   │   │   │   ├── locators.cpython-311.pyc
│   │           │   │   │   │   ├── manifest.cpython-311.pyc
│   │           │   │   │   │   ├── markers.cpython-311.pyc
│   │           │   │   │   │   ├── metadata.cpython-311.pyc
│   │           │   │   │   │   ├── resources.cpython-311.pyc
│   │           │   │   │   │   ├── scripts.cpython-311.pyc
│   │           │   │   │   │   ├── util.cpython-311.pyc
│   │           │   │   │   │   ├── version.cpython-311.pyc
│   │           │   │   │   │   └── wheel.cpython-311.pyc
│   │           │   │   │   ├── compat.py
│   │           │   │   │   ├── database.py
│   │           │   │   │   ├── index.py
│   │           │   │   │   ├── locators.py
│   │           │   │   │   ├── manifest.py
│   │           │   │   │   ├── markers.py
│   │           │   │   │   ├── metadata.py
│   │           │   │   │   ├── resources.py
│   │           │   │   │   ├── scripts.py
│   │           │   │   │   ├── util.py
│   │           │   │   │   ├── version.py
│   │           │   │   │   └── wheel.py
│   │           │   │   ├── distro/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   └── distro.cpython-311.pyc
│   │           │   │   │   └── distro.py
│   │           │   │   ├── idna/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── codec.cpython-311.pyc
│   │           │   │   │   │   ├── compat.cpython-311.pyc
│   │           │   │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   │   ├── idnadata.cpython-311.pyc
│   │           │   │   │   │   ├── intranges.cpython-311.pyc
│   │           │   │   │   │   ├── package_data.cpython-311.pyc
│   │           │   │   │   │   └── uts46data.cpython-311.pyc
│   │           │   │   │   ├── codec.py
│   │           │   │   │   ├── compat.py
│   │           │   │   │   ├── core.py
│   │           │   │   │   ├── idnadata.py
│   │           │   │   │   ├── intranges.py
│   │           │   │   │   ├── package_data.py
│   │           │   │   │   └── uts46data.py
│   │           │   │   ├── msgpack/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── ext.cpython-311.pyc
│   │           │   │   │   │   └── fallback.cpython-311.pyc
│   │           │   │   │   ├── exceptions.py
│   │           │   │   │   ├── ext.py
│   │           │   │   │   └── fallback.py
│   │           │   │   ├── packaging/
│   │           │   │   │   ├── __about__.py
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __about__.cpython-311.pyc
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _manylinux.cpython-311.pyc
│   │           │   │   │   │   ├── _musllinux.cpython-311.pyc
│   │           │   │   │   │   ├── _structures.cpython-311.pyc
│   │           │   │   │   │   ├── markers.cpython-311.pyc
│   │           │   │   │   │   ├── requirements.cpython-311.pyc
│   │           │   │   │   │   ├── specifiers.cpython-311.pyc
│   │           │   │   │   │   ├── tags.cpython-311.pyc
│   │           │   │   │   │   ├── utils.cpython-311.pyc
│   │           │   │   │   │   └── version.cpython-311.pyc
│   │           │   │   │   ├── _manylinux.py
│   │           │   │   │   ├── _musllinux.py
│   │           │   │   │   ├── _structures.py
│   │           │   │   │   ├── markers.py
│   │           │   │   │   ├── requirements.py
│   │           │   │   │   ├── specifiers.py
│   │           │   │   │   ├── tags.py
│   │           │   │   │   ├── utils.py
│   │           │   │   │   └── version.py
│   │           │   │   ├── pkg_resources/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   └── py31compat.cpython-311.pyc
│   │           │   │   │   └── py31compat.py
│   │           │   │   ├── platformdirs/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   ├── android.cpython-311.pyc
│   │           │   │   │   │   ├── api.cpython-311.pyc
│   │           │   │   │   │   ├── macos.cpython-311.pyc
│   │           │   │   │   │   ├── unix.cpython-311.pyc
│   │           │   │   │   │   ├── version.cpython-311.pyc
│   │           │   │   │   │   └── windows.cpython-311.pyc
│   │           │   │   │   ├── android.py
│   │           │   │   │   ├── api.py
│   │           │   │   │   ├── macos.py
│   │           │   │   │   ├── unix.py
│   │           │   │   │   ├── version.py
│   │           │   │   │   └── windows.py
│   │           │   │   ├── pygments/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   ├── cmdline.cpython-311.pyc
│   │           │   │   │   │   ├── console.cpython-311.pyc
│   │           │   │   │   │   ├── filter.cpython-311.pyc
│   │           │   │   │   │   ├── formatter.cpython-311.pyc
│   │           │   │   │   │   ├── lexer.cpython-311.pyc
│   │           │   │   │   │   ├── modeline.cpython-311.pyc
│   │           │   │   │   │   ├── plugin.cpython-311.pyc
│   │           │   │   │   │   ├── regexopt.cpython-311.pyc
│   │           │   │   │   │   ├── scanner.cpython-311.pyc
│   │           │   │   │   │   ├── sphinxext.cpython-311.pyc
│   │           │   │   │   │   ├── style.cpython-311.pyc
│   │           │   │   │   │   ├── token.cpython-311.pyc
│   │           │   │   │   │   ├── unistring.cpython-311.pyc
│   │           │   │   │   │   └── util.cpython-311.pyc
│   │           │   │   │   ├── cmdline.py
│   │           │   │   │   ├── console.py
│   │           │   │   │   ├── filter.py
│   │           │   │   │   ├── filters/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   └── __pycache__/
│   │           │   │   │   │       └── __init__.cpython-311.pyc
│   │           │   │   │   ├── formatter.py
│   │           │   │   │   ├── formatters/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── _mapping.cpython-311.pyc
│   │           │   │   │   │   │   ├── bbcode.cpython-311.pyc
│   │           │   │   │   │   │   ├── groff.cpython-311.pyc
│   │           │   │   │   │   │   ├── html.cpython-311.pyc
│   │           │   │   │   │   │   ├── img.cpython-311.pyc
│   │           │   │   │   │   │   ├── irc.cpython-311.pyc
│   │           │   │   │   │   │   ├── latex.cpython-311.pyc
│   │           │   │   │   │   │   ├── other.cpython-311.pyc
│   │           │   │   │   │   │   ├── pangomarkup.cpython-311.pyc
│   │           │   │   │   │   │   ├── rtf.cpython-311.pyc
│   │           │   │   │   │   │   ├── svg.cpython-311.pyc
│   │           │   │   │   │   │   ├── terminal.cpython-311.pyc
│   │           │   │   │   │   │   └── terminal256.cpython-311.pyc
│   │           │   │   │   │   ├── _mapping.py
│   │           │   │   │   │   ├── bbcode.py
│   │           │   │   │   │   ├── groff.py
│   │           │   │   │   │   ├── html.py
│   │           │   │   │   │   ├── img.py
│   │           │   │   │   │   ├── irc.py
│   │           │   │   │   │   ├── latex.py
│   │           │   │   │   │   ├── other.py
│   │           │   │   │   │   ├── pangomarkup.py
│   │           │   │   │   │   ├── rtf.py
│   │           │   │   │   │   ├── svg.py
│   │           │   │   │   │   ├── terminal.py
│   │           │   │   │   │   └── terminal256.py
│   │           │   │   │   ├── lexer.py
│   │           │   │   │   ├── lexers/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── _mapping.cpython-311.pyc
│   │           │   │   │   │   │   └── python.cpython-311.pyc
│   │           │   │   │   │   ├── _mapping.py
│   │           │   │   │   │   └── python.py
│   │           │   │   │   ├── modeline.py
│   │           │   │   │   ├── plugin.py
│   │           │   │   │   ├── regexopt.py
│   │           │   │   │   ├── scanner.py
│   │           │   │   │   ├── sphinxext.py
│   │           │   │   │   ├── style.py
│   │           │   │   │   ├── styles/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   └── __pycache__/
│   │           │   │   │   │       └── __init__.cpython-311.pyc
│   │           │   │   │   ├── token.py
│   │           │   │   │   ├── unistring.py
│   │           │   │   │   └── util.py
│   │           │   │   ├── pyparsing/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── actions.cpython-311.pyc
│   │           │   │   │   │   ├── common.cpython-311.pyc
│   │           │   │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── helpers.cpython-311.pyc
│   │           │   │   │   │   ├── results.cpython-311.pyc
│   │           │   │   │   │   ├── testing.cpython-311.pyc
│   │           │   │   │   │   ├── unicode.cpython-311.pyc
│   │           │   │   │   │   └── util.cpython-311.pyc
│   │           │   │   │   ├── actions.py
│   │           │   │   │   ├── common.py
│   │           │   │   │   ├── core.py
│   │           │   │   │   ├── diagram/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   └── __pycache__/
│   │           │   │   │   │       └── __init__.cpython-311.pyc
│   │           │   │   │   ├── exceptions.py
│   │           │   │   │   ├── helpers.py
│   │           │   │   │   ├── results.py
│   │           │   │   │   ├── testing.py
│   │           │   │   │   ├── unicode.py
│   │           │   │   │   └── util.py
│   │           │   │   ├── pyproject_hooks/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _compat.cpython-311.pyc
│   │           │   │   │   │   └── _impl.cpython-311.pyc
│   │           │   │   │   ├── _compat.py
│   │           │   │   │   ├── _impl.py
│   │           │   │   │   └── _in_process/
│   │           │   │   │       ├── __init__.py
│   │           │   │   │       ├── __pycache__/
│   │           │   │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │   │       │   └── _in_process.cpython-311.pyc
│   │           │   │   │       └── _in_process.py
│   │           │   │   ├── requests/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __version__.cpython-311.pyc
│   │           │   │   │   │   ├── _internal_utils.cpython-311.pyc
│   │           │   │   │   │   ├── adapters.cpython-311.pyc
│   │           │   │   │   │   ├── api.cpython-311.pyc
│   │           │   │   │   │   ├── auth.cpython-311.pyc
│   │           │   │   │   │   ├── certs.cpython-311.pyc
│   │           │   │   │   │   ├── compat.cpython-311.pyc
│   │           │   │   │   │   ├── cookies.cpython-311.pyc
│   │           │   │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── help.cpython-311.pyc
│   │           │   │   │   │   ├── hooks.cpython-311.pyc
│   │           │   │   │   │   ├── models.cpython-311.pyc
│   │           │   │   │   │   ├── packages.cpython-311.pyc
│   │           │   │   │   │   ├── sessions.cpython-311.pyc
│   │           │   │   │   │   ├── status_codes.cpython-311.pyc
│   │           │   │   │   │   ├── structures.cpython-311.pyc
│   │           │   │   │   │   └── utils.cpython-311.pyc
│   │           │   │   │   ├── __version__.py
│   │           │   │   │   ├── _internal_utils.py
│   │           │   │   │   ├── adapters.py
│   │           │   │   │   ├── api.py
│   │           │   │   │   ├── auth.py
│   │           │   │   │   ├── certs.py
│   │           │   │   │   ├── compat.py
│   │           │   │   │   ├── cookies.py
│   │           │   │   │   ├── exceptions.py
│   │           │   │   │   ├── help.py
│   │           │   │   │   ├── hooks.py
│   │           │   │   │   ├── models.py
│   │           │   │   │   ├── packages.py
│   │           │   │   │   ├── sessions.py
│   │           │   │   │   ├── status_codes.py
│   │           │   │   │   ├── structures.py
│   │           │   │   │   └── utils.py
│   │           │   │   ├── resolvelib/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── providers.cpython-311.pyc
│   │           │   │   │   │   ├── reporters.cpython-311.pyc
│   │           │   │   │   │   ├── resolvers.cpython-311.pyc
│   │           │   │   │   │   └── structs.cpython-311.pyc
│   │           │   │   │   ├── compat/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   └── collections_abc.cpython-311.pyc
│   │           │   │   │   │   └── collections_abc.py
│   │           │   │   │   ├── providers.py
│   │           │   │   │   ├── reporters.py
│   │           │   │   │   ├── resolvers.py
│   │           │   │   │   └── structs.py
│   │           │   │   ├── rich/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   ├── _cell_widths.cpython-311.pyc
│   │           │   │   │   │   ├── _emoji_codes.cpython-311.pyc
│   │           │   │   │   │   ├── _emoji_replace.cpython-311.pyc
│   │           │   │   │   │   ├── _export_format.cpython-311.pyc
│   │           │   │   │   │   ├── _extension.cpython-311.pyc
│   │           │   │   │   │   ├── _inspect.cpython-311.pyc
│   │           │   │   │   │   ├── _log_render.cpython-311.pyc
│   │           │   │   │   │   ├── _loop.cpython-311.pyc
│   │           │   │   │   │   ├── _null_file.cpython-311.pyc
│   │           │   │   │   │   ├── _palettes.cpython-311.pyc
│   │           │   │   │   │   ├── _pick.cpython-311.pyc
│   │           │   │   │   │   ├── _ratio.cpython-311.pyc
│   │           │   │   │   │   ├── _spinners.cpython-311.pyc
│   │           │   │   │   │   ├── _stack.cpython-311.pyc
│   │           │   │   │   │   ├── _timer.cpython-311.pyc
│   │           │   │   │   │   ├── _win32_console.cpython-311.pyc
│   │           │   │   │   │   ├── _windows.cpython-311.pyc
│   │           │   │   │   │   ├── _windows_renderer.cpython-311.pyc
│   │           │   │   │   │   ├── _wrap.cpython-311.pyc
│   │           │   │   │   │   ├── abc.cpython-311.pyc
│   │           │   │   │   │   ├── align.cpython-311.pyc
│   │           │   │   │   │   ├── ansi.cpython-311.pyc
│   │           │   │   │   │   ├── bar.cpython-311.pyc
│   │           │   │   │   │   ├── box.cpython-311.pyc
│   │           │   │   │   │   ├── cells.cpython-311.pyc
│   │           │   │   │   │   ├── color.cpython-311.pyc
│   │           │   │   │   │   ├── color_triplet.cpython-311.pyc
│   │           │   │   │   │   ├── columns.cpython-311.pyc
│   │           │   │   │   │   ├── console.cpython-311.pyc
│   │           │   │   │   │   ├── constrain.cpython-311.pyc
│   │           │   │   │   │   ├── containers.cpython-311.pyc
│   │           │   │   │   │   ├── control.cpython-311.pyc
│   │           │   │   │   │   ├── default_styles.cpython-311.pyc
│   │           │   │   │   │   ├── diagnose.cpython-311.pyc
│   │           │   │   │   │   ├── emoji.cpython-311.pyc
│   │           │   │   │   │   ├── errors.cpython-311.pyc
│   │           │   │   │   │   ├── file_proxy.cpython-311.pyc
│   │           │   │   │   │   ├── filesize.cpython-311.pyc
│   │           │   │   │   │   ├── highlighter.cpython-311.pyc
│   │           │   │   │   │   ├── json.cpython-311.pyc
│   │           │   │   │   │   ├── jupyter.cpython-311.pyc
│   │           │   │   │   │   ├── layout.cpython-311.pyc
│   │           │   │   │   │   ├── live.cpython-311.pyc
│   │           │   │   │   │   ├── live_render.cpython-311.pyc
│   │           │   │   │   │   ├── logging.cpython-311.pyc
│   │           │   │   │   │   ├── markup.cpython-311.pyc
│   │           │   │   │   │   ├── measure.cpython-311.pyc
│   │           │   │   │   │   ├── padding.cpython-311.pyc
│   │           │   │   │   │   ├── pager.cpython-311.pyc
│   │           │   │   │   │   ├── palette.cpython-311.pyc
│   │           │   │   │   │   ├── panel.cpython-311.pyc
│   │           │   │   │   │   ├── pretty.cpython-311.pyc
│   │           │   │   │   │   ├── progress.cpython-311.pyc
│   │           │   │   │   │   ├── progress_bar.cpython-311.pyc
│   │           │   │   │   │   ├── prompt.cpython-311.pyc
│   │           │   │   │   │   ├── protocol.cpython-311.pyc
│   │           │   │   │   │   ├── region.cpython-311.pyc
│   │           │   │   │   │   ├── repr.cpython-311.pyc
│   │           │   │   │   │   ├── rule.cpython-311.pyc
│   │           │   │   │   │   ├── scope.cpython-311.pyc
│   │           │   │   │   │   ├── screen.cpython-311.pyc
│   │           │   │   │   │   ├── segment.cpython-311.pyc
│   │           │   │   │   │   ├── spinner.cpython-311.pyc
│   │           │   │   │   │   ├── status.cpython-311.pyc
│   │           │   │   │   │   ├── style.cpython-311.pyc
│   │           │   │   │   │   ├── styled.cpython-311.pyc
│   │           │   │   │   │   ├── syntax.cpython-311.pyc
│   │           │   │   │   │   ├── table.cpython-311.pyc
│   │           │   │   │   │   ├── terminal_theme.cpython-311.pyc
│   │           │   │   │   │   ├── text.cpython-311.pyc
│   │           │   │   │   │   ├── theme.cpython-311.pyc
│   │           │   │   │   │   ├── themes.cpython-311.pyc
│   │           │   │   │   │   ├── traceback.cpython-311.pyc
│   │           │   │   │   │   └── tree.cpython-311.pyc
│   │           │   │   │   ├── _cell_widths.py
│   │           │   │   │   ├── _emoji_codes.py
│   │           │   │   │   ├── _emoji_replace.py
│   │           │   │   │   ├── _export_format.py
│   │           │   │   │   ├── _extension.py
│   │           │   │   │   ├── _inspect.py
│   │           │   │   │   ├── _log_render.py
│   │           │   │   │   ├── _loop.py
│   │           │   │   │   ├── _null_file.py
│   │           │   │   │   ├── _palettes.py
│   │           │   │   │   ├── _pick.py
│   │           │   │   │   ├── _ratio.py
│   │           │   │   │   ├── _spinners.py
│   │           │   │   │   ├── _stack.py
│   │           │   │   │   ├── _timer.py
│   │           │   │   │   ├── _win32_console.py
│   │           │   │   │   ├── _windows.py
│   │           │   │   │   ├── _windows_renderer.py
│   │           │   │   │   ├── _wrap.py
│   │           │   │   │   ├── abc.py
│   │           │   │   │   ├── align.py
│   │           │   │   │   ├── ansi.py
│   │           │   │   │   ├── bar.py
│   │           │   │   │   ├── box.py
│   │           │   │   │   ├── cells.py
│   │           │   │   │   ├── color.py
│   │           │   │   │   ├── color_triplet.py
│   │           │   │   │   ├── columns.py
│   │           │   │   │   ├── console.py
│   │           │   │   │   ├── constrain.py
│   │           │   │   │   ├── containers.py
│   │           │   │   │   ├── control.py
│   │           │   │   │   ├── default_styles.py
│   │           │   │   │   ├── diagnose.py
│   │           │   │   │   ├── emoji.py
│   │           │   │   │   ├── errors.py
│   │           │   │   │   ├── file_proxy.py
│   │           │   │   │   ├── filesize.py
│   │           │   │   │   ├── highlighter.py
│   │           │   │   │   ├── json.py
│   │           │   │   │   ├── jupyter.py
│   │           │   │   │   ├── layout.py
│   │           │   │   │   ├── live.py
│   │           │   │   │   ├── live_render.py
│   │           │   │   │   ├── logging.py
│   │           │   │   │   ├── markup.py
│   │           │   │   │   ├── measure.py
│   │           │   │   │   ├── padding.py
│   │           │   │   │   ├── pager.py
│   │           │   │   │   ├── palette.py
│   │           │   │   │   ├── panel.py
│   │           │   │   │   ├── pretty.py
│   │           │   │   │   ├── progress.py
│   │           │   │   │   ├── progress_bar.py
│   │           │   │   │   ├── prompt.py
│   │           │   │   │   ├── protocol.py
│   │           │   │   │   ├── region.py
│   │           │   │   │   ├── repr.py
│   │           │   │   │   ├── rule.py
│   │           │   │   │   ├── scope.py
│   │           │   │   │   ├── screen.py
│   │           │   │   │   ├── segment.py
│   │           │   │   │   ├── spinner.py
│   │           │   │   │   ├── status.py
│   │           │   │   │   ├── style.py
│   │           │   │   │   ├── styled.py
│   │           │   │   │   ├── syntax.py
│   │           │   │   │   ├── table.py
│   │           │   │   │   ├── terminal_theme.py
│   │           │   │   │   ├── text.py
│   │           │   │   │   ├── theme.py
│   │           │   │   │   ├── themes.py
│   │           │   │   │   ├── traceback.py
│   │           │   │   │   └── tree.py
│   │           │   │   ├── six.py
│   │           │   │   ├── tenacity/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _asyncio.cpython-311.pyc
│   │           │   │   │   │   ├── _utils.cpython-311.pyc
│   │           │   │   │   │   ├── after.cpython-311.pyc
│   │           │   │   │   │   ├── before.cpython-311.pyc
│   │           │   │   │   │   ├── before_sleep.cpython-311.pyc
│   │           │   │   │   │   ├── nap.cpython-311.pyc
│   │           │   │   │   │   ├── retry.cpython-311.pyc
│   │           │   │   │   │   ├── stop.cpython-311.pyc
│   │           │   │   │   │   ├── tornadoweb.cpython-311.pyc
│   │           │   │   │   │   └── wait.cpython-311.pyc
│   │           │   │   │   ├── _asyncio.py
│   │           │   │   │   ├── _utils.py
│   │           │   │   │   ├── after.py
│   │           │   │   │   ├── before.py
│   │           │   │   │   ├── before_sleep.py
│   │           │   │   │   ├── nap.py
│   │           │   │   │   ├── retry.py
│   │           │   │   │   ├── stop.py
│   │           │   │   │   ├── tornadoweb.py
│   │           │   │   │   └── wait.py
│   │           │   │   ├── tomli/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _parser.cpython-311.pyc
│   │           │   │   │   │   ├── _re.cpython-311.pyc
│   │           │   │   │   │   └── _types.cpython-311.pyc
│   │           │   │   │   ├── _parser.py
│   │           │   │   │   ├── _re.py
│   │           │   │   │   └── _types.py
│   │           │   │   ├── typing_extensions.py
│   │           │   │   ├── urllib3/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _collections.cpython-311.pyc
│   │           │   │   │   │   ├── _version.cpython-311.pyc
│   │           │   │   │   │   ├── connection.cpython-311.pyc
│   │           │   │   │   │   ├── connectionpool.cpython-311.pyc
│   │           │   │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── fields.cpython-311.pyc
│   │           │   │   │   │   ├── filepost.cpython-311.pyc
│   │           │   │   │   │   ├── poolmanager.cpython-311.pyc
│   │           │   │   │   │   ├── request.cpython-311.pyc
│   │           │   │   │   │   └── response.cpython-311.pyc
│   │           │   │   │   ├── _collections.py
│   │           │   │   │   ├── _version.py
│   │           │   │   │   ├── connection.py
│   │           │   │   │   ├── connectionpool.py
│   │           │   │   │   ├── contrib/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   ├── _appengine_environ.cpython-311.pyc
│   │           │   │   │   │   │   ├── appengine.cpython-311.pyc
│   │           │   │   │   │   │   ├── ntlmpool.cpython-311.pyc
│   │           │   │   │   │   │   ├── pyopenssl.cpython-311.pyc
│   │           │   │   │   │   │   ├── securetransport.cpython-311.pyc
│   │           │   │   │   │   │   └── socks.cpython-311.pyc
│   │           │   │   │   │   ├── _appengine_environ.py
│   │           │   │   │   │   ├── _securetransport/
│   │           │   │   │   │   │   ├── __init__.py
│   │           │   │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   │   ├── bindings.cpython-311.pyc
│   │           │   │   │   │   │   │   └── low_level.cpython-311.pyc
│   │           │   │   │   │   │   ├── bindings.py
│   │           │   │   │   │   │   └── low_level.py
│   │           │   │   │   │   ├── appengine.py
│   │           │   │   │   │   ├── ntlmpool.py
│   │           │   │   │   │   ├── pyopenssl.py
│   │           │   │   │   │   ├── securetransport.py
│   │           │   │   │   │   └── socks.py
│   │           │   │   │   ├── exceptions.py
│   │           │   │   │   ├── fields.py
│   │           │   │   │   ├── filepost.py
│   │           │   │   │   ├── packages/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   └── six.cpython-311.pyc
│   │           │   │   │   │   ├── backports/
│   │           │   │   │   │   │   ├── __init__.py
│   │           │   │   │   │   │   ├── __pycache__/
│   │           │   │   │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   │   │   └── makefile.cpython-311.pyc
│   │           │   │   │   │   │   └── makefile.py
│   │           │   │   │   │   └── six.py
│   │           │   │   │   ├── poolmanager.py
│   │           │   │   │   ├── request.py
│   │           │   │   │   ├── response.py
│   │           │   │   │   └── util/
│   │           │   │   │       ├── __init__.py
│   │           │   │   │       ├── __pycache__/
│   │           │   │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │   │       │   ├── connection.cpython-311.pyc
│   │           │   │   │       │   ├── proxy.cpython-311.pyc
│   │           │   │   │       │   ├── queue.cpython-311.pyc
│   │           │   │   │       │   ├── request.cpython-311.pyc
│   │           │   │   │       │   ├── response.cpython-311.pyc
│   │           │   │   │       │   ├── retry.cpython-311.pyc
│   │           │   │   │       │   ├── ssl_.cpython-311.pyc
│   │           │   │   │       │   ├── ssl_match_hostname.cpython-311.pyc
│   │           │   │   │       │   ├── ssltransport.cpython-311.pyc
│   │           │   │   │       │   ├── timeout.cpython-311.pyc
│   │           │   │   │       │   ├── url.cpython-311.pyc
│   │           │   │   │       │   └── wait.cpython-311.pyc
│   │           │   │   │       ├── connection.py
│   │           │   │   │       ├── proxy.py
│   │           │   │   │       ├── queue.py
│   │           │   │   │       ├── request.py
│   │           │   │   │       ├── response.py
│   │           │   │   │       ├── retry.py
│   │           │   │   │       ├── ssl_.py
│   │           │   │   │       ├── ssl_match_hostname.py
│   │           │   │   │       ├── ssltransport.py
│   │           │   │   │       ├── timeout.py
│   │           │   │   │       ├── url.py
│   │           │   │   │       └── wait.py
│   │           │   │   ├── vendor.txt
│   │           │   │   └── webencodings/
│   │           │   │       ├── __init__.py
│   │           │   │       ├── __pycache__/
│   │           │   │       │   ├── __init__.cpython-311.pyc
│   │           │   │       │   ├── labels.cpython-311.pyc
│   │           │   │       │   ├── mklabels.cpython-311.pyc
│   │           │   │       │   ├── tests.cpython-311.pyc
│   │           │   │       │   └── x_user_defined.cpython-311.pyc
│   │           │   │       ├── labels.py
│   │           │   │       ├── mklabels.py
│   │           │   │       ├── tests.py
│   │           │   │       └── x_user_defined.py
│   │           │   └── py.typed
│   │           ├── pkg_resources/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   └── __init__.cpython-311.pyc
│   │           │   ├── _vendor/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── typing_extensions.cpython-311.pyc
│   │           │   │   │   └── zipp.cpython-311.pyc
│   │           │   │   ├── importlib_resources/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _adapters.cpython-311.pyc
│   │           │   │   │   │   ├── _common.cpython-311.pyc
│   │           │   │   │   │   ├── _compat.cpython-311.pyc
│   │           │   │   │   │   ├── _itertools.cpython-311.pyc
│   │           │   │   │   │   ├── _legacy.cpython-311.pyc
│   │           │   │   │   │   ├── abc.cpython-311.pyc
│   │           │   │   │   │   ├── readers.cpython-311.pyc
│   │           │   │   │   │   └── simple.cpython-311.pyc
│   │           │   │   │   ├── _adapters.py
│   │           │   │   │   ├── _common.py
│   │           │   │   │   ├── _compat.py
│   │           │   │   │   ├── _itertools.py
│   │           │   │   │   ├── _legacy.py
│   │           │   │   │   ├── abc.py
│   │           │   │   │   ├── readers.py
│   │           │   │   │   └── simple.py
│   │           │   │   ├── jaraco/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── context.cpython-311.pyc
│   │           │   │   │   │   └── functools.cpython-311.pyc
│   │           │   │   │   ├── context.py
│   │           │   │   │   ├── functools.py
│   │           │   │   │   └── text/
│   │           │   │   │       ├── __init__.py
│   │           │   │   │       └── __pycache__/
│   │           │   │   │           └── __init__.cpython-311.pyc
│   │           │   │   ├── more_itertools/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── more.cpython-311.pyc
│   │           │   │   │   │   └── recipes.cpython-311.pyc
│   │           │   │   │   ├── more.py
│   │           │   │   │   └── recipes.py
│   │           │   │   ├── packaging/
│   │           │   │   │   ├── __about__.py
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __about__.cpython-311.pyc
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _manylinux.cpython-311.pyc
│   │           │   │   │   │   ├── _musllinux.cpython-311.pyc
│   │           │   │   │   │   ├── _structures.cpython-311.pyc
│   │           │   │   │   │   ├── markers.cpython-311.pyc
│   │           │   │   │   │   ├── requirements.cpython-311.pyc
│   │           │   │   │   │   ├── specifiers.cpython-311.pyc
│   │           │   │   │   │   ├── tags.cpython-311.pyc
│   │           │   │   │   │   ├── utils.cpython-311.pyc
│   │           │   │   │   │   └── version.cpython-311.pyc
│   │           │   │   │   ├── _manylinux.py
│   │           │   │   │   ├── _musllinux.py
│   │           │   │   │   ├── _structures.py
│   │           │   │   │   ├── markers.py
│   │           │   │   │   ├── requirements.py
│   │           │   │   │   ├── specifiers.py
│   │           │   │   │   ├── tags.py
│   │           │   │   │   ├── utils.py
│   │           │   │   │   └── version.py
│   │           │   │   ├── platformdirs/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __main__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── __main__.cpython-311.pyc
│   │           │   │   │   │   ├── android.cpython-311.pyc
│   │           │   │   │   │   ├── api.cpython-311.pyc
│   │           │   │   │   │   ├── macos.cpython-311.pyc
│   │           │   │   │   │   ├── unix.cpython-311.pyc
│   │           │   │   │   │   ├── version.cpython-311.pyc
│   │           │   │   │   │   └── windows.cpython-311.pyc
│   │           │   │   │   ├── android.py
│   │           │   │   │   ├── api.py
│   │           │   │   │   ├── macos.py
│   │           │   │   │   ├── unix.py
│   │           │   │   │   ├── version.py
│   │           │   │   │   └── windows.py
│   │           │   │   ├── pyparsing/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── actions.cpython-311.pyc
│   │           │   │   │   │   ├── common.cpython-311.pyc
│   │           │   │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── helpers.cpython-311.pyc
│   │           │   │   │   │   ├── results.cpython-311.pyc
│   │           │   │   │   │   ├── testing.cpython-311.pyc
│   │           │   │   │   │   ├── unicode.cpython-311.pyc
│   │           │   │   │   │   └── util.cpython-311.pyc
│   │           │   │   │   ├── actions.py
│   │           │   │   │   ├── common.py
│   │           │   │   │   ├── core.py
│   │           │   │   │   ├── diagram/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   └── __pycache__/
│   │           │   │   │   │       └── __init__.cpython-311.pyc
│   │           │   │   │   ├── exceptions.py
│   │           │   │   │   ├── helpers.py
│   │           │   │   │   ├── results.py
│   │           │   │   │   ├── testing.py
│   │           │   │   │   ├── unicode.py
│   │           │   │   │   └── util.py
│   │           │   │   ├── typing_extensions.py
│   │           │   │   └── zipp.py
│   │           │   └── extern/
│   │           │       ├── __init__.py
│   │           │       └── __pycache__/
│   │           │           └── __init__.cpython-311.pyc
│   │           ├── pylab.py
│   │           ├── pyparsing-3.2.5.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   └── licenses/
│   │           │       └── LICENSE
│   │           ├── pyparsing/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── actions.cpython-311.pyc
│   │           │   │   ├── common.cpython-311.pyc
│   │           │   │   ├── core.cpython-311.pyc
│   │           │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   ├── helpers.cpython-311.pyc
│   │           │   │   ├── results.cpython-311.pyc
│   │           │   │   ├── testing.cpython-311.pyc
│   │           │   │   ├── unicode.cpython-311.pyc
│   │           │   │   └── util.cpython-311.pyc
│   │           │   ├── actions.py
│   │           │   ├── common.py
│   │           │   ├── core.py
│   │           │   ├── diagram/
│   │           │   │   ├── __init__.py
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── exceptions.py
│   │           │   ├── helpers.py
│   │           │   ├── py.typed
│   │           │   ├── results.py
│   │           │   ├── testing.py
│   │           │   ├── tools
│   │           │   ├── tools/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   └── cvt_pyparsing_pep8_names.cpython-311.pyc
│   │           │   │   └── cvt_pyparsing_pep8_names.py
│   │           │   ├── unicode.py
│   │           │   └── util.py
│   │           ├── python_dateutil-2.9.0.post0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   ├── top_level.txt
│   │           │   └── zip-safe
│   │           ├── setuptools-66.1.1.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── REQUESTED
│   │           │   ├── WHEEL
│   │           │   ├── entry_points.txt
│   │           │   └── top_level.txt
│   │           ├── setuptools/
│   │           │   ├── __init__.py
│   │           │   ├── __pycache__/
│   │           │   │   ├── __init__.cpython-311.pyc
│   │           │   │   ├── _deprecation_warning.cpython-311.pyc
│   │           │   │   ├── _entry_points.cpython-311.pyc
│   │           │   │   ├── _imp.cpython-311.pyc
│   │           │   │   ├── _importlib.cpython-311.pyc
│   │           │   │   ├── _itertools.cpython-311.pyc
│   │           │   │   ├── _path.cpython-311.pyc
│   │           │   │   ├── _reqs.cpython-311.pyc
│   │           │   │   ├── archive_util.cpython-311.pyc
│   │           │   │   ├── build_meta.cpython-311.pyc
│   │           │   │   ├── dep_util.cpython-311.pyc
│   │           │   │   ├── depends.cpython-311.pyc
│   │           │   │   ├── discovery.cpython-311.pyc
│   │           │   │   ├── dist.cpython-311.pyc
│   │           │   │   ├── errors.cpython-311.pyc
│   │           │   │   ├── extension.cpython-311.pyc
│   │           │   │   ├── glob.cpython-311.pyc
│   │           │   │   ├── installer.cpython-311.pyc
│   │           │   │   ├── launch.cpython-311.pyc
│   │           │   │   ├── logging.cpython-311.pyc
│   │           │   │   ├── monkey.cpython-311.pyc
│   │           │   │   ├── msvc.cpython-311.pyc
│   │           │   │   ├── namespaces.cpython-311.pyc
│   │           │   │   ├── package_index.cpython-311.pyc
│   │           │   │   ├── py34compat.cpython-311.pyc
│   │           │   │   ├── sandbox.cpython-311.pyc
│   │           │   │   ├── unicode_utils.cpython-311.pyc
│   │           │   │   ├── version.cpython-311.pyc
│   │           │   │   ├── wheel.cpython-311.pyc
│   │           │   │   └── windows_support.cpython-311.pyc
│   │           │   ├── _deprecation_warning.py
│   │           │   ├── _distutils/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _collections.cpython-311.pyc
│   │           │   │   │   ├── _functools.cpython-311.pyc
│   │           │   │   │   ├── _log.cpython-311.pyc
│   │           │   │   │   ├── _macos_compat.cpython-311.pyc
│   │           │   │   │   ├── _msvccompiler.cpython-311.pyc
│   │           │   │   │   ├── archive_util.cpython-311.pyc
│   │           │   │   │   ├── bcppcompiler.cpython-311.pyc
│   │           │   │   │   ├── ccompiler.cpython-311.pyc
│   │           │   │   │   ├── cmd.cpython-311.pyc
│   │           │   │   │   ├── config.cpython-311.pyc
│   │           │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   ├── cygwinccompiler.cpython-311.pyc
│   │           │   │   │   ├── debug.cpython-311.pyc
│   │           │   │   │   ├── dep_util.cpython-311.pyc
│   │           │   │   │   ├── dir_util.cpython-311.pyc
│   │           │   │   │   ├── dist.cpython-311.pyc
│   │           │   │   │   ├── errors.cpython-311.pyc
│   │           │   │   │   ├── extension.cpython-311.pyc
│   │           │   │   │   ├── fancy_getopt.cpython-311.pyc
│   │           │   │   │   ├── file_util.cpython-311.pyc
│   │           │   │   │   ├── filelist.cpython-311.pyc
│   │           │   │   │   ├── log.cpython-311.pyc
│   │           │   │   │   ├── msvc9compiler.cpython-311.pyc
│   │           │   │   │   ├── msvccompiler.cpython-311.pyc
│   │           │   │   │   ├── py38compat.cpython-311.pyc
│   │           │   │   │   ├── py39compat.cpython-311.pyc
│   │           │   │   │   ├── spawn.cpython-311.pyc
│   │           │   │   │   ├── sysconfig.cpython-311.pyc
│   │           │   │   │   ├── text_file.cpython-311.pyc
│   │           │   │   │   ├── unixccompiler.cpython-311.pyc
│   │           │   │   │   ├── util.cpython-311.pyc
│   │           │   │   │   ├── version.cpython-311.pyc
│   │           │   │   │   └── versionpredicate.cpython-311.pyc
│   │           │   │   ├── _collections.py
│   │           │   │   ├── _functools.py
│   │           │   │   ├── _log.py
│   │           │   │   ├── _macos_compat.py
│   │           │   │   ├── _msvccompiler.py
│   │           │   │   ├── archive_util.py
│   │           │   │   ├── bcppcompiler.py
│   │           │   │   ├── ccompiler.py
│   │           │   │   ├── cmd.py
│   │           │   │   ├── command/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _framework_compat.cpython-311.pyc
│   │           │   │   │   │   ├── bdist.cpython-311.pyc
│   │           │   │   │   │   ├── bdist_dumb.cpython-311.pyc
│   │           │   │   │   │   ├── bdist_rpm.cpython-311.pyc
│   │           │   │   │   │   ├── build.cpython-311.pyc
│   │           │   │   │   │   ├── build_clib.cpython-311.pyc
│   │           │   │   │   │   ├── build_ext.cpython-311.pyc
│   │           │   │   │   │   ├── build_py.cpython-311.pyc
│   │           │   │   │   │   ├── build_scripts.cpython-311.pyc
│   │           │   │   │   │   ├── check.cpython-311.pyc
│   │           │   │   │   │   ├── clean.cpython-311.pyc
│   │           │   │   │   │   ├── config.cpython-311.pyc
│   │           │   │   │   │   ├── install.cpython-311.pyc
│   │           │   │   │   │   ├── install_data.cpython-311.pyc
│   │           │   │   │   │   ├── install_egg_info.cpython-311.pyc
│   │           │   │   │   │   ├── install_headers.cpython-311.pyc
│   │           │   │   │   │   ├── install_lib.cpython-311.pyc
│   │           │   │   │   │   ├── install_scripts.cpython-311.pyc
│   │           │   │   │   │   ├── py37compat.cpython-311.pyc
│   │           │   │   │   │   ├── register.cpython-311.pyc
│   │           │   │   │   │   ├── sdist.cpython-311.pyc
│   │           │   │   │   │   └── upload.cpython-311.pyc
│   │           │   │   │   ├── _framework_compat.py
│   │           │   │   │   ├── bdist.py
│   │           │   │   │   ├── bdist_dumb.py
│   │           │   │   │   ├── bdist_rpm.py
│   │           │   │   │   ├── build.py
│   │           │   │   │   ├── build_clib.py
│   │           │   │   │   ├── build_ext.py
│   │           │   │   │   ├── build_py.py
│   │           │   │   │   ├── build_scripts.py
│   │           │   │   │   ├── check.py
│   │           │   │   │   ├── clean.py
│   │           │   │   │   ├── config.py
│   │           │   │   │   ├── install.py
│   │           │   │   │   ├── install_data.py
│   │           │   │   │   ├── install_egg_info.py
│   │           │   │   │   ├── install_headers.py
│   │           │   │   │   ├── install_lib.py
│   │           │   │   │   ├── install_scripts.py
│   │           │   │   │   ├── py37compat.py
│   │           │   │   │   ├── register.py
│   │           │   │   │   ├── sdist.py
│   │           │   │   │   └── upload.py
│   │           │   │   ├── config.py
│   │           │   │   ├── core.py
│   │           │   │   ├── cygwinccompiler.py
│   │           │   │   ├── debug.py
│   │           │   │   ├── dep_util.py
│   │           │   │   ├── dir_util.py
│   │           │   │   ├── dist.py
│   │           │   │   ├── errors.py
│   │           │   │   ├── extension.py
│   │           │   │   ├── fancy_getopt.py
│   │           │   │   ├── file_util.py
│   │           │   │   ├── filelist.py
│   │           │   │   ├── log.py
│   │           │   │   ├── msvc9compiler.py
│   │           │   │   ├── msvccompiler.py
│   │           │   │   ├── py38compat.py
│   │           │   │   ├── py39compat.py
│   │           │   │   ├── spawn.py
│   │           │   │   ├── sysconfig.py
│   │           │   │   ├── text_file.py
│   │           │   │   ├── unixccompiler.py
│   │           │   │   ├── util.py
│   │           │   │   ├── version.py
│   │           │   │   └── versionpredicate.py
│   │           │   ├── _entry_points.py
│   │           │   ├── _imp.py
│   │           │   ├── _importlib.py
│   │           │   ├── _itertools.py
│   │           │   ├── _path.py
│   │           │   ├── _reqs.py
│   │           │   ├── _vendor/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── ordered_set.cpython-311.pyc
│   │           │   │   │   ├── typing_extensions.cpython-311.pyc
│   │           │   │   │   └── zipp.cpython-311.pyc
│   │           │   │   ├── importlib_metadata/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _adapters.cpython-311.pyc
│   │           │   │   │   │   ├── _collections.cpython-311.pyc
│   │           │   │   │   │   ├── _compat.cpython-311.pyc
│   │           │   │   │   │   ├── _functools.cpython-311.pyc
│   │           │   │   │   │   ├── _itertools.cpython-311.pyc
│   │           │   │   │   │   ├── _meta.cpython-311.pyc
│   │           │   │   │   │   └── _text.cpython-311.pyc
│   │           │   │   │   ├── _adapters.py
│   │           │   │   │   ├── _collections.py
│   │           │   │   │   ├── _compat.py
│   │           │   │   │   ├── _functools.py
│   │           │   │   │   ├── _itertools.py
│   │           │   │   │   ├── _meta.py
│   │           │   │   │   └── _text.py
│   │           │   │   ├── importlib_resources/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _adapters.cpython-311.pyc
│   │           │   │   │   │   ├── _common.cpython-311.pyc
│   │           │   │   │   │   ├── _compat.cpython-311.pyc
│   │           │   │   │   │   ├── _itertools.cpython-311.pyc
│   │           │   │   │   │   ├── _legacy.cpython-311.pyc
│   │           │   │   │   │   ├── abc.cpython-311.pyc
│   │           │   │   │   │   ├── readers.cpython-311.pyc
│   │           │   │   │   │   └── simple.cpython-311.pyc
│   │           │   │   │   ├── _adapters.py
│   │           │   │   │   ├── _common.py
│   │           │   │   │   ├── _compat.py
│   │           │   │   │   ├── _itertools.py
│   │           │   │   │   ├── _legacy.py
│   │           │   │   │   ├── abc.py
│   │           │   │   │   ├── readers.py
│   │           │   │   │   └── simple.py
│   │           │   │   ├── jaraco/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── context.cpython-311.pyc
│   │           │   │   │   │   └── functools.cpython-311.pyc
│   │           │   │   │   ├── context.py
│   │           │   │   │   ├── functools.py
│   │           │   │   │   └── text/
│   │           │   │   │       ├── __init__.py
│   │           │   │   │       └── __pycache__/
│   │           │   │   │           └── __init__.cpython-311.pyc
│   │           │   │   ├── more_itertools/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── more.cpython-311.pyc
│   │           │   │   │   │   └── recipes.cpython-311.pyc
│   │           │   │   │   ├── more.py
│   │           │   │   │   └── recipes.py
│   │           │   │   ├── ordered_set.py
│   │           │   │   ├── packaging/
│   │           │   │   │   ├── __about__.py
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __about__.cpython-311.pyc
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _manylinux.cpython-311.pyc
│   │           │   │   │   │   ├── _musllinux.cpython-311.pyc
│   │           │   │   │   │   ├── _structures.cpython-311.pyc
│   │           │   │   │   │   ├── markers.cpython-311.pyc
│   │           │   │   │   │   ├── requirements.cpython-311.pyc
│   │           │   │   │   │   ├── specifiers.cpython-311.pyc
│   │           │   │   │   │   ├── tags.cpython-311.pyc
│   │           │   │   │   │   ├── utils.cpython-311.pyc
│   │           │   │   │   │   └── version.cpython-311.pyc
│   │           │   │   │   ├── _manylinux.py
│   │           │   │   │   ├── _musllinux.py
│   │           │   │   │   ├── _structures.py
│   │           │   │   │   ├── markers.py
│   │           │   │   │   ├── requirements.py
│   │           │   │   │   ├── specifiers.py
│   │           │   │   │   ├── tags.py
│   │           │   │   │   ├── utils.py
│   │           │   │   │   └── version.py
│   │           │   │   ├── pyparsing/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── actions.cpython-311.pyc
│   │           │   │   │   │   ├── common.cpython-311.pyc
│   │           │   │   │   │   ├── core.cpython-311.pyc
│   │           │   │   │   │   ├── exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── helpers.cpython-311.pyc
│   │           │   │   │   │   ├── results.cpython-311.pyc
│   │           │   │   │   │   ├── testing.cpython-311.pyc
│   │           │   │   │   │   ├── unicode.cpython-311.pyc
│   │           │   │   │   │   └── util.cpython-311.pyc
│   │           │   │   │   ├── actions.py
│   │           │   │   │   ├── common.py
│   │           │   │   │   ├── core.py
│   │           │   │   │   ├── diagram/
│   │           │   │   │   │   ├── __init__.py
│   │           │   │   │   │   └── __pycache__/
│   │           │   │   │   │       └── __init__.cpython-311.pyc
│   │           │   │   │   ├── exceptions.py
│   │           │   │   │   ├── helpers.py
│   │           │   │   │   ├── results.py
│   │           │   │   │   ├── testing.py
│   │           │   │   │   ├── unicode.py
│   │           │   │   │   └── util.py
│   │           │   │   ├── tomli/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── _parser.cpython-311.pyc
│   │           │   │   │   │   ├── _re.cpython-311.pyc
│   │           │   │   │   │   └── _types.cpython-311.pyc
│   │           │   │   │   ├── _parser.py
│   │           │   │   │   ├── _re.py
│   │           │   │   │   └── _types.py
│   │           │   │   ├── typing_extensions.py
│   │           │   │   └── zipp.py
│   │           │   ├── archive_util.py
│   │           │   ├── build_meta.py
│   │           │   ├── cli-32.exe
│   │           │   ├── cli-64.exe
│   │           │   ├── cli-arm64.exe
│   │           │   ├── cli.exe
│   │           │   ├── command/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── alias.cpython-311.pyc
│   │           │   │   │   ├── bdist_egg.cpython-311.pyc
│   │           │   │   │   ├── bdist_rpm.cpython-311.pyc
│   │           │   │   │   ├── build.cpython-311.pyc
│   │           │   │   │   ├── build_clib.cpython-311.pyc
│   │           │   │   │   ├── build_ext.cpython-311.pyc
│   │           │   │   │   ├── build_py.cpython-311.pyc
│   │           │   │   │   ├── develop.cpython-311.pyc
│   │           │   │   │   ├── dist_info.cpython-311.pyc
│   │           │   │   │   ├── easy_install.cpython-311.pyc
│   │           │   │   │   ├── editable_wheel.cpython-311.pyc
│   │           │   │   │   ├── egg_info.cpython-311.pyc
│   │           │   │   │   ├── install.cpython-311.pyc
│   │           │   │   │   ├── install_egg_info.cpython-311.pyc
│   │           │   │   │   ├── install_lib.cpython-311.pyc
│   │           │   │   │   ├── install_scripts.cpython-311.pyc
│   │           │   │   │   ├── py36compat.cpython-311.pyc
│   │           │   │   │   ├── register.cpython-311.pyc
│   │           │   │   │   ├── rotate.cpython-311.pyc
│   │           │   │   │   ├── saveopts.cpython-311.pyc
│   │           │   │   │   ├── sdist.cpython-311.pyc
│   │           │   │   │   ├── setopt.cpython-311.pyc
│   │           │   │   │   ├── test.cpython-311.pyc
│   │           │   │   │   ├── upload.cpython-311.pyc
│   │           │   │   │   └── upload_docs.cpython-311.pyc
│   │           │   │   ├── alias.py
│   │           │   │   ├── bdist_egg.py
│   │           │   │   ├── bdist_rpm.py
│   │           │   │   ├── build.py
│   │           │   │   ├── build_clib.py
│   │           │   │   ├── build_ext.py
│   │           │   │   ├── build_py.py
│   │           │   │   ├── develop.py
│   │           │   │   ├── dist_info.py
│   │           │   │   ├── easy_install.py
│   │           │   │   ├── editable_wheel.py
│   │           │   │   ├── egg_info.py
│   │           │   │   ├── install.py
│   │           │   │   ├── install_egg_info.py
│   │           │   │   ├── install_lib.py
│   │           │   │   ├── install_scripts.py
│   │           │   │   ├── launcher manifest.xml
│   │           │   │   ├── py36compat.py
│   │           │   │   ├── register.py
│   │           │   │   ├── rotate.py
│   │           │   │   ├── saveopts.py
│   │           │   │   ├── sdist.py
│   │           │   │   ├── setopt.py
│   │           │   │   ├── test.py
│   │           │   │   ├── upload.py
│   │           │   │   └── upload_docs.py
│   │           │   ├── config
│   │           │   ├── config/
│   │           │   │   ├── __init__.py
│   │           │   │   ├── __pycache__/
│   │           │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   ├── _apply_pyprojecttoml.cpython-311.pyc
│   │           │   │   │   ├── expand.cpython-311.pyc
│   │           │   │   │   ├── pyprojecttoml.cpython-311.pyc
│   │           │   │   │   └── setupcfg.cpython-311.pyc
│   │           │   │   ├── _apply_pyprojecttoml.py
│   │           │   │   ├── _validate_pyproject/
│   │           │   │   │   ├── __init__.py
│   │           │   │   │   ├── __pycache__/
│   │           │   │   │   │   ├── __init__.cpython-311.pyc
│   │           │   │   │   │   ├── error_reporting.cpython-311.pyc
│   │           │   │   │   │   ├── extra_validations.cpython-311.pyc
│   │           │   │   │   │   ├── fastjsonschema_exceptions.cpython-311.pyc
│   │           │   │   │   │   ├── fastjsonschema_validations.cpython-311.pyc
│   │           │   │   │   │   └── formats.cpython-311.pyc
│   │           │   │   │   ├── error_reporting.py
│   │           │   │   │   ├── extra_validations.py
│   │           │   │   │   ├── fastjsonschema_exceptions.py
│   │           │   │   │   ├── fastjsonschema_validations.py
│   │           │   │   │   └── formats.py
│   │           │   │   ├── expand.py
│   │           │   │   ├── pyprojecttoml.py
│   │           │   │   └── setupcfg.py
│   │           │   ├── dep_util.py
│   │           │   ├── depends.py
│   │           │   ├── discovery.py
│   │           │   ├── dist.py
│   │           │   ├── errors.py
│   │           │   ├── extension.py
│   │           │   ├── extern/
│   │           │   │   ├── __init__.py
│   │           │   │   └── __pycache__/
│   │           │   │       └── __init__.cpython-311.pyc
│   │           │   ├── glob.py
│   │           │   ├── gui-32.exe
│   │           │   ├── gui-64.exe
│   │           │   ├── gui-arm64.exe
│   │           │   ├── gui.exe
│   │           │   ├── installer.py
│   │           │   ├── launch.py
│   │           │   ├── logging.py
│   │           │   ├── monkey.py
│   │           │   ├── msvc.py
│   │           │   ├── namespaces.py
│   │           │   ├── package_index.py
│   │           │   ├── py34compat.py
│   │           │   ├── sandbox.py
│   │           │   ├── script (dev).tmpl
│   │           │   ├── script.tmpl
│   │           │   ├── unicode_utils.py
│   │           │   ├── version.py
│   │           │   ├── wheel.py
│   │           │   └── windows_support.py
│   │           ├── six-1.17.0.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   ├── WHEEL
│   │           │   └── top_level.txt
│   │           ├── six.py
│   │           ├── werkzeug-3.1.3.dist-info/
│   │           │   ├── INSTALLER
│   │           │   ├── LICENSE.txt
│   │           │   ├── METADATA
│   │           │   ├── RECORD
│   │           │   └── WHEEL
│   │           └── werkzeug/
│   │               ├── __init__.py
│   │               ├── __pycache__/
│   │               │   ├── __init__.cpython-311.pyc
│   │               │   ├── _internal.cpython-311.pyc
│   │               │   ├── _reloader.cpython-311.pyc
│   │               │   ├── exceptions.cpython-311.pyc
│   │               │   ├── formparser.cpython-311.pyc
│   │               │   ├── http.cpython-311.pyc
│   │               │   ├── local.cpython-311.pyc
│   │               │   ├── security.cpython-311.pyc
│   │               │   ├── serving.cpython-311.pyc
│   │               │   ├── test.cpython-311.pyc
│   │               │   ├── testapp.cpython-311.pyc
│   │               │   ├── urls.cpython-311.pyc
│   │               │   ├── user_agent.cpython-311.pyc
│   │               │   ├── utils.cpython-311.pyc
│   │               │   └── wsgi.cpython-311.pyc
│   │               ├── _internal.py
│   │               ├── _reloader.py
│   │               ├── datastructures/
│   │               │   ├── __init__.py
│   │               │   ├── __pycache__/
│   │               │   │   ├── __init__.cpython-311.pyc
│   │               │   │   ├── accept.cpython-311.pyc
│   │               │   │   ├── auth.cpython-311.pyc
│   │               │   │   ├── cache_control.cpython-311.pyc
│   │               │   │   ├── csp.cpython-311.pyc
│   │               │   │   ├── etag.cpython-311.pyc
│   │               │   │   ├── file_storage.cpython-311.pyc
│   │               │   │   ├── headers.cpython-311.pyc
│   │               │   │   ├── mixins.cpython-311.pyc
│   │               │   │   ├── range.cpython-311.pyc
│   │               │   │   └── structures.cpython-311.pyc
│   │               │   ├── accept.py
│   │               │   ├── auth.py
│   │               │   ├── cache_control.py
│   │               │   ├── csp.py
│   │               │   ├── etag.py
│   │               │   ├── file_storage.py
│   │               │   ├── headers.py
│   │               │   ├── mixins.py
│   │               │   ├── range.py
│   │               │   └── structures.py
│   │               ├── debug/
│   │               │   ├── __init__.py
│   │               │   ├── __pycache__/
│   │               │   │   ├── __init__.cpython-311.pyc
│   │               │   │   ├── console.cpython-311.pyc
│   │               │   │   ├── repr.cpython-311.pyc
│   │               │   │   └── tbtools.cpython-311.pyc
│   │               │   ├── console.py
│   │               │   ├── repr.py
│   │               │   ├── shared/
│   │               │   │   ├── ICON_LICENSE.md
│   │               │   │   ├── console.png
│   │               │   │   ├── debugger.js
│   │               │   │   ├── less.png
│   │               │   │   ├── more.png
│   │               │   │   └── style.css
│   │               │   └── tbtools.py
│   │               ├── exceptions.py
│   │               ├── formparser.py
│   │               ├── http.py
│   │               ├── local.py
│   │               ├── middleware/
│   │               │   ├── __init__.py
│   │               │   ├── __pycache__/
│   │               │   │   ├── __init__.cpython-311.pyc
│   │               │   │   ├── dispatcher.cpython-311.pyc
│   │               │   │   ├── http_proxy.cpython-311.pyc
│   │               │   │   ├── lint.cpython-311.pyc
│   │               │   │   ├── profiler.cpython-311.pyc
│   │               │   │   ├── proxy_fix.cpython-311.pyc
│   │               │   │   └── shared_data.cpython-311.pyc
│   │               │   ├── dispatcher.py
│   │               │   ├── http_proxy.py
│   │               │   ├── lint.py
│   │               │   ├── profiler.py
│   │               │   ├── proxy_fix.py
│   │               │   └── shared_data.py
│   │               ├── py.typed
│   │               ├── routing/
│   │               │   ├── __init__.py
│   │               │   ├── __pycache__/
│   │               │   │   ├── __init__.cpython-311.pyc
│   │               │   │   ├── converters.cpython-311.pyc
│   │               │   │   ├── exceptions.cpython-311.pyc
│   │               │   │   ├── map.cpython-311.pyc
│   │               │   │   ├── matcher.cpython-311.pyc
│   │               │   │   └── rules.cpython-311.pyc
│   │               │   ├── converters.py
│   │               │   ├── exceptions.py
│   │               │   ├── map.py
│   │               │   ├── matcher.py
│   │               │   └── rules.py
│   │               ├── sansio/
│   │               │   ├── __init__.py
│   │               │   ├── __pycache__/
│   │               │   │   ├── __init__.cpython-311.pyc
│   │               │   │   ├── http.cpython-311.pyc
│   │               │   │   ├── multipart.cpython-311.pyc
│   │               │   │   ├── request.cpython-311.pyc
│   │               │   │   ├── response.cpython-311.pyc
│   │               │   │   └── utils.cpython-311.pyc
│   │               │   ├── http.py
│   │               │   ├── multipart.py
│   │               │   ├── request.py
│   │               │   ├── response.py
│   │               │   └── utils.py
│   │               ├── security.py
│   │               ├── serving.py
│   │               ├── test.py
│   │               ├── testapp.py
│   │               ├── urls.py
│   │               ├── user_agent.py
│   │               ├── utils.py
│   │               ├── wrappers/
│   │               │   ├── __init__.py
│   │               │   ├── __pycache__/
│   │               │   │   ├── __init__.cpython-311.pyc
│   │               │   │   ├── request.cpython-311.pyc
│   │               │   │   └── response.cpython-311.pyc
│   │               │   ├── request.py
│   │               │   └── response.py
│   │               └── wsgi.py
│   ├── pyvenv.cfg
│   └── share/
│       └── man/
│           └── man1/
│               └── ttx.1
└── web_ui/
    ├── AccessPoint/
    │   └── AP_hotspot.py
    ├── app_server.py
    └── templates/
        └── dashboard.html

~~~
