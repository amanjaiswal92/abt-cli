import sys
import os
import json
import template as tm
import time
import argparse
from config import *

PROJECT = "Project"
CLI_PATH = "/cli/src/product/"
CLI_NAME = "cli"

def readData(jsonFile):
    with open(jsonFile) as data_file:    
        try:
            data = json.load(data_file)
            logger.info("JSON file read success.")
        except Exception as ex:
            logger.error(ex, "Invalid JSON file")
            print "Invalid JSON file"
            exit(1)
    return data


def commandStruct(val, feature, fp):
    try:
        logger.info("Creating command structure")
        if val == {} or val == '':
            return
        key = val.keys()
        if key == []:
            return
        if ("optional" in key ) or ("required" in key) :
            return
       
        fp.write('var ' + feature.capitalize() + 'Commands' + ' = []cli.Command {\n')
        for i in key:
            flags = val[i].keys()
            if val[i].values() == []:
                fp.write(tm.GetActionTemplate(i))
            elif ("required" in flags) and ("optional" in flags):
                fp.write(tm.GetFlagsTemplate(i, val[i]))
            else: 
                feature = i
                fp.write(tm.GetTemplate(i))
        fp.write("}\n")
        for i in key:
           commandStruct(val[i],i, fp) 
        logger.info("Command structure success.")
    except Exception as e:
        logger.error(e, "Command structure failed.")
        print e



def createData(val,str1):
    logger.info("Create data {}/{}".format(val, str1) )
    pc = 'readline.PcItem('
    if val == {}:
        return str1
    try:
        for k,v in val.items():
            if k == "required" or k == "optional" :
                return str1
            str1.join(pc+ "\"" + k + "\",")
            data = createData(v, str1)
            return data + '),'
        logger.info("create data success.")
    except Exception as e:
        logger.error(e)
	print e


def createCommands(feature, val, fp):
    logger.info("Create commands ")
    var_cmd = ""
    if val == {} or val == '':
        return ''
    try:
        for k, v in val.items():
	    if  k == "optional" or k == "required":
	        continue
            createCommands(k, v, fp)
            var_cmd += "\""+k+"\", "
        if var_cmd != '' :
            data = 'var ' + feature.capitalize() + "CommandStrings" + " = []string {" + var_cmd + "}\n"
            fp.write(data)
        logger.info("Create command success")
    except Exception as e:
        logger.error(e)
        print e


def readlineTemplate(key, space, fp):
    logger.info("Readline template")
    try:
        pc = 'readline.PcItem('
        if key == {} :
            return
        if ("optional" in key) and ("required" in key):
            return
        ls = key.keys()
        if ls == []:
            return
        for i in ls:
            data =  " "*space + pc + "\"" + i + "\""
            if key[i] != {} and not (("optional" in key[i]) and ("required" in key[i])):
                data += ","
            elif key[i] == {} or (("optional" in key[i]) and ("required" in key[i])):
                data += "),"
            fp.write(data+"\n")
            space = space + 2
            readlineTemplate(key[i], space, fp)
            space = space - 2
        fp.write(" "*(space-2) +"),\n")
        logger.info("success.")
    except Exception as e:
        logger.error(e)
        print e

def createFeatureDir(feature):
    logger.info("create directory")
    global PROJECT
    dirs = PROJECT + "/cli/src/product/"
    dirs += feature
    try:
        if not os.path.exists(dirs):
            os.mkdir(path)
        logger.info("Success.")
    except Exception as e:
        logger.error(e)
        print e

