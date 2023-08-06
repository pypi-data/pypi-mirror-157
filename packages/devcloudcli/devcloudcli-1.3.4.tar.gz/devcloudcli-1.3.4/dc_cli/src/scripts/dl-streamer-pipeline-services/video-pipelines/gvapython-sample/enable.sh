#!/bin/bash
INTEL_OPENVINO_DIR=/opt/intel/openvino_2021
INPUT_VIDEO=https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-female-and-male.mp4
SINK_ELEMENT=fps
DEVICE=CPU
USER=/home/intel
DIR=$USER/dlstreamer

if [ -d "$DIR" ]; then
    echo -e "\e[1;32mSuccess\e[0m"
    export $MODELS_PATH=$USER
    source $INTEL_OPENVINO_DIR/bin/setupvars.sh
    cd $DIR/samples/gst_launch/gvapython/face_detection_and_classification/
    ./face_detection_and_classification.sh $INPUT_VIDEO $DEVICE $SINK_ELEMENT 
else
    echo -e "\e[1;31mError: ${DIR} not found. Please run installation script.\e[0m"
fi
