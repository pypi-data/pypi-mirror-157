### selenium_shortcuts
Shortcut functions for Python selenium

Installation:
`pip install selenium_shortcuts`

Usage:
```
from selenium_shortcuts import setup

helper = setup(driver) # Put this after you define the webdriver
find, finds, click, text, send = helper.find, helper.finds, helper.click, helper.text, helper.send

info = text('#info')
print(info)

click('#submit')

info = find('#info')
print(info.text)
info.click()

items = finds('.items')
for item in items:
	print(item.text)

 info, classes = find('#info', attribute='class')
print(classes)
```
