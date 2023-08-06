_B='result'
_A='AWS::CDK::Metadata'
import json
from localstack import config
from localstack.services.awslambda import lambda_executors
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import recurse_object,retry,short_uid,to_str
from localstack.utils.testutil import map_all_s3_objects
from localstack_ext.services.cloudformation.service_models import CUSTOM_RESOURCE_STATUSES,CUSTOM_RESOURCES_RESULT_POLL_TIMEOUT,CUSTOM_RESOURCES_RESULTS_BUCKET,LOG
from localstack_ext.utils.aws import aws_utils
class CDKMetadata(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return _A
	def fetch_state(A,stack_name,resources):return{'type':_A}
class CustomResource(GenericBaseModel):
	@staticmethod
	def cloudformation_type():return'AWS::CloudFormation::CustomResource'
	def fetch_state(A,stack_name,resources):B=A.logical_resource_id;C=CUSTOM_RESOURCE_STATUSES.get(aws_stack.get_region(),{}).get(stack_name,{}).get(B);return C
	def get_physical_resource_id(A,attribute,**B):return A.state[_B]['PhysicalResourceId']
	@staticmethod
	def get_deploy_templates():
		def A(resource_id,resources,resource_type,func,stack_name,*X):
			D=stack_name;C=resource_id;E=resources[C];F=E['Properties'];A=F.get('ServiceToken')
			if not A:LOG.warning('Missing ServiceToken attribute in custom resource: %s'%E);return
			def L(obj,**D):
				A=obj
				if isinstance(A,dict):
					for (C,B) in A.items():
						if isinstance(B,bool):A[C]=str(B).lower()
				return A
			recurse_object(F,L);aws_stack.get_or_create_bucket(CUSTOM_RESOURCES_RESULTS_BUCKET);G=short_uid();M=lambda_executors.get_main_endpoint_from_container();N=f"http://{M}:{config.get_edge_port_http()}";O=aws_stack.generate_presigned_url('put_object',Params={'Bucket':CUSTOM_RESOURCES_RESULTS_BUCKET,'Key':G},endpoint_url=N);P=aws_stack.cloudformation_stack_arn(D);I={'RequestType':'Create','ResponseURL':O,'StackId':P,'RequestId':short_uid(),'ResourceType':E.get('Type'),'LogicalResourceId':C,'ResourceProperties':F}
			if str(A).startswith('arn:aws:lambda'):H=A.split(':')[3];Q=aws_stack.lambda_function_name(A);R=aws_stack.connect_to_service('lambda',region_name=H);R.invoke(FunctionName=Q,Payload=json.dumps(I))
			elif str(A).startswith('arn:aws:sns'):H=A.split(':')[3];S=aws_stack.connect_to_service('sns',region_name=H);S.publish(TopicArn=A,Message=json.dumps(I))
			else:LOG.warning('Unsupported ServiceToken attribute in custom resource: %s'%A);return
			def T():return aws_utils.download_s3_object(CUSTOM_RESOURCES_RESULTS_BUCKET,G)
			B=None
			try:B=retry(T,retries=int(CUSTOM_RESOURCES_RESULT_POLL_TIMEOUT/2),sleep=2);B=json.loads(to_str(B))
			except Exception:U=map_all_s3_objects(buckets=[CUSTOM_RESOURCES_RESULTS_BUCKET]);LOG.info('Unable to fetch CF custom resource result from s3://%s/%s . Existing keys: %s'%(CUSTOM_RESOURCES_RESULTS_BUCKET,G,list(U.keys())));raise
			J=aws_stack.get_region();K=CUSTOM_RESOURCE_STATUSES[J]=CUSTOM_RESOURCE_STATUSES.get(J,{});V=K[D]=K.get(D)or{};W=B.get('Data')or{};V[C]={_B:B,**W};return B
		return{'create':{'function':A}}