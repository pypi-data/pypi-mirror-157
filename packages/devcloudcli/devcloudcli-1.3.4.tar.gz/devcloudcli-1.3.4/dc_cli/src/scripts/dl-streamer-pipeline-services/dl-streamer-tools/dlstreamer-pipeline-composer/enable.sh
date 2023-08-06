#!/bin/bash
INTEL_OPENVINO_DIR=/opt/intel/openvino_2021
SINK_ELEMENT=fps
DECODE_DEVICE=CPU
INFERENCE_DEVICE=CPU
CHANNELS_COUNT=1

USER=/home/intel
DIR=$USER/dlstreamer
INPUT_VIDEO=$USER/sample-videos/people-detection.mp4
if [ -d "$DIR" ]; then
    echo -e "\e[1;32mSuccess\e[0m"
    source $INTEL_OPENVINO_DIR/bin/setupvars.sh
    export MODELS_PATH=$PWD/
    cd $DIR/samples/benchmark/
    ./benchmark.sh $INPUT_VIDEO $DECODE_DEVICE $INFERENCE_DEVICE $CHANNELS_COUNT
else
    echo -e "\e[1;31mError: ${DIR} not found. Please run installation script.\e[0m"
fi
