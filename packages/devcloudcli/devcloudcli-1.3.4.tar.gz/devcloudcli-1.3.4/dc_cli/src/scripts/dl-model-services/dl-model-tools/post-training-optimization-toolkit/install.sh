#!/bin/bash


# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#checking git 
if [[ $(which git) && $(git --version) ]]; then
         echo -e "\e[1;36mgit installed in the system\e[0m"
     else
         echo -e "\e[1;36mInstalling git....\e[0m"
	 sudo apt-get install git -y
fi


#installing POT
if !(git clone -b 2022.1.0 https://github.com/openvinotoolkit/openvino.git) then
   exit 1
   echo -e "\e[1;32mgit is failing check with version or with the git link\e[0m"
else
    echo -e "\e[1;32mSuccess\e[0m"
    cd openvino/tools/pot/
    sudo python3 setup.py install
    echo -e "\e[1;32mpot is installed\e[0m"
fi

echo -e "\e[1;31mFor further queries please follow below URL\e[0m"
echo -e "\e[1;32m\nhttps://github.com/openvinotoolkit/openvino/tree/master/tools\e[0m"


