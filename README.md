# aws-cloudtrail

The following repository is a sample workflow for an ETL for CloudTrail logs that can be queried using either AWS Athena or can be further copied into redshift. The json logs will be formatted by AWS Lambda and Glue Crawlers will update the data catalog so that a Glue Job can output into a columnar parquet file.

The stack launches all the resources needed for the workflow defined below. The stack will launch with the trail not set to record and must be turned on manually. The glue crawlers and job are not activated as well and need to be scheduled on your own based on your own personal requirements. The event source mapping for the lambda function is enabled by default.


## Workflow Image
![](/images/workflow.png)


## Command Line tool
A command line tool was built to assist in deploying the cloudformation stack. After cloning the repository, you can run the following bash command:
```bash
python setup.py install
```

The command line tool has one function `trailstackdeploy`. Information on the function to deploy can be found by running `trailstackdeploy -h`:

```
$ trailstackdeploy -h
usage: trailstackdeploy [-h] [--cfbucket CFBUCKET] [--stackname STACKNAME]
                        [--logbucket LOGBUCKET] [--trailname TRAILNAME]
                        [--gluepolicyarn [GLUEPOLICYARN]]

You can use this to help deploy the stack or even update the stack to your AWS
environment

optional arguments:
  -h, --help            show this help message and exit
  --cfbucket CFBUCKET   The name of the bucket where the cf yaml file will be
                        uploaded to
  --stackname STACKNAME
                        What do you want to name your cloudformation stack?
  --logbucket LOGBUCKET
                        What do you want the bucket where logs will be stored
                        called?
  --trailname TRAILNAME
                        What do you want your trail to be called?
  --gluepolicyarn [GLUEPOLICYARN]
                        Update if you want to change the default glue policy
                        arn. defaults to the AWS managed policy.
```


In the example below, I used the following command to deploy my stack. I have a bucket for my cloudformation templates `cfbucket cf-templates-17p4szdics9ar-us-east-1`. I selected my own name for the stack and trail created and used the default `arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole` policy ARN by leaving `--gluepolicyarn` blank.
```bash
trailstackdeploy --cfbucket cf-templates-17p4szdics9ar-us-east-1 --stackname cloudtrail-stack --logbucket danielchoi-cloudtrail-logs --trailname danielchoi-trail-name
```
