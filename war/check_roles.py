import boto3
from datetime import datetime


def get_boto_client(service_name, region_name="us-east-1"):
    return boto3.client(service_name, region_name=region_name)


def check_roles(iam_client):
    try:
        paginator = iam_client.get_paginator('list_roles')
        total_roles = 0
        assumable_roles = 0
        roles_with_boundary = 0
        inactive_roles = 0
        
        for page in paginator.paginate():
            for role in page['Roles']:
                total_roles += 1
                role_name = role['RoleName']
                
                assume_role_policy = role.get('AssumeRolePolicyDocument', {})
                can_be_assumed = bool(assume_role_policy.get('Statement'))
                
                has_boundary = 'PermissionsBoundary' in role
                
                last_used = role.get('RoleLastUsed', {}).get('LastUsedDate')
                days_inactive = None
                if last_used:
                    days_inactive = (datetime.now(last_used.tzinfo) - last_used).days
                
                if can_be_assumed:
                    assumable_roles += 1
                if has_boundary:
                    roles_with_boundary += 1
                if days_inactive and days_inactive > 90:
                    inactive_roles += 1
                    print(f"\033[31mRole: {role_name} | Assumable: {can_be_assumed} | Boundary: {has_boundary} | Inactive: {days_inactive} days\033[0m")
                else:
                    print(f"Role: {role_name} | Assumable: {can_be_assumed} | Boundary: {has_boundary} | Inactive: {days_inactive} days")
        
        print(f"\n\nTotal roles: {total_roles}")
        print(f"Assumable roles: {assumable_roles}")
        print(f"Roles with permission boundaries: {roles_with_boundary}")
        print(f"Roles inactive > 90 days: {inactive_roles}")
        
    except Exception as e:
        print(f"Error fetching roles: {e}")


if __name__ == "__main__":
    iam_client = get_boto_client('iam')
    check_roles(iam_client)
