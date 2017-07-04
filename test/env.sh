
#!/usr/bin/env bash
if [ $GOBIN ]; then
    PATH=$(echo $PATH | sed -e "s;\(^$GOBIN:\|:$GOBIN$\|:$GOBIN\(:\)\);\2;g")
fi
CLI_DIR=$PWD
export CTEST_OUTPUT_ON_FAILURE=1
export GOPATH=$CLI_DIR/cli
export LD_LIBRARY_PATH=
export DYLD_LIBRARY_PATH=
export GOBIN=$GOPATH/bin
export PATH=$GOBIN:$PATH
