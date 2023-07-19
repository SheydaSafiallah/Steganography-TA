import PySimpleGUI as sg
from Steganography import encode
from Steganography import decode

sg.theme('LightBlue1')

def mainGui():

    layout = [
        [sg.Button("Encode", pad=(85, 5))],
        [sg.Button("Decode", pad=(85, 5))]
    ]
    mainWindow = sg.Window("Encode/Decode", layout, size=(280, 100))
    while True:
        event, values = mainWindow.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "Encode":
            encode()
        elif event == "Decode":
            decode()

# ----------------------------------Decode Phase-----------------------------------#
def decodeGui():
    layout = [
        [sg.Text("Enter the number of images")],
        [sg.Text("that you want to decode:     "), sg.Input()],
        [sg.Text("key:     "), sg.Input()],
        [sg.Button("Next", pad=(80, 20))]

    ]
    decodeWindow = sg.Window("Hidden Message", layout, size=(250, 150))
    event, values = decodeWindow.read()
    if event == "Next":
        return values


def writePaths():
    layout = [
        [sg.Text("Write Image Path", justification='center', size=(100, 1), font=12)],
        [sg.Text("file path", font=20), sg.InputText(pad=10)],
        [sg.Button("Next", pad=(135, 20))]
    ]
    writePathWindow = sg.Window("Choose Path", layout, size=(400, 400))
    event, value = writePathWindow.read()
    if event == "Next":
        return value


def showMessage(msg):
    layout = [
        [sg.Text("This is the hidden message:", justification='center', size=(100, 1), font=12)],
        [sg.Button("show")],
        [sg.Multiline(size=(300, 10), key='message')]
    ]
    showMessageWindow = sg.Window("Hidden Message", layout, size=(400, 200))
    while True:
        event, values = showMessageWindow.read()
        if event == sg.WIN_CLOSED:
            break
        showMessageWindow.find_element('message').update(msg)


# ----------------------------------End of Decode Phase-----------------------------------#


# ----------------------------------Encode Phase-----------------------------------#
def encodeGui():
    layout = [
        [sg.Text("Text", font=20), sg.Multiline(size=(300, 10))],
        [sg.Text("Key", font=20), sg.InputText(pad=10)],
        [sg.Text('choose cover image:', pad=(20)), sg.FileBrowse()],
        [sg.Text('choose a path:', pad=(20)), sg.InputText(pad=10)],
        [sg.Button("Next", pad=(160, 10))]
    ]
    encodeWindow = sg.Window("Encode", layout, size=(400, 380))
    event, values = encodeWindow.read()
    if event == "Next":
        return values


def chooseImagePath():
    layout = [
        [sg.Text('choose a cover image:', pad=(20)), sg.FileBrowse()],
        [sg.Text('choose a path:', pad=(20)), sg.InputText(pad=10)],
        [sg.Button("ok", pad=(100,10))]
    ]
    choosePathsWindow = sg.Window("chooseFile",layout,size=(280,200))
    event , value = choosePathsWindow.read()
    if event == "ok":
        return value


# ----------------------------------End of Encode Phase-----------------------------------#


# ----------------------------------Message Phase-----------------------------------#
def popupMessage(msg):
    sg.popup(msg)
# ----------------------------------End of Message Phase-----------------------------------#


if __name__ == "__main__":
    mainGui()
