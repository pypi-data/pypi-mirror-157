import pandas as pd
import logging
import os

class Wav2Vec2DataSanityCheck:
    """
    To validate the source data prior to training of Wav2Vec2
    """
    
    def getfaultydata(self, df, textcolumn = "text", filepathcolumn = "file") -> pd.DataFrame:
        """
        Validate dataset of column text and filepath if exist
        Attributes
        ----------
        textcolumn : str, optional
            Column name for text 
        filepathcolumn : str, optional
            Column name for filepath
            
        Returns
        -------
        Dataframe with errors
        textcolumn : text contains digits or punctuation marks
        filepathcolumn: filepath not found
        """
        indexlist = []
        textcolumnlist = []
        filepathcolumnlist = []

        dfout = pd.DataFrame({"index": [], textcolumn: [], filepathcolumn: []})

        if df.empty is True:
            logging.warning("Input dataframe for sanity check is empty")
            return dfout

        columns_missing = list(filter(lambda column : column not in df.columns, [textcolumn, filepathcolumn]))

        #check if columns required is missing
        if columns_missing:
            logging.error(f"Columns required {columns_missing} missing")
            return dfout

        for index, row in df.iterrows():

                if any(chr.isdigit() for chr in row[textcolumn]) is True or os.path.exists(row[filepathcolumn]) is False:

                    indexlist.append(index + 2) #1 for header, 1 for table start with index 1 than index 0
                    textcolumnlist.append(row[textcolumn])
                    filepathcolumnlist.append(row[filepathcolumn])

        #no faulty data
        if not indexlist:
            logging.info("No faulty lines")
            return dfout
                    
        dictcolumn = {"index": indexlist, textcolumn: textcolumnlist, filepathcolumn: filepathcolumnlist}
        
        return pd.DataFrame(dictcolumn)