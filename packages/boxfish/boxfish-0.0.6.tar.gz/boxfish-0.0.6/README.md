<img src="boxfish.svg" width="100%" alt="">

# boxfish: lightweight table extraction from HTML

[![PyPI](https://img.shields.io/pypi/v/boxfish)](https://img.shields.io/pypi/v/boxfish)
[![PyPI - Status](https://img.shields.io/pypi/status/boxfish)](https://img.shields.io/pypi/status/boxfish)
[![PyPI - License](https://img.shields.io/pypi/l/boxfish)](https://img.shields.io/pypi/l/boxfish)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/boxfish)](https://img.shields.io/pypi/pyversions/boxfish)

[![GitHub top language](https://img.shields.io/github/languages/top/peterkorteweg/peterkorteweg)](https://img.shields.io/github/languages/top/peterkorteweg/boxfish)

### What is it?
Boxfish is a lightweight tool for table extraction from HTML pages. 

### Main features

- Easy configuration. No knowledge of CSS or Xpaths required.
- Fast table extraction to CSV files.
- Integration of `requests` and `selenium`.

### Quick start


``` python
import boxfish as bf
import pandas as pd

# Define table layout of an url with strings from two rows.
aurl = ''
row1 = ''
row2 = ''

# Build a configuration 
aconfig = bf.build(url=aurl, astr = [row1, row2])

# Extract a table
data = bf.extract(aconfig, url=aurl)

# View results
df = pd.DataFrame(data)
df.head() 
```

### Where to get it?
Boxfish is available on [Pypi](https://pypi.org/project/boxfish/) and [Github](https://github.com/peterkorteweg/boxfish/).

```
pip install boxfish
```

### Dependencies

The main dependencies are:
- [**BeautifulSoup4**](https://pypi.org/project/beautifulsoup4/), a Python library for pulling data out of HTML and XML files.
- [**lxml**](https://pypi.org/project/lxml/), a powerful and Pythonic XML processing library.
- [**Requests**](https://pypi.org/project/requests/), a simple, yet elegant, HTTP library.
- [**Selenium**](https://pypi.org/project/selenium/), automated web browser interaction from Python.


### License
Boxfish is available with an [MIT license](https://github.com/peterkorteweg/boxfish/blob/main/LICENSE).

### Limitations

Boxfish extracts text from HTML. To see if the HTML file contains the
text of interest, open the page in a browser, then access the HTML in the developer tools via 
<kbd>Cntrl</kbd>+<kbd>Shift</kbd>+ <kbd>I</kbd>.

### Documentation

Full documentation is available [here](https://github.com/peterkorteweg/boxfish/blob/main/Documentation.md).


