#!/bin/bash

# Apply a bug, run prover and restore original file
# Run from the root git directory. Run without bug's number parameter to not apply any patches
# Examples:
#    ./certora/mutations/verifyBug.sh verifyRewardsController --rule initializeCalledOnce
#    ./certora/mutations/verifyBug.sh verifyRewardsController certora --rule initializeCalledOnce
#    ./certora/mutations/verifyBug.sh verifyRewardsController participants 2

if [ "$#" -lt 1 ]; then
    echo "Please provide the configuration name as the first argument (e.g., 'verifyRewardsController'). Optionally, provide the path as the second argument (either 'certora' or 'participants')."
    exit 1
fi

CONFIG_NAME="$1" # Capture the configuration name from the first parameter
shift            # Shift to analyze next argument

# Default DIR_NAME to empty string
DIR_NAME=""

# Check if next argument is a directory name and not a bug number or option
if [[ -n "$1" && ! $1 =~ ^[0-9]+$ && ! $1 =~ ^-- ]]; then
    DIR_NAME="$1"
    shift
fi

MSG="[run ${CONFIG_NAME}] $@"

# Check if the next argument is a bug number
if [[ $1 =~ ^[0-9]+$ ]]; then
  FILE_NAME="bug$1"
  shift 1 
  MSG="[prove ${DIR_NAME}_${CONFIG_NAME}/$FILE_NAME] $@"
fi

# If the patch file exists then apply and restore a bug
PATCH_PATH="certora/mutations/${DIR_NAME}_${CONFIG_NAME}/${FILE_NAME}.patch"
if [ -f "$PATCH_PATH" ]; then
  git apply "$PATCH_PATH"
  certoraRun certora/confs/${CONFIG_NAME}_verified.conf --send_only --msg "${MSG}" "$@"
  git apply -R "$PATCH_PATH"
else
  # Run without patching 
  certoraRun certora/confs/${CONFIG_NAME}_verified.conf --send_only --msg "${MSG}" "$@" 
fi