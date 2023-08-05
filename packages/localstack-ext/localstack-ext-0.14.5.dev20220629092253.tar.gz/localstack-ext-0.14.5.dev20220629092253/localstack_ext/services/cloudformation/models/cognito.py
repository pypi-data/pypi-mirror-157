_T='_deployed'
_S='ClientId'
_R='cognito-identity'
_Q='PoolName'
_P='LogicalResourceId'
_O='Properties'
_N='Domain'
_M='ClientName'
_L='IdentityPoolId'
_K='IdentityPoolName'
_J='GroupName'
_I='UserPoolName'
_H='cognito-idp'
_G='delete'
_F='create'
_E='ProviderName'
_D=None
_C='parameters'
_B='UserPoolId'
_A='function'
from localstack.constants import TEST_AWS_ACCOUNT_ID,TRUE_STRINGS
from localstack.services.cloudformation.deployment_utils import generate_default_name_without_stack
from localstack.services.cloudformation.service_models import REF_ATTRS,REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cognito_idp.cognito_utils import get_issuer_url
from localstack_ext.utils.aws import aws_utils
class CognitoUserPool(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPool'
	def fetch_state(B,stack_name,resources):A=B.props[_I];A=B.resolve_refs_recursively(stack_name,A,resources);C=aws_stack.connect_to_service(_H);D=C.list_user_pools(MaxResults=100)['UserPools'];return([B for B in D if B['Name']==A]or[_D])[0]
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		if A in REF_ATTRS:return B.get_physical_resource_id(A)
		C=B._get_id()
		if A=='Arn':return aws_utils.cognito_userpool_arn(C)
		if A==_E:return 'cognito-idp.{r}.amazonaws.com/{r}_{a}'.format(r=aws_stack.get_region(),a=TEST_AWS_ACCOUNT_ID)
		if A=='ProviderURL':return get_issuer_url(pool_id=C)
		return super(CognitoUserPool,B).get_cfn_attribute(A)
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_O]
		if not B.get(_I):B[_I]=generate_default_name_without_stack(A[_P])
	def get_physical_resource_id(B,attribute,**C):
		A=B._get_id()
		if not A:return A
		if attribute in REF_ATTRS:return A
		return aws_utils.cognito_userpool_arn(A)
	def get_resource_name(A):return A.props.get(_Q)
	def _get_id(B):A=B.props;return A.get(_B)or A.get('Id')
	@staticmethod
	def get_deploy_templates():
		def A(params,**Q):
			K='MaxLength';J='MinLength';I='Schema';H='Policies';F='MinimumLength';D='AutoVerifiedAttributes';L=[H,'LambdaConfig',D,'AliasAttributes','UsernameAttributes','VerificationMessageTemplate','EmailVerificationMessage','EmailVerificationSubject','SmsVerificationMessage','SmsAuthenticationMessage','DeviceConfiguration','EmailConfiguration','SmsConfiguration','UserPoolTags','AdminCreateUserConfig',I,'UserPoolAddOns'];G={A:A for A in L};G[_Q]=_I;A={A:params.get(B)for(A,B)in G.items()};M=A.get(H)or{};B=M.get('PasswordPolicy')or{}
			if B.get(F):B[F]=int(B[F])
			N=['RequireLowercase','RequireNumbers','RequireSymbols','RequireUppercase'];O=list(TRUE_STRINGS)+[True]
			for E in N:
				if E in B:B[E]=B[E]in O
			if isinstance(A.get(D),str):A[D]=[A[D]]
			for P in A.get(I)or[]:
				C=P.get('StringAttributeConstraints')
				if C:C[J]=str(C.get(J,1));C[K]=str(C.get(K,50))
			return A
		return{_F:{_A:'create_user_pool',_C:A},_G:{_A:'delete_user_pool',_C:{_B:'Id'}}}
class UserPoolGroup(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolGroup'
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_J)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_H);D=A.props;F=A.resolve_refs_recursively(B,D.get(_J),C);G=A.resolve_refs_recursively(B,D.get(_B),C);H=E.list_groups(UserPoolId=G)['Groups'];I=[A for A in H if A[_J]==F];return(I or[_D])[0]
	@staticmethod
	def get_deploy_templates():return{_F:{_A:'create_group'},_G:{_A:'delete_group',_C:[_J,_B]}}
