# SIS 3: Infrastructure as Code (Cloud Application Development, Week 11)

One CloudFormation template (`template.yaml`) describes everything from practices 5 and 6:

- Messaging: SNS topic -> SQS queue (+ DLQ, maxReceiveCount 5) -> Lambda consumer -> DynamoDB
- Idempotency: the consumer writes with `attribute_not_exists(orderId)`; the dedup key is `orderId`
- Container: ECR (immutable tags, scan on push, lifecycle policy) -> ECS Fargate service behind an ALB
- Two separate roles for the container (execution role and task role), logs in CloudWatch with retention
- Parameters: `Environment` (dev/staging/prod), `VpcId`, `SubnetIds`, `ImageTag`. No secrets in the template

## Requirements
AWS CLI configured (`aws configure`, with a region), Docker running, git repo with at least one commit.

## Deploy (one command)
```
./deploy.sh <stack-name> [dev|staging|prod]
```
Second copy for the reproducibility test: the same command with a different stack name.

## Try it
```
curl <ServiceUrl>/health
curl -X POST <ServiceUrl>/orders -d '{"orderId":"order-001","amount":1500}'
```
Send the same order twice: the table still has one item (the log says `duplicate_skipped`).
`{"orderId":"bad","amount":-1}` fails 5 times and lands in the DLQ.

## Delete
```
./delete.sh <stack-name>
```
Nothing is left behind: no Retain resources, ECR is emptied on delete.
