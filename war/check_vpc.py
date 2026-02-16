import boto3


def get_boto_client(service_name, region_name="us-east-1"):
    return boto3.client(service_name, region_name=region_name)


def check_vpcs_and_subnets(ec2_client):
    try:
        vpcs = ec2_client.describe_vpcs()['Vpcs']
        
        for vpc in vpcs:
            vpc_id = vpc['VpcId']
            vpc_name = next((tag['Value'] for tag in vpc.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            
            subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
            
            has_public = any(subnet.get('MapPublicIpOnLaunch', False) for subnet in subnets)
            has_private = any(not subnet.get('MapPublicIpOnLaunch', False) for subnet in subnets)
            
            if not (has_public and has_private):
                print(f"\033[31mVPC: {vpc_name} | ID: {vpc_id} | Missing: {'Public' if not has_public else 'Private'} subnet\033[0m")
            else:
                print(f"VPC: {vpc_name} | ID: {vpc_id} | Has both public and private subnets")
    
    except Exception as e:
        print(f"Error checking VPCs: {e}")


def list_vpc_endpoints(ec2_client):
    try:
        endpoints = ec2_client.describe_vpc_endpoints()['VpcEndpoints']
        
        vpc_endpoints = {}
        for endpoint in endpoints:
            vpc_id = endpoint['VpcId']
            endpoint_type = endpoint['VpcEndpointType']
            service_name = endpoint['ServiceName']
            
            if vpc_id not in vpc_endpoints:
                vpc_endpoints[vpc_id] = {'Gateway': [], 'Interface': []}
            
            vpc_endpoints[vpc_id][endpoint_type].append(service_name)
        if len(vpc_endpoints) > 0:
            for vpc_id, endpoints_data in vpc_endpoints.items():
                print(f"\nVPC: {vpc_id}")
                print(f"  Gateway Endpoints: {len(endpoints_data['Gateway'])} - {endpoints_data['Gateway']}")
                print(f"  Interface Endpoints: {len(endpoints_data['Interface'])} - {endpoints_data['Interface']}")
        else:
             print(f"\033[31m No VPC endpoints found... \033[0m")
    
    except Exception as e:
        print(f"Error listing endpoints: {e}")


def check_security_groups(ec2_client):
    try:
        security_groups = ec2_client.describe_security_groups()['SecurityGroups']
        
        for sg in security_groups:
            sg_id = sg['GroupId']
            sg_name = sg['GroupName']
            vpc_id = sg.get('VpcId', 'N/A')
            
            exposed_ports = []
            for rule in sg.get('IpPermissions', []):
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        from_port = rule.get('FromPort', 'All')
                        to_port = rule.get('ToPort', 'All')
                        protocol = rule.get('IpProtocol', 'All')
                        exposed_ports.append(f"{protocol}:{from_port}-{to_port}")
            
            if exposed_ports:
                print(f"\033[31mSG: {sg_name} | ID: {sg_id} | VPC: {vpc_id} | Exposed Ports: {', '.join(exposed_ports)}\033[0m")
    
    except Exception as e:
        print(f"Error checking security groups: {e}")


if __name__ == "__main__":
    ec2_client = get_boto_client('ec2')
    
    print("Checking VPCs and Subnets...")
    check_vpcs_and_subnets(ec2_client)
    
    print("\n\nListing VPC Endpoints...")
    list_vpc_endpoints(ec2_client)
    
    print("\n\nChecking Security Groups for 0.0.0.0/0 access...")
    check_security_groups(ec2_client)
