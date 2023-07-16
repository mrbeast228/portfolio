import openai
import cv2
import pytesseract
import sys
import numpy as np

openai.api_key = 'YOUR OPENAI TOKEN HERE'

def requestGpt(ocrText):
    taskDesc = "I have some photos of parking tickets, which contains information about their end date, end time, price and parking zone. I used OCR to read text from them, but it's unformatted. It also sometimes contains glitches. I need you to automatically extract information from this text. Please give me information about end date, end time, price and parking zone of ticket. Other information should be stripped. Please note that price may be damaged - it's in euros and around 1 euro. Here is the OCR-read text:\n"
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": taskDesc + ocrText}
      ]
    )
    return completion.choices[0].message.content

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
config = ('-l deu')
camera = cv2.VideoCapture(0)

columns = ['Date', 'End Time', 'Price', 'Parking Zone']
file = open('out_data_1.csv', 'w', newline ='')

original_stdout = sys.stdout
sys.stdout = file
print('"', end='')
print(*columns, sep='","', end='')
print('"')

while True:
    ret, frame = camera.read()
    beta = 100
    #frame = cv2.imread(sys.argv[1])
    submonoch = cv2.addWeighted(frame, 1.2, frame, 0, -beta)

    subtest = pytesseract.image_to_string(submonoch, config=config).lower()
    if 'ischl' in subtest or 'magistrat' in subtest:
        (thresh, monoch) = cv2.threshold(cv2.cvtColor(cv2.addWeighted(submonoch, 1, submonoch, 0, beta), cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
    else:
        monoch = submonoch

    pretext = pytesseract.image_to_string(monoch, config=config)
    if not pretext:
        continue
    sys.stdout = original_stdout
    print('Ticket detected, please wait 15 seconds!')
    sys.stdout = file

    gptAnswer = requestGpt(pretext)
    if ':' not in gptAnswer:
        continue # no data detected by ChatGPT
    gptData = gptAnswer.splitlines()
    result = ['' for i in range(4)]
    for line in gptData:
        if line.startswith('End date'):
            result[0] = line.split(': ')[1]
            continue
        if line.startswith('End time'):
            result[1] = line.split(': ')[1]
            continue
        if line.startswith('Price'):
            result[2] = line.split(': ')[1]
            continue
        if line.startswith('Parking'):
            result[3] = line.split(': ')[1]
            continue
    print('"', end='')
    print(*result, sep='","', end='')
    print('"')

file.close()
sys.stdout = original_stdout
