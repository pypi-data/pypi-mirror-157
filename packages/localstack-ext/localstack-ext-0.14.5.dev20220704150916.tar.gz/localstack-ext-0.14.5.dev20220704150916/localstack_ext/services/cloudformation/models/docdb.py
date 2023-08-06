_F='PreferredMaintenanceWindow'
_E='DBClusterIdentifier'
_D='DBClusterParameterGroupName'
_C='Properties'
_B='Engine'
_A='docdb'
from typing import Dict,List
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.models.rds import RDSDBCluster,RDSDBClusterParameterGroup,RDSDBInstance,RDSDBSubnetGroup
class DocDBCluster(RDSDBCluster):
	@staticmethod
	def cloudformation_type():return'AWS::DocDB::DBCluster'
	@staticmethod
	def add_defaults(resource,stack_name):A=resource;A[_C][_B]=_A;RDSDBCluster.add_defaults(A,stack_name)
	def get_client(A):return aws_stack.connect_to_service(_A)
	@classmethod
	def get_creation_params(A):return['AvailabilityZones','BackupRetentionPeriod','CopyTagsToSnapshot',_E,_D,'DBSubnetGroupName','DeletionProtection','EnableCloudwatchLogsExports',_B,'EngineVersion','KmsKeyId','MasterUsername','MasterUserPassword','Port','PreferredBackupWindow',_F,'SnapshotIdentifier','StorageEncrypted','Tags','VpcSecurityGroupIds']
class DocDBInstance(RDSDBInstance):
	@staticmethod
	def cloudformation_type():return'AWS::DocDB::DBInstance'
	def get_client(A):return aws_stack.connect_to_service(_A)
	@staticmethod
	def add_defaults(resource,stack_name):A=resource;A[_C][_B]=_A;RDSDBInstance.add_defaults(A,stack_name)
	@classmethod
	def get_creation_params(A):return['AutoMinorVersionUpgrade','AvailabilityZone',_E,'DBInstanceClass','DBInstanceIdentifier','EnablePerformanceInsights',_B,_F,'Tags']
class DocDBClusterParameterGroup(RDSDBClusterParameterGroup):
	@staticmethod
	def cloudformation_type():return'AWS::DocDB::DBClusterParameterGroup'
	def get_client(A):return aws_stack.connect_to_service(_A)
	@staticmethod
	def add_defaults(resource,stack_name):
		B=resource;A=B[_C]
		if not A.get(_D):C=A.get('Name')or generate_default_name_without_stack(B['LogicalResourceId']);A[_D]=C
class DocDBSubnetGroup(RDSDBSubnetGroup):
	@staticmethod
	def cloudformation_type():return'AWS::DocDB::DBSubnetGroup'
	def get_client(A):return aws_stack.connect_to_service(_A)