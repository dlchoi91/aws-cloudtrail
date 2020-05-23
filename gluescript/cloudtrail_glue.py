import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3
import time

## @params: [JOB_NAME] [CF_STACK]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'cfstackname', 'region_name'])

#get the bucket name from cloudformation outputs
cf = boto3.client('cloudformation', region_name = args['region_name'])
for i in cf.describe_stacks(StackName = args['cfstackname'])['Stacks'][0]['Outputs']:
    if i['OutputKey'] == 'TrailBucket':
        bucket = i['OutputValue']
    else: pass
path = 's3://' + bucket + '/parquettrails/'


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "cloudtrail", table_name = "flatfiles", transformation_ctx = "datasource0")
resolvechoice1 = ResolveChoice.apply(frame = datasource0, choice = "make_struct", transformation_ctx = "resolvechoice1")
relationalized1 = resolvechoice1.relationalize("trail", args["TempDir"]).select("trail")
datasink = glueContext.write_dynamic_frame.from_options(frame = relationalized1, connection_type = "s3", connection_options = {"path": path}, format = "parquet", transformation_ctx = "datasink4")
#using glue contexxts
#datasink = glueContext.write_dynamic_frame.from_catalog(frame = relationalized1, database = "cloudtrail", table_name = "parquettrails", transformation_ctx = "datasink4")
job.commit()


