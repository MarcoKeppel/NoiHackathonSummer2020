import base64
import sys
import serial
import time
from threading import Thread
from PIL import Image
from io import BytesIO


def imagePreprocessing(imgPath): # That's nasty
    print("Started image preprocessing")
    imageFile = Image.open(imgPath)
    imageFile.save("compressedImage.jpeg", "JPEG", optimize=True, quality=30)
    compressedImage = Image.open("compressedImage.jpeg")
    width, height = compressedImage.size
    downscaledImage = compressedImage.resize((int(width * 0.5), int(height * 0.5)), resample=Image.LANCZOS, box=None,
                                             reducing_gap=None)
    downscaledImage.save("downscaledImage.jpeg", "JPEG")
    print("Finished picture preprocessing")


def serializeFromPath(path):  # Serialize an image
    with open(path,"rb") as imageFile:
        s = base64.b64encode(imageFile.read())
    return s.decode('utf-8')


def serializeFromImage(imageFile):
    buffered = BytesIO()
    imageFile.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str


def serial_connection(serialized_text, port):  # Sends a serialized image over socket connection
    # print(serialized_text)
    arduino = serial.Serial(port, 115200, timeout=1)
    time.sleep(2)  # give the connection a second to settle
    start = time.time()
    block_size = 250
    arduino.timeout = 2
    print(serialized_text)

    while serialized_text != "" and len(serialized_text) != 0:
        tmp = serialized_text[:block_size]
        print(len(serialized_text))
        arduino.write(tmp+bytes("\n", "ascii"))
        arduino.flush()
        print("Inviato:" + tmp.decode("ascii"))

        # print("Printing: " + tmp)
        start2 = time.time()
        tmp = ""
        reset = False
        while tmp == '' or tmp==' ':
            if arduino.in_waiting > 0:
                tmp = arduino.read().decode("ascii")
            if time.time() - start2 > 3:
                reset = True
                print("reset!")
                break
        if not reset:
            serialized_text = serialized_text[block_size:]
        print("Exit on: " + tmp)
        # time.sleep(0.5)
    end = time.time()
    arduino.write(bytes("!!!!####", "ascii"))
    print("Elapsed time: " + str(end-start))



def send_image(path):
    im = Image.open("downscaledImage.jpeg")
    width, height = im.size
    # Setting the points for cropped image
    left = 0
    top = 0
    right = width
    bottom = height / 2

    # Cropped image of above dimension
    # (It will not change orginal image)
    im1 = im.crop((left, top, right, bottom))

    left = 0
    top = height / 2
    right = width
    bottom = height

    im2 = im.crop((left, top, right, bottom))

    # Thread(target=serial_connection, daemon=True, args=(serializeFromImage(im1), "/dev/ttyACM0")).start()
    # Thread(target=serial_connection, daemon=True, args=(serializeFromImage(im2), "/dev/ttyACM1")).start()
    Thread(target=thread, args=(im1, im2)).start()
    #serial_connection(serializeFromImage(im2)+, "/dev/ttyACM1")


def thread(im1, im2):
    serial_connection(serializeFromImage(im1), "/dev/ttyACM0")
    serial_connection(serializeFromImage(im2), "/dev/ttyACM1")


def main():
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        print("No path given, using default one")
        img_path = "img/landscape_00.jpg"
    print("Image path: " + img_path)
    imagePreprocessing(img_path)

    send_image(img_path)
    '''
    s1 = serializeFromPath("downscaledImage.jpeg")
    f1 = open("out1.txt","w")
    f1.write(s1)
    f1.close()

    im1 = Image.open("downscaledImage.jpeg")
    s2 = serializeFromImage(im1)
    f2 = open("out2.txt","wb")
    f2.write(s2)
    f2.close()
    '''
    # serial_connection(serialize("img/photo5866024388682429456.jpg"), "/dev/ttyACM0")
    # serial_connection(serialize("img/photo5866024388682429456.jpg"), "/dev/ttyACM1")
    # serial_connection(bytes("keppo", "ascii"))


if __name__ == "__main__":
    main()