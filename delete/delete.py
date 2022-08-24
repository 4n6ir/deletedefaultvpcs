import boto3
import json

def handler(event, context):

    client = boto3.client('ec2')
    regions = client.describe_regions()

    for region in regions['Regions']:
        ec2_client = boto3.client('ec2', region_name=region['RegionName'])
        paginator = ec2_client.get_paginator('describe_vpcs')
        response_iterator = paginator.paginate()
        for page in response_iterator:
            if len(page['Vpcs']) > 0:
                for item in page['Vpcs']:
                    if item['IsDefault'] is True:

                        paginator2 = ec2_client.get_paginator('describe_internet_gateways')
                        response_iterator2 = paginator2.paginate()
                        for page2 in response_iterator2:
                            for item2 in page2['InternetGateways']:
                                if len(page2['InternetGateways']) > 0:
                                    if item2['Attachments'][0]['VpcId'] == item['VpcId']:
                                        try:
                                            ec2_client.detach_internet_gateway(
                                                InternetGatewayId=item2['InternetGatewayId'],
                                                VpcId=item['VpcId']
                                            )
                                            ec2_client.delete_internet_gateway(
                                                InternetGatewayId=item2['InternetGatewayId']
                                            )
                                        except:
                                            print('ERROR '+str(item2))

                        paginator3 = ec2_client.get_paginator('describe_subnets')
                        response_iterator3 = paginator3.paginate()
                        for page3 in response_iterator3:
                            for item3 in page3['Subnets']:
                                if len(page3['Subnets']) > 0:
                                    if item3['VpcId'] == item['VpcId']:
                                        try:
                                            ec2_client.delete_subnet(
                                                SubnetId=item3['SubnetId']
                                            )
                                        except:
                                            print('ERROR '+str(item3))

                        try:
                            ec2_client.delete_vpc(
                                VpcId=item['VpcId']
                            )
                        except:
                            print('ERROR '+str(item))
                            pass

    return {
        'statusCode': 200,
        'body': json.dumps('Delete Default VPCs')
    }
