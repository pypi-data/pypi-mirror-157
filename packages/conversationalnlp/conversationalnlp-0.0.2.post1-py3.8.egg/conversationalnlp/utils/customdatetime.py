#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : codenamewei
# Created Date: 2021-12-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""Module related to datetime formatting"""
# ---------------------------------------------------------------------------
from datetime import datetime

def getstringdatetime():

    current_time = datetime.now()
    strtime = current_time.strftime("%Y%h%d_%H%M%S")
    return strtime
