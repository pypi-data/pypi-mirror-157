from conversationalnlp.utils import customdatetime
import pandas as pd
import platform
import logging
import os
from typing import List


class ModelTracker:
    """
    Save to modeltracker_consolidation.xlsx with two sheets

    First Sheet - Training Log: {os_name}_{date}_progress

    | wer | datetime | 
    |  ---------------------  | ---------------------  |
    | 0.70 | 2022Mar04_19-45-18 |
    | 0.2 | 2022Mar04_19-45-18 |

    Second sheet - Training Summary: {os_name}_{date}_summary

    No exact format as long as writable

    | Description | Content | 
    |  ---------------------  | ---------------------  |
    | Base Model | wav2vec2-base |
    | Training Shape | (1234, 5) |
    | Training Shape | (1234, 5) |
    | Dataset | file1 | 
    """

    columndict = dict()
    modelcolumnname = "model"
    datecolumnname = "datetime"

    def __init__(self, metrics: List[str], trackerpath: str, modelsummary: pd.DataFrame = None):
        """
        Create attributes to track models performances

        Attributes
        ----------
        metrics_name : str 
            Name of metric to track. 
        trackerpath : str 
            Path of output excel file <relativepath>\test.xlsx
        trackerfileheader : str, optional 
            Filename header

        Returns
        -------
        None
        """

        if trackerpath.endswith(".xlsx") is False and os.path.exists(trackerpath) is False:

            logging.error(
                "Model tracker trackerpath is neither a valid path nor a valid path. Setting modeltracker failed.")
            return

        elif trackerpath.endswith(".xlsx") is False and os.path.exists(trackerpath) is True:

            trackerpath = os.path.join(trackerpath, "modeltracker.xlsx")
            logging.info(f"Model tracker set at path {trackerpath}")

        column_name = [self.modelcolumnname,
                       self.datecolumnname]  # default column name

        column_name.extend(metrics)

        for name in column_name:

            self.columndict[name] = []

        self.trackerpath = trackerpath

        # Append date time to prevent duplication
        datetime = customdatetime.getstringdatetime()
        self.trackersheetbase = platform.system().lower() + "_" + datetime.lower()

        logging.info(f"Model tracker: {self.trackerpath}")

        if modelsummary is not None:
            self._save_to_model_summary_file(modelsummary)

        self._save_to_model_progress_file()

    def additem(self, info: dict):
        """
        Create attributes to track models performances

        Attributes
        ----------
        metrics_name : str 
            Name of metircs to track. Each will become a column

        Returns
        -------
        None
        """
        info[self.datecolumnname] = customdatetime.getstringdatetime()

        if self.modelcolumnname not in info.keys():

            info[self.modelcolumnname] = None

        for key, value in info.items():

            if key not in self.columndict.keys():
                logging.info(
                    f"New {key} key not available in modeltracker. Value not saved.")
            else:
                self.columndict[key].append(value)

        keysmissing = list(set(self.columndict.keys()) - set(info.keys()))

        if keysmissing:
            logging.warning(
                f"Keys necessary for model tracking missing. {keysmissing}")

        # to prevent column name not same
        for key in keysmissing:

            self.columndict[key].append(None)

        # save every iteration
        self._save_to_model_progress_file()

    def _save_to_model_progress_file(self):
        """
        Write to output csv file
        Attributes
        ----------
        None

        Returns
        -------
        None
        """
        df = pd.DataFrame(self.columndict)

        mode = 'a' if os.path.exists(self.trackerpath) is True else 'w'

        with pd.ExcelWriter(self.trackerpath, mode=mode) as writer:

            sheet_name = self.trackersheetbase + "_1"

            workBook = writer.book
            try:
                workBook.remove(workBook[sheet_name])
            except:
                pass
            finally:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()

    def _save_to_model_summary_file(self, df):
        """
        Write to output csv file
        Attributes
        ----------
        None

        Returns
        -------
        None
        """

        mode = 'a' if os.path.exists(self.trackerpath) is True else 'w'

        with pd.ExcelWriter(self.trackerpath, mode=mode) as writer:

            sheet_name = self.trackersheetbase + "_0"

            workBook = writer.book
            try:
                workBook.remove(workBook[sheet_name])
            except:
                pass
            finally:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()
