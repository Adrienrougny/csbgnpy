#!/bin/bash
DIR=`dirname $0`
java -jar ${DIR}/KEGGtranslator_v2.5.jar --input $1 --output $2 --format SBGN &>/dev/null
