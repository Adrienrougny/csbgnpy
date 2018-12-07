#!/bin/bash

DIR=`dirname $0`
java -jar ${DIR}/paxtools-5.0.1.jar toSBGN $1 $2 -nolayout
