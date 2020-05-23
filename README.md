# aws-security

The following repository is a sample workflow for an ETL for CloudTrail logs that can be queried using either AWS Athena or can be further copied into redshift. The json logs will be formatted by AWS Lambda and Glue Crawlers will update the data catalog so that a Glue Job can output into a columnar parquet file. There are currently two cloudformation templates (yaml).

The IAM cloudformation template creates the IAM resources that all services (Glue, Lambda, CloudTrail) will use. The CloudTrail cloudformation template creates the other AWS resources and will leverage the IAM roles for the rest of the workflow. Two templates were initially created so that I can practice working with outputs/exports and parameters in CloudFormation but it makes it difficult to deploy all at once and to delete stacks. I will refactor the templates so that they can be easily deployed and deleted as necessary (See backlog below!).


## Workflow Image
![](/images/workflow.png)



