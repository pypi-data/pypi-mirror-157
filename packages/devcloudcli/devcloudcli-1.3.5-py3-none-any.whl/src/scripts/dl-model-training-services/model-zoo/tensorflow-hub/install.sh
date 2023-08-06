# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0



if [[ $(pip --version) ]]; then
         echo -e "\e[1;32mpip3 is installed\e[0m"
     else
         echo -e "\e[1;32mInstalling pip3\e[0m"
         sudo apt-get update
         sudo apt-get -y install python3-pip
fi

#installing tensorflow-hub
if [[ $(pip3 show tensorflow_hub) ]]; then
         echo -e "\e[1;32mtensorflow_hub is installed\e[0m"
     else
         echo -e "\e[1;32mInstalling tensorflow_hub repository of trained models\e[0m"
         sudo pip3 install --upgrade tensorflow_hub
         echo -e "\e[1;32mTensorFlow Hub of trained machine learning model is installed\e[0m"
         echo -e "\e[1;34m\nRefer-->https://www.tensorflow.org/hub/tutorials to know more about TensorFlow-Hub\e[0m"

fi


echo -e "\e[1;31mFor further queries please follow below URL\e[0m"


echo -e "\e[1;32mhttps://tfhub.dev/\e[0m"
