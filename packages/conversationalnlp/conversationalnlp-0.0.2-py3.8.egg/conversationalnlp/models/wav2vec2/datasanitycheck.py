import pandas as pd
import logging
import os
from typing import Dict


class Wav2Vec2DataSanityCheck:
    """
    To validate the source data prior to training of Wav2Vec2
    """

    __cleandfparam = "clean"
    __faultydfparam = "faulty"

    def run(self, df, textcolumn: str = "text", filepathcolumn: str = "file") -> Dict[str, pd.DataFrame]:
        """
        - Validate dataset of column text where vocabulary fits in vocabulary size
        - Validate file path if exist
        Attributes
        ----------
        textcolumn : str, optional
            Column name for text 
        filepathcolumn : str, optional
            Column name for filepath

        Returns
        -------
        dict of dataframe with "clean" and "faulty"

        Dataframe with errors of following columns
        index : index in original dataframe 
        textcolumn param : text 
        filepathcolumn param: filepath 
        note: whether is "path not exist" or "digit not valid"

        """
        faultyindexlist = []
        faultytextcolumnlist = []
        faultyfilepathcolumnlist = []
        faultynotelist = []  # "path not exist", "digit not valid"

        if df.empty is True:
            logging.warning("Input dataframe for sanity check is empty")
            return None

        # Remove nan column

        dforishape = df.shape
        df = df.dropna(axis=1)

        if df.shape[0] != dforishape[0]:

            logging.info(
                f"Dataframe shape not same, contains invalid rows. Removed rows {dforishape[0] - df.shape[0]}")

        columns_missing = list(
            filter(lambda column: column not in df.columns, [textcolumn, filepathcolumn]))

        # check if columns required is missing
        if columns_missing:
            logging.error(f"Columns required {columns_missing} missing")
            return None

        for index, row in df.iterrows():

            isfaulty = False

            if any(chr.isdigit() for chr in row[textcolumn]) is True:
                isfaulty = True
                faultynotelist.append("digit not valid")

            elif os.path.exists(row[filepathcolumn]) is False:
                isfaulty = True
                faultynotelist.append("path not exist")

            if isfaulty:
                # 1 for header, 1 for table start with index 1 than index 0
                faultyindexlist.append(index)
                faultytextcolumnlist.append(row[textcolumn])
                faultyfilepathcolumnlist.append(row[filepathcolumn])

        # no faulty data
        if not faultyindexlist:
            logging.info("No faulty lines")
            return {self.__cleandfparam: df, self.__faultydfparam: pd.DataFrame()}

        dffaulty = pd.DataFrame({"index": faultyindexlist, textcolumn: faultytextcolumnlist,
                                 filepathcolumn: faultyfilepathcolumnlist, "note": faultynotelist})

        dfcleaned = df.drop(faultyindexlist).reset_index(drop=True)

        return {self.__cleandfparam: dfcleaned, self.__faultydfparam: dffaulty}
