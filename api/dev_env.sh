#!/bin/bash

set -o pipefail
set -o errexit

## This script must be sourced!
if [ "x${BASH}" != "x/bin/bash" ] && [ "x${BASH}" != "x/usr/bin/bash" ]; then
    echo "Error: -- You're not using BASH, so this isn't going to work out between us.  Goodbye!" >&2
    return 42 >/dev/null 2>&1 # Return if being sourced in wrong shell
    exit 42 # Couldn't return, so not being sourced exit instead
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: -- You've not sourced me, so you have failed.  Quitting"
    exit 33
fi

api_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

rm -rf "$api_dir/.ve" || true

python3 -m venv "$api_dir/.ve"

source "$api_dir/.ve/bin/activate"

pip install --upgrade pip
pip install -r "$api_dir/src/requirements/base.txt"

set +o pipefail
set +o errexit

echo "Done creating the environment"
