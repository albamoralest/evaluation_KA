'''
Created on 5 Feb 2020

@author: acmt2
'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PATIENTS_PER_PAGE = 1
    PER_PAGE_PARAMETER = 10