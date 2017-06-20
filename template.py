import time
def StructureHeaderTemplates(feature):
    header = 'import(\n\
        "fmt"\n\
        "github.com/chzyer/readline"\n\
        "github.com/codegangsta/cli"\n\
        "product/common"\n\
      )\n'
    return 'package '+feature+'\n'+header

def GetCommonTemplate():
    template = '\n\
package common\n\
\n\
import (\n\
        "github.com/codegangsta/cli"\n\
        "github.com/chzyer/readline"\n\
        "product/logger"\n\
)\n\
\n\
var RlSession *readline.Instance\n\
var logs = logger.GetLogger(logger.GetLoggerName("common"))\n\
\n\
\n\
type RestCall func(reqType string, reqUrl string, reqBody string, headerMap map[string]string)([]byte, error)\n\
func RestFunction(reqType string, reqUrl string, reqBody string, headerMap map[string]string)([]byte, error){\n\
    return []byte{\'A\'}, nil\n\
}\n\
\n\
type fn func(*cli.Context, string, string, RestCall) bool\n\
func ExecuteCommand(c *cli.Context, f fn) {\n\
    RlSession.SetPrompt("cli$ ")\n\
    f(c, "", "", RestFunction)\n\
    return\n\
}\n'
    return template
def GetFunctionTemplate(feature):
    header = 'import (\n\
         "fmt"\n\
         "github.com/codegangsta/cli"\n\
         "product/common"\n\
         "product/logger"\n\
         "os"\n\
       )\n'

    log  = 'var logs = logger.GetLogger(logger.GetLoggerName("'+feature+'"))\n'
    header += log
    template = '\n\
func YourDummyFunction(c *cli.Context, token string, url string, httpcall common.RestCall) bool{\n\
\n\
    var requestBody string\n\
    if c.String("your-flags") == "None"{\n\
        logs.Error("Please specify your flags. Refer to help.")\n\
        fmt.Fprintln(os.Stderr, "Please specify your flags. Refer to help.")\n\
        return false\n\
    } else {\n\
        // if requestbody need to set for calling RESTful API\n\
        requestBody = `{"your-flag":"`+c.String("your-flag")+ `"}`\n\
    }\n\
    logs.Debug(requestBody)\n\
    headerMap := make(map[string]string)\n\
    headerMap["X-Auth-Token"] = token\n\
    headerMap["Content-Type"] = "application/json"\n\
    respBody, err := httpcall("POST", url+"/api/dummy/version/", requestBody, headerMap)\n\
    if err != nil || respBody == nil{\n\
        logs.Error("Your error message- http request error")\n\
        fmt.Fprintln(os.Stderr, "Your error message - http request error")\n\
        return false\n\
    }\n\
    if c.Bool("json") == true {\n\
        //return common.PrintJson(respBody)\n\
    } else {\n\
          // unmashal your json fields here in your structure variable\n\
    }\n\
    logs.Info("Success message")\n\
    fmt.Println("Success message")\n\
    return true\n\
}\n'

    return 'package '+feature+'\n'+ header + template


def GetActionTemplate(subcmd):
    template = '\n\
                 {\n\
                    Name:      \"'+subcmd +'\",\n\
                    Usage:  "Place your message here",\n\
                    Flags: []cli.Flag {\n\
                        cli.BoolFlag{Name: "json, j", Usage: "(Optional) Show output in JSON format"},\n\
                    },\n\
                    Action: func(c *cli.Context) error {\n\
                        fmt.Println("")\n\
                        common.ExecuteCommand(c, YourDummyFunction)\n\
                        return nil\n\
                    },\n\
                 },\n'
    return template

def FillFlagsTemplate(val):
    try:
        data = ''
        for k, v in val.items():
            flags = v.keys()    
            for i in flags:
                tmp ='\n\
                        cli.StringFlag {\n\
                            Name:        \"'+i +'\",\n\
                            Value:       "None",\n\
                            Usage:       \"('+ k.capitalize() +') Place your message",\n\
                        },\n'
                data = data + tmp
        return data
    except Exception as e:
        print e
     
    

def GetFlagsTemplate(subcmd, val):
    data = FillFlagsTemplate(val)
    templates = '\n\
                 {\n\
                    Name:   \"'+subcmd +'\",\n\
                    Usage:  "Place your message here",\n\
                    Flags: []cli.Flag {\n' + data +'\n\
                    },\n\
                    Action: func(c *cli.Context) error {\n\
                        fmt.Println("")\n\
                        common.ExecuteCommand(c, YourDummyFunction)\n\
                        return nil\n\
                    },\n\
                 },\n'

    return  templates

