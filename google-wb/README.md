# Google API thin-client (and PoC integration with Wildberries)
This directory contains Python module with GoogleAPI class, which you can use to work with Google Spreadsheets (wrapped most useful methods), and Wildberries question-answer module

## Requirments
+ Python 3.7+
+ google-api-python-client
+ google-auth-httplib2
+ google-auth-oauthlib
+ argparse (for WB)

## Usage
GoogleAPI module is not standalone module - it doesn't contain main '__main\__' function, it's intended to be imported from another modules:
```
from google_api import GoogleAPI
google = GoogleAPI(configFile=path/to/config.json)
```
This realization uses services accounts, which authorize via JSON token-files, so module should be configured to use it. Before usage configuration should be placed in JSON file, and path to it should be specified in class initialization. By default modules use 'google_config.json' near itself as configuration. Configuration must have 3 fields:
+ serviceFile - path to service account JSON
+ spreadId - ID of spreadsheet which will be used
+ defaultSheet - not necessary - name of sheet to use by default

Example of configuration is placed in _google\_config.json_ in current directory.

## Methods
GoogleAPI class have next methods (italic parametes are unnecessary):
+ `read(range: str, _sheet: str_) -> list` - reads table fromm sheet from range and return list of rows. Here and further range have format 'A1:H10' (as in Excel, from cell to cell), and id _sheet_ not specified, reads from **defaultSheet** from configuration
+ `bufferizeSheet(_sheet: str_)` - reads entire table into 2-dimensional list in **self.currentSheet**. Useful when need analyze data
+ `write(range: str, table: list, _sheet: str_)` - writes table (must be 2-dimensional list) to range. If table is smaller than specified range - writes starting from left upper cell, if bigger - raises exception
+ `appendRows(rows: list, _sheet: str_)` - append rows (must be 2-dimensional list) to bottom of current data
+ `listSheets()` - creates dict with pairs 'sheetName - sheetId' in _self.currentSheet_, service function, useful only for _batchUpdate_ Google API method (which used in next method)
+ `removeRow(rowNum: int, _sheet: str_)` - removes row by it number (entire row, not only data in it, to remove data write spaces to range 'A{rowNum}:Z{rowNum}')

## Examples

We will use next sheet:
![Снимок экрана от 2023-07-27 17-25-39](https://github.com/spbupos/projects-database/assets/105380669/1e02b44a-c788-4a18-b73b-8f8d51952409)
+ read from sheet
```
>>> from google_api import GoogleAPI
>>> google = GoogleAPI()
>>> google.read('A1:B2')
[['a', 'b '], ['1', '2']]
```
+ write to sheet
```
>>> google.write('A1:C3', [['B' for i in range(3)] for j in range(3)])
```
Result:

![Снимок экрана от 2023-07-27 17-30-28](https://github.com/spbupos/projects-database/assets/105380669/8e350371-f7ed-4d48-8a63-7414e58daf59)
+ append rows
```
>>> google.appendRows([['bebra' for i in range(3)] for j in range(2)])
```
Result:

![Снимок экрана от 2023-07-27 17-33-20](https://github.com/spbupos/projects-database/assets/105380669/e2364408-6b45-46c5-9409-5dfbe4afd4a2)
+ remove row:
```
>>> google.removeRow(1)
```
Result:

![Снимок экрана от 2023-07-27 17-34-30](https://github.com/spbupos/projects-database/assets/105380669/7145c279-78bb-4407-b4b6-cf99a9ece41f)

## Wildberries integration
This scripts loads all questions and feedbacks from multi WB accounts, loads answers from Spreadsheets and send them back to WB

### Usage
```
./question_collector.py --wb-token-file TOKEN_FILE
```
where TOKEN_FILE - text file with list of Wildberries access tokens, one token per line. Script will use data from all of them.
By default, scripts load all questions and feedbacks, and split them into 4 sheets:
+ Вопросы новые - unanswered questions
+ Вопросы все - all questions
+ Отзывы новые - unanswered feedbacks
+ Отзывы все - all feeadbacks

The intercation is happening only with unanswered. There is example of such sheet: ![photo_2023-07-27_17-44-31](https://github.com/spbupos/projects-database/assets/105380669/c36a8652-51d6-4dd2-a84a-497e1976ca05)

To answer the question/feedback, write answer to 'Ответ' column and 'Да' in 'Отвечено'. This is real case I worked
