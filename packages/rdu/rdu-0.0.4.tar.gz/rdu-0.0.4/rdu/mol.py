#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2022/7/4 15:03
# @Author  : zbc@mail.ustc.edu.cn
# @File    : mol.py
# @Software: PyCharm

import pandas as pd


class Mol:

    @classmethod
    def init_from_series(cls, ser: pd.Series):
        mol = Mol()
        mol.id = ser['id']
        mol.mol_code = ser['mol_code']
        # mol.names = eval(ser['names'])
        mol.inchi = ser['inchi']
        mol.smiles = ser['smiles']
        return mol

    def __init__(self):
        self.id: int = 0
        self.mol_code: str = ''
        # self.names: [str] = []
        self.inchi: str = ''
        self.smiles: str = ''


if __name__ == "__main__":
    pass
