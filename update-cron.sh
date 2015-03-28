#!/bin/bash

set -eu

run_tests () {
        local DIR=/home/2015tracker/IATI-Updates
        cd $DIR

        # 'activate' script cannot cope with set -u, so temp disable it
        set +u
        . pyenv/bin/activate
        set -u
        ./updater.py
}
