#!/usr/bin/env bash
# ./delete.sh <stack-name>
set -euo pipefail
STACK="${1:?usage: ./delete.sh <stack-name>}"
aws cloudformation delete-stack --stack-name "$STACK"
aws cloudformation wait stack-delete-complete --stack-name "$STACK"
echo "Deleted $STACK"
