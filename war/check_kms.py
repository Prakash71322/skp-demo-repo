 
 
def check_kms_policy(kms_client):
    """
    Validation:
    Implement secure key management
    Enforce KMS key policy existence and status
    """
 
    try:
        keys = kms_client.list_keys().get("Keys", [])
 
        if not keys:
            return "FAIL: No KMS keys found"
 
        for key in keys:
            key_id = key["KeyId"]
            metadata = kms_client.describe_key(KeyId=key_id)["KeyMetadata"]
 
            # Check key is enabled
            if metadata["KeyState"] != "Enabled":
                return f"FAIL: KMS key {key_id} is not enabled"
 
            # Validate key policy exists
            try:
                kms_client.get_key_policy(
                    KeyId=key_id,
                    PolicyName="default"
                )
            except Exception:
                return f"FAIL: KMS key {key_id} has no valid key policy"
 
        return "PASS: All KMS keys have enforced policies"
 
    except Exception as e:
        return f"ERROR: {str(e)}"
 
 
def check_default_kms_keys(kms_client):
    """
    Validation:
    Enforce Default KMS Keys (AWS Managed Keys)
    """
 
    try:
        keys = kms_client.list_keys().get("Keys", [])
 
        if not keys:
            return "FAIL: No KMS keys found"
 
        aws_managed_keys = 0
 
        for key in keys:
            metadata = kms_client.describe_key(
                KeyId=key["KeyId"]
            )["KeyMetadata"]
 
            if metadata.get("KeyManager") == "AWS" and metadata.get("KeyState") == "Enabled":
                aws_managed_keys += 1
 
        if aws_managed_keys > 0:
            return "PASS: Default AWS-managed KMS keys are enforced"
 
        return "FAIL: No enabled AWS-managed default KMS keys found"
 
    except Exception as e:
        return f"ERROR: {str(e)}"