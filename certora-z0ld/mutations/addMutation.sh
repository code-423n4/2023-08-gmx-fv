#!/bin/bash

CONTRACTS_DIR="$1"
CONFIG_NAME="$2"

if [ -z "$CONTRACTS_DIR" ] || [ -z "$CONFIG_NAME" ]; then
    echo "usage:"
    echo "  ./addMutation.sh [CONTRACTS_DIR] [CONFIG_NAME] : generates a patch containing a manually injected bug and then restores the contracts directory"
    echo "Example:"
    echo "  ./addMutation.sh ../contracts/rewards oracle"
    exit 0
fi

# Bug generation
LAST_BUG_NUMBER=$(find certora/mutations/participants_${CONFIG_NAME} -type f -name "bug*.patch" | sort -t 'g' -k 2n | tail -n 1 | tr -dc '0-9' | awk '{$1=$1+1; print}')
git diff certora -- $CONTRACTS_DIR > certora/mutations/participants_${CONFIG_NAME}/bug${LAST_BUG_NUMBER}.patch

# Restore changes
git restore $CONTRACTS_DIR/*