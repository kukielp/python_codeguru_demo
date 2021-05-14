import boto3
import subprocess

successes = 0

# Dummy AWS Handler to kick off high level processes
def lambda_handler(source_region, destination_region, credentials):

    session = boto3.Session()

    # Load Records into KINESIS
    CLIENT_NAME = 'kinesis'
    kinesis = session.client(CLIENT_NAME, region_name=source_region, aws_access_key_id=credentials,
                             aws_secret_access_key=credentials['SecretAccessKey'],
                             aws_session_token=credentials['SessionToken'])
    process_kinesis(kinesis, "some_file_path.txt")

    # Get SNS Topic ARNs
    CLIENT_NAME = 'sns'
    for region in [source_region, destination_region]:
        sns = session.client(CLIENT_NAME, region_name=region, aws_access_key_id=credentials,
                             aws_secret_access_key=credentials['SecretAccessKey'],
                             aws_session_token=credentials['SessionToken'])
        topic_arns = list_sns(sns)
        print(len(topic_arns))

    # Sync Source DDB to Destination Region
    CLIENT_NAME = 'dynamodb'
    source_ddb = session.client(CLIENT_NAME, region_name=source_region, aws_access_key_id=credentials['AccessKeyId'],
                              aws_secret_access_key=credentials['SecretAccessKey'],
                              aws_session_token=credentials['SessionToken'])

    destination_ddb = session.client(CLIENT_NAME, region_name=destination_region)
    sync_ddb_table(source_ddb, destination_ddb)


# Scan returns paginated results, so only partial data will be copied
def sync_ddb_table(source_ddb, destination_ddb):
    response = source_ddb.scan(
        TableName="table1"
    )
    for item in response['Items']:
        destination_ddb.put_item(
            TableName="table2",
            Item=item
        )

# This code uses a mutable default argument and modifies it to return. This would leak results across calls
def list_sns(sns, topics=[]):
    response = sns.list_topics()
    for topic_arn in response["Topics"]:
        topics.append(topic_arn["TopicArn"])
    return topics


# Infinite loop because a list is modified while being iterated over, Indices are not updated.
def infinite_loop():
    words = ['aws', 'amazon', 'codeguru']
    for w in words:
        if len(w) > 4:
            words.insert(0, w)
    return words
