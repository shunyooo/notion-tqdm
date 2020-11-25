# notion-tqdm

[![PyPI version](https://badge.fury.io/py/notion-tqdm.svg)](https://badge.fury.io/py/notion-tqdm) [![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

Progress Bar displayed in Notion like tqdm for Python.

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

<img src="https://s3.us-west-2.amazonaws.com/secure.notion-static.com/b5abd2eb-1690-46fb-af44-3b22a3a4c559/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20201124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20201124T201006Z&X-Amz-Expires=86400&X-Amz-Signature=7adcab42158710e0db92099c95c0c47988f13fde18efbefe1a2200a7bc04963c&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22" width='500px' />



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

![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/8131c29a-7e55-4dd4-99df-361b409bdded/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20201124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20201124T201623Z&X-Amz-Expires=86400&X-Amz-Signature=52bbe9c2416eb3bdc89204223d9b7b2a793b3c0f649e97a51b0bc22715870081&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22)



### Example: Running with the existing tqdm

```python
from tqdm.auto import tqdm
from time import sleep
# Nest tqdm
extqdm = lambda *args, **kwags: tqdm(notion_tqdm(*args, **kwags))
for i in extqdm(range(100)):
  sleep(1)
  print(i)
```



### Example: Timeline View

With Notion's **timeline view**, you can visualize the **execution time of the progress**.

![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/897aa5aa-7ad4-4913-9f3f-2002ebdd8603/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20201124%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20201124T202304Z&X-Amz-Expires=86400&X-Amz-Signature=1991a50ecb1fcbe2a77a576803e45ee91907336ce4a1d646f45f7e2ce38d6ea4&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22)

