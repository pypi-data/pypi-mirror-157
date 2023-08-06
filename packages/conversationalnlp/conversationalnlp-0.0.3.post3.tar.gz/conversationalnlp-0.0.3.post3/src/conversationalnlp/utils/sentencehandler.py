import re

def remove_emoji(instr: str) -> str:
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', instr)

def cleansentence(instr: str) -> str:
    """
    Clean sentence from 
    - strip white space
    - \n \t
    - remove emoji
    """    
    
    clean_list = ["tldr:", "\n", "\t"]
    
    for clean_item in clean_list:
        instr = instr.replace(clean_item, "")
       
    #strip white space
    workingstr = instr.strip()
        
    outstr = remove_emoji(workingstr)
        
    return outstr.lower()

def splitbysentence(instr: str) -> list:
    """
    split a string and return list of string following separator \".\", \".\", \".\"
    Note: Current version exclude the separator
    
    #splitbysentence("Hello. My name is C? But! Really, It's impossible.")
    """
    
    workinglist = [instr]
    
    splitter = [".", "?", "!"]
    
    for current_split in splitter:
        
        outlist = []
        for sentence in workinglist:
            
            templist = list(filter(lambda x : len(x) > 1, sentence.split(current_split)))
            outlist.extend(templist)
            
        workinglist = outlist
        
    workinglist = [cleansentence(i) for i in workinglist]
        
    outlist = list(filter(lambda instr: len(instr) > 1, workinglist))
                
    return outlist


#teststr = 'Hi! Howdy! 😎.\ntldr: i am recovering alcoholic'
#splitbysentence(teststr)