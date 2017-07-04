import logging
import os

# create logger
logger = logging.getLogger('abt-cli')
try:
    log_dir =  os.path.join(os.path.expanduser('~'), "abt-cli.log")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir, 0777)
except Exception as ex :
    print " log dir creation failed"
    pass

hdlr = logging.FileHandler(log_dir +'/abt-cli.log')
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)s] - %(message)s')
# add formatter to hdlr
hdlr.setFormatter(formatter)
# add hdlr to logger
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
