
_result_dict: dict = {}


class BotoClients:
    def __init__(self, s3_client, ec2_client, efs_client, rds_client, sm_client, 
                 dynamodb_client, redshift_client, elasticache_client, 
                 sagemaker_client, lambda_client, emr_client):
        self.s3_client = s3_client
        self.ec2_client = ec2_client
        self.efs_client = efs_client
        self.rds_client = rds_client
        self.sm_client = sm_client
        self.dynamodb_client = dynamodb_client
        self.redshift_client = redshift_client
        self.elasticache_client = elasticache_client
        self.sagemaker_client = sagemaker_client
        self.lambda_client = lambda_client
        self.emr_client = emr_client



def check_s3_buckets_encryption(s3_client):
    buckets = s3_client.list_buckets()['Buckets']
    _result = False
    _buckets = []
    for bucket in buckets:
        try:
            s3_client.get_bucket_encryption(Bucket=bucket['Name'])
            _result = True
            _buckets.append(bucket['Name'])
        except Exception as e:
            # print_red(f"  ✗ {bucket_name}: Encryption NOT enabled ")
            pass
    _result_dict["buckets"] = _buckets
    return _result


def check_ebs_encryption(ec2_client):
    _result = False
    _ebs_volumes = []
    try:
        volumes = ec2_client.describe_volumes()['Volumes']
        if not volumes:
            return True
        for volume in volumes:
            volume_id = volume['VolumeId']
            encrypted = volume.get('Encrypted', False)
            if encrypted:
                #print_green(f"  ✓ {volume_id}: Encryption enabled")
                _result = True
                _ebs_volumes.append(volume_id)

    except Exception as e:
        pass
    _result_dict["volumes"] = _ebs_volumes
    return _result


def check_efs_encryption(efs_client):
    _result = False
    _efs = []
    try:
        file_systems = efs_client.describe_file_systems()['FileSystems']
        if not file_systems:
            return True
        
        print(f"\nEFS File Systems ({len(file_systems)}):")
        for fs in file_systems:
            fs_id = fs['FileSystemId']
            encrypted = fs.get('Encrypted', False)
            if encrypted:
                _efs.append(fs_id)
                _result = True
    except Exception as e:
        pass
    _result_dict["efs"] = _efs
    return _result


def check_rds_encryption(rds_client):
    _result = False
    _rds = []
    try:
        instances = rds_client.describe_db_instances()['DBInstances']
        if not instances:
            return True

        for instance in instances:
            db_id = instance['DBInstanceIdentifier']
            encrypted = instance.get('StorageEncrypted', False)
            if encrypted:
                _rds.append(db_id)
    except Exception as e:
        pass
    _result_dict["rds"] = _rds
    return _result


def check_dynamodb_encryption(dynamodb_client):
    _result = False
    _dynamodbs = []
    try:
        tables = dynamodb_client.list_tables()['TableNames']
        
        if not tables:
           return True

        for table_name in tables:
            table = dynamodb_client.describe_table(TableName=table_name)['Table']
            sse = table.get('SSEDescription', {})
            status = sse.get('Status', 'DISABLED')
            if status == 'ENABLED':
                _result = True
                _dynamodbs.append(table_name)
            
    except Exception as e:
        pass
    _result_dict["dynamodbs"] = _dynamodbs
    return _result


def check_secrets_manager_encryption(sm_client):
    _result = False
    _ssm = []
    try:
        
        secrets = sm_client.list_secrets()['SecretList']
        
        if not secrets:
           return True

        for secret in secrets:
            secret_name = secret['Name']
            kms_key = secret.get('KmsKeyId')
            if kms_key:
                _result = True
                _ssm.append(secret_name)
            
    except Exception as e:
        pass

    _result_dict["ssm"] = _ssm
    return _result


def check_redshift_encryption(redshift_client):
    _result = False
    _redshifts = []
    try:
        clusters = redshift_client.describe_clusters()['Clusters']
        if not clusters:
            return True
        
        print(f"\nRedshift Clusters ({len(clusters)}):")
        for cluster in clusters:
            cluster_id = cluster['ClusterIdentifier']
            encrypted = cluster.get('Encrypted', False)
            if encrypted:
                _result = True
                _redshifts.append(cluster_id)
    except Exception as e:
        pass
    _result_dict["redshifts"] = _redshifts
    return _result


