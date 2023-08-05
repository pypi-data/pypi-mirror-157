__all__ = [  # noqa: F405
    "amplify",
    "apigateway",
    "apigatewayv2",
    "applicationautoscaling",
    "appsync",
    "awslambda",
    "backup",
    "cloudfront",
    "cloudtrail",
    "cognito",
    "custom",
    "docdb",
    "ec2",
    "ecr",
    "ecs",
    "elasticache",
    "elasticloadbalancingv2",
    "glue",
    "iot",
    "iotanalytics",
    "kinesisanalytics",
    "msk",
    "qldb",
    "rds",
    "redshift",
    "route53",
    "servicediscovery",
    "ses",
    "timestream",
]

# leave this star import here, so we can "import ...cloudformation.models" inside patch functions (not module level)
from localstack_ext.services.cloudformation.models import *
