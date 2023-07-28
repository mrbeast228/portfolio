# Web activity generator
Script for headless opening and scrolling websites and generating activity

## Functions
+ open website in background
+ simulate different traffic sources (using UTM)
+ adjust scrolling time and speed
+ use proxy
+ _work in multithreaded mode (TODO)_

## Requirments
+ Python 3.6+
+ selenium
+ selenium-wire
+ argparse

## Usage
```
python3 activity_generator.py --url [-t SECONDS] [-r TIMES] [-p path/to/file.txt]
```
+ `--url` - URL of site to generate activity
+ `-t` - time of scrolling the page in secs, script will automatically count speed of scrolling based on it. Default is 100
+ `-r` - how much times script should reopen page using different proxies and sources. Default is 10
+ `-p` - path to file with list of proxy. It should have next format (one proxy per line, at least one proxy needed):
  ```
  <addr> <port> <user> <passwd>
  1.2.3.4 8080 username password
  5.6.7.8 9090 user pwd
  ...
  ```

## Tips
+ Script automatically and randomly simulates the source of opening the site, such as media networks and search systems, using UTM parameters
+ Script automatically and randomly selects proxy from list for each (re)opening of web page
+ Internal class `Selener` and function `scroller` can be imported from other modules and be used, for example, in telegram bots
