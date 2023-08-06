_K='state_archive'
_J='presigned_url_metadata'
_I='presigned_url_state'
_H='services'
_G='ci_pod'
_F='api_states'
_E='presigned_urls'
_D='pod_name'
_C=None
_B=False
_A=True
import json,logging,os,re
from abc import ABCMeta,abstractmethod
from typing import Any,Dict,List,Optional,Set,Union
import requests
from localstack import config,constants
from localstack.utils.common import cp_r,disk_usage,download,load_file,new_tmp_dir,new_tmp_file,retry,rm_rf,safe_requests,save_file,to_str
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.testutil import create_zip_file
from requests import Response
from localstack_ext.bootstrap.licensing import get_auth_headers
from localstack_ext.bootstrap.pods.models import Serialization
from localstack_ext.bootstrap.pods.pods_api import PodsApi
from localstack_ext.bootstrap.pods.servicestate.service_state import ServiceState
from localstack_ext.bootstrap.pods.utils import remote_utils
from localstack_ext.bootstrap.pods.utils.adapters import ServiceStateMarshaller
from localstack_ext.bootstrap.pods.utils.common import PodsConfigContext
from localstack_ext.bootstrap.pods.utils.metamodel_utils import CommitMetamodelUtils
from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives
from localstack_ext.bootstrap.state_utils import API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR
from localstack_ext.constants import API_PATH_PODS
LOG=logging.getLogger(__name__)
PERSISTED_FOLDERS=[API_STATES_DIR,DYNAMODB_DIR,KINESIS_DIR]
class PodInfo:
	def __init__(A,name=_C,pod_size=0):A.name=name;A.pod_size=pod_size;A.pod_size_compressed=0;A.persisted_resource_names=[]
def get_state_zip_from_instance(get_content=_B,services=_C):
	B=services;C=f"{get_pods_endpoint()}/state";E=','.join(B)if B else'';A=requests.get(C,params={_H:E})
	if A.status_code>=400:raise Exception(f"Unable to get local pod state via management API {C} (code {A.status_code}): {A.content}")
	if get_content:return A.content
	D=f"{new_tmp_file()}.zip";save_file(D,A.content);return D
class CloudPodsManager(metaclass=ABCMeta):
	def __init__(A,pod_name):B=pod_name;A.pod_name=B;C=PodsConfigContext(pod_name=B);A.pods_api=PodsApi(C)
	@abstractmethod
	def init(self):...
	@abstractmethod
	def delete(self,remote):...
	@abstractmethod
	def push(self,comment=_C,services=_C):...
	@abstractmethod
	def push_overwrite(self,version,comment=_C):...
	@abstractmethod
	def fetch(self):...
	@abstractmethod
	def commit(self,message):...
	@abstractmethod
	def inject(self,version,reset_state,merge):...
	@abstractmethod
	def get_version_summaries(self):...
	@abstractmethod
	def version_metamodel(self,version):...
	@abstractmethod
	def set_version(self,version,inject_version_state,reset_state,commit_before):...
	@abstractmethod
	def list_version_commits(self,version):...
	@abstractmethod
	def get_commit_diff(self,version,commit):...
	@abstractmethod
	def register_remote(self,pod_name,ci_pod):...
	@abstractmethod
	def rename_pod(self,current_pod_name,new_pod_name):...
	@abstractmethod
	def list_pods(self,fetch_remote):...
	@staticmethod
	def restart_container():
		LOG.info('Restarting LocalStack instance with updated persistence state - this may take some time ...');B={'action':'restart'};A='%s/health'%config.get_edge_url()
		try:requests.post(A,data=json.dumps(B))
		except requests.exceptions.ConnectionError:pass
		def C():LOG.info('Waiting for LocalStack instance to be fully initialized ...');B=requests.get(A);C=json.loads(to_str(B.content));D=[A for(B,A)in C[_H].items()];assert set(D)=={'running'}
		retry(C,sleep=3,retries=10)
	def get_pod_info(C,pod_data_dir=_C):
		A=pod_data_dir;B=PodInfo(C.pod_name)
		if A:B.pod_size=disk_usage(A);B.persisted_resource_names=get_persisted_resource_names(A)
		return B
