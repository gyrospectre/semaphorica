## Semaphorica in Code, in AWS

In this directory is a sample CloudFormation template that will deploy Semaphorica to AWS, to run once a day via a serverless function. This is the recommended deployment method for any serious use cases.

To deploy, install [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) and the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), then:

0. Add AWS credentials to your shell, with enough permissions to make the required changes.

1. Create the referenced `semaphorica/SplunkHEC` credentials in Secrets Manager. This is a sample, if you're not using Splunk feel free to skip (and remove from the template!), or add other secrets as required.
```
aws secretsmanager create-secret \
--name semaphorica/SplunkHEC \
--description "Spunk HEC Token for Ingestion of Semaphorica Data" \
--secret-string 12345678-abcd-1234-1234-123456789abc
```

2. Next, create an S3 bucket with sane permissions, for deployment and log output testing.

```
aws s3 mb s3://semaphorica-bucket --region ap-southeast-2
aws s3api put-public-access-block \
--bucket semaphorica-bucket \
--public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```
3. Now use SAM to build and deploy the stack.
```
sam build
sam deploy \
--stack-name semaphorica \
--s3-bucket semaphorica-bucket \
--capabilities=CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

4. That's it! Semaphorica will now run every day at 12pm UTC.

If you want to test via an ad-hoc execution, you can run the function directly. Optionally, you can set debug or specify a list of inputs to run.

An example, that just runs the one module (`aws-networks`) in debug mode:

```
aws lambda invoke --function-name semaphorica \
--cli-binary-format raw-in-base64-out \
--payload '{ "debug": true, "modules": ["aws-networks"]}' \
response.json

aws logs tail /aws/lambda/semaphorica
```
The provided config for this route sends the output to S3, so you can check out the results using something like:
```
aws s3 ls s3://semaphorica-bucket
aws s3 cp s3://semaphorica-bucket/awsnets_2023-01-15T00:37:50.txt - | jq .
```
Once you're done, you can cleanup your AWS account with:
```
aws cloudformation delete-stack --stack-name semaphorica
aws logs delete-log-group --log-group-name /aws/lambda/semaphorica
aws s3 rb s3://semaphorica-bucket --force
aws secretsmanager delete-secret \
--secret-id semaphorica/SplunkHEC \
--recovery-window-in-days 7
```