def GetFlagsTemplateSingle(subcmd, val):
    data = FillFlagsTemplate(val)
    templates = '\n\
                 {\n\
                    Name:   \"'+subcmd +'\",\n\
                    Usage:  "Place your message here",\n\
                    Flags: []cli.Flag {\n' + data +'\n\
                    },\n\
                    Action: func(c *cli.Context) error {\n\
                        fmt.Println("")\n\
                        //'+ subcmd+'.YourDummyFunction(c, common.RestFunction)\n\
                        return nil\n\
                    },\n\
                 },\n'

    return  templates

def GetTemplate(subcmd):
    template = '\n\
                 {\n\
                    Name:      \"'+subcmd +'\",\n\
                    Usage:     \"'+subcmd.capitalize()+' commands",\n\
                    BashComplete: func(c *cli.Context) {\n\
                        if c.NArg() > 0 {\n\
                            return\n\
                        }\n\
                        for _, t := range '+subcmd.capitalize()+'CommandStrings {\n\
                            fmt.Println(t)\n\
                        }\n\
                    },\n\
                    Subcommands: '+subcmd.capitalize()+'Commands,\n\
                 },\n'
    return template


def GetLoggerTemplate():
    template = 'package logger\n\
import (\n\
    "github.com/hhkbp2/go-logging"\n\
    "os"\n\
    "fmt"\n\
    "encoding/json"\n\
    "io/ioutil"\n\
    "time"\n\
)\n\
\n\
type Loggers struct {\n\
   LoggerNames map[string]string `json:"loggers"`\n\
}\n\
\n\
var Logs []string\n\
\n\
func InitLog(logFile ...string) {\n\
   if (len(logFile) != 0) {\n\
       _, err_ := os.Stat(logFile[0])\n\
\n\
       if os.IsNotExist(err_){\n\
           fmt.Println("Log file path does not exist.")\n\
           return\n\
       }\n\
       file, _ := ioutil.ReadFile(logFile[0])\n\
       var loggers Loggers\n\
       json.Unmarshal(file, &loggers)\n\
       for key := range loggers.LoggerNames {\n\
           Logs = append(Logs, key)\n\
       }\n\
\n\
       if err := logging.ApplyConfigFile(logFile[0]); err != nil {\n\
           fmt.Println("Invalid log config file.")\n\
       }\n\
    }else{\n\
        filePath := os.Getenv("HOME")+"/.mycli.log"\n\
        fileMode := os.O_APPEND\n\
        bufferSize := 0\n\
        bufferFlushTime := 30 * time.Second\n\
        inputChanSize := 0\n\
        fileMaxBytes := uint64(100 * 1024 * 1024)\n\
        backupCount := uint32(10)\n\
        handler := logging.MustNewRotatingFileHandler(\n\
        filePath, fileMode, bufferSize, bufferFlushTime, inputChanSize,\n\
        fileMaxBytes, backupCount)\n\
        format := "%(asctime)s (%(filename)s:%(lineno)d:%(funcname)s) %(levelname)s : %(message)s"\n\
        dateFormat := "%Y-%m-%d %H:%M:%S.%3n"\n\
        formatter := logging.NewStandardFormatter(format, dateFormat)\n\
        handler.SetFormatter(formatter)\n\
\n\
        logs := GetLogger(GetLoggerName("ascli"))\n\
        logs.SetLevel(logging.LevelInfo)\n\
        logs.AddHandler(handler)\n\
    }\n\
}\n\
\n\
func GetLogger(name string) logging.Logger {\n\
    return logging.GetLogger(name)\n\
}\n\
\n\
func GetLoggerName(name string) string {\n\
    for _ ,key := range Logs {\n\
        if name == key {\n\
            return key\n\
        }\n\
    }\n\
    return "cli"\n\
}\n\
'
    return template




def GetCommandTemp(feature):
    template = '\n        {\n\
            Name:      "'+feature+'",\n\
            Usage:     "Your Usage",\n\
            BashComplete: func(c *cli.Context) {\n\
                if c.NArg() > 0 {\n\
                    return\n\
                }\n\
                for _, t := range '+feature+'.'+feature.capitalize()+'CommandStrings {\n\
                    fmt.Println(t)\n\
                }\n\
            },\n\
            Subcommands: '+feature+'.'+feature.capitalize()+'Commands,\n\
        },'
    return template

