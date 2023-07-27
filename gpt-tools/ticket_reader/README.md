# Tickets OCR reader
This tool can read parking ticket data from camera using OCR and ChatGPT. This is real case

## Requirments
+ opencv-python
+ pytesseract
+ numpy
+ tesseract binary (specify path in line 19)
+ tesseract trained data for your language (default Deustch)

## Limitations
+ OCR is very glitchy if lightning is bad or ticket contains fonts with very different size
+ Ticket can be read only on one language per run. Language can be specified in line 20
+ Multithreading not realized

## Usage
Read tickets will be saved in CSV file with name specified on line 24, it will contain columns **End date**, **End time**, **Price**, **Parking**. After every ticket wait 15-20 seconds until it'll be processed

## Examples
This tickets was tested:

![photo_2023-07-27_18-37-36](https://github.com/spbupos/projects-database/assets/105380669/f904a2ba-eefa-42c4-aa8e-e8d6db528eed)
![photo_2023-07-27_18-37-52](https://github.com/spbupos/projects-database/assets/105380669/ccefbca7-dd54-4008-8a6d-6d801c77dd67)
