from os import listdir
from cnq import am
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
import logging
import logging.config
import subprocess
from subprocess import PIPE, Popen
from pyspark import SparkContext, SparkConf
from pathlib import Path
import configparser
from configparser import ConfigParser, ExtendedInterpolation

#Configuration init-----------------------------------------------------------------------------------------------------------
class EnvInterpolation(configparser.BasicInterpolation):
    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)

even = EnvInterpolation()
        
class Configuration():
    def call_conf():
      config = configparser.SafeConfigParser(interpolation=even)
      print("call conf test 2")
      path = Path(__file__)
      parent_dir = path.parent.parent.parent
      parent_path= os.path.abspath(parent_dir)
      config_path = os.path.join(parent_path, "configuration.ini")
      print(config_path)
      config = configparser.ConfigParser(interpolation=even)
      #Local
      if (os.access(config_path, os.F_OK)== True):
        config.read(config_path)
      #HDFS
      else:
        config.read("configuration.ini")
      return config
      

#Variables de la configuration a utiliser dans le script:

config = Configuration.call_conf()
driver = 'AM'
all = 'ALL'
#Configuration fin-----------------------------------------------------------------------------------------------------------

#logging init-------------------------------------------------------------------------------------------------------------

"""path = Path(__file__)
parent_dir = path.parent.parent
parent_path= os.path.abspath(parent_dir)
logging_path = os.path.join(parent_path, "logging.ini")
#Local
if (os.access(logging_path, os.F_OK)== True):
  logging.config.fileConfig(logging_path, disable_existing_loggers=False)#logging.ini
#HDFS
else:
  logging.config.fileConfig("loggging.ini", disable_existing_loggers=False)#logging.ini  
logger = logging.getLogger(__name__)
path_to_logs = (config.get(driver,'driver_logs_path'))
print("path to logos***********************************************")
print(path_to_logs)
date_name_log= '{:%Y-%m-%d_%H%M}'.format(datetime.now())
fh = logging.FileHandler(path_to_logs+date_name_log+'_'+driver+'.log',mode='w')
logger.addHandler(fh)
formatter = logging.Formatter('[ %(asctime)s | %(filename)s | %(funcName)s line %(lineno)d | %(levelname)s ] %(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.DEBUG)"""

#logging fin-------------------------------------------------------------------------------------------------------------

spark = SparkSession.builder.appName("HOP ENRI")\
                            .config("spark.jars.packages", "com.crealytics:spark-excel_2.12:0.13.5")\
                            .config("spark.network.timeout", "600s")\
                            .config("spark.sql.catalogImplementation=hive")\
                            .enableHiveSupport()\
                            .getOrCreate()
spark.conf.set("spark.sql.crossJoin.enabled" , "true" )
spark.conf.set("spark.sql.codegen.wholeStage", "false")

sc = spark.sparkContext

