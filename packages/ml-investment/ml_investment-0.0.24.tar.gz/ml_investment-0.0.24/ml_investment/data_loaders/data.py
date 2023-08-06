'''
Loading utils
'''

import pandas as pd
from typing import List



class HashingDataWrapper:
    '''    
    Wrapper to store already loaded data in memory 
    to increase reloading speed.
    '''
    def __init__(self, data_loader):
        '''
        Parameters
        ----------
        data_loader:
            class implementing
            ``load(index) -> pd.DataFrame`` interface
        '''
        self.data_loader = data_loader
        self.data_by_index = {}
        
    def load(self, index: List):
        '''
        Parameters
        ----------
        index:
            list of index to lad data for
            
        Returns
        -------
            ``pd.DataFrame`` with data provided by ``data_loader``
        '''
        exist_index = set(self.data_by_index.keys()).intersection(set(index))
        skipped_index = set(index).difference(self.data_by_index.keys())

        for key in skipped_index:
            self.data_by_index[key] = self.data_loader.load([key])
           
        arr = [self.data_by_index[key] for key in index
                            if self.data_by_index[key] is not None]
        if len(arr) == 0:
            return

        result = pd.concat(arr, axis=0)
        
        return result
    

    def existing_index(self):
        '''  
        Returns
        -------
        ``List``
            existing index values that can pe pushed to `load`
        '''
        return self.data_loader.existing_index()



class ExtraDataWrapper:
    '''    
    Wrapper to load data from multiple extra sources if regular is ``None``.
    '''
    def __init__(self, data_loaders):
        '''
        Parameters
        ----------
        data_loaders:
            list of classes implementing
            ``load(index) -> pd.DataFrame`` interface
        '''
        self.data_loaders = data_loaders
        

    def load(self, index):
        '''
        Parameters
        ----------
        index:
            list of index to lad data for
            
        Returns
        -------
            first not-None ``pd.DataFrame`` provided by ``data_loaders``
        '''
        for k in range(len(self.data_loaders)):
            df = self.data_loaders[k].load(index)
            if df is not None:
                break
                
        return df


    def existing_index(self):
        '''  
        Returns
        -------
        ``List``
            existing index values that can pe pushed to `load`
        '''
        index = []
        for k in range(len(self.data_loaders)):
            index.extend(self.data_loaders[k].existing_index())
        index = list(set(index))
        
        return index







