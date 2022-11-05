import cdk_nag

from aws_cdk import (
    Aspects,
    CustomResource,
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs,
    aws_logs_destinations as _destinations,
    custom_resources as _custom
)

from constructs import Construct

class DeletedefaultvpcsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Aspects.of(self).add(
            cdk_nag.AwsSolutionsChecks(
                log_ignores = True,
                verbose = True
            )
        )

        cdk_nag.NagSuppressions.add_stack_suppressions(
            self, suppressions = [
                {'id': 'AwsSolutions-IAM4','reason': 'GitHub Issue'},
                {'id': 'AwsSolutions-IAM5','reason': 'GitHub Issue'},
                {'id': 'AwsSolutions-L1','reason': 'GitHub Issue'}
            ]
        )

        account = Stack.of(self).account                                            # ChatOps
        region = Stack.of(self).region

        if region == 'ap-northeast-1' or region == 'ap-south-1' or region == 'ap-southeast-1' or \
            region == 'ap-southeast-2' or region == 'eu-central-1' or region == 'eu-west-1' or \
            region == 'eu-west-2' or region == 'me-central-1' or region == 'us-east-1' or \
            region == 'us-east-2' or region == 'us-west-2': number = str(1)

        if region == 'af-south-1' or region == 'ap-east-1' or region == 'ap-northeast-2' or \
            region == 'ap-northeast-3' or region == 'ap-southeast-3' or region == 'ca-central-1' or \
            region == 'eu-north-1' or region == 'eu-south-1' or region == 'eu-west-3' or \
            region == 'me-south-1' or region == 'sa-east-1' or region == 'us-west-1': number = str(2)

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:'+number
        )

        role = _iam.Role(
            self, 'role', 
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'ec2:DescribeRegions',
                    'ec2:DescribeVpcs',
                    'ec2:DeleteVpc',
                    'ec2:DescribeInternetGateways',
                    'ec2:DetachInternetGateway',
                    'ec2:DeleteInternetGateway',
                    'ec2:DescribeSubnets',
                    'ec2:DeleteSubnet'
                ],
                resources = ['*']
            )
        )

        delete = _lambda.Function(
            self, 'delete',
            code = _lambda.Code.from_asset('delete'),
            handler = 'delete.handler',
            runtime = _lambda.Runtime.PYTHON_3_9,
            architecture = _lambda.Architecture.ARM_64,
            timeout = Duration.seconds(60),
            memory_size = 256,
            role = role,
            layers = [
                layer
            ]
        )

        logs = _logs.LogGroup(
            self, 'logs',
            log_group_name = '/aws/lambda/'+delete.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        error = _lambda.Function.from_function_arn(                                 # ChatOps
            self, 'error',                                                          #
            'arn:aws:lambda:'+region+':'+account+':function:shipit-error'           #
        )                                                                           #

        errorsub = _logs.SubscriptionFilter(                                        # ChatOps
            self, 'errorsub',                                                       #
            log_group = logs,                                                       #
            destination = _destinations.LambdaDestination(error),                   #
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')                 #
        )

        timeout = _lambda.Function.from_function_arn(                               # ChatOps
            self, 'timeout',                                                        #
            'arn:aws:lambda:'+region+':'+account+':function:shipit-timeout'         #
        )                                                                           #

        timesub = _logs.SubscriptionFilter(                                         # ChatOps
            self, 'timesub',                                                        #
            log_group = logs,                                                       #
            destination = _destinations.LambdaDestination(timeout),                 #
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')    #
        )                                                                           #

        deleteevent = _events.Rule(
            self, 'deleteevent',
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '0',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )

        deleteevent.add_target(_targets.LambdaFunction(delete))

        provider = _custom.Provider(
            self, 'provider',
            on_event_handler = delete
        )

        resource = CustomResource(
            self, 'resource',
            service_token = provider.service_token
        )