class CloudPodsVersionManager(CloudPodsManager):
	@staticmethod
	def parse_pod_name_from_qualifying_name(qualifying_name):return qualifying_name.split(PODS_NAMESPACE_DELIM,1)[1]
	@staticmethod
	def _prepare_archives_from_pre_signed_urls(content):
		A=new_tmp_file();B=content.get(_E);I=B.get('presigned_version_space_url');download(url=I,path=A);C={};D={};J=B.get('presigned_meta_state_urls')
		for (E,F) in J.items():G=new_tmp_file();H=new_tmp_file();K=F['meta'];L=F['state'];download(K,G);download(L,H);D[E]=G;C[E]=H
		return A,D,C
	@classmethod
	def _get_max_version_for_pod_from_platform(B,pod_name,auth_headers):
		C=CloudPodsVersionManager.create_platform_url(pod_name);A=safe_requests.get(url=C,headers=auth_headers);D='Failed to get version information from platform.. aborting'
		if not B._check_response(A,message=D,raise_error=_A):return
		E=json.loads(A.content);F=int(E['known_max_version']);return F
	def _add_state_to_cloud_pods_store(A,extract_assets=_B,services=_C):
		B=services;from localstack_ext.utils.persistence import marshall_backend as F
		if not A.pods_api.config_context.is_initialized():LOG.debug('No Cloud Pod instance detected in the local context - unable to add state');return
		B=B or A.pods_api.config_context.get_services_from_config();G=get_state_zip_from_instance(get_content=_A,services=B);D=ServiceStateMarshaller.unmarshall(G)
		for (C,H) in D.state.items():
			for (I,J) in H.backends.items():A.pods_api.create_state_file_from_fs(file_name=I,service=C.service,region=C.region,root=_F,account_id=C.account_id,serialization=Serialization.MAIN,object=F(J))
		if extract_assets:
			for (K,L) in D.assets.items():
				for (E,M) in L.items():A.pods_api.create_state_file_from_fs(rel_path=E,file_name=os.path.basename(E),service=K,region='NA',root='assets',account_id='NA',serialization=Serialization.MAIN,object=M)
		N=CommitMetamodelUtils.get_metamodel_from_instance();A.pods_api.add_metamodel_to_current_revision(N)
	def _fetch_versions(A,auth_headers,required_versions):
		D=A.create_platform_url(f"{A.pod_name}/data?versions={required_versions}");B=safe_requests.get(url=D,headers=auth_headers);E='Failed to pull requested versions from platform (code <status_code>)'
		if not A._check_response(B,message=E,raise_error=_A):return
		F=json.loads(B.content);C=CloudPodsVersionManager._prepare_archives_from_pre_signed_urls(F);G=C[1];H=C[2];extract_meta_and_state_archives(meta_archives=G,state_archives=H,config_context=A.pods_api.config_context)
	def init(A):A.pods_api.init(pod_name=A.pod_name)
	def delete(A,remote):
		C=A.pods_api.config_context.cloud_pods_root_dir;B=os.path.join(C,A.pod_name)
		if os.path.isdir(B):rm_rf(B);return _A
		if remote:0
		return _B
	def _push_to_remote(A,url):
		C=get_auth_headers();B=safe_requests.post(url=url,headers=C);D='Failed to get presigned URLs to upload new version.. aborting'
		if not A._check_response(B,message=D):return
		E=json.loads(B.content);F=E.get(_E);A.pods_api.upload_version_and_product_space(presigned_urls=F)
	def push(A,comment=_C,services=_C):
		D=comment;A.pods_api.set_pod_context(A.pod_name);A._add_state_to_cloud_pods_store(extract_assets=_A,services=services);B:0;C=A.pods_api.get_head().version_number
		if A.pods_api.is_remotely_managed():
			E=get_auth_headers();F=A._get_max_version_for_pod_from_platform(pod_name=A.pod_name,auth_headers=E);B=C<F
			if B:A.fetch()
			A.pods_api.push(comment=D);G=A.create_platform_url(f"{A.pod_name}/data?version={C}");A._push_to_remote(url=G)
		else:H=A.pods_api.get_max_version_no();B=C<H;I=A.pods_api.push(comment=D);LOG.debug(f"Created new version: {I}")
		if B:A.inject(version=-1,reset_state=_A,merge=_B)
		return PodInfo()
	def push_overwrite(A,version,comment=_C):
		B=version;A.pods_api.set_pod_context(pod_name=A.pod_name)
		if B>A.pods_api.get_max_version_no():LOG.warning(f"Version {B} does not exist");return _B
		A._add_state_to_cloud_pods_store();A.pods_api.push_overwrite(version=B,comment=comment)
		if A.pods_api.is_remotely_managed():C=CloudPodsVersionManager.create_platform_url(f"push-overwrite/{A.pod_name}?version={B}");A._push_to_remote(url=C)
		return _A
	def fetch(A):
		E=get_auth_headers();B=0
		if A.pod_name in A.pods_api.list_locally_available_pods(show_remote_or_local=_B):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_max_version_no()
		else:A.pods_api.init(pod_name=A.pod_name)
		C=CloudPodsVersionManager._get_max_version_for_pod_from_platform(A.pod_name,E)
		if not C:return
		if C==B:LOG.info('No new version available remotely. Nothing to fetch');return
		D=range(B+1,C+1);D=','.join(map(lambda ver:str(ver),D));A._fetch_versions(auth_headers=E,required_versions=D)
	def commit(A,message=_C):A.pods_api.set_pod_context(A.pod_name);A._add_state_to_cloud_pods_store();B=A.pods_api.commit(message=message);LOG.debug('Completed revision: %s',B.hash_ref)
	def _download_version_product(D,version,retain=_B):
		A=version;E=D._get_presigned_url_for_version_product(version=A);F=E.get(_I);G=E.get(_J);B=new_tmp_file();C=new_tmp_file();download(F,B);download(G,C)
		if retain:from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives as H;H(meta_archives={A:C},state_archives={A:B},config_context=D.pods_api.config_context)
		return{'metadata_archive':C,_K:B}
	def _get_presigned_url_for_version_product(A,version):
		B=version;C=A.create_platform_url(f"{A.pod_name}/version/product")
		if B!=-1:C+=f"?version={B}"
		E=get_auth_headers();D=safe_requests.get(C,headers=E);F=f"Failed to retrieve presigned URL from remote for version {B} of pod {A.pod_name}"
		if not A._check_response(D,message=F):return
		return json.loads(D.content)
	def _inject_from_remote(B,version,retain=_B):
		C=version;from localstack_ext.bootstrap.pods.utils.remote_utils import extract_meta_and_state_archives as F;D=B._get_presigned_url_for_version_product(version=C);G=D.get(_I);A=new_tmp_file();download(G,A);B.deploy_pod_into_instance(pod_path=A)
		if not retain:rm_rf(A);return _A
		H=D.get(_J);E=new_tmp_file();download(H,E);F(meta_archives={C:E},state_archives={C:A},config_context=B.pods_api.config_context);return _A
	@staticmethod
	def deploy_pod_into_instance(pod_path):
		A=pod_path
		if not A:raise Exception(f"Unable to restore pod state via local pods management API: Pod Path {A} not valid")
		D=_B
		if os.path.isdir(A):
			B=new_tmp_dir()
			for E in PERSISTED_FOLDERS:
				F=os.path.join(A,E)
				if not os.path.exists(F):continue
				H=os.path.join(B,E);cp_r(F,H,rm_dest_on_conflict=_A)
			A=create_zip_file(B);rm_rf(B);D=_A
		I=load_file(A,mode='rb');G=get_pods_endpoint();C=requests.post(G,data=I)
		if C.status_code>=400:raise Exception('Unable to restore pod state via local pods management API %s (code %s): %s'%(G,C.status_code,C.content))
		if D:rm_rf(A)
		else:return A
	def inject(A,version,reset_state,merge):
		B=version
		if not A.pods_api.config_context.pod_exists_locally(A.pod_name):LOG.debug(f"Pod {A.pod_name} does not exist locally. Requesting state from remote..");C=A._download_version_product(version=B).get(_K)
		else:
			A.pods_api.set_pod_context(A.pod_name)
			if B==-1:B=A.pods_api.get_max_version_no(require_state_archive=_A)
			C=A.pods_api.config_context.get_version_state_archive(B)
			if not C and A.pods_api.is_remotely_managed():
				LOG.debug('Fetching requested archive from remote..');D=A._download_version_product(version=B,retain=_A)
				if not D:return _B
				C=A.pods_api.commit_metamodel_utils.get_version_state_archive(B)
		if reset_state:reset_local_state(reset_data_dir=_A)
		if merge:C=merge_local_state_with(C)
		A.deploy_pod_into_instance(C);return _A
	def get_version_summaries(A):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_version_summaries();return B
	def version_metamodel(A,version):
		B=version;A.pods_api.set_pod_context(A.pod_name)
		if B==-1:B=A.pods_api.get_max_version_no(require_state_archive=_A)
		D=A.pods_api.get_version_by_number(B);E=D.get_latest_revision(with_commit=_A);C=A.pods_api.commit_metamodel_utils.reconstruct_metamodel(version=D,revision=E)
		if not C and A.pods_api.is_remotely_managed():A._download_version_product(version=B,retain=_A);C=A.pods_api.commit_metamodel_utils.create_metamodel_from_state_files(version=B)
		return C
	def set_version(A,version,inject_version_state,reset_state,commit_before):
		B=version;A.pods_api.set_pod_context(A.pod_name);C=A.pods_api.set_active_version(version_no=B,commit_before=commit_before)
		if not C:LOG.warning(f"Could not find version {B}")
		if inject_version_state:A.inject(version=B,reset_state=reset_state,merge=_B)
		return C
	def list_version_commits(A,version):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.list_version_commits(version_no=version);C=[A.get_summary()for A in B];return C
	def get_commit_diff(A,version,commit):A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.commit_metamodel_utils.get_commit_diff(version_no=version,commit_no=commit);return B
	def register_remote(A,pod_name,ci_pod=_B):
		F='storage_uuid';A.pods_api.set_pod_context(A.pod_name);B=A.pods_api.get_max_version_no(require_state_archive=_A)
		if B==0:A.pods_api.push('Initial Version');B=1
		G=get_auth_headers();H=A.create_platform_url(A.pod_name);C={_D:A.pod_name,'max_ver':B,_G:ci_pod};C=json.dumps(C);E=safe_requests.put(H,C,headers=G);I=f"Failed to register pod {A.pod_name}: <content>"
		if not A._check_response(E,message=I):return _B
		D=json.loads(E.content);J={F:D.get(F),'qualifying_name':D.get(_D)};K=D.get(_E);A.pods_api.upload_version_and_product_space(presigned_urls=K);remote_utils.register_remote(remote_info=J,config_context=A.pods_api.config_context);return _A
	def rename_pod(A,current_pod_name,new_pod_name):
		C=current_pod_name;B=new_pod_name;A.pods_api.set_pod_context(C)
		if B in A.pods_api.list_locally_available_pods():LOG.warning(f"{B} already exists locally");return _B
		if A.pods_api.is_remotely_managed():
			E=get_auth_headers();F=A.create_platform_url(f"{C}/rename");D={'new_pod_name':B};D=json.dumps(D);G=safe_requests.put(F,D,headers=E);H=f"Failed to rename {C} to {B}: <content>"
			if not A._check_response(G,message=H):return _B
		A.pods_api.rename_pod(B);return _A
	def list_pods(A,fetch_remote):
		C=A.pods_api.list_locally_available_pods()
		if fetch_remote:
			E=get_auth_headers();F=A.create_platform_url('');D=safe_requests.get(F,headers=E);A._check_response(D,message='Error fetching list of pods from API (status <status_code>)',raise_error=_A);G=json.loads(D.content)
			for B in G or[]:H=B.get(_D)if isinstance(B,dict)else B;C.add(f"remote/{H}")
		return C
	@classmethod
	def _check_response(C,response,message,raise_error=_B):
		B=response;A=message
		if B.ok:return _A
		if B.status_code in[401,403]:raise Exception('Access denied - please log in first.')
		A=A.replace('<content>',to_str(B.content));A=A.replace('<status_code>',str(B.status_code))
		if raise_error:raise Exception(A)
		LOG.warning(A);return _B
	@staticmethod
	def create_platform_url(path):A=path;B=f"{constants.API_ENDPOINT}/cloudpods";A=A if not A or A.startswith('/')else f"/{A}";return f"{B}{A}"
