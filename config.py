'''
Created on 5 Feb 2020

@author: acmt2
'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '71d60150a7888feabeddbfc279658ffc0261fa972fae1191a595c2ffa79e1281'
    # PATIENTS_PER_PAGE = 1
    # PER_PAGE_PARAMETER = 10
