"""
# -*- coding: utf-8 -*-

__author__ = "Akash"
__email__ = "akashjio6666@gmail.com"
__version__ = 1.0.0"
__copyright__ = "Copyright (c) 2004-2020 Leonard Richardson"
# Use of this source code is governed by the MIT license.
__license__ = "MIT"

Description:
            Py-Insta Is A Python Library
            Created By Akash Pattnaik From
            India..
            Py-Insta Helps Users To Easily
            Scrape Instagram Data
            And Print It Or You Can Define It Into A Variable...
            If You Find Bugs Then Please Report To
            @AKASH_AM1 On Telegram...

Pre-Requests:
            from bs4 import BeautifulSoup
            import requests

Documentation:
            Github: https://github.com/BLUE-DEVIL1134/Py-Insta
            PyPi: https://pypi.org/user/AkashPattnaik/
"""
__version__ = 1.0
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init

init()
n = Fore.RESET
lg = Fore.LIGHTGREEN_EX
r = Fore.RED
w = Fore.WHITE
cy = Fore.CYAN
ye = Fore.YELLOW
colors = [lg, r, w, cy, ye]


def bannerred():
    print(f"""
{r}
 ██████╗ ███████╗ █████╗ ███████╗████████╗{r}  
 ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝{r}
 ██████╔╝█████╗  ███████║███████╗   ██║    {r}
 ██╔══██╗██╔══╝  ██╔══██║╚════██║   ██║   {r}
 ██████╔╝███████╗██║  ██║███████║   ██║    {r}
 ╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝   ╚═╝   {r}
            Author: github.com/msy1717{r}
            Developer : @Godmrunal{r}


""")

def bannerwhite():
    print(f"""
{r}
 ██████╗ ███████╗ █████╗ ███████╗████████╗
 ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝
 ██████╔╝█████╗  ███████║███████╗   ██║    
 ██╔══██╗██╔══╝  ██╔══██║╚════██║   ██║   
 ██████╔╝███████╗██║  ██║███████║   ██║    
 ╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝   ╚═╝   
            Author: github.com/msy1717
            Developer : @Godmrunal


""")