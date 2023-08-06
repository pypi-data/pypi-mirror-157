import os
import urllib
import zipfile
import string
import random
import shutil
import hashlib
from . import customdatetime
import logging
import sys

logging.basicConfig(
            format="%(asctime)s | %(levelname)s | %(name)s |  [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=os.environ.get("LOGLEVEL", "INFO").upper(),
            stream=sys.stdout,
        )

def checksum(path): 
    f = open(path, 'rb')
    data = f.read()
    hash = hashlib.md5(data).hexdigest().lower()
    return hash

def downloadurl(zipinfo) -> bool:
    """
    Download url to local file

    Attributes
    ----------
    Dict of 
        url : str 
            URL to download
        filepath : str 
            File path to save to 
        hash : str
            Hash of file

    Returns
    -------
    Boolean if zip successfully download/exist
    """
    hash =  zipinfo['hash'].lower()

    if os.path.exists(zipinfo['filepath']) and hash is not None:

        if checksum(zipinfo['filepath']) == hash:

            logging.info(f"Checksum same. Skip in downloading {zipinfo['filepath']}")  
            return True

    try:
        _, _ = urllib.request.urlretrieve(zipinfo['url'], zipinfo['filepath'])
        logging.info(f"File downloaded at {zipinfo['filepath']}")

        
    except urllib.error.HTTPError as err:
        
        logging.error(f"Error in downloading {zipinfo['url']}: {err}")
        return False

    return True

def unzip(unzipinfo):
    """
    Unzip local zip path to uncompressed file

    Attributes
    ----------
    dict of 
        filepath : str 
            Path of zip file
        unzippath : str
            Folder to unzip to 
        overwrite: bool, optional 
            Existing folder will be deleted

    Returns
    -------
    None
    """
    unzippath = unzipinfo['unzippath']
    
    if os.path.exists(unzippath):

        if(('overwrite' in unzipinfo.keys()) and (unzipinfo['overwrite'] is True)):

            shutil.rmtree(unzippath)
            
        else:
            
            logging.info(f"{unzippath} exist. Unzipping skipped")
            return

    os.mkdir(unzippath)

    tempfolder = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    temppath = os.path.join(unzippath, tempfolder)

    with zipfile.ZipFile(unzipinfo['filepath'], 'r') as zipref:
        zipref.extractall(temppath)

    iterfiles = os.walk(temppath)
    for item in iterfiles:

        #assume only have one level sub directory
        currentfolder = item[0].split(os.sep)[-1]

        if(currentfolder != tempfolder):
            currentunzippath = os.path.join(unzippath, currentfolder)
            os.mkdir(currentunzippath)

        else:
            currentunzippath = unzippath

        for file in item[2]:
            src = os.path.join(item[0], file)
            dest = os.path.join(currentunzippath, file)
            shutil.move(src, dest)

    #remove temp path
    shutil.rmtree(temppath)
    
        
def createfolders(path):

    if not os.path.exists(path):

        logging.info(f"Folder created: {path}")
        os.makedirs(path)
    else:
        logging.info(f"Folder exist: {path}")


def generatefoldername(headername = ""):

    """
    Create unique folder name based on date

    Attributes
    ----------
    filepath : str 
        Path of zip file

    Returns
    -------
    foldername : str
        Unique folder name
    """

    strdatetime = customdatetime.getstringdatetime()

    return (headername + "_" + strdatetime) if headername != "" else strdatetime