class Hop:
    def verifier_existence_hive():
        #Fonction qui verifie l'existence des tables necessaires pour le fonctionnement du driver. Dans le cas ou les tables n'exitent pas, les crée. 
        if not (spark.catalog._jcatalog.tableExists(list_of_arguments[1]+'.hop_enri_auto')):
          spark.sql('DROP TABLE IF EXISTS '+list_of_arguments[1]+'.hop_enri_auto')
          spark.sql('CREATE TABLE IF NOT EXISTS '+list_of_arguments[1]+'.hop_enri_auto (rework string, mrr string, barcode string, creation_date string, closed_date string, category string, classification string, position string, side string, frame string, stringer string, defect_type_raw string, status string, last_update string, profile string, user_raw string, description string, object_inspection string, criticality string, qty string, udb string, repeated string, localisation_1_intermediaire string, localisation_2_intermediaire string, localisation_3_intermediaire string, defect_type_cnq string, msn_initial string, msn_reaffecte string, wp_level_1_avant_qms string, wp_level_2_avant_qms string, wp_level_3_avant_qms string, defect_type_avant_qms string, mft_accountable_pgi_code string, mft_accountable_pgi_name_1 string, mft_accountable_sap_atr_code string, mft_accountable_sap_atr_name_1 string, mft_comment string, qms_location_1 string, qms_location_2 string, qms_location_3 string, qms_defect_type string, qms_final_accountable_pgi_code string, qms_final_accountable_pgi_name_1 string, qms_final_accountable_sap_atr_code string, qms_final_accountable_sap_atr_name_1 string, qms_final_accountable_qms_supplier_liability string, subdriver string, nc_reference string, msn_final string, ac_type string, ac_model string, ac_status string, wp_level_1 string, wp_level_2 string, wp_level_3 string, defect_type string, operator_level_1_pgi_code string, operator_level_1_pgi_name_1 string, operator_level_1_sap_atr_code string, operator_level_1_sap_atr_name_1 string, operator_level_2 string, operator_level_3 string, accountable_level_1_pgi_code string, accountable_level_1_pgi_name_1 string, accountable_level_1_sap_atr_code string, accountable_level_1_sap_atr_name_1 string, accountable_level_2 string, accountable_level_3 string, theoretical_accountable_1_pgi_code string, theoretical_accountable_1_pgi_name_1 string, theoretical_accountable_1_sap_atr_code string, theoretical_accountable_1_sap_atr_name_1 string, theoretical_accountable_2 string, theoretical_accountable_3 string, cost_value_allocation_date string, extra_cost_posting_date string, id_extra_cost string, claim_creation_date string, id_claim string, buyer_responsible string, status_r string, claim_category string, extra_cost_task_responsible string, e_unit_first_amount_claimed string, e_unit_last_amount_claimed string, claim_closing_date string, e_unit_amount_secured string, materialization_type string, destination_department string, destination_other string, materialization_type_reference string, comment_business string, comment_buyer string, pain_point_reference string, erreur_nettoyage string, nc_creation_hive string) CLUSTERED BY (localisation_1_intermediaire) INTO 10 BUCKETS STORED AS ORC TBLPROPERTIES ("transactional"="true")')
        if not (spark.catalog._jcatalog.tableExists(list_of_arguments[1]+'.hop_enri_auto_temp')):
          spark.sql('DROP TABLE IF EXISTS '+list_of_arguments[1]+'.hop_enri_auto_temp')
          spark.sql('CREATE TABLE IF NOT EXISTS '+list_of_arguments[1]+'.hop_enri_auto_temp (rework string, mrr string, barcode string, creation_date string, closed_date string, category string, classification string, position string, side string, frame string, stringer string, defect_type_raw string, status string, last_update string, profile string, user_raw string, description string, object_inspection string, criticality string, qty string, udb string, repeated string, localisation_1_intermediaire string, localisation_2_intermediaire string, localisation_3_intermediaire string, defect_type_cnq string, msn_initial string, msn_reaffecte string, wp_level_1_avant_qms string, wp_level_2_avant_qms string, wp_level_3_avant_qms string, defect_type_avant_qms string, mft_accountable_pgi_code string, mft_accountable_pgi_name_1 string, mft_accountable_sap_atr_code string, mft_accountable_sap_atr_name_1 string, mft_comment string, qms_location_1 string, qms_location_2 string, qms_location_3 string, qms_defect_type string, qms_final_accountable_pgi_code string, qms_final_accountable_pgi_name_1 string, qms_final_accountable_sap_atr_code string, qms_final_accountable_sap_atr_name_1 string, qms_final_accountable_qms_supplier_liability string, subdriver string, nc_reference string, msn_final string, ac_type string, ac_model string, ac_status string, wp_level_1 string, wp_level_2 string, wp_level_3 string, defect_type string, operator_level_1_pgi_code string, operator_level_1_pgi_name_1 string, operator_level_1_sap_atr_code string, operator_level_1_sap_atr_name_1 string, operator_level_2 string, operator_level_3 string, accountable_level_1_pgi_code string, accountable_level_1_pgi_name_1 string, accountable_level_1_sap_atr_code string, accountable_level_1_sap_atr_name_1 string, accountable_level_2 string, accountable_level_3 string, theoretical_accountable_1_pgi_code string, theoretical_accountable_1_pgi_name_1 string, theoretical_accountable_1_sap_atr_code string, theoretical_accountable_1_sap_atr_name_1 string, theoretical_accountable_2 string, theoretical_accountable_3 string, cost_value_allocation_date string, extra_cost_posting_date string, id_extra_cost string, claim_creation_date string, id_claim string, buyer_responsible string, status_r string, claim_category string, extra_cost_task_responsible string, e_unit_first_amount_claimed string, e_unit_last_amount_claimed string, claim_closing_date string, e_unit_amount_secured string, materialization_type string, destination_department string, destination_other string, materialization_type_reference string, comment_business string, comment_buyer string, pain_point_reference string, erreur_nettoyage string, nc_creation_hive string) CLUSTERED BY (localisation_1_intermediaire) INTO 10 BUCKETS STORED AS ORC TBLPROPERTIES ("transactional"="true")')
          
    def lire_folder():   
        sources_name= config.get(driver,'sources')
        #path_inbox = config.get(all,'serveur_name') + config.get(driver,'driver_inbox_path') 
        #path_archive = config.get(all,'serveur_name') +config.get(driver,'driver_archive_path') 
        path_inbox = config.get(driver,'driver_inbox_path') 
        path_archive = config.get(driver,'driver_archive_path') 
        docs = sh.hadoop('fs', '-ls', path_inbox)
        docs = [sources_name + doc.split(" "+sources_name, 1)[-1].replace("\n", "") for doc in docs]
        docs = docs[2:]
        for arc in docs:  
          sh.hadoop('fs','-cp','-f', arc, path_archive)
        return docs
        
        
        
        
        
        
        
        