def check_elasticache_encryption(elasticache_client):
    _result = False
    _elasticaches = []
    try:
        clusters = elasticache_client.describe_cache_clusters()['CacheClusters']
        if not clusters:
            return True

        for cluster in clusters:
            cluster_id = cluster['CacheClusterId']
            encrypted = cluster.get('AtRestEncryptionEnabled', False)
            if encrypted:
                _elasticaches.append(cluster_id)
                _result = True
    except Exception as e:
        pass
    _result_dict["elasticaches"] = _elasticaches
    return _result


def check_lambda_encryption(lambda_client):
    _result = False
    _lambdas = []
    try:
        functions = lambda_client.list_functions()['Functions']
        
        if not functions:
            return True
        
        print(f"\nLambda Functions ({len(functions)}):")
        for function in functions:
            func_name = function['FunctionName']
            kms_key = function.get('KMSKeyArn')
            if kms_key:
                _lambdas.append(func_name)
           
    except Exception as e:
        pass
    _result_dict["lambdas"] = _lambdas
    return _result


def check_sagemaker_encryption(sagemaker_client):
    _result = False
    _sagemakers = []
    try:
        
        notebooks = sagemaker_client.list_notebook_instances()['NotebookInstances']
        
        if not notebooks:
            return True
        
        print(f"\nSageMaker Notebook Instances ({len(notebooks)}):")
        for notebook in notebooks:
            notebook_name = notebook['NotebookInstanceName']
            details = sagemaker_client.describe_notebook_instance(NotebookInstanceName=notebook_name)
            kms_key = details.get('KmsKeyId')
            if kms_key:
                _sagemakers.append(notebook_name)
                _result = True
            
    except Exception as e:
        pass
    _result_dict["sagemaker"] = _sagemakers
    return _result


def check_emr_encryption(emr_client):
    _result = False
    _emrs = []
    try:
        
        clusters = emr_client.list_clusters(ClusterStates=['RUNNING', 'WAITING'])['Clusters']
        
        if not clusters:
            return True

        for cluster in clusters:
            cluster_id = cluster['Id']
            cluster_name = cluster['Name']
            details = emr_client.describe_cluster(ClusterId=cluster_id)['Cluster']
            security_config = details.get('SecurityConfiguration')
            if security_config:
                _emrs.append(cluster_name + "  " + cluster_id)

    except Exception as e:
        pass
    _result_dict["emrs"] = _emrs
    return _result


def main(boto_clients: BotoClients):
    # print("=" * 60)
    # print("AWS Data-at-Rest Encryption Verification")
    # print("=" * 60)
    _result: dict = {}
    _result["buckets"] = check_s3_buckets_encryption(boto_clients.s3_client)
    _result["volumes"] = check_ebs_encryption(boto_clients.ec2_client)
    _result["efs"] = check_efs_encryption(boto_clients.efs_client)
    _result["rds"] = check_rds_encryption(boto_clients.rds_client)
    _result["dynamodbs"] = check_dynamodb_encryption(boto_clients.dynamodb_client)
    _result["ssm"] = check_secrets_manager_encryption(boto_clients.sm_client)
    _result["redshifts"] = check_redshift_encryption(boto_clients.redshift_client)
    _result["elasticaches"] = check_elasticache_encryption(boto_clients.elasticache_client)
    _result["lambdas"] = check_lambda_encryption(boto_clients.lambda_client)
    _result["sagemakers"] = check_sagemaker_encryption(boto_clients.sagemaker_client)
    _result["emrs"] = check_emr_encryption(boto_clients.emr_client)
    _result["data"] = _result_dict
    return _result
    # print("\n" + "=" * 60)
    # print("Verification Complete")
    # print("=" * 60)


def check_kms_policy(kms_client):
    try:
        keys = kms_client.list_keys().get("Keys", [])
 
        if not keys:
            return ("KMS not configured", "Red")
 
        aws_managed_keys = 0
 
        for key in keys:
            metadata = kms_client.describe_key(
                KeyId=key["KeyId"]
            )["KeyMetadata"]
 
            if metadata.get("KeyManager") == "AWS" and metadata.get("KeyState") == "Enabled":
                aws_managed_keys += 1

    except Exception as e:
        return f"ERROR: {str(e)}"
    if aws_managed_keys > 0 :
        return ("KMS configured", "Green")
    else:
        return ("KMS not configured", "Red")



if __name__ == "__main__":
    main()
