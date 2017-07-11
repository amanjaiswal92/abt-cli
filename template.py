import time

from config import *


def StructureHeaderTemplates(feature):
    logger.info("StructureHeaderTemplates")
    header = 'import(\n\
        "fmt"\n\
        "github.com/chzyer/readline"\n\
        "github.com/codegangsta/cli"\n\
        "product/common"\n\
      )\n'
    
    logger.info("StructureHeaderTemplates success")
    return 'package '+feature+'\n'+header

def GetCommonTemplate():
    logger.info("GetCommonTemplate")
    template = '\n\
package common\n\
import (\n\
	"fmt"\n\
	"github.com/codegangsta/cli"\n\
	"github.com/chzyer/readline"\n\
	"io/ioutil"\n\
	"net/http"\n\
	"os"\n\
	"bytes"\n\
	"encoding/json"\n\
	"errors"\n\
	"strings"\n\
	"io"\n\
	"time"\n\
	"bufio"\n\
	"mime/multipart"\n\
        "crypto/x509"\n\
	"crypto/tls"\n\
)\n\
\n\
\n\
var SessionFile string = os.Getenv("HOME")+"/.pioSessions"\n\
const DefaultTimeoutSeconds int = 5\n\
const DefaultSessionTimeoutMinutes int = 6\n\
var TimeoutSeconds int = DefaultTimeoutSeconds\n\
var RlSession *readline.Instance\n\
var IsLoggedIn bool = false\n\
var InteractiveMode bool\n\
var SecureHttpFlag bool\n\
\n\
type invalidResponse struct {\n\
    Message string `json:"message"`\n\
    Success bool   `json:"success"`\n\
}\n\
\n\
func ExitFromCli(ctx *cli.Context) {\n\
    os.Exit(0)\n\
}\n\
\n\
func PrintJson(body []byte) bool {\n\
        var out bytes.Buffer\n\
        err := json.Indent(&out, body, "", "  ")\n\
        if err != nil {\n\
            fmt.Fprintln(os.Stderr, "Unable to pretty print JSON: ", err)\n\
            return false\n\
        }\n\
        fmt.Print(string(out.Bytes())+"\n")\n\
        return true\n\
}\n\
\n\
func LoginRest(reqType string, reqUrl string, reqBody string, headerMap map[string]string)([]byte, error){\n\
    var bodyStream = []byte(reqBody)\n\
    var  skipVerifyFlag bool = false\n\
    tls_connection_url := reqUrl\n\
    caFile := ""\n\
    req, err := http.NewRequest(reqType, reqUrl, bytes.NewBuffer(bodyStream))\n\
    if err != nil {\n\
        fmt.Fprintln(os.Stderr, "Error creating request: ", err)\n\
    }\n\
\n\
    for key, value := range headerMap {\n\
        req.Header.Set(key, value)\n\
    }\n\
\n\
    var client *http.Client\n\
    var tlsConfig = &tls.Config{}\n\
\n\
    if caFile == "" {\n\
        tlsConfig = &tls.Config{\n\
            InsecureSkipVerify: true,\n\
        }\n\
    } else {\n\
        // Load CA cert\n\
        caCert, err := ioutil.ReadFile(caFile)\n\
        if err != nil {\n\
            fmt.Println("Failed to open certificate file")\n\
            return nil, err\n\
        }\n\
\n\
        // create the set of root certificates\n\
        caCertPool := x509.NewCertPool()\n\
        ok := caCertPool.AppendCertsFromPEM(caCert)\n\
        if !ok {\n\
            fmt.Println("Failed to parse root certificate")\n\
            return nil, errors.New("Failed to parse root certificate")\n\
        }\n\
\n\
        // creating tls request url to check connection\n\
        if string(reqUrl[4]) == "s" {\n\
            tls_connection_url = strings.TrimRight(string(reqUrl[8:]), "/login")\n\
        } else {\n\
            tls_connection_url = strings.TrimRight(string(reqUrl[7:]), "/login")\n\
        }\n\
\n\
        // Setup HTTPS client\n\
        if skipVerifyFlag {\n\
            tlsConfig = &tls.Config{\n\
                RootCAs:      caCertPool,\n\
                InsecureSkipVerify: true,\n\
            }\n\
        } else {\n\
            tlsConfig = &tls.Config{\n\
                RootCAs:      caCertPool,\n\
            }\n\
        }\n\
\n\
        // checking if connection is successful\n\
        conn, err := tls.Dial("tcp", tls_connection_url, tlsConfig)\n\
	if err != nil {\n\
	    fmt.Println("Failed to connect: " + err.Error())\n\
            return nil, errors.New("Failed to connect: " + err.Error())\n\
	}\n\
	conn.Close()\n\
    }\n\
    if string(reqUrl[4]) == "s" {\n\
        tr := &http.Transport{\n\
	    TLSClientConfig: tlsConfig,\n\
        }\n\
        client = &http.Client{\n\
	    Timeout: time.Duration(TimeoutSeconds) * time.Second,\n\
	    Transport: tr,\n\
        }\n\
    } else {\n\
        client = &http.Client{Timeout: time.Duration(TimeoutSeconds)*time.Second}\n\
    }\n\
    resp, err := client.Do(req)\n\
    if err != nil {\n\
    	fmt.Fprintln(os.Stderr, err)\n\
        return nil, err\n\
    }\n\
\n\
    defer resp.Body.Close()\n\
    body,err := ioutil.ReadAll(resp.Body)\n\
    if err != nil {\n\
    	fmt.Fprintln(os.Stderr, "Unable to read response body: ", err)\n\
    	return nil, err\n\
    }\n\
    if resp.StatusCode != 200 {\n\
    	fmt.Fprintln(os.Stderr, resp.Status)\n\
    	var errResponse invalidResponse\n\
    	err = json.Unmarshal(body, &errResponse)\n\
        if err != nil {\n\
            fmt.Fprintln(os.Stderr, "Unable to parse error response")\n\
        }\n\
        fmt.Fprintln(os.Stderr, errResponse.Message)\n\
    	return nil, errors.New(errResponse.Message)\n\
    }\n\
    return body, nil\n\
\n\
\n\
}\n\
\n\
type RestCall func(reqType string, reqUrl string, reqBody string, headerMap map[string]string)([]byte, error)\n\
func RestFunction(reqType string, reqUrl string, reqBody string, headerMap map[string]string)([]byte, error){\n\
	var bodyStream = []byte(reqBody)\n\
	req, err := http.NewRequest(reqType, reqUrl, bytes.NewBuffer(bodyStream))\n\
	if err != nil {\n\
		fmt.Fprintln(os.Stderr, "Error creating request: ", err)\n\
	}\n\
	for key, value := range headerMap {\n\
		req.Header.Set(key, value)\n\
	}\n\
	var client *http.Client\n\
        client = GetClient(reqUrl)\n\
\n\
        resp, err := client.Do(req)\n\
\n\
    if err != nil {\n\
        fmt.Fprintln(os.Stderr, err)\n\
        return nil, err\n\
    }\n\
\n\
    defer resp.Body.Close()\n\
    body,err := ioutil.ReadAll(resp.Body)\n\
    if err != nil {\n\
    	fmt.Fprintln(os.Stderr, "Unable to read response body: ", err)\n\
    	return nil, err\n\
    }\n\
    if resp.StatusCode != 200 && resp.StatusCode != 201 {\n\
    	fmt.Fprintln(os.Stderr, resp.Status)\n\
    	var errResponse invalidResponse\n\
    	err = json.Unmarshal(body, &errResponse)\n\
        if err != nil {\n\
            fmt.Fprintln(os.Stderr, "Unable to parse error response")\n\
        }\n\
        fmt.Fprintln(os.Stderr, errResponse.Message)\n\
    	return nil, errors.New(errResponse.Message)\n\
    }\n\
    return body, nil\n\
}\n\
\n\
func RestDownload(reqType string, reqUrl string, outfile string, headerMap map[string]string)([]byte, error){\n\
	fmt.Println("Downloading", reqUrl, "to", outfile)\n\
        \n\
	req, err := http.NewRequest(reqType, reqUrl, nil)\n\
\n\
	if err != nil {\n\
		fmt.Fprintln(os.Stderr, "Error creating request: ", err)\n\
	}\n\
\n\
	for key, value := range headerMap {\n\
		req.Header.Set(key, value)\n\
	}\n\
	var client *http.Client\n\
	SecureHttpFlag = false\n\
\n\
        client = GetClient(reqUrl)\n\
	resp, err := client.Do(req)\n\
	if err != nil {\n\
            return nil, err\n\
	}\n\
\n\
	defer resp.Body.Close()\n\
\n\
\n\
	if resp.StatusCode != 200 {\n\
	    return nil, errors.New(resp.Status)\n\
	}\n\
\n\
	output, err := os.Create(outfile)\n\
	if err != nil {\n\
		fmt.Fprintln(os.Stderr, "Error while creating", outfile, "-", err)\n\
		return nil, errors.New("Unable to download file")\n\
	}\n\
	defer output.Close()\n\
\n\
	n, err := io.Copy(output, resp.Body)\n\
	if err != nil {\n\
		fmt.Fprintln(os.Stderr, "Error while downloading", reqUrl, "-", err)\n\
		return nil, errors.New("Unable to download file")\n\
	}\n\
\n\
	fmt.Println(n, "Bytes downloaded.")\n\
	return nil, nil\n\
}\n\
\n\
func GetClient(url string) *http.Client {\n\
\n\
    var client *http.Client\n\
    if string(url[4]) == "s" {\n\
        SecureHttpFlag = true\n\
        tr := &http.Transport{\n\
            TLSClientConfig: &tls.Config{InsecureSkipVerify: true},\n\
        }\n\
        client = &http.Client{\n\
		//Timeout: time.Duration(TimeoutSeconds) * time.Second,\n\
		Transport: tr,\n\
        }\n\
    } else{\n\
		client = &http.Client{ }\n\
    }\n\
    return client\n\
\n\
}\n\
\n\
func RestUpload(reqType string, url string,  file string, headerMap map[string]string) ([]byte, error) {\n\
\n\
    var b bytes.Buffer\n\
    SecureHttpFlag = false\n\
    w := multipart.NewWriter(&b)\n\
    f, err := os.Open(file)\n\
    if err != nil {\n\
        return nil, err\n\
    }\n\
    defer f.Close()\n\
    fw, err := w.CreateFormFile("filename", file)\n\
    if err != nil {\n\
        return nil, err\n\
    }\n\
    if _, err = io.Copy(fw, f); err != nil {\n\
        return nil, err\n\
    }\n\
    w.Close()\n\
\n\
\n\
    req, err := http.NewRequest(reqType, url, &b)\n\
    if err != nil {\n\
        return nil, err\n\
    }\n\
\n\
    for key, value := range headerMap {\n\
        req.Header.Set(key, value)\n\
    }\n\
    req.Header.Set("Content-Type", w.FormDataContentType())\n\
\n\
    var client *http.Client\n\
    client = GetClient(url)\n\
    res, err := client.Do(req)\n\
    if err != nil {\n\
	return nil, err\n\
    }\n\
    defer res.Body.Close()\n\
\n\
    body,err := ioutil.ReadAll(res.Body)\n\
    if err != nil {\n\
        fmt.Fprintln(os.Stderr, "Unable to read response body: ", err)\n\
        return nil, err\n\
    }\n\
    if res.StatusCode != 200 {\n\
        var errResponse invalidResponse\n\
        err = json.Unmarshal(body, &errResponse)\n\
        if err != nil {\n\
            fmt.Fprintln(os.Stderr, "Unable to parse error response")\n\
        }\n\
        fmt.Fprintln(os.Stderr, errResponse.Message)\n\
        return nil, errors.New(errResponse.Message)\n\
    }\n\
\n\
    return body, nil\n\
}\n\
\n\
\n\
func GetTokenAndUrl()(string, string) {\n\
    f,err := os.Open(SessionFile)\n\
\n\
    if err != nil {\n\
        return "NONE", "NONE"\n\
    }\n\
    token, url := "NONE", "NONE"\n\
    if err != nil {\n\
        return token, url\n\
    }\n\
    scanner:=bufio.NewScanner(f)\n\
    for scanner.Scan(){\n\
        line := scanner.Text()\n\
        s := strings.Split(line, "=")\n\
        if s[0] == "TOKEN" {\n\
            token = s[1]\n\
        } else if s[0] == "URL" {\n\
            url = s[1]\n\
        }\n\
    }\n\
    return token, url\n\
}\n\
type fn func(*cli.Context, string, string, RestCall) bool\n\
func ExecuteCommand(c *cli.Context, f fn) bool {\n\
    var retbool bool\n\
    if IsLoggedIn == false {\n\
        fmt.Println("Please login")\n\
        return true\n\
    }\n\
    token, url := GetTokenAndUrl()\n\
    if token == "None" || url == "None" {\n\
        fmt.Println("Please Login.")\n\
        return false\n\
    }\n\
    if c.Command.Name == "download" { \n\
        retbool = f(c, token, url, RestDownload)\n\
    } else if c.Command.Name == "upload" {\n\
        retbool = f(c, token, url, RestUpload)\n\
    } else {\n\
        retbool = f(c, token, url, RestFunction)\n\
    }\n\
\n\
    return retbool \n\
}\n\
    return \n\
}'   
    logger.info("GetCommonTemplate success.")
    return template

