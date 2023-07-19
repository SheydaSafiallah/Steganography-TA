import binascii
from cv2 import imread, imwrite, cv2
import Gui


def main():
    Gui.mainGui()

#to hide message in picture
def encode():
    #get information from gui
    values = Gui.encodeGui()
    secret_txt = values[0]
    key = values[1]
    ip_path = values['Browse']
    op_path = values[2]
    #convert to binary
    bin_txt = bin(int(binascii.hexlify(bytes(secret_txt, 'utf-8')), 16))[2:]
    #find length of message
    length_msg = 32 + len(secret_txt) * 8 - 1
    #make key
    arr_key = parse_key(key)
    #variable to check bits in steganography
    total_bits = 0
    completed_total = False
    i_key = 0
    modified_bits = 0

    while not completed_total:
        #get image
        try:
            img = imread(ip_path)
            height, width = img.shape[0], img.shape[1]
        except AttributeError or IOError:
            error = 'Input path not valid. Couldn\'t read file.\n'
            Gui.popupMessage(error)
            return

        #check capacity to save text in 1 or more images
        encoding_capacity = height * width
        total_bits += encoding_capacity

        if length_msg <= encoding_capacity:
            length_txt = bin(length_msg - 32)[2:].zfill(32)
            bin_txt_cur = bin_txt
            completed_total = True

        else:
            length_txt = bin(encoding_capacity - 32)[2:].zfill(32)
            length_msg = length_msg - encoding_capacity + 32
            bin_txt_cur = bin_txt[:(encoding_capacity - 32)]
            bin_txt = bin_txt[(encoding_capacity - 32):]
        #implement of algorithm
        msg = iter(length_txt + bin_txt_cur)
        completed_pic = False
        for i in range(height):
            for j in range(width):

                red = img[i, j, 0]
                green = img[i, j, 1]
                blue = img[i, j, 2]
                try:
                    x = next(msg)
                except StopIteration:
                    completed_pic = True
                    break
                if red % 2 != int(arr_key[i_key]):
                    if x == '0' and green % 2 == 1:
                        green -= 1
                        modified_bits += 1
                    elif x == '1' and green % 2 == 0:
                        green += 1
                        modified_bits += 1
                else:
                    if x == '0' and blue % 2 == 1:
                        blue -= 1
                        modified_bits += 1
                    elif x == '1' and blue % 2 == 0:
                        blue += 1
                        modified_bits += 1
                img[i, j, 1] = green
                img[i, j, 2] = blue
                i_key += 1
                if i_key == len(arr_key):
                    i_key = 0
            if completed_pic:
                break

        try:
            imwrite(op_path, img)
        except cv2.error:
            error = 'Output path not valid. Couldn\'t write file.\n'
            Gui.popupMessage(error)
            return

        if not completed_total:
            valeus = Gui.chooseImagePath()
            ip_path = valeus['Browse']
            op_path = valeus[0]

    str = (f'{modified_bits} bits out of {total_bits} bits were modified({round(modified_bits/total_bits * 100, 2)}%)')
    error = 'encoded successfully!\n'+ str
    Gui.popupMessage(error)

#encode image - to show message in image
def decode():
    #get values from gui
    values = Gui.decodeGui()
    num = values[0]
    key = values[1]
    #parse the key
    arr_key = parse_key(key)
    #variable to check data
    bin_txt = ''
    i_key = 0

    #implement of algorithm
    for n in range(int(num)):
        path = Gui.writePaths()
        try:
            img = imread(path[0])
            height, width = img.shape[0], img.shape[1]
        except AttributeError or IOError:
            error = 'Input path not valid. Couldn\'t read file.\n'
            Gui.popupMessage(error)
            return

        extracted_bits = 0
        completed = False
        length_txt = None
        for i in range(height):
            for j in range(width):

                red = img[i, j, 0]
                green = img[i, j, 1]
                blue = img[i, j, 2]

                if red % 2 != int(arr_key[i_key]):
                    bin_txt += str(green % 2)
                else:
                    bin_txt += str(blue % 2)
                extracted_bits += 1
                if extracted_bits == 32 and length_txt is None:
                    length_txt = int(bin_txt[len(bin_txt) - 32:], 2)
                    bin_txt = bin_txt[:len(bin_txt) - 32]
                    extracted_bits = 0
                i_key += 1
                if i_key == len(arr_key):
                    i_key = 0
                elif extracted_bits == length_txt:
                    completed = True
                    break
            if completed:
                break

    msg = format(binascii.unhexlify(hex(int(bin_txt, 2))[2:]).decode());
    Gui.showMessage(msg)

#parser
def parse_key(key):
    bin_key = iter(bin(int(binascii.hexlify(bytes(key, 'utf-8')), 16))[2:])
    length_key = len(key) * 8 -1
    arr_key = []
    for i in range(length_key-1):
        arr_key.append(next(bin_key))
    return arr_key


if __name__ == "__main__":
    main()
