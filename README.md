# notion-tqdm

[![PyPI version](https://badge.fury.io/py/notion-tqdm.svg)](https://badge.fury.io/py/notion-tqdm) [![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

Progress Bar displayed in Notion like tqdm for Python using [`notion-py`](https://github.com/jamalex/notion-py).

![demo](https://user-images.githubusercontent.com/17490886/100184781-97ae2580-2f25-11eb-9700-2d9c5ce95592.gif)

 `notion-tqdm` inherits from [tqdm](https://github.com/tqdm/tqdm), so it can be run in the same way as tqdm.



# Installation

```
pip install notion-tqdm
```



# Usage

## Preparation

1. **Get Notion's Token** for reference **[here](https://www.notion.so/How-to-get-your-token-d7a3421b851f406380fb9ff429cd5d47)**

2.  [**Duplicate this page**](https://www.notion.so/syunyo/notion-tqdm-template-7d2d53595e774c9eb7a020e00fd81fab) in your own workspace and **get the table link**.
    （Note that it is a table link, not a page link.）

<img src="https://user-images.githubusercontent.com/17490886/100450226-9f71f380-30f8-11eb-97c5-2538d99d4a5b.png" width='500px' />



## QuickStart

```python
from notion_tqdm import notion_tqdm
from time import sleep

# Configure
token_v2 = '<token_v2>'
table_url = '<table_url>'
notion_email = '<notion_email>' # For multi-account users
notion_tqdm.set_config(token_v2, table_url, email=notion_email, timezone='Asia/Tokyo')

# Run Iterate
for i in notion_tqdm(range(100), desc='Processing'):
    sleep(1)
    print(i)
```

A row representing the progress should be added to the table as shown below.

![](https://user-images.githubusercontent.com/17490886/100450225-9ed95d00-30f8-11eb-8932-19c4d9a1e955.png)



### Example: Running with the Other tqdm

```python
from tqdm.auto import tqdm as tqdm_auto
from time import sleep
# Nest tqdm
tqdm = lambda *args, **kwags: tqdm_auto(notion_tqdm(*args, **kwags))
for i in tqdm(range(100)):
  sleep(1)
  print(i)
```



### Example: Set Custom Property

#### Set the common parameters before the iterative process.

```python
# After this setting, the value will be added to the column by default.
# The `machine` column must be added to the table beforehand.
notion_tqdm.set_common_props(machine='Jupyter1')
```

#### Set the dynamic parameters during the iterative process.

```python
with notion_tqdm(range(50), desc='process') as pbar:
    for i in pbar:
        # ... some process ...
        # The `precision`, `highparam` column must be 
        # added to the table beforehand.
        pbar.update_props(precision=precision, highparam=highparam)
```



### Example: Add text to a page in table row.

```python
with notion_tqdm(range(500), desc='add text test') as pbar:
    for i in pbar:
        sleep(1)
        pbar.add_text(f'text: {i}')
```

<img src="https://tva1.sinaimg.cn/large/0081Kckwgy1gl40e5odp3j30a40cw0t6.jpg" alt="image-20201127213525339" height=400 />



### Example: Timeline View

With Notion's **timeline view**, you can visualize the **execution time of the progress**.

![](https://user-images.githubusercontent.com/17490886/100450217-9c770300-30f8-11eb-8b8a-241fc622d700.png)

