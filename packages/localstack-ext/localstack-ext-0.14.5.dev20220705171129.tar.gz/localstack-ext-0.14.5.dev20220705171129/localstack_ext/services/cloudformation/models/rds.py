_p='AllocatedStorage'
_o='DomainIAMRoleName'
_n='Domain'
_m='CopyTagsToSnapshot'
_l='DeletionProtection'
_k='ScalingConfiguration'
_j='EnableCloudwatchLogsExports'
_i='EnableIAMDatabaseAuthentication'
_h='KmsKeyId'
_g='StorageEncrypted'
_f='PreferredMaintenanceWindow'
_e='PreferredBackupWindow'
_d='OptionGroupName'
_c='MasterUserPassword'
_b='MasterUsername'
_a='EngineVersion'
_Z='Engine'
_Y='VpcSecurityGroupIds'
_X='CharacterSetName'
_W='Endpoint'
_V='Endpoint.Port'
_U='localhost'
_T='Endpoint.Address'
_S='DBParameterGroupFamily'
_R='BackupRetentionPeriod'
_Q='LogicalResourceId'
_P='Family'
_O='delete'
_N='create'
_M='rds'
_L='Properties'
_K='Tags'
_J='DBInstanceIdentifier'
_I='DBParameterGroupName'
_H='DBClusterParameterGroupName'
_G='Description'
_F='Port'
_E='DBClusterIdentifier'
_D='parameters'
_C='DBSubnetGroupName'
_B='function'
_A=None
from typing import Dict,List
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import short_uid
class RDSDBSubnetGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBSubnetGroup'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_C)
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_L]
		if not B.get(_C):B[_C]=generate_default_name_without_stack(A[_Q])
	def fetch_state(A,stack_name,resources):B=A.get_client();C=A.resolve_refs_recursively(stack_name,A.props.get(_C),resources);D=B.describe_db_subnet_groups()['DBSubnetGroups'];E=[A for A in D if A[_C]==C];return(E or[_A])[0]
	def get_client(A):return aws_stack.connect_to_service(_M)
	@staticmethod
	def get_deploy_templates():return{_N:{_B:'create_db_subnet_group'},_O:{_B:'delete_db_subnet_group',_D:{_C:_C}}}
class RDSDBCluster(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBCluster'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource[_L]
		if not A.get(_E):A[_E]=f"dbc-{short_uid()}"
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_E)
	def fetch_state(A,stack_name,resources):B=A.get_client();C=B.describe_db_clusters().get('DBClusters',[]);D=A.resolve_refs_recursively(stack_name,A.props.get(_E),resources);E=[A for A in C if A[_E]==D];return(E or[_A])[0]
	def get_client(A):return aws_stack.connect_to_service(_M)
	def get_cfn_attribute(B,attribute):
		A=attribute
		if A==_T:return _U
		C=B.props
		if A==_V:return C.get(_F)or C.get(_W,{}).get(_F)
		return super(RDSDBCluster,B).get_cfn_attribute(A)
	@classmethod
	def get_creation_params(A):return['AvailabilityZones',_R,_X,'DatabaseName',_E,_H,_Y,_C,_Z,_a,_F,_b,_c,_d,_e,_f,'ReplicationSourceIdentifier',_K,_g,_h,'PreSignedUrl',_i,'BacktrackWindow',_j,'EngineMode',_k,_l,'GlobalClusterIdentifier','EnableHttpEndpoint',_m,_n,_o,'EnableGlobalWriteForwarding','SourceRegion']
	@classmethod
	def get_deploy_templates(A):
		E=A.get_creation_params()
		def B(params,**F):
			D='MaxCapacity';C='MinCapacity';B=params;B={A:C for(A,C)in B.items()if A in E};A=B.get(_k)
			if A:
				if C in A:A[C]=int(A[C])
				if D in A:A[D]=int(A[D])
			return B
		C={_N:{_B:'create_db_cluster',_D:B,'types':{_R:int,_F:int}},_O:{_B:'delete_db_cluster',_D:[_E]}};return C
class RDSDBParameterGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBParameterGroup'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_I)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=A.get_client();D=A.props;F=A.resolve_refs_recursively(B,D.get(_G),C);G=A.resolve_refs_recursively(B,D.get(_P),C);H=E.describe_db_parameter_groups()['DBParameterGroups'];I=[A for A in H if A[_P]==G and A[_G]==F];return(I or[_A])[0]
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_L]
		if not B.get(_I):B[_I]=generate_default_name_without_stack(A[_Q])
	def get_client(A):return aws_stack.connect_to_service(_M)
	@staticmethod
	def get_deploy_templates():return{_N:{_B:'create_db_parameter_group',_D:{_I:_I,_S:_P,_G:_G,_K:_K}},_O:{_B:'delete_db_parameter_group',_D:[_I]}}
class RDSDBClusterParameterGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBClusterParameterGroup'
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_H)
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_L]
		if not B.get(_H):B[_H]=generate_default_name_without_stack(A[_Q])
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=A.get_client();D=A.props;F=A.resolve_refs_recursively(B,D.get(_G),C);G=A.resolve_refs_recursively(B,D.get(_P),C);H=E.describe_db_cluster_parameter_groups()['DBClusterParameterGroups'];I=[A for A in H if A[_S]==G and A[_G]==F];return(I or[_A])[0]
	def get_client(A):return aws_stack.connect_to_service(_M)
	@staticmethod
	def get_deploy_templates():return{_N:{_B:'create_db_cluster_parameter_group',_D:{_H:_H,_S:_P,_G:_G,_K:_K}},_O:{_B:'delete_db_cluster_parameter_group',_D:[_H]}}
class RDSDBInstance(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::RDS::DBInstance'
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource[_L]
		if not A.get(_J):A[_J]=f"db-{short_uid()}"
	def get_physical_resource_id(A,attribute=_A,**B):return A.props.get(_J)
	def get_cfn_attribute(B,attribute):
		A=attribute
		if A==_T:return _U
		C=B.props
		if A==_V:return C.get(_W,{}).get(_F)or C.get(_F)
		return super(RDSDBInstance,B).get_cfn_attribute(A)
	def fetch_state(A,stack_name,resources):B=A.props.get(_J);B=A.resolve_refs_recursively(stack_name,B,resources);C=A.get_client();D=C.describe_db_instances()['DBInstances'];E=[A for A in D if A[_J]==B];return(E or[_A])[0]
	def get_client(A):return aws_stack.connect_to_service(_M)
	@classmethod
	def get_creation_params(A):return['DBName',_J,_p,'DBInstanceClass',_Z,_b,_c,'DBSecurityGroups','AvailabilityZone',_C,_f,_I,_R,_e,_F,'MultiAZ',_a,'AutoMinorVersionUpgrade','LicenseModel','Iops',_d,_X,'NcharCharacterSetName','PubliclyAccessible',_K,_E,'StorageType','TdeCredentialArn','TdeCredentialPassword',_g,_h,_n,_m,'MonitoringInterval','MonitoringRoleArn',_o,'PromotionTier','Timezone',_i,'EnablePerformanceInsights','PerformanceInsightsKMSKeyId','PerformanceInsightsRetentionPeriod',_j,'ProcessorFeatures',_l,'MaxAllocatedStorage','EnableCustomerOwnedIp']
	@classmethod
	def get_deploy_templates(A):B=A.get_creation_params();return{_N:{_B:'create_db_instance',_D:B+[{_Y:'VPCSecurityGroups'}],'types':{_p:int,_F:int}},_O:{_B:'delete_db_instance',_D:[_J]}}