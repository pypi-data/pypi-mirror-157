# Python client
The Python Selenium Session Client (SSC) integrates into your tests, retrieves the session information from the Selenium Session Server and applies the session cookies into the running selenium browser.

Note that support to the Selenium Session Manager and its components is available at the BlinqIO forum: https://community.blinq.io/ .

Following is a code example to integrate it into your Python Selenium tests:
```python
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_session_client.session_client import init_session

def test():
    driver = webdriver.Chrome('chromedriver')
    init_session(driver, ['github'])
    driver.get("https://github.com/")
    sleep(5)
    driver.quit()

test()
```

To add the dependencies into your project:
### PIP
```bash
pip install selenium-session-client
```
