import boto3
from collections import defaultdict
from botocore.exceptions import ClientError


def get_boto_client(service_name, region_name="us-east-1"):
    return boto3.client(service_name, region_name=region_name)


def check_cost_tags():
    tagging_client = get_boto_client('resourcegroupstaggingapi')
    service_counts = defaultdict(lambda: {'tagged': 0, 'total': 0})
    total_tagged_count = 0
    total_res = 0
    try:
        paginator = tagging_client.get_paginator('get_resources')
        for page in paginator.paginate():
            for resource in page['ResourceTagMappingList']:
                arn = resource['ResourceARN']
                service_type = arn.split(':')[2]
                tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                total_res+= 1
                service_counts[service_type]['total'] += 1
                if 'Project' in tags or 'Cost Center' in tags:
                    service_counts[service_type]['tagged'] += 1
                    total_tagged_count += 1
        
        print("--- Cost Tag Compliance by Service ---")
        for service in sorted(service_counts.keys()):
            counts = service_counts[service]
            print(f"{service}: {counts['tagged']}/{counts['total']} resources tagged")
        print (f"Total tagged resources: {total_tagged_count}")
        print (f"Total resources: {total_res}")
        
    except ClientError as e:
        print(f"\033[31mError checking tags: {e}\033[0m")


if __name__ == "__main__":
    check_cost_tags()
