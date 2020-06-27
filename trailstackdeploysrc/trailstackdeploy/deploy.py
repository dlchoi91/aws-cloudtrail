import boto3
import re
import time
import sys

def _put_cf_yaml(cftemplatebucket, s3_resource, cfyaml='cloudformation.yaml'):
    """
    Puts the cf yaml file into specified s3 bucket using boto3

    :param cftemplatebucket: The bucket name where the cf file will be loaded as a string
    :param s3_resource: The boto3 resource for s3 as an object
    :param cfyaml: The filename of the cloudformation yaml file to be loaded  as a string
    :return: "Uploaded cf template to bucket"

    >>> _put_cf_yaml(cftemplatebucket='my-cloudformation-bucket', s3_resource=boto3.resource('s3'), cfyaml='cloudformation.yaml')
    Uploaded cf template to bucket

    >>> _put_cf_yaml(cftemplatebucket='restricted-bucket-name, s3_resource=boto3.resource('s3'), cfyaml='cloudformation.yaml')
    botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the PutObject operation: Access Denied
    """

    try:
        with open(cfyaml, 'r') as f:
            response = s3_resource.Object(cftemplatebucket, cfyaml).put(Body= f.read())
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "CF Template S3 Put Unsuccessful - HTTP Status Code was not 200"
            sys.stdout.write("Uploaded cf template to bucket\n")
            sys.stdout.flush()
    except:
        raise

def _validate_cf_template(cf_client, cfyaml):
    """
    Validate your cf yaml file and print results to console

    :param cf_client: The boto3 client for cloudformation as an object
    :param cfyaml: The filename of the cloudformation yaml file to be loaded  as a string
    :return: "Template is valid."

    >>> _validate_cf_template(cf_client=boto3.client('cloudformation'), cfyaml='cf_valid.yaml')
    Template is valid

    >>> _validate_cf_template(cf_client=boto3.client('cloudformation'), cfyaml='cf_invalid.yaml')
    botocore.exceptions.ClientError: An error occurred (ValidationError) when calling the ValidateTemplate operation: Template format error: YAML not well-formed. (line 286, column 4)
    """
    try:
        with open(cfyaml, 'r') as f:
            response = cf_client.validate_template(TemplateBody=f.read())
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "HTTP status code not 200 for validation of template. Stopping."
        sys.stdout.write("Template is valid. \n")
        sys.stdout.flush()
    except:
        raise

def _stack_exist_checker(StackName, cf_client):
    """
    Checks if the stack name exists in your default aws region and returns a boolean and prints if the stack exists or not

    :param StackName: The name of the stack you want to create or update as a string
    :param cf_client: The boto3 client for cloudformation as an object
    :return: a boolean (True/False)

    >>>_stack_exist_checker(StackName='valid-stack', cf_client=boto3.client('cloudformation'))
    True
    Stack exists, will update stack
    >>>_stack_exist_checker(StackName='new-stack', cf_client=boto3.client('cloudformation'))
    False
    Stack does not exists, will create stack
    """
    try:
        cf_client.describe_stacks(StackName=StackName)
        exists = True
        sys.stdout.write("Stack exists, will update stack\n")
        sys.stdout.flush()
        return exists

    except:
        exists = False
        sys.stdout.write("Stack does not exists, will create stack\n")
        sys.stdout.flush()
        return exists

def _set_cf_create_kwargs(StackName, cftemplatebucket, cfyaml, LogBucketName, GluePolicyARN, CTName):
    """
    Creates the arguments dictionary to pass to create or update stack function

    :param StackName: The name of the stack you want to create or update as a string
    :param cftemplatebucket: The bucket name where the cf file will be loaded as a string
    :param cfyaml: The filename of the cloudformation yaml file to be loaded  as a string
    :param LogBucketName: The bucket name that will be created to house CloudTrail logs as a string
    :param GluePolicyARN: The AWS Resource Name (ARN) of the Glue Policy that crawlers and job will assume as a string
    :param CTName: The name of the Trail that will be created in the stack as a string
    :return: a dictionary of values


    """
    args = {'StackName': StackName,
            'TemplateURL': 'https://' + cftemplatebucket + '.s3.amazonaws.com/' + cfyaml,
            'Parameters': [
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
            'Capabilities': ['CAPABILITY_NAMED_IAM']
    }
    return args

def _load_script_after_stack_create(StackName, s3_resource, cf_client, LogBucketName):
    """
    Prints the status of the stack update/creationand loads the Glue Script after stack update/completion

    :param StackName: The name of the stack you want to create or update as a string
    :param s3_resource: The boto3 resource for s3 as an object
    :param cf_client: The boto3 client for cloudformation as an object
    :param LogBucketName: The bucket name that will be created to house CloudTrail logs as a string
    :return:
    """
    try:
        status = cf_client.describe_stacks(StackName=StackName)['Stacks'][0]['StackStatus']
        while (bool(re.match('.*_IN_PROGRESS$', status)) == True):
            status = cf_client.describe_stacks(StackName=StackName)['Stacks'][0]['StackStatus']
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

def create_update_stack(cftemplatebucket = 'cf-templates-17p4szdics9ar-us-east-1', StackName = 'dc-cf-test-stack',
           LogBucketName = 'dc-cf-test-stack-bucket',
           CTName = 'dc-kick-ass-trail-name',
           GluePolicyARN = 'arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'):
    """
    Function called by CLI command to create or update the stack in your AWS environment

    :param cftemplatebucket: The bucket name where the cf file will be loaded as a string
    :param StackName: The name of the stack you want to create or update as a string
    :param LogBucketName: The bucket name that will be created to house CloudTrail logs as a string
    :param CTName: The name of the Trail that will be created in the stack as a string
    :param GluePolicyARN: The AWS Resource Name (ARN) of the Glue Policy that crawlers and job will assume as a string
    :return:
    """

    try:
        cf = boto3.client('cloudformation')
        cfyaml = 'cloudformation.yaml'  # note this is the yaml in repo
        _validate_cf_template(cf_client=cf, cfyaml=cfyaml)
    except:
        raise

    try:
        s3_resource = boto3.resource('s3')
        _put_cf_yaml(cftemplatebucket=cftemplatebucket, s3_resource=s3_resource)
    except AssertionError as error:
        raise error

    try:
        exists = _stack_exist_checker(StackName=StackName, cf_client=cf)
    except:
        raise

    try:
        cf_args = _set_cf_create_kwargs(StackName=StackName, cftemplatebucket=cftemplatebucket, cfyaml=cfyaml,
                                     LogBucketName=LogBucketName, GluePolicyARN=GluePolicyARN, CTName=CTName)
    except:
        raise

    if exists == False:
        try:
            response = cf.create_stack(**cf_args)
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "HTTP status code not 200 for creating stack"
        except AssertionError as error:
            raise error
    if exists == True:
        try:
            response = cf.update_stack(**cf_args)
            assert response.get("ResponseMetadata").get(
                "HTTPStatusCode") == 200, "HTTP status code not 200 for updating stack"
        except AssertionError as error:
            raise error

    try:
        _load_script_after_stack_create(StackName=StackName, s3_resource=s3_resource, cf_client=cf, LogBucketName=LogBucketName)
    except AssertionError as error:
        raise error
    return
