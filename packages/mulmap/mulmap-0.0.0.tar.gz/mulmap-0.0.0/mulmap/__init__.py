
# 簡易的な並列処理 [mulmap]

import sys
import joblib

# 簡易的な並列処理 [mulmap]
def mulmap(func, input_ls):
	# 計算すべき内容のリストを生成
	calc_ls = [joblib.delayed(func)(e) for e in input_ls]
	# 計算実行
	pool = joblib.Parallel(n_jobs = -1)
	ret_ls = pool(calc_ls)
	# 結果を返す
	return ret_ls

# 呼び出しの準備
sys.modules[__name__] = mulmap	# モジュールオブジェクトとmulmap関数を同一視
