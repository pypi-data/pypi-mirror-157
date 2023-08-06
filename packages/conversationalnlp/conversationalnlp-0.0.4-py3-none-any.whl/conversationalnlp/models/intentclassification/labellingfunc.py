import numpy as np
import pandas as pd
import os

class LabellingFunc:

    def __init__(self):

        luttablepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata", "intentlut.csv")
        lutdf = pd.read_csv(luttablepath, engine = 'python')
        
        counter = 0
        
        self._labeltable = dict()
        
        lutkey = lutdf.columns.tolist()
        for key in lutkey: 
            self._labeltable[key] = counter
            counter += 1
            
        #default out of scope label 
        lutkey['out-of-scope'] = -1
        
    @property
    def labeltable(self):
        return self._labeltable
    
    def filter(self, words : str) -> str:
        # TODO: adaptive change the splitting og strin gaccording to row
        end_index = words.find(" ") 
        return words[:end_index] if end_index != -1 else words

    def pseudolabel(self, words :str) -> int:
        """
        Label a sequence/sentence with intent classification based on heuristics
        
        Attributes
        ----------
        sentence : str
            a single sentence

        Returns
        -------
        int
        0: (Follow Up) Question
        1: (Follow Up) Action
        -1: Out-Of-Scope
        """
        wordsfiltered = self.filter(words)
        
        for key in self._labeltable.keys():
        
            rowsfound = lut.loc[lut[key].eq(targetstr)].shape[0]
        
            if rowsfound != -1:
                return self._labeltable[key]
            
        #default return out of scope label if not found 
        return self._labeltable['out-of-scope']
                
                