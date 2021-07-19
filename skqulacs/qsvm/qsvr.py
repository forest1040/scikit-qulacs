import numpy as np
from qulacs.state import inner_product
from sklearn import svm

from skqulacs.qsvm.qsvmbase import get_qvec


class QSVR:
    def __init__(self, tlotstep: int = 4) -> None:
        self.regr = svm.SVR(kernel="precomputed")
        self.data_states = []
        self.n_qubit = 0
        self.tlotstep = tlotstep

    def fit(self, x, y):
        self.n_qubit = len(x[0])
        kar = np.zeros((len(x), len(x)))  # サンプル数の二乗の情報量　距離を入れる
        # xとyのカーネルを計算する
        # そのために、UΦxを計算する
        # expを含む計算なので、トロッター法を使って計算する
        # その後、|Φx> = UΦx H  UΦx H |0>^n を行う
        # その後、　x[i]とx[j]]の類似度は、　内積をとって計算する
        for i in range(len(x)):
            self.data_states.append(get_qvec(x[i], self.n_qubit, self.tlotstep))
        for i in range(len(x)):
            for j in range(len(x)):
                kar[i][j] = (
                    abs(inner_product(self.data_states[i], self.data_states[j])) ** 2
                )
        self.regr.fit(kar, y)

    def predict(self, xs):
        kar = np.zeros((len(xs), len(self.data_states)))  # サンプル数の二乗の情報量　距離を入れる
        for i in range(len(xs)):
            x_qc = get_qvec(xs[i], self.n_qubit, self.tlotstep)
            for j in range(len(self.data_states)):
                kar[i][j] = abs(inner_product(x_qc, self.data_states[j])) ** 2
        return self.regr.predict(kar)