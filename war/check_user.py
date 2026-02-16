import boto3
from datetime import datetime 


_usr_groups: dict = {}


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
                print(f"Checking role: {role_name}")
                assume_role_policy = role.get('AssumeRolePolicyDocument', {})
                can_be_assumed = bool(assume_role_policy.get('Statement'))
                
                has_boundary = 'PermissionsBoundary' in role    
                _res = iam_client.get_role(RoleName=role_name).get('Role').get('RoleLastUsed')
                      
                _last_used = _res.get('LastUsedDate', None)
                if _last_used:
                    _days_inactive = (datetime.now(_last_used.tzinfo) - _last_used).days
                else:
                    _days_inactive = None
                
                if can_be_assumed:
                    assumable_roles += 1
                if has_boundary:
                    roles_with_boundary += 1
                if _days_inactive and _days_inactive > 90:
                    inactive_roles += 1
                #     print(f"\033[31mRole: {role_name}  Assumable: {can_be_assumed} | Permission Boundary: {has_boundary} | Inactive: {_days_inactive} days\033[0m")
                # else:
                #     print(f"Role: {role_name} | Assumable: {can_be_assumed} | Boundary: {has_boundary} | Inactive: Not available")
        
        print(f"\nTotal roles: {total_roles}")
        print(f"Assumable roles: {assumable_roles}")
        print(f"Roles with permission boundaries: {roles_with_boundary}")
        print(f"Roles inactive > 90 days: {inactive_roles}")
    except Exception as e:
        print(f"Error fetching roles: {e}")

def check_password_policy(iam_client):
    try:
        response = iam_client.get_account_password_policy()
        password_policy = response['PasswordPolicy']
        print(password_policy)
        print("Password policy is set:")
    except iam_client.exceptions.NoSuchEntityException:
        print("\033[31m" + "No password policy is set for this account." + "\033[0m")


def get_user_last_login(iam_client, username):
    try:     
        access_keys = iam_client.list_access_keys(UserName=username)['AccessKeyMetadata']
        access_key_last_used = None
        for key in access_keys:
            key_last_used = iam_client.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])
            if 'LastUsedDate' in key_last_used.get('AccessKeyLastUsed', {}):
                last_used = key_last_used['AccessKeyLastUsed']['LastUsedDate']
                if not access_key_last_used or last_used > access_key_last_used:
                    access_key_last_used = last_used
        
        if access_key_last_used:
            days_ago = (datetime.now(access_key_last_used.tzinfo) - access_key_last_used).days
            return days_ago
        return None
    except Exception as e:
        print(f"Error fetching last login for {username}: {e}")
        return None


def check_admin_permissions(iam_client, username):
    try:
        attached_policies = iam_client.list_attached_user_policies(UserName=username)['AttachedPolicies']
        for policy in attached_policies:
            if 'AdministratorAccess' in policy['PolicyName']:
                return True
        
        groups = iam_client.list_groups_for_user(UserName=username)['Groups']
        _usr_groups[username] = [group['GroupName'] for group in groups]
        for group in groups:
            group_policies = iam_client.list_attached_group_policies(GroupName=group['GroupName'])['AttachedPolicies']
            for policy in group_policies:
                if 'AdministratorAccess' in policy['PolicyName']:
                    return True
        
        return False
    except Exception as e:
        print(f"Error checking admin permissions for {username}: {e}")
        return False


def get_users(iam_client):
    try:
        paginator = iam_client.get_paginator('list_users')
        count = 0
        _admin_user_count = 0
        _inactive_users = 0
        for page in paginator.paginate():
            count+= len(page['Users'])
            for user in page['Users']:
                _user_name = user['UserName']
                print(f"Checking user: {_user_name}")
                days_ago = get_user_last_login(iam_client, _user_name)
                if check_admin_permissions(iam_client, _user_name):
                    _admin_user_count+= 1
                    #print("\033[31m" + f"User {_user_name} has admin permissions!" + "\033[0m", end=" ")
                if days_ago is not None and days_ago > 90:
                    _inactive_users += 1
                
                
        print(f"\nTotal number of users: {count}")
        print(f"Number of users with last login > 90 days: {_inactive_users}")
        print(f"Number of users with Administrator privilege: {_admin_user_count}")
        global _usr_groups
        for user, groups in _usr_groups:
            print(f"User: {user} | Groups: {groups}")
    except Exception as e:
        print(f"Error fetching users: {e}")


if __name__ == "__main__":
    iam_client = get_boto_client('iam')
    print("Calling users ...")
    get_users(iam_client)
    check_password_policy(iam_client)
    check_roles(iam_client)
