# mulmap

下の方に日本語の説明があります

## Overview
- map based easy paralell processing tool
- description is under construction.

## Usage
```python
import time
import mulmap

def func(i):
	time.sleep(2)
	return i ** 2

res = mulmap(func, [1, 2, 3])
print(res)	# -> [1,4,9]
```

## 概要
- mapの形式の並列処理。1引数関数を別々の引数で並列で動作させる。
- 説明は執筆中です

## 使用例
```python
import time
import mulmap

def func(i):
	time.sleep(2)
	return i ** 2

res = mulmap(func, [1, 2, 3])
print(res)	# -> [1,4,9]
```
