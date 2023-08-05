This is a very simple WLed controller, which can be used to control a single WLed or multiple WLed.

dont call funtions fast after each other 
this is still a work in progress 

setup:
    - import WLedControl as wlc
    - create a WLed object with "wled = wlc.WLed(ip, port(optional))"

Control lights
    to turn it on or off or toggle:
        use: onOff()
            choses are ["on", "off", "toggle"]

Control brightness
    to get the brightness:
        use: get_bri()

    to set the brightness:
        use set_bri()
            with a value between 0 and 255

Control color
    to get the color:
        use: get_col()
            you will get the RGB values

    to set the color:
        use: set_col() 
            with the RGB values or a color name

Control effect
    to get the effect:
        use: get_fx()

    to set the effect:
        use: set_fx()
            with a value between 0 and 101 or the name of the effect

Control speed
    to set speed:
        use: set_speed()
            with a value between 0 and 255

Exstre funtions:
    to get the current status:
        use: get_status()
            you will get a all information about the current status of WLed

    use blink funtion:
        use: blink()
            color is optional default is red, time is optional default is 2 minimum is 2
            exsample: blink("green", 3)
            exsample: blink("green")
            exsample: blink(, 3)
