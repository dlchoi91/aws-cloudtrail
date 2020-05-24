import boto3
import re
import time
import sys

def _put_cf_yaml(cftemplatebucket, s3_resource, cfyaml='cloudformation.yaml'):
    with open(cfyaml, 'r') as f:
        response = s3_resource.Object(cftemplatebucket, cfyaml).put(Body= f.read())
        assert response.get("ResponseMetadata").get(
            "HTTPStatusCode") == 200, "CF Template S3 Put Unsuccessful - HTTP Status Code was not 200"

def create_update_stack(cftemplatebucket = 'cf-templates-17p4szdics9ar-us-east-1', StackName = 'dc-cf-test-stack',
           LogBucketName = 'dc-cf-test-stack-bucket',
           CTName = 'dc-kick-ass-trail-name',
           GluePolicyARN = 'arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'):

    try:
        cf = boto3.client('cloudformation')
        cfyaml = 'cloudformation.yaml'  # note this is the yaml in repo
        with open(cfyaml, 'r') as f:
            response = cf.validate_template(TemplateBody=f.read())
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "HTTP status code not 200 for validation of template. Stopping."
        sys.stdout.write("Template is valid. \n")
        sys.stdout.flush()
    except:
        raise

    try:
        s3_resource = boto3.resource('s3')
        _put_cf_yaml(cftemplatebucket = cftemplatebucket, s3_resource=s3_resource)
        sys.stdout.write("Uploaded cf template to bucket\n")
        sys.stdout.flush()
    except AssertionError as error:
        raise error

    try:
        cf.describe_stacks( StackName=StackName)
        exists = True
        sys.stdout.write("Stack exists, will update stack\n")
        sys.stdout.flush()

    except:
        exists = False
        sys.stdout.write("Stack does not exists, will create stack\n")
        sys.stdout.flush()
        pass

    if exists == False:
        try:
            response = cf.create_stack(
                StackName = StackName,
                TemplateURL = 'https://' + cftemplatebucket + '.s3.amazonaws.com/' + cfyaml,
                Parameters=[
                    {
                        'ParameterKey': 'LogBucketName',
                        'ParameterValue': LogBucketName
                    },
                    {
                        'ParameterKey': 'GlueServicePolicyArn',
                        'ParameterValue': GluePolicyARN
                    },
                    {
                        'ParameterKey': 'CTName',
                        'ParameterValue': CTName
                    }
                ],
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ],
            )
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "HTTP status code not 200 for creating stack"
        except AssertionError as error:
            raise error
    if exists == True:
        try:
            response = cf.update_stack(
                StackName = StackName,
                TemplateURL = 'https://' + cftemplatebucket + '.s3.amazonaws.com/' + cfyaml,
                Parameters=[
                    {
                        'ParameterKey': 'LogBucketName',
                        'ParameterValue': LogBucketName
                    },
                    {
                        'ParameterKey': 'GlueServicePolicyArn',
                        'ParameterValue': GluePolicyARN
                    },
                    {
                        'ParameterKey': 'CTName',
                        'ParameterValue': CTName
                    }
                ],
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ],
            )
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "HTTP status code not 200 for updating stack"
        except AssertionError as error:
            raise error

    try:
        status = cf.describe_stacks(StackName=StackName)['Stacks'][0]['StackStatus']
        while (bool(re.match('.*_IN_PROGRESS$', status)) == True):
            status = cf.describe_stacks(StackName=StackName)['Stacks'][0]['StackStatus']
            sys.stdout.write("Stack updating/creating status: " + status + "\n")
            sys.stdout.flush()
            time.sleep(5)
    except AssertionError as error:
        raise error
    try:
        if status == 'CREATE_COMPLETE' or status == 'UPDATE_COMPLETE':
            gluescript = 'gluescript/cloudtrail_glue.py'
            with open(gluescript, 'r') as f:
                response = s3_resource.Object(LogBucketName, gluescript).put(Body= f.read())
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "Glue Script S3 Put Unsuccessful - HTTP Status Code was not 200"
            sys.stdout.write("Uploaded the glue script for job\n")
            sys.stdout.flush()
        else:
            sys.stdout.write("create or update did not complete, did not update glue script\n")
            sys.stdout.flush()
    except AssertionError as error:
        raise error
    return
