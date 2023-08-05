import webcolors as wc
from requests import get, post
from time import sleep

class wled:
    def __init__(self, ip, port="80"):
        self.ip = ip
        self.port = port
        
    def get_status(self):
        return get(f"http://{self.ip}/json").json()
        
    def onOff(self, master):
        if master.lower() == "on":
            post(f"http://{self.ip}/win&T=1")
        if master.lower() == "off":
            post(f"http://{self.ip}/win&T=0")
        if master.lower() == "toggle":
            post(f"http://{self.ip}/win&T=2")
        
    def get_bri(self):
        return get(f"http://{self.ip}/json/state").json()["bri"]
    
    def set_bri(self, bri):
        post(f"http://{self.ip}/win&A={bri}")
        
    def get_col(self):
        return get(f"http://{self.ip}/json").json()["state"]["seg"][0]["col"][0]

    
    def set_col(self, col):
        if type(col) == str:
            col = wc.name_to_rgb(col)
            post(f"http://{self.ip}/win&R={col[0]}&G={col[1]}&B={col[2]}")
        else:
            post(f"http://{self.ip}/win&R={col[0]}&G={col[1]}&B={col[2]}")
            
    def get_fx(self):
        fx = get(f"http://{self.ip}/json").json()["state"]["seg"][0]["fx"]
        effects = get(f"http://{self.ip}/json").json()["effects"]
        return effects[fx]
    
    def set_fx(self, efx):
        if type(efx) == str:
            efx = efx.capitalize()
            effects = get(f"http://{self.ip}/json").json()["effects"]
            index = effects.index(efx)
            post(f"http://{self.ip}/win&FX={index}")
        else:
            post(f"http://{self.ip}/win&FX={efx}")
            
    def get_speed(self):
        return get(f"http://{self.ip}/json").json()["state"]["seg"][0]["sx"]
    
    def set_speed(self, speed):
        post(f"http://{self.ip}/win&SX={speed}")
    
    def blink(self, col="red", time=2):
        oldColor = self.get_col()
        effects = get(f"http://{self.ip}/json").json()["effects"]
        index = effects.index(self.get_fx())
        oldSpeed = self.get_speed()
        
        if time <= 1:
            time = 1
        
        if type(col) == str:
            col = wc.name_to_rgb(col)
            
        post(f"http://{self.ip}/win&R={col[0]}&G={col[1]}&B={col[2]}&FX=1&SX=230")
        sleep(time)
        post(f"http://{self.ip}/win&R={oldColor[0]}&G={oldColor[1]}&B={oldColor[2]}&FX={index}&SX={oldSpeed}")
        
        
            
    
if __name__ == '__main__':
    wled = wled('192.168.1.180')
    wled.blink("green")