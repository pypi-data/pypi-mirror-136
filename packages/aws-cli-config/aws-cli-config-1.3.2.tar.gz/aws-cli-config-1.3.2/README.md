This tool helps to configure the `.aws/config` and `.aws/credentials` for multi-account and multi-role AWS environments 
in which identities (IAM users) are deployed in a centralized account. IAM Roles are used to log into the accounts 
of an AWS organization.


### How to install `aws-cli-config`

The tool can be installed issuing the following command:

```shell
pip install aws-cli-config
```

If the installation is successful, an configuration file is created in the user home folder. On unix-like systems, this 
file can be found under `/Users/<my-username>/.aws-cli-config`


### How to configure `aws-cli-config`

As mentioned in the previous paragraph, file named `.aws-cli-config` is automatically created in the user home folder. 
This file can be personalized to contain an unlimited number of AWS organizations, AWS accounts, and IAM roles. Herewith 
is presented a short example with 2 AWS organizations: 

- **Organization-1** has 2 accounts (Account A and Account B) with 3 IAM roles each
- **Organization-2** has 1 account (Account A) with 3 IAM roles


```
profiles:
  # Organizations / Groups
  org1:
    # The following profiles must be already present in the .aws/config file
    profile_default: org1-default
    profile_mfa: org1-mfa-enabled-profile
    # List of accounts in the organization 1
    accounts:
      # ---------------------------------------------------------
      # The following are roles deployed in the Account A (org 1)
      # ---------------------------------------------------------
      - profile_prefix: org1-account-A
        account_source: org1-mfa-enabled-profile
        account_id: 000000000000
        account_roles:
          role_1: org1-aws-iam-role-1
          role_2: org1-aws-iam-role-2
          role_n: org1-aws-iam-role-n
      # -------------------------------------------------
      # The following are roles deployed in the Account B (org 1)
      # -------------------------------------------------
      - profile_prefix: org1-account-B
        account_source: org1-mfa-enabled-profile
        account_id: 000000000000
        account_roles:
          role_1: org1-aws-iam-role-1
          role_2: org1-aws-iam-role-2
          role_n: org1-aws-iam-role-n

  org2:
    # The following profiles must be already present in the .aws/config file
    profile_default: org2-default
    profile_mfa: org2-mfa-enabled-profile
    # List of accounts in the organization 2
    accounts:
      # ---------------------------------------------
      - profile_prefix: org2-account-A
        account_source: org2-mfa-enabled-profile
        account_id: 000000000000
        account_roles:
          role_1: org2-aws-iam-role-1
          role_2: org2-aws-iam-role-2
          role_n: org2-aws-iam-role-n
```

Given the above configuration file, the `.aws/credentials` file must contain the following entries: 

```
[org1-default]
aws_access_key_id = <REDACTED>
aws_secret_access_key = <REDACTED>
region = eu-west-1
output = json

[org1-mfa-enabled-profile]
aws_arn_mfa = <REDACTED>


[org2-default]
aws_access_key_id = <REDACTED>
aws_secret_access_key = <REDACTED>
region = eu-west-1
output = json

[org2-mfa-enabled-profile]
aws_arn_mfa = <REDACTED>

```

The REDACTED values must be retrieved from the AWS account into which the IAM Users are provisioned, and from where the 
STS Assume Role operation is executed.

### How to use `aws-cli-config`

#### Assume the configured roles using MFA

```
aws-cli-config <org> <mfa-token>
```

#### Listing all the available roles (and their alias)

```
aws-cli-config -l <org>

org1-account-A (000000000000)
[1] org1-account-A_role_1 (org1-aws-iam-role-1)
[2] org1-account-A_role_2 (org1-aws-iam-role-2)
[3] org1-account-A_role_n (org1-aws-iam-role-n)
org1-account-B (000000000000)
[1] org1-account-B_role_1 (org1-aws-iam-role-1)
[2] org1-account-B_role_2 (org1-aws-iam-role-2)
[3] org1-account-B_role_n (org1-aws-iam-role-n)
org2-account-A (000000000000)
[1] org2-account-A_role_1 (org2-aws-iam-role-1)
[2] org2-account-A_role_2 (org2-aws-iam-role-2)
[3] org2-account-A_role_n (org2-aws-iam-role-n)

```

#### Exporting a profile to the environment
Once **Assume Role with MFA** operation is completed the `.aws/credentials` and `.aws/config` files are updated with the 
newly generated temporary credentials. You can test if the credentials are correctly loaded with the following command:

```
export AWS_PROFILE=org1-account-A_role_1 
aws s3 ls 
```

A list of S3 buckets in the Account A (Org1) will be listed (assuming that `role_1` has sufficient privileges).

### Supported arguments

```
usage: aws-cli-config [-h] [-l] [--aws-cli-config-filepath AWS_CLI_CONFIG_FILEPATH] [--max-role-duration MAX_ROLE_DURATION] [-v] [profile] [mfa]

positional arguments:
  profile               the name of the AWS parent profile / name of the AWS Organization group
  mfa                   the MFA code generated with an external hardware/virtual device

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list accounts and roles for an organization/profile
  --aws-cli-config-filepath AWS_CLI_CONFIG_FILEPATH
                        filepath of the YML config file containing the multi-account/multi-role structure
  --max-role-duration MAX_ROLE_DURATION
                        the duration (in seconds) of the AWS IAM role session
  -v, --verbose         verbose mode

```

