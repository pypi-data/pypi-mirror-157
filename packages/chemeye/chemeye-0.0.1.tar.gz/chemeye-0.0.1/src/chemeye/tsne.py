import numpy as np
from rdkit import DataStructs
from typing import Iterable


def sim_matrix(row_prints:Iterable, col_prints:Iterable, key_type:str='ecfp'):
    full_array = np.zeros((len(row_prints), len(col_prints)))

    for i, row in enumerate(row_prints):
        for j, col in enumerate(col_prints):
            if key_type == 'ecfp':
                similarity = DataStructs.TanimotoSimilarity(row, col)
            elif key_type == 'maccs':
                similarity = DataStructs.FingerprintSimilarity(row, col)
            else:
                raise('Key type must be either "ecfp" or "maccs".')
                
            full_array[i][j] = similarity
    
    return full_array
