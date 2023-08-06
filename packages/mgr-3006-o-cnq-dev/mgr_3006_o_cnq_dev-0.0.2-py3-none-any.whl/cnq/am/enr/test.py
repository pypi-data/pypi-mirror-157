#from cnq import configuration
from os import listdir
import numpy as np
import pandas as pd
import numpy as np
from datetime import datetime
import openpyxl
import findspark
findspark.init("/opt/mapr/spark/spark-3.1.2/")
print("ok")
import pyspark
from pyspark.sql import SparkSession, HiveContext
from pyspark.sql import Row
from pyspark.sql import functions as F
from pyspark.sql import SQLContext as sqlContext
import xlrd
import sh
from pyspark.sql.types import StringType, DateType
import os
#import logging
#import logging.config
import subprocess
from subprocess import PIPE, Popen
from pyspark import SparkContext, SparkConf
from pathlib import Path
import configparser
from configparser import ConfigParser, ExtendedInterpolation
import sys 
#Import .ini
#import importlib_resources
#from importlib_resources import files
# Reads contents with UTF-8 encoding and returns str.

#config_path = files('config').joinpath('configuration.ini')

#spark = SparkSession.builder.appName("test_dev").master("local[1]").config("spark.jars.packages", "com.crealytics:spark-excel_2.12:0.13.5").config("spark.network.timeout", "600s").enableHiveSupport().getOrCreate()
spark = SparkSession.builder.appName("test_dev_31_05").getOrCreate()
spark.conf.set("spark.sql.crossJoin.enabled" , "true" )
#spark.conf.set("spark.cleaner.referenceTracking.cleanCheckpoints", "true")<-- Set effectué dans le fichier de conf

#Hide error with the limitation of the Java class file:
#spark.conf.set("spark.sql.codegen.wholeStage", "false").set("spark.yarn.dist.archives","hdfs://ezdcluster.int.aosis.net/user/cnqdev/env_test/..pyPackTest.zip#pythonlib")
spark.conf.set("spark.sql.codegen.wholeStage", "false")
sc = spark.sparkContext
class EnvInterpolation(configparser.BasicInterpolation):
    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)
        
        
print("succés!")

even = EnvInterpolation()
'''
#path = Path(__file__)
#parent_dir = path.parent.parent.parent
#parent_path= os.path.abspath(parent_dir)
#print(parent_dir)
"config_path = os.path.join(parent_path, "configuration.ini")

print(str(os.path.dirname(os.path.abspath(__file__))))
path = os.path.dirname(os.path.abspath(__file__))
parent_dir = path.parent.parent
parent_path = os.path.abspath(parent_dir)
config_path = os.path.join(parent_path, "configuration.ini")
#config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration.ini')
config = configparser.ConfigParser(interpolation=even)
config.read(config_path)
#config.read(.cnq.configuration.ini)
driver = 'HOP'
all = 'ALL'
'''
class Test:
    def __init__():
      print("in init")
    
    def succes():
      print("succés-esto es un test!")
      

    def autre_succes():
      test= self.succes()