class PodConfigManagerMeta(type):
	def __getattr__(C,attr):
		def A(*D,**E):
			A=_C
			for F in C.CHAIN:
				try:
					B=getattr(F,attr)(*(D),**E)
					if B:
						if not A:A=B
						elif isinstance(B,list)and isinstance(A,list):A.extend(B)
				except Exception:
					if LOG.isEnabledFor(logging.DEBUG):LOG.exception('error during PodConfigManager call chain')
			if A is not _C:return A
			raise Exception('Unable to run operation "%s" for local or remote configuration'%attr)
		return A
class PodConfigManager(metaclass=PodConfigManagerMeta):
	CHAIN=[]
	@classmethod
	def pod_config(D,pod_name):
		A=pod_name;C=PodConfigManager.list_pods();B=[B for B in C if B[_D]==A]
		if not B:raise Exception('Unable to find config for pod named "%s"'%A)
		return B[0]
def get_pods_manager(pods_name):return CloudPodsVersionManager(pod_name=pods_name)
def init_cloudpods(pod_name,**B):A=get_pods_manager(pods_name=pod_name);A.init()
def delete_pod(pod_name,remote):A=get_pods_manager(pods_name=pod_name);B=A.delete(remote=remote);return B
def register_remote(pod_name,pre_config,**D):A=pod_name;B=get_pods_manager(pods_name=A);C=B.register_remote(pod_name=A,ci_pod=pre_config.get(_G,_B));return C
def rename_pod(current_pod_name,new_pod_name,**D):A=new_pod_name;B=get_pods_manager(pods_name=A);C=B.rename_pod(current_pod_name=current_pod_name,new_pod_name=A);return C
def list_pods(remote,**C):A=get_pods_manager(pods_name='');B=A.list_pods(fetch_remote=remote);return B
def commit_state(pod_name,message=_C,**C):
	B=pod_name;A=get_pods_manager(pods_name=B)
	if not A.pods_api.config_context.is_initialized():A.init()
	A.pods_api.set_pod_context(pod_name=B);A.commit(message=message)