def GetCommandHeader(features, val, cli_name):
    
    commands = '    commands := []cli.Command{\n\
                 {\n\
                     Name:      "help",\n\
                     Usage:     "Shows a list of commands",\n\
                     ArgsUsage: "[command]",\n\
                     Action: func(c *cli.Context) error {\n\
                         args := c.Args()\n\
                         if args.Present() {\n\
                             return cli.ShowCommandHelp(c, args.First())\n\
                         }\n\
                         cli.ShowAppHelp(c)\n\
                         return nil\n\
                     },\n\
                 },\n\
                 {\n\
                     Name:      "exit",\n\
                     Usage:     "Exit from CLI",\n\
                     Action: func(c *cli.Context) error {\n\
                     \n\
                           os.Exit(0)\n\
                           return nil\n\
                     },\n\
                 },\n\
    '
 
    setup = '    rl, err := readline.NewEx(&readline.Config{\n\
        Prompt:       "'+ cli_name +':~$ ",\n\
        HistoryFile:  os.Getenv("HOME")+"/.cli.history",\n\
        AutoComplete: completer,\n\
        HistoryLimit: 5000,\n\
    })\n\
    if err != nil {\n\
        panic(err)\n\
    }\n\
'
    completer = ""
    cmList = 'func GetCommandsList() (*readline.Instance,[]cli.Command) {\n\
    var completer = readline.NewPrefixCompleter(\n'

    template = 'package commandHandler\n\
\n\
import (\n\
    "fmt"\n\
    "github.com/chzyer/readline"\n\
    "github.com/codegangsta/cli"\n\
    "os"\n\
    "product/common"\n\
'
    foot = '\n    }\n\
    return rl,commands\n\
}'
    i = 0
    for f in features:
        
        template += "    \"product/" + f + "\"\n"
        k,v = val[i].keys()
        if  (k=="required" and v == "optional") or (v == "required" and k == "optional"):
            completer += '\n        readline.PcItem("' + f + '"),\n'
            isCommon = True
        else:
            completer += "        " + f + "." + f.capitalize() + "Readline,\n"
        commands += GetFlagsTemplateSingle(f, val[i])
        i = i + 1
    completer += "        readline.PcItem(\"exit\"),\n" +  "        readline.PcItem(\"help\"),\n" + "    )\n\n"
    template += ")\n"
    template += cmList + completer + setup + commands + foot
    
        
    return template 

def BuildTemplate(cli_name):
    template = '#!/usr/bin/env bash\n\
# set up our environment\n\
. ./env.sh\n\
if [ -d "cli/src/git.apache.org/thrift.git" ] ; then\n\
    rm -rf cli/src/git.apache.org/thrift.git\n\
fi\n\
# build cli executable\n\
echo Building cli...$GOPATH\n\
go get github.com/codegangsta/cli\n\
go get github.com/chzyer/readline\n\
go get  github.com/olekukonko/tablewriter\n\
go get  github.com/kballard/go-shellquote\n\
git clone https://github.com/apache/thrift.git cli/src/git.apache.org/thrift.git\n\
go get github.com/hhkbp2/go-logging\n\
go install cli/src/product/productcli/'+ cli_name +'.go\n\
cp -f cli/src/github.com/codegangsta/cli/autocomplete/bash_autocomplete cli/bin/.\n\
'
    return template


def GetCliTemplate(cli_name):
    template = 'package main\n\
\n\
import (\n\
    "fmt"\n\
    "github.com/codegangsta/cli"\n\
    "os"\n\
    "os/signal"\n\
    "syscall"\n\
    "product/logger"\n\
    "product/common"\n\
    "product/commandHandler"\n\
    "github.com/kballard/go-shellquote"\n\
)\n\
\n\
var logs = logger.GetLogger(logger.GetLoggerName("cli"))\n\
var Version = "0.0"\n\
\n\
func main() {\n\
    c := make(chan os.Signal)\n\
    signal.Notify(c, os.Interrupt, syscall.SIGTERM)\n\
    rl,commands := commandHandler.GetCommandsList()\n\
    defer rl.Close()\n\
    \n\
    app := cli.NewApp()\n\
    app.EnableBashCompletion = true\n\
    app.Commands = commands\n\
    app.Name = "'+ cli_name +'"\n\
    app.Version = Version\n\
    app.Usage = "'+ cli_name +'"\n\
    app.Action = func(ctx *cli.Context) error {\n\
        console := cli.NewApp()\n\
        console.Commands = commands\n\
        console.HideVersion = true\n\
        console.Version = Version\n\
        console.Action = func(c *cli.Context) error {\n\
            fmt.Println("Command not found. Type \'help\' for a list of commands.")\n\
            return nil\n\
        }\n\
        common.RlSession = rl\n\
\n\
        for {\n\
            line, err := rl.Readline()\n\
            words, err := shellquote.Split("cmd " + line)\n\
            if err != nil {\n\
                fmt.Println(err)\n\
                logs.Error(err)\n\
                continue\n\
            }\n\
            logger.InitLog()\n\
            console.Run(words)\n\
        }\n\
        return nil\n\
    }\n\
    app.Run(os.Args)\n\
}'


    return template 
