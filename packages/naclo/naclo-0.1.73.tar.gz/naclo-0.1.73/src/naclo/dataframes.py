from rdkit import Chem
from warnings import warn
from rdkit.Chem import PandasTools
import pandas as pd
from typing import Union
import numpy as np

# Nested imports
from naclo.Writer import Writer


def __exception_2_nan(x, func):
        try:
            return func(x)
        except Exception:
            return np.nan
    

def df_smiles_2_mols(df, smiles_name, mol_name, dropna=True):  # *
    """Adds rdkit Mol column to df using SMILES column as reference.

    Args:
        df (pandas DataFrame): DataFrame to add Mol column to.
        smiles_name (str): Name of SMILES column in df.
        molecule_name (str): Name of Mol column in df.
        dropna (bool, optional): Drop NA Mols. Defaults to True.

    Returns:
        pandas DataFrame: DataFrame with Mol column appended.
    """
    df[mol_name] = df[smiles_name].map(lambda x: __exception_2_nan(x, Chem.MolFromSmiles), na_action='ignore')
    return df.dropna(subset=[mol_name]) if dropna else df

def df_mols_2_inchi_keys(df, mol_name, inchi_name, dropna=True):  # *
    """Adds InChi Key column to df using Mol column as reference.
    
    Args:
        df (pandas DataFrame): DataFrame to add InChi column to.
        mol_name (str): Name of InChi column in df.
        inchi_name (str): Name of InChi column in df.
        dropna (bool, optional): Drop NA InChis. Defaults to True.

    Returns:
        pandas DataFrame: DataFrame with InChi column appended.
    """
    df[inchi_name] = df[mol_name].map(lambda x: __exception_2_nan(x, Chem.MolToInchiKey), na_action='ignore')
    return df.dropna(subset=[inchi_name]) if dropna else df
    
def df_mols_2_smiles(df, mol_name, smiles_name, dropna=True):  # *
    """Adds SMILES Key column to df using Mol column as reference.

    Args:
        df (pandas DataFrame): DataFrame to add SMILES column to.
        mol_name (str): Name of Mol column in df.
        inchi_name (str): Name of InChi column in df.
        dropna (bool, optional): Drop NA SMILES. Defaults to True.

    Returns:
        pandas DataFrame: DataFrame with SMILES column appended.
    """
    df[smiles_name] = df[mol_name].map(lambda x: __exception_2_nan(x, Chem.MolToSmiles), na_action='ignore')
    return df.dropna(subset=[smiles_name]) if dropna else df

def write_sdf(df, out_path, mol_col_name, id_column_name='RowID'):  # *
    """Writes dataframe to SDF file. Includes ID name if ID is valid.

    Args:
        df (DataFrame): Data to write.
        out_path (str or file-like): Path to save SDF to.
        mol_col_name (str): Name of molecule column in dataframe.
        id_column_name (str, optional): Name of id column. Defaults to 'ID'.
    """
    try:
        PandasTools.WriteSDF(df, out_path, molColName=mol_col_name, properties=df.columns, idName=id_column_name)
    except KeyError:
        PandasTools.WriteSDF(df, out_path, molColName=mol_col_name, properties=df.columns, idName='RowID')
        warn(f'write_sdf \'{id_column_name}\' ID name invalid', UserWarning)

def id_mol_col(df:pd.DataFrame) -> Union[None, pd.Index]:
    """Identifies first column that contains a Mol object based on first row.

    Args:
        df (pd.DataFrame): Input data.

    Returns:
        Union[None, pd.Index]: Index of first Mol column if found. Else None.
    """
    for i in range(len(df)):
        df.iloc[i]
        first_row = [isinstance(m, Chem.rdchem.Mol) for m in df.iloc[i]]
        if sum(first_row) > 0:
            return df.columns[first_row.index(True)]
        
    return None
