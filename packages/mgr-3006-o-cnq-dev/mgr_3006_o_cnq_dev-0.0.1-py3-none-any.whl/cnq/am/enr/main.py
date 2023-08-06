from cnq import hop
#from cnq import config
import subprocess
from datetime import datetime
import os
from subprocess import PIPE, Popen
from pathlib import Path
import configparser
from configparser import ConfigParser, SafeConfigParser, ExtendedInterpolation
import logging
import logging.config


#INTEGRATION
#test2=hop.enr.hop.Hop.verifier_existence_hive()
dfFolder= hop.enr.hop.Hop.lire_folder()

#test1=hop.enr.test.Test.succes()

#test3=hop.enr.hop.Hop.param_test()
