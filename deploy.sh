#!/usr/bin/env bash
# One command: ./deploy.sh <stack-name> [dev|staging|prod]
set -euo pipefail
STACK="${1:?usage: ./deploy.sh <stack-name> [dev|staging|prod]}"
ENVIRONMENT="${2:-dev}"
REGION="${AWS_REGION:-$(aws configure get region)}"
export AWS_DEFAULT_REGION="$REGION"

VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
SUBNETS=$(aws ec2 describe-subnets --filters Name=vpc-id,Values="$VPC" --query 'Subnets[].SubnetId' --output text | tr '\t' ',')
TAG=$(git rev-parse --short HEAD)

deploy() {
  aws cloudformation deploy --stack-name "$STACK" --template-file template.yaml \
    --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset \
    --parameter-overrides Environment="$ENVIRONMENT" VpcId="$VPC" SubnetIds="$SUBNETS" ImageTag="$1"
}
out() { aws cloudformation describe-stacks --stack-name "$STACK" --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }

echo ">> 1/3 infrastructure (0 tasks until the image exists)"
if [ "$(aws cloudformation describe-stacks --stack-name "$STACK" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || true)" = "" ]; then
  deploy ""
fi

REPO=$(out RepositoryUri)
echo ">> 2/3 image $REPO:$TAG"
if ! aws ecr describe-images --repository-name "${REPO#*/}" --image-ids imageTag="$TAG" >/dev/null 2>&1; then
  aws ecr get-login-password | docker login --username AWS --password-stdin "${REPO%%/*}"
  docker build --platform linux/amd64 -t "$REPO:$TAG" app/
  docker push "$REPO:$TAG"
fi

echo ">> 3/3 service with image $TAG"
deploy "$TAG"
echo "Service URL: $(out ServiceUrl)"
