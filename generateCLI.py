import sys
import os
import json
import template as tm
import time
import argparse
PROJECT = "Project"
CLI_PATH = "/cli/src/product/"
CLI_NAME = "cli"

def readData(jsonFile):
    with open(jsonFile) as data_file:    
        try:
            data = json.load(data_file)
        except:
            print "Invalid JSON file"
            exit(1)
    return data


def commandStruct(val, feature, fp):
    try:

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

    except Exception as e:
        print e



def createData(val,str1):
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
    except Exception as e:
	print e


def createCommands(feature, val, fp):
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
    except Exception as e:
        print e


def readlineTemplate(key, space, fp):
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
    except Exception as e:
        print e

def createFeatureDir(feature):
    global PROJECT
    dirs = PROJECT + "/cli/src/product/"
    dirs += feature
    try:
        if not os.path.exists(dirs):
            os.mkdir(path)
    except Exception as e:
        print e

def createFiles(path, feature, val):
    
    k, v = val.items()
    mainFile = path+"/"+feature+".go"
    if (k[0]=="required" and v[0] == "optional") or (v[0]=="required" and k[0] == "optional"):
        fpCommand = open(mainFile,"w")
        fpCommand.write(tm.GetFunctionTemplate(feature))
        fpCommand.close()
        return
    pc = 'readline.PcItem('
    commandFile = path+"/"+feature+"Commands.go"
    structureFile = path+"/"+feature+"Structures.go"
    testFile = path+"/"+feature+"_test.go"
    
    fpCommand = open(commandFile,"w")
    fpCommand.write(tm.StructureHeaderTemplates(feature))
    
    data = 'var ' + feature.capitalize() + "Readline" + " = " + pc + "\"" + feature + "\",\n"
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
    try:
        for k, v in val.items():
            createCommands(k, v, fpCommand)
    except Exception as e:
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
    fp = open(PROJECT + "/cli/src/product/commandHandler/commandHandler.go","w")
    features = []
    val = []
    for f , v in data.items():
        features.append(f)
        val.append(v)
    fp.write(tm.GetCommandHeader(features, val, CLI_NAME))
    
    

def createCli(data):
    global CLI_PATH, CLI_NAME
    global PROJECT
    try:
        for feature , val in data.items():
            path = CLI_PATH + feature
        #    k, v = val.items()
        #    if (k[0]!="required" or v[0] != "required") and (v[0] != "optional" or k[0] != "optional"):
            if not os.path.exists(path):
                os.mkdir(path)
            createFiles(path, feature, val)
        commandsHandle(data)
        fp = open(PROJECT +"/cli/src/product/common/common.go","w")
        fp.write(tm.GetCommonTemplate())
        fp.close()
        fp = open(PROJECT+"/cli/src/product/logger/logger.go","w")
        fp.write(tm.GetLoggerTemplate())
        fp.close()
        fp = open(PROJECT+"/cli/src/product/productcli/"+ CLI_NAME +".go","w")
        fp.write(tm.GetCliTemplate(CLI_NAME))
        fp.close()
        fp = open(PROJECT+"/build.sh","w")
        fp.write(tm.BuildTemplate(CLI_NAME))
        fp.close()
        
    except Exception as e:
        print e


def generateBasicStructure():
    global PROJECT
    cwd = os.getcwd()
    if not os.path.exists(PROJECT):
        os.makedirs(PROJECT)
    os.chdir(PROJECT)
    dir1 = ['cli', 'cli/bin', 'cli/docs', 'cli/pkg', 'cli/src', 'cli/src/product']
    dir2 = ['cli/src/product/common', 'cli/src/product/logger', 'cli/src/product/commandHandler', 'cli/src/product/productcli']
    dirs = dir1 + dir2
    try:
        for i in dirs:
            if not os.path.exists(i):
                os.makedirs(i)
        os.chdir(cwd)
        return 0
        
    except Exception as e:
        print e
    return 1

if __name__=="__main__":
   
#    global PROJECT
#    global CLI_PATH
    try:
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
    except :
        print parser.print_help()
        sys.exit(0)