def GetFunctionTemplate(feature):
    logger.info("GetFunctionTemplate")
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

    logger.info("GetFunctionTemplate success")
    return 'package '+feature+'\n'+ header + template


def GetActionTemplate(subcmd):
    logger.info("GetActionTemplate")
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
    logger.info("GetActionTemplate success")
    return template

def FillFlagsTemplate(val):
    logger.info("FillFlagsTemplate.")
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
        logger.info("success")
        return data
    except Exception as e:
        logger.error("FillFlagsTemplate.", e)
        print e
     
    

def GetFlagsTemplate(subcmd, val):
    logger.info("GetFlagsTemplate")
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

    logger.info("GetFlagsTemplate success.")
    return  templates

def GetFlagsTemplateSingle(subcmd, val):
    logger.info("GetFlagsTemplateSingle")
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

    logger.info("GetFlagsTemplateSingle success")
    return  templates

def GetTemplate(subcmd):
    logger.info("GetTemplate")
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
    logger.info("GetTemplate success")
    return template


def GetLoggerTemplate():
    logger.info("GetLoggerTemplate")
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
    logger.info("GetLoggerTemplate success")
    return template




def GetCommandTemp(feature):
    logger.info("GetCommandTemp")
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
    logger.info("GetCommandTemp success")
    return template

def GetCommandHeader(features, val, cli_name):
    
    logger.info("GetCommandHeader")
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
    
        
    logger.info(" GetCommandHeader success.")
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
