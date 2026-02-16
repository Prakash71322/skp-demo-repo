import boto3
from collections import defaultdict


def get_boto_client(service_name, region_name="us-east-1"):
    return boto3.client(service_name, region_name=region_name)


def get_enabled_regions(ec2_client):
    try:
        regions = ec2_client.describe_regions()['Regions']
        enabled_regions = [region['RegionName'] for region in regions if region['State'] == 'available']
        return enabled_regions
    except Exception as e:
        print(f"Error fetching regions: {e}")
        return []

def get_resources_from_explorer(resource_explorer_client):
    try:
        service_counts = defaultdict(int)
        region_counts = defaultdict(int)
        service_region_counts = defaultdict(lambda: defaultdict(int))
        next_token = None
        
        while True:
            if next_token:
                response = resource_explorer_client.search(QueryString="*", MaxResults=1000, NextToken=next_token)
            else:
                response = resource_explorer_client.search(QueryString="*", MaxResults=1000)
            
            for resource in response.get('Resources', []):
                resource_type = resource.get('ResourceType', 'Unknown')
                service = resource_type.split(':')[0] if ':' in resource_type else resource_type
                region = resource.get('Region', 'global')
                
                service_counts[service] += 1
                region_counts[region] += 1
                service_region_counts[service][region] += 1
            
            next_token = response.get('NextToken')
            if not next_token:
                break
        
        print("Resource counts by service:\n")
        for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{service}: {count}")
        
        print("\n\nResource counts by region:\n")
        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{region}: {count}")
        
        print("\n\nResource counts by service and region:\n")
        for service in sorted(service_region_counts.keys()):
            print(f"\n{service}:")
            for region, count in sorted(service_region_counts[service].items(), key=lambda x: x[1], reverse=True):
                print(f"  {region}: {count}")
        
        print(f"\n\nTotal resources: {sum(service_counts.values())}")
        print(f"Total services: {len(service_counts)}")
        print(f"Total regions: {len(region_counts)}")
        
    except Exception as e:
        print(f"Error fetching resources: {e}")


if __name__ == "__main__":
    resource_explorer_client = get_boto_client('resource-explorer-2')
    get_resources_from_explorer(resource_explorer_client)
