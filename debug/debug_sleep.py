from lib.waveshare_epd import epd2in13_V3

if __name__ == "__main__":
    epd = epd2in13_V3.EPD()
    epd.init()
    epd.sleep()