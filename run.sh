#!/bin/bash

cd $(dirname $0)
. ./python_env/bin/activate

set -o errexit -o nounset -o xtrace

./client.py
