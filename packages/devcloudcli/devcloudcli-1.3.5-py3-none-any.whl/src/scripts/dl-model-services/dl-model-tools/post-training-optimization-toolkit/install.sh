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
# Creating a symbolic link 

ln -s /opt/intel/openvino_2021/deployment_tools/tools/ workload/

echo -e "\e[1;31mSymbolic link created in workloads folder\e[0m"

echo -e "\e[1;32m\nFollow the README.md for usage\e[0m"




