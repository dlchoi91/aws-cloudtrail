from argparse import ArgumentParser


def create_parser():
    parser = ArgumentParser(description="""
    You can use this to help deploy the stack or even update the stack to your AWS environment
    """)

    parser.add_argument("--cfbucket", help="The name of the bucket where the cf yaml file will be uploaded to")
    parser.add_argument("--stackname", help="What do you want to name your cloudformation stack?")
    parser.add_argument("--logbucket", help="What do you want the bucket where logs will be stored called?")
    parser.add_argument("--trailname", help="What do you want your trail to be called?")
    parser.add_argument("--gluepolicyarn", nargs='?', default='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole', help="Update if you want to change the default glue policy arn. defaults to the AWS managed policy.")
    return parser

def main():
    from trailstackdeploy import deploy
    args = create_parser().parse_args()
    deploy.create_update_stack(cftemplatebucket = args.cfbucket,
                               StackName = args.stackname,
                               LogBucketName = args.logbucket,
                               CTName = args.trailname,
                               GluePolicyARN = args.gluepolicyarn)
