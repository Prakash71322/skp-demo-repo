import check_encryption
import check_network
import check_user
import check_vulnerability
import boto3
import utils


def get_b_clients():
  s3_client = get_boto_client('s3')
  ec2_client = get_boto_client('ec2')
  efs_client = get_boto_client('efs')
  rds_client = get_boto_client('rds')
  sm_client = get_boto_client('secretsmanager')
  dynamodb_client = get_boto_client('dynamodb')
  redshift_client = get_boto_client('redshift')
  elasticache_client = get_boto_client('elasticache')
  sagemaker_client = get_boto_client('sagemaker')
  lambda_client = get_boto_client('lambda')
  emr_client = get_boto_client('emr')
  _b_clients = check_encryption.BotoClients(s3_client, ec2_client, efs_client, rds_client, sm_client, dynamodb_client, redshift_client, elasticache_client, sagemaker_client, lambda_client, emr_client)
  return _b_clients
  

def close_b_clients(b_c: check_encryption.BotoClients):
  b_c.s3_client.close()
  b_c.ec2_client.close()
  b_c.efs_client.close()
  b_c.rds_client.close()
  b_c.sm_client.close()
  b_c.dynamodb_client.close()
  b_c.redshift_client.close()
  b_c.elasticache_client.close()
  b_c.sagemaker_client.close()
  b_c.lambda_client.close()
  b_c.emr_client.close()


def get_boto_client(service_name, region_name="us-east-1"):
    return boto3.client(service_name, region_name=region_name)


def one():
  iam_client = get_boto_client('iam')
  _qsec: dict = {}
  _qsec["Pillar"] = "Security"
  _qsec["Question"] = "How do you manage identities and permissions for people and machines?" 
  _qsec["Best Practice"] = "Use strong sign-in mechanism"
  _qsec["Severity"] = "High"
  _qsec["Validation"] = "Enforce Secure password policy"
  _qsec["Status"] = utils.get_colored_message(check_user.check_password_policy(iam_client))   
  print()
  utils.print_table(_qsec)
  print("\n")
  _qsec["Best Practice"] = "Store and use secrets securely"
  _qsec["Validation"] = "Enforce trusted entities for roles"
  _res = check_user.check_roles(iam_client)
  _qsec["Status"] = utils.get_colored_message(_res["status"])
  _qsec['Data'] = _res["roles"]
  utils.print_table(_qsec)
  print("\n")
  _qsec["Best Practice"] = "Credential rotation policy"
  _qsec["Validation"] = "Identify credentials inactive for more than 90 days"
  _res = check_user.get_users(iam_client)
  _qsec["Status"] = utils.get_colored_message(_res["status"])
  if _res["users"] :
    _qsec["Data"] = _res["users"]
  utils.print_table(_qsec)
  print("\n")
  _qsec["Best Practice"] = "Employ user groups and attributes"
  _qsec["Severity"] = "Low"
  _qsec["Validation"] = "Identify group(s) availability"
  _qsec["Status"] = utils.get_colored_message(("Not Enforced", "Red"))
  if _res["groups"] :
    _qsec["Data"] = _res["groups"]
  utils.print_table(_qsec)
  print("\n")
  _qsec["Question"] = "How do you protect your network resources?" 
  _qsec["Best Practice"] = "Create network layers"
  _qsec["Severity"] = "High"
  _qsec["Validation"] = "Identify public and private subnets availability"
  ec2_client = get_boto_client('ec2')
  del _qsec["Data"]
  _qsec["Status"] = utils.get_colored_message(check_network.check_vpcs_and_subnets(ec2_client))
  utils.print_table(_qsec)
  print("\n")
  _qsec["Best Practice"] = "Control traffic within your network layers"
  _qsec["Validation"] = "Availability Routes for all the subnets"
  utils.print_table(_qsec)
  print("\n")
  _qsec["Best Practice"] = "Implement inspection-based protection"
  _qsec["Severity"] = "Low"
  _qsec["Validation"] = "Availability of WAF or Transit Gateway"
  waf2_client = get_boto_client('wafv2')
  _qsec["Status"] = utils.get_colored_message(check_network.check_waf_transit_gateway(waf2_client, ec2_client))
  utils.print_table(_qsec)
  print("\n")
  _qsec["Best Practice"] = "Automate network protection"
  _qsec["Severity"] = "Medium"
  _qsec["Validation"] = "Automation Pipeline availability"
  _qsec["Status"] = utils.get_colored_message(("Not Implemented", "Red"))
  utils.print_table(_qsec)
  print("\n")


def two():
  _qsec: dict = {}
  config_client = get_boto_client('config')
  inspector2_client = get_boto_client('inspector2')
  securityhub_client = get_boto_client('securityhub')
  _qsec["Pillar"] = "Security"
  _qsec["Question"] = "How do you protect compute resources?" 
  _qsec["Best Practice"] = "Perform vulnerability management"
  _qsec["Severity"] = "High"
  _qsec["Validation"] = "Enforcing AWS Inspector, Config and Security Hub"
  if check_vulnerability.check_vulnerability(inspector2_client, config_client, securityhub_client):
    _qsec["Status"] = utils.get_colored_message(("Enforced", "Green"))
  else:
    _qsec["Status"] = utils.get_colored_message(("Not Enforced", "Red"))
  print()
  utils.print_table(_qsec)
  print("\n")
  kms_client = get_boto_client('kms')
  _qsec: dict = {}
  _qsec["Pillar"] = "Security"
  _qsec["Question"] = "How do you protect data at rest?"
  _qsec["Best Practice"] = "Implement secure key management"
  _qsec["Validation"] = "Enforce KMS policy"
  _qsec["Severity"] = "High"
  kms_client = get_boto_client("kms")
  _qsec["Status"] = utils.get_colored_message(check_encryption.check_kms_policy(kms_client))  
  print()
  utils.print_table(_qsec)
  print("\n")
  _qsec["Question"] = "How do you protect data at rest?"
  _qsec["Best Practice"] = "Enforce encryption at rest"
  _qsec["Validation"] = "Enforce Default KMS Keys to applicable services"
  _qsec["Severity"] = "High"
  b_client = get_b_clients()
  _result_enc = check_encryption.main(b_client)
  _false_count = 0
  _t_count = 0
  for _key, _value in _result_enc.items():
    if _key == "data":
      continue
    _t_count += 1
    if not _value:
      _false_count += 1
  close_b_clients(b_client)
  b_client = None
  if _false_count > 0 and _false_count < _t_count:
    _qsec["Status"] = utils.get_colored_message(("Encryption partially applied", "Red"))
  else:
    _qsec["Status"] = utils.get_colored_message(("Encryption Enforced", "Green"))
  print()
  utils.print_table(_qsec) 
  print("\n")
  
  
if __name__ == "__main__" :
  #one()
  two()