class IdentityPool(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::IdentityPool'
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		try:return super(IdentityPool,B).get_cfn_attribute(A)
		except Exception:
			if A in REF_ID_ATTRS:return B.get_physical_resource_id(A)
			if A==_E:return 'cognito.{r}.amazonaws.com/{r}_{a}'.format(r=aws_stack.get_region(),a=TEST_AWS_ACCOUNT_ID)
			raise
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_O]
		if not B.get(_K):B[_K]=generate_default_name_without_stack(A[_P])
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_L)
	def fetch_state(B,stack_name,resources):A=B.props[_K];A=B.resolve_refs_recursively(stack_name,A,resources);C=aws_stack.connect_to_service(_R);D=C.list_identity_pools(MaxResults=100)['IdentityPools'];E=[B for B in D if B[_K]==A];return(E or[_D])[0]
	@staticmethod
	def get_deploy_templates():return{_F:{_A:'create_identity_pool'},_G:{_A:'delete_identity_pool',_C:[_L]}}
class CognitoUserPoolClient(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolClient'
	def get_cfn_attribute(B,attribute_name):
		A=attribute_name
		if A in REF_ID_ATTRS:return B.get_physical_resource_id(A)
		return super(CognitoUserPoolClient,B).get_cfn_attribute(A)
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_S)
	@staticmethod
	def add_defaults(resource,stack_name):
		A=resource;B=A[_O]
		if not B.get(_M):B[_M]=generate_default_name_without_stack(A[_P])
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;D=A.props;E=A.resolve_refs_recursively(B,D.get(_M),C);F=A.resolve_refs_recursively(B,D[_B],C);G=aws_stack.connect_to_service(_H);H=G.list_user_pool_clients(UserPoolId=F)['UserPoolClients'];return([A for A in H if A[_M]==E]or[_D])[0]
	@staticmethod
	def get_deploy_templates():
		def A(params,**C):
			B='RefreshTokenValidity';A=params
			if A.get(B)is not _D:A[B]=int(A[B])
			return A
		return{_F:{_A:'create_user_pool_client',_C:A},_G:{_A:'delete_user_pool_client',_C:[_B,_S]}}
class CognitoUserPoolDomain(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolDomain'
	def get_physical_resource_id(A,attribute,**B):
		if attribute in REF_ID_ATTRS:return A.props.get(_N)
	def fetch_state(A,stack_name,resources):B=aws_stack.connect_to_service(_H);C=A.resolve_refs_recursively(stack_name,A.props.get(_N),resources);D=B.describe_user_pool_domain(Domain=C)['DomainDescription'];return D or _D
	@staticmethod
	def get_deploy_templates():return{_F:{_A:'create_user_pool_domain'},_G:{_A:'delete_user_pool_domain',_C:{_B:_B,_N:_N}}}
class CognitoIdentityPoolRoleAttachment(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::IdentityPoolRoleAttachment'
	def fetch_state(B,stack_name,resources):
		C=aws_stack.connect_to_service(_R);D=B.resolve_refs_recursively(stack_name,B.props.get(_L),resources);A=C.get_identity_pool_roles(IdentityPoolId=D)
		if A:A[_T]=True
		return A or _D
	def get_physical_resource_id(B,attribute,**C):A=B.props;return A.get(_T)and'cognito-pool-roles-%s'%A.get(_L)
	@staticmethod
	def get_deploy_templates():
		def A(params,*H,**I):
			F='IdentityProvider';E='RoleMappings';B=params;D=B.get(E)
			if D:
				C={}
				for (G,A) in D.items():
					if A.get(F):C[A.pop(F)]=A
					else:C[G]=A
				B[E]=C
			return B
		return{_F:{_A:'set_identity_pool_roles',_C:A}}
class CognitoUserPoolIdentityProvider(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::Cognito::UserPoolIdentityProvider'
	def get_physical_resource_id(A,attribute,**B):return A.props.get(_E)
	def fetch_state(A,stack_name,resources):C=resources;B=stack_name;E=aws_stack.connect_to_service(_H);D=A.props;F=A.resolve_refs_recursively(B,D.get(_B),C);G=A.resolve_refs_recursively(B,D.get(_E),C);H=E.list_identity_providers(UserPoolId=F)['Providers'];I=[A for A in H if A[_E]==G];return(I or[_D])[0]
	@staticmethod
	def get_deploy_templates():return{_F:{_A:'create_identity_provider'},_G:{_A:'delete_identity_provider',_C:{_B:_B,_E:_E}}}