#!/bin/bash

# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Creating a symbolic link 

FILE=${PWD}/devcloud/dl-model-benchmark
echo ${PWD}
if [ ! -d "$FILE" ]; then
        echo -e "\e[1;31mdl-model-benchmark folder doesn't exists\e[0m"
else

        echo "intel123" | mv devcloud/dl-model-benchmark .

        echo -e "\e[1;34mDl-model-benchmark files are present in workload folder\e[0m"
        echo -e "\e[1;36m\nPre-requistes:\e[0m\n
                \e[1;33mpip3 install -r requirements.txt\e[0m\n
                \e[1;35m** Initialze OpenVino Environment mentioned in below command: **\e[0m \n
                \e[1;33msource /opt/intel/openvino_2021/bin/setupvars.sh\e[0m"
        echo -e "\e[1;32m\nFollow the README.md in the respective folders for usage\e[0m"
fi

