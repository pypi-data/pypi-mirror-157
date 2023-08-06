#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2022/7/4 15:51
# @Author  : zbc@mail.ustc.edu.cn
# @File    : rxn_data_utils.py
# @Software: PyCharm

from typing import Iterator

import pandas as pd

from rdu.mol_data_utils import MolDataUtils, Mol
from rdu.rxn import Rxn


class RxnDataUtils:

    def __init__(self, rxn_data_fp: str, mol_data_utils: MolDataUtils):
        self._rxn_df = pd.read_csv(rxn_data_fp, sep='\t', encoding='utf-8')
        self._mol_data_utils = mol_data_utils

    def iter_rxn(self) -> Iterator[Rxn]:
        self._rxn_df = self._rxn_df.sample(frac=1)
        for _, row in self._rxn_df.iterrows():
            rxn = Rxn.init_from_series(row)
            rxn.reactants = [self._mol_data_utils.get_mol_with_code(mol_code) for mol_code in rxn.reactants_codes]
            rxn.products = [self._mol_data_utils.get_mol_with_code(rxn.product_code)]
            rxn.catalysts = [self._mol_data_utils.get_mol_with_code(mol_code) for mol_code in rxn.catalysts_codes]
            rxn.solvents = [self._mol_data_utils.get_mol_with_code(mol_code) for mol_code in rxn.solvents_codes]
            yield rxn


if __name__ == "__main__":
    mfp = "C:\\Users\\zhang\\OneDrive\\Projects\\RXN-PREDICTOR\\Data\\SYNPREPY\\RXNData\\rxndb_base_mol.tsv"
    rfp = "C:\\Users\\zhang\\OneDrive\\Projects\\RXN-PREDICTOR\\Data\\SYNPREPY\\RXNData\\rxndb_base_cleaned_rxn.tsv"
    mdu = MolDataUtils(mfp)
    rdu = RxnDataUtils(rfp, mdu)
    for r in rdu.iter_rxn():
        print(r)
