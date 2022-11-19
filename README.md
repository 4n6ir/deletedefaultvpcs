# deletedefaultvpcs

The enabled regions for new Amazon Web Services (AWS) accounts have a default VPC deployed as standard. Any newly activated regions will have these as well leaving more networks requiring protection.

A custom resource initiates the deletion on the original deployment with regular checks daily.

1. Detach Internet Gateway
2. Delete Internet Gateway
3. Delete Subnets
4. Delete VPC

If the default VPC is in use, it will not be deleted and an error will be generatored, after Internet access has been mitigated.