def inject_state(pod_name,version,reset_state,merge,**C):A=get_pods_manager(pods_name=pod_name);B=A.inject(version=version,reset_state=reset_state,merge=merge);return B
def get_version_summaries(pod_name):B=get_pods_manager(pods_name=pod_name);A=B.get_version_summaries();A=A[::-1];return A
def get_version_metamodel(version,pod_name,**C):A=get_pods_manager(pods_name=pod_name);B=A.version_metamodel(version=version);return B
def set_version(version,inject_version_state,reset_state,commit_before,pod_name,**C):A=get_pods_manager(pods_name=pod_name);B=A.set_version(version=version,inject_version_state=inject_version_state,reset_state=reset_state,commit_before=commit_before);return B
def list_version_commits(version,pod_name):A=get_pods_manager(pods_name=pod_name);B=A.list_version_commits(version=version);return B
def get_commit_diff(version,commit,pod_name):A=get_pods_manager(pods_name=pod_name);B=A.get_commit_diff(version=version,commit=commit);return B
def push_overwrite(version,pod_name,comment):A=get_pods_manager(pods_name=pod_name);A.push_overwrite(version=version,comment=comment)
def push_state(pod_name,pre_config=_C,comment=_C,register=_B,services=_C,**F):
	C=services;B=pod_name
	if C is _C:C=[]
	A=get_pods_manager(pods_name=B);A.pods_api.set_pod_context(pod_name=B)
	if not A.pods_api.config_context.is_initialized():A.init()
	A.push(comment=comment,services=C);D=_A
	if register:E=(pre_config or{}).get(_G,_B);D&=A.register_remote(pod_name=B,ci_pod=E)
	return D
