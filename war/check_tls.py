import boto3
from botocore.exceptions import ClientError


def get_boto_client(service_name, region_name="us-east-1"):
    return boto3.client(service_name, region_name=region_name)

def check_tls_policies():
    # List all load balancers
    elbv2_client = get_boto_client('elbv2')
    lbs = elbv2_client.describe_load_balancers()
    for lb in lbs['LoadBalancers']:
        lb_arn = lb['LoadBalancerArn']
        lb_name = lb['LoadBalancerName']
        
        # Describe listeners for each load balancer
        listeners = elbv2_client.describe_listeners(LoadBalancerArn=lb_arn)
        for listener in listeners['Listeners']:
            if 'SslPolicy' in listener:
                policy = listener['SslPolicy']
                # Check for TLS 1.3 or 1.2 in the policy name
                if 'TLS13' in policy or 'TLS12' in policy:
                    print(f"LB: {lb_name} - Listener: {listener['Port']} uses TLS 1.3 policy")
                else:
                    print("\033[31m" + f"LB: {lb_name} - Listener: {listener['Port']} uses Policy: {policy}" +  "\033[0m")


def check_inspector_enabled():
    inspector2_client = get_boto_client('inspector2')
    try:
        response = inspector2_client.batch_get_account_status()
        for account in response['accounts']:
            enabled_services = []
            non_enabled_services = []
            for service, state in account['resourceState'].items():
                if state['status'] == 'ENABLED':
                    enabled_services.append(service.upper())
                else:
                    non_enabled_services.append(service.upper())
            if enabled_services:
                print(f"  Enabled services: {', '.join(enabled_services)}")
            else:
              if len(non_enabled_services) > 0:
                  print(f"  Disabled services: {', '.join(non_enabled_services)}")
              else:
                print("\033[31m  No services enabled\033[0m")
    except ClientError as e:
        print(f"\033[31mError checking Inspector: {e}\033[0m")


if __name__ == "__main__":
  check_tls_policies()
  print("\n--- AWS Inspector Status ---")
  check_inspector_enabled()