def createFiles(path, feature, val):
    logger.info("create file :  val -> {}".format( val))
    #k, v = val.items()
    #logger.debug("{} {} ".format(k,v))
    mainFile = path+"/"+feature+".go"
    #if (k[0]=="required" and v[0] == "optional") or (v[0]=="required" and k[0] == "optional"):
    #    logger.debug("returning")    
    #    fpCommand = open(mainFile,"w")
    #    fpCommand.write(tm.GetFunctionTemplate(feature))
    #    fpCommand.close()
    #    return
    pc = 'readline.PcItem('
    commandFile = path+"/"+feature+"Commands.go"
    structureFile = path+"/"+feature+"Structures.go"
    testFile = path+"/"+feature+"_test.go"
    
    fpCommand = open(commandFile,"w")
    logger.debug("Header strcuture")
    fpCommand.write(tm.StructureHeaderTemplates(feature))
    
    data = 'var ' + feature.capitalize() + "Readline" + " = " + pc + "\"" + feature + "\",\n"
    logger.debug("Create feature dir")
    createFeatureDir(feature)
    
    fpCommand.write(data)
    readlineTemplate(val, 20, fpCommand)
    pos = fpCommand.tell()
    fpCommand.seek(pos-3)
    fpCommand.write(")\n\n")
    features = []
    head = "var " + feature.capitalize() + "CommandStrings = []string{" 
    for f , _ in val.items():
        head += "\"" + f + "\","
    head += "}\n"

    fpCommand.write(head)
    logger.debug("{} *** done".format(head))
    try:
        for k, v in val.items():
            createCommands(k, v, fpCommand)
        
    except Exception as e:
        logger.error(e)
        print e

    commandStruct(val, feature, fpCommand)
    fpCommand.close()
    fpCommand = open(mainFile,"w") 
    fpCommand.write(tm.GetFunctionTemplate(feature))
    fpCommand.close()

    #fpCommand = open(structureFile,"w")   

    #fpCommand.close()

    #fpCommand = open(testFile,"w")   

    #fpCommand.close()

    


def commandsHandle(data):
    global PROJECT, CLI_NAME
    logger.info("command handle")
    fp = open(PROJECT + "/cli/src/product/commandHandler/commandHandler.go","w")
    features = []
    val = []
    for f , v in data.items():
        features.append(f)
        val.append(v)
    logger.info("Command handler template")    
    fp.write(tm.GetCommandHeader(features, val, CLI_NAME))
    logger.info("success")    
    

def createCli(data):
    logger.info("create cli")
    global CLI_PATH, CLI_NAME
    global PROJECT
    try:
        for feature , val in data.items():
            logger.info("feature : {}  value : {}".format(feature, val))
            path = CLI_PATH + feature
        #    if (k[0]!="required" or v[0] != "required") and (v[0] != "optional" or k[0] != "optional"):
            if not os.path.exists(path):
                os.mkdir(path)
            createFiles(path, feature, val)
        
        logger.info("Command Handle")
        commandsHandle(data)
        logger.info("Common template")
        fp = open(PROJECT +"/cli/src/product/common/common.go","w")
        fp.write(tm.GetCommonTemplate())
        fp.close()
        logger.info("CLI template")
        fp = open(PROJECT+"/cli/src/product/productcli/"+ CLI_NAME +".go","w")
        fp.write(tm.GetCliTemplate(CLI_NAME))
        fp.close()
        logger.info("Build template")
        fp = open(PROJECT+"/build.sh","w")
        fp.write(tm.BuildTemplate(CLI_NAME))
        fp.close()
        logger.info("env template")
        fp = open(PROJECT+"/env.sh","w")
        fp.write(tm.GetEnv())
        fp.close() 
    except Exception as e:
        logger.error(e)
        print e


def generateBasicStructure():
    logger.info("Generate basic structure")
    global PROJECT
    cwd = os.getcwd()
    if not os.path.exists(PROJECT):
        os.makedirs(PROJECT)
    os.chdir(PROJECT)
    dir1 = ['cli', 'cli/bin', 'cli/docs', 'cli/pkg', 'cli/src', 'cli/src/product']
    dir2 = ['cli/src/product/common', 'cli/src/product/commandHandler', 'cli/src/product/productcli']
    dirs = dir1 + dir2
    try:
        for i in dirs:
            if not os.path.exists(i):
                os.makedirs(i)
        os.chdir(cwd)
        return 0
        
    except Exception as e:
        logger.error(e)
        print e
    return 1

if __name__=="__main__":
   
#    global PROJECT
#    global CLI_PATH
    try:
        logger.info("*******************Generating*****************************")
        parser = argparse.ArgumentParser(description='CLI tool')
        parser.add_argument('--config', nargs='?', help= "Configuration file in JSON")
        parser.add_argument('--project-name', nargs='?', help= "Project name")
        parser.add_argument('--cli-name', nargs='?', help= "CLI name")
        args = parser.parse_args()
        jsonFile = args.config
        PROJECT = args.project_name
        CLI_NAME = args.cli_name
        CLI_PATH = PROJECT + CLI_PATH
        data = readData(jsonFile)
        generateBasicStructure()
        createCli(data)
        logger.info("*********************************Done**************************")
    except Exception as e:
        logger.error(e)
        print parser.print_help()
        sys.exit(0)



