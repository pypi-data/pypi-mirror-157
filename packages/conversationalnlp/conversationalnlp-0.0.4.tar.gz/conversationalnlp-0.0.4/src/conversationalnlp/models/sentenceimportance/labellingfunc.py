import numpy as np
import pandas as pd
import os

class LabellingFunc:

    def __init__(self):

        keywordspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata", "keywords0.txt")
        filein = open(keywordspath, "r")
        raw_keywords_class0 = filein.readlines()
        self.keywords_class0 = list(map(str.strip, raw_keywords_class0))

        self._labelidxlut =  {"important": 1, "not important": 0}
        self._labelstrlut = {v: k for k, v in self._labelidxlut.items()}

    @property
    def labelidxlut(self):

        return self._labelidxlut

    @property
    def labelstrlut(self):

        return self._labelstrlut

    def filter(self, sentence) -> list:
        """
        - Remove words that matches keywords of class 0
        - Remove repetitive words
        """
        raw_words = sentence.split()
        processed_words = [str.lower(word.replace('\'', '')) for word in raw_words]

        repetitives = pd.value_counts(np.array(processed_words))

        for word, count in repetitives.items():
            for _ in range(0, count - 1):
                processed_words.remove(word)

        return [word for word in processed_words if word not in self.keywords_class0]

    def pseudolabel(self, words :str) -> int:
        """
        Label a sequence/sentence with importance classification based on heuristics
        
        Attributes
        ----------
        sentence : str
            a single sentence

        Returns
        -------
        int
        0: not important
        1: important
        -1: needs further inspection
        """
        wordsfiltered = self.filter(words)

        wordcount = len(wordsfiltered)

        if wordcount < 3:

            if (wordcount == 1) and (words.lower() in ["okay", "ok", "yes", "no"]):
                return 1
            else:
                return 0
        elif wordcount > 5:
            return 1
        else:
            return -1
        
        

        