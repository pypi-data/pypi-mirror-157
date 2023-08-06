#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2022/7/4 15:03
# @Author  : zbc@mail.ustc.edu.cn
# @File    : rxn.py
# @Software: PyCharm

import pandas as pd

from rdu.mol import Mol


class Rxn:

    @classmethod
    def init_from_series(cls, ser: pd.Series):
        rxn = Rxn()
        rxn.id = ser['id']
        rxn.rxn_code = ser['rxn_code']
        rxn.rxn_mols_code = ser['rxn_mols_code']
        rxn.reactants_codes = eval(ser['reactants_codes'])
        rxn.product_code = ser['product_code']
        rxn.catalysts_codes = eval(ser['catalysts_codes'])
        rxn.solvents_codes = eval(ser['solvents_codes'])
        rxn.yield_product = ser['yield_product']
        rxn.rxn_smiles = ser['rxn_smiles']
        rxn.create_year = ser['create_year']
        return rxn

    def __init__(self):
        self.id: int = 0
        self.rxn_code: str = ''
        self.rxn_mols_code: str = ''
        self.reactants_codes: [str] = []
        self.product_code: str = ''
        self.catalysts_codes: [str] = []
        self.solvents_codes: [str] = []
        self.yield_product: float = 0
        self.rxn_smiles: str = ''
        self.create_year: int = 0

        self.reactants: [Mol] = []
        self.products: [Mol] = []
        self.catalysts: [Mol] = []
        self.solvents: [Mol] = []


if __name__ == "__main__":
    pass
