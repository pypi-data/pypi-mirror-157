from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.model_selection import train_test_split
import os
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from rdkit.ML.Descriptors import MoleculeDescriptors
import pickle
class model_selection:
    def __init__(self, 
                 saved_spe_model , 
                 saved_spe_scaler,
                 saved_lcms_model ,
                 saved_lcms_scaler):
        #if the saved_model is not empty load the saved_model to self.model
        if saved_spe_model != None:
            self.spe_model = pickle.load(open(saved_spe_model,'rb'))
        else:
            print('Where is the saved spe model!!!???')
            return
        if saved_spe_scaler != None:
            self.spe_scaler = pickle.load(open(saved_spe_scaler,'rb'))
        else:
            print('Where is the saved spe scaler!!!?')
            return
        
        if saved_lcms_model != None:
            self.lcms_model = pickle.load(open(saved_lcms_model,'rb'))
        else:
            print('Where is the saved lcms model!!!???')
            return
        if saved_lcms_scaler != None:
            self.lcms_scaler = pickle.load(open(saved_lcms_scaler,'rb'))
        else:
            print('Where is the saved lcms scaler!!!?')
            return
    def calculate_descriptors_df(self, smiles, ipc_avg=False):
        mol = Chem.MolFromSmiles(smiles)
        if names is None:
            names = [d[0] for d in Descriptors._descList]
        calc = MoleculeDescriptors.MolecularDescriptorCalculator(names)
        descriptors = calc.CalcDescriptors(mol)
        if 'Ipc' in names and ipc_avg:
            descriptors['Ipc'] = [Descriptors.Ipc(mol, avg=True)]
        return descriptors
    
    def calculate_descriptors(self, smiles, ipc_avg=False):
        mol = Chem.MolFromSmiles(smiles)
        names = ['MolWt', 'exactMolWt', 'qed', 'TPSA', 'HeavyAtomMolWt', 'MolLogP', 'MolMR', 'FractionCSP3', 'NumValenceElectrons', 'MaxPartialCharge', 'MinPartialCharge', 'FpDensityMorgan1', 'BalabanJ', 'BertzCT', 'HallKierAlpha', 'Ipc', 'Kappa2', 'LabuteASA', 'PEOE_VSA10', 'PEOE_VSA2', 'SMR_VSA10', 'SMR_VSA4', 'SlogP_VSA2', 'SlogP_VSA6','MaxEStateIndex', 'MinEStateIndex', 'EState_VSA3', 'EState_VSA8', 'HeavyAtomCount', 'NHOHCount', 'NOCount', 'NumAliphaticCarbocycles', 'NumAliphaticHeterocycles', 'NumAliphaticRings', 'NumAromaticCarbocycles', 'NumAromaticHeterocycles', 'NumAromaticRings', 'NumHAcceptors', 'NumHDonors', 'NumHeteroatoms', 'NumRotatableBonds', 'NumSaturatedCarbocycles', 'NumSaturatedHeterocycles', 'NumSaturatedRings', 'RingCount']
        if names is None:
            names = [d[0] for d in Descriptors._descList]
        calc = MoleculeDescriptors.MolecularDescriptorCalculator(names)

        descs = [calc.CalcDescriptors(mol)]
        descs_df = pd.DataFrame(descs, columns=names)
        print(descs_df)
        if 'Ipc' in names and ipc_avg:
            descs['Ipc'] = Descriptors.Ipc(mol, avg=True)
        return descs_df
    
    def RunSPEPrediction(self, smiles):
        features = self.calculate_descriptors(smiles)
        features_scaled = self.spe_scaler.transform(features)
        features_scaled_df = pd.DataFrame(features_scaled)
        y = self.spe_model.predict(features_scaled_df)
        return y
    
    def RunLCMSPrediction(self, smiles):
        features = self.calculate_descriptors(smiles)
        features_scaled = self.lcms_scaler.transform(features)
        features_scaled_df = pd.DataFrame(features_scaled)
        y = self.lcms_model.predict(features_scaled_df)
        return y
    
if __name__ == '__main__':
    smiles = "CC1CCN(CC1N(C)C2=NC=NC3=C2C=CN3)C(=O)CC#N"
    model_object = model_selection('/Users/yycheung/Analysis project/purifAI/base-purifai/purifai/spe_brf_model.pkl', 
                 '/Users/yycheung/Analysis project/purifAI/base-purifai/purifai/spe_scaler.pkl',
                 '/Users/yycheung/Analysis project/purifAI/base-purifai/purifai/lcms_brf_model.pkl',
                 '/Users/yycheung/Analysis project/purifAI/base-purifai/purifai/lcms_scaler.pkl')
    descs = [model_object.calculate_descriptors(smiles)]
    
    print(f'The SPE method you should use is : {model_object.RunSPEPrediction(smiles)}')
    print(f'The LCMS method you should use is : {model_object.RunLCMSPrediction(smiles)}')