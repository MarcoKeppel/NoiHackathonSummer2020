import serial
import base64
import time
from PIL import Image
from threading import Thread
from io import BytesIO
import time

imgSlices = []

def de_serialize(imgstring, save=False, path=None):  # Convert a serialized image to a PIL image
    #print(imgstring)
    imgdata = Image.open(BytesIO(base64.b64decode(imgstring)))
    #imgdata = base64.b64decode(imgstring)
    #image = Image.open(imgdata)
    
    if save is True:
        if path is None:
            path = "img/output.jpg"
        with open(path, 'wb') as f:
            f.write(imgdata)
    imgSlices.append(imgdata)
    return imgdata


def render_image(img):  # Display the image
    img.show()


def listen(port):  # Listen to port event
    arduino = serial.Serial(port, 115200, timeout=1)
    time.sleep(2)  # give the connection a second to settle
    print("Socket successfully activated")
    content = ""
    while True:
        if arduino.in_waiting > 0: #Check whether data has been aldready sent or not 
            tmp = arduino.read().decode("ascii")
            content += tmp
            #print(content)
            #print(content[:-8])
            if content[-8:] == "!!!!####": #Check whether we arrived at the end of sequence
                render_image(de_serialize(content[:-8]))

if __name__ == "__main__":
    #Two threads are started and are listening on serial ports
    Thread(target=listen, args=("COM3",)).start()
    Thread(target=listen, args=("COM4",)).start()

    while len(imgSlices) != 2: 
        time.sleep(1)
    
    #Merge the two separated pictures together
    width0 , height0 = imgSlices[0].size
    width1 , height1 = imgSlices[1].size
    mergedPictures = Image.new('RGB', (width0, height0 + height1))
    mergedPictures.paste(imgSlices[0],(0,0))
    mergedPictures.paste(imgSlices[1],(0,height0))

    #Picture upscaling
    output = mergedPictures.resize((width0*2,(height0+height1)*2),resample=Image.LANCZOS, box=None, reducing_gap=None)
    output.save("output.jpeg","JPEG")
    output.show()