
# 簡易的な並列処理 [mulmap]
# 【動作確認 / 使用例】

import sys
import time
from ezpip import load_develop
# 簡易的な並列処理 [mulmap]
mulmap = load_develop("mulmap", "../", develop_flag = True)

def func(i):
	time.sleep(2)
	return i ** 2

res = mulmap(func, [1, 2, 3])	# 並列map
print(res)