def get_pods_endpoint():A=config.get_edge_url();return f"{A}{API_PATH_PODS}"
def fetch_state(pod_name,**C):
	A=pod_name
	if not A:raise Exception('Need to specify a pod name')
	B=get_pods_manager(pods_name=A);B.fetch();print('Done.')
def reset_local_state(reset_data_dir=_B,exclude_from_reset=_C):
	C=exclude_from_reset;A=f"{get_pods_endpoint()}/state"
	if reset_data_dir:A+='/datadir'
	if C:A+=f"?exclude={','.join(C)}"
	print('Sending request to reset the service states in local instance ...');B=requests.delete(A)
	if B.status_code>=400:raise Exception('Unable to reset service state via local management API %s (code %s): %s'%(A,B.status_code,B.content))
	print('Done.')
def merge_local_state_with(state_archive_path):from localstack_ext.utils.cloud_pods import handle_get_state_request_in_memory as C;D=C();A=ServiceStateMarshaller.unmarshall(D.data);E=ServiceStateMarshaller.unmarshall_zip_archive(state_archive_path);A.merge(E,_C);B=new_tmp_file();ServiceStateMarshaller.marshall_zip_archive(B,A);return B
def save_pods_config(options):A=get_pods_manager('');A.pods_api.config_context.save_pods_config(options=options)
def get_pod_name_from_config():A=get_pods_manager('');return A.pods_api.config_context.get_pod_name_from_config()
def is_initialized(pod_name):A=get_pods_manager(pods_name=pod_name);return A.pods_api.config_context.is_initialized()
def get_data_dir_from_container():
	try:
		C=DOCKER_CLIENT.inspect_container(config.MAIN_CONTAINER_NAME);D=C.get('Mounts');E=C.get('Config',{}).get('Env',[]);A=[A for A in E if A.startswith('DATA_DIR=')][0].partition('=')[2]
		try:B=[B for B in D if B['Destination']==A][0]['Source'];B=re.sub('^(/host_mnt)?','',B);A=B
		except Exception:LOG.debug(f"No docker volume for data dir '{A}' detected")
		return A
	except Exception:LOG.warning('Unable to determine DATA_DIR from LocalStack Docker container - please make sure $MAIN_CONTAINER_NAME is configured properly')
def get_persisted_resource_names(data_dir):
	D=data_dir;B=[]
	with os.scandir(D)as C:
		for A in C:
			if A.is_dir()and A.name!=_F:B.append(A.name)
	with os.scandir(os.path.join(D,_F))as C:
		for A in C:
			if A.is_dir()and len(os.listdir(A.path))>0:B.append(A.name)
	LOG.debug(f"Detected state files for the following APIs: {B}");return B
PODS_NAMESPACE_DELIM='-'