_A=None
import json,logging,os,zipfile
from typing import Dict,List,Union
from localstack import config as localstack_config
from localstack.utils.files import load_file
from localstack.utils.json import FileMappedDocument
from localstack_ext.bootstrap.auth import get_auth_cache
from localstack_ext.bootstrap.pods.constants import ASSETS_ROOT_DIR,CLOUD_PODS_DIR,COMMIT_FILE,COMPRESSION_FORMAT,DEFAULT_POD_DIR,DELTA_LOG_DIR,HEAD_FILE,KNOWN_VER_FILE,MAX_VER_FILE,META_ZIP,OBJ_STORE_DIR,PODS_CONFIG_FILE,REMOTE_FILE,STATE_ZIP,VER_LOG_FILE,VER_LOG_STRUCTURE,VERSION_SPACE_DIRS,VERSION_SPACE_FILES,VERSIONS_DIR
LOG=logging.getLogger(__name__)
class PodsConfigContext:
	def __init__(A,pods_root_dir=_A,pod_name=_A):A.cloud_pods_root_dir=pods_root_dir or A.get_pods_root_dir();A.pod_name=pod_name;A.user=_A
	@property
	def pod_root_dir(self):
		A=self
		if not A.pod_name:raise Exception('Unable to determine pod root dir as pod name is not configured')
		return os.path.join(A.cloud_pods_root_dir,A.pod_name)
	@classmethod
	def get_pod_config_dir(A,pod_name):return os.path.join(A.get_pods_root_dir(),pod_name)
	@classmethod
	def get_pods_root_dir(B):
		A=os.environ.get('POD_DIR')
		if not A:A=os.path.join(localstack_config.dirs.tmp,DEFAULT_POD_DIR)
		A=os.path.join(A,CLOUD_PODS_DIR);return A
	def get_pod_context(A):return os.path.basename(A.pod_root_dir)
	def get_context_user(A):return A.user
	def get_pod_root_dir(A):return A.pod_root_dir
	def get_head_path(A):return os.path.join(A.pod_root_dir,HEAD_FILE)
	def get_max_ver_path(A):return os.path.join(A.pod_root_dir,MAX_VER_FILE)
	def get_known_ver_path(A):return os.path.join(A.pod_root_dir,KNOWN_VER_FILE)
	def get_ver_log_path(A):return os.path.join(A.pod_root_dir,VER_LOG_FILE)
	def get_obj_store_path(A):return os.path.join(A.pod_root_dir,OBJ_STORE_DIR)
	def get_versions_path(A):return os.path.join(A.pod_root_dir,VERSIONS_DIR)
	def get_delta_log_path(A):return os.path.join(A.pod_root_dir,A.get_obj_store_path(),DELTA_LOG_DIR)
	def get_assets_root_path(A):return os.path.join(A.pod_root_dir,ASSETS_ROOT_DIR)
	def get_version_meta_archive_path(B,version,with_format=True):
		A=os.path.join(B.get_pod_root_dir(),META_ZIP.format(version_no=version))
		if not with_format:return A
		return f"{A}.{COMPRESSION_FORMAT}"
	def get_version_state_archive_path(B,version,with_format=True):
		A=os.path.join(B.get_pod_root_dir(),STATE_ZIP.format(version_no=version))
		if not with_format:return A
		return f"{A}.{COMPRESSION_FORMAT}"
	def update_ver_log(A,author,ver_no,rev_id,rev_no):
		with open(A.get_ver_log_path(),'a')as B:B.write(f"{VER_LOG_STRUCTURE.format(author=author,ver_no=ver_no,rev_rid_no=f'{rev_id}_{rev_no}')}\n")
	def is_initialized(A):return A.pod_root_dir and os.path.isdir(A.pod_root_dir)
	def get_head_version_number(A):return int(A._read_file(A.get_head_path()))
	def get_max_version_number(A):return int(A._read_file(A.get_max_ver_path()))
	def list_known_versions(A):B=A._read_file(A.get_known_ver_path()).split('\n');C=[int(A)for A in B if A.strip()];return C
	def _read_file(A,path):return load_file(path).strip()
	def get_obj_file_path(A,key):return os.path.join(A.get_obj_store_path(),key)
	def get_remote_info_path(A):return os.path.join(A.pod_root_dir,REMOTE_FILE)
	def is_remotely_managed(A,pod_name=_A):
		B=pod_name
		if B:return os.path.isfile(os.path.join(A.cloud_pods_root_dir,B,REMOTE_FILE))
		else:return os.path.isfile(A.get_remote_info_path())
	def set_pod_context(A,pod_name):
		B=pod_name;C=get_auth_cache();D=C.get('username','unknown');A.pod_name=B
		if not os.path.isdir(A.pod_root_dir):raise Exception(f"Unable to find local cloud pod named '{B}'")
		A.user=D
	def pod_exists_locally(A,pod_name):return os.path.isdir(os.path.join(A.cloud_pods_root_dir,pod_name))
	def rename_pod(A,new_pod_name):C=A.get_pod_root_dir();B=os.path.join(A.cloud_pods_root_dir,new_pod_name);os.rename(C,B);A.set_pod_context(B)
	def get_pod_name(A):return os.path.basename(A.get_pod_root_dir())
	def get_version_space_dir_paths(A):return[os.path.join(A.get_pod_root_dir(),B)for B in VERSION_SPACE_DIRS]
	def get_version_space_file_paths(A):return[os.path.join(A.get_pod_root_dir(),B)for B in VERSION_SPACE_FILES]
	def get_pods_config_cache(A,conf_cache_file=PODS_CONFIG_FILE):return FileMappedDocument(os.path.join(A.cloud_pods_root_dir,conf_cache_file),mode=384)
	def save_pods_config(B,options):A=B.get_pods_config_cache();A.update(options);A.save()
	def metamodel_file(B,revision,version=_A,absolute=False):
		C=version;A=B.commit_metamodel_file(revision)
		if absolute:
			if C is _A:raise Exception('Missing pod version when constructing revision metamodel file path')
			A=os.path.join(B.metadata_dir(C),A)
		return A
	@staticmethod
	def commit_metamodel_file(commit_no):return COMMIT_FILE.format(commit_no=commit_no)
	def metadata_dir(A,version):return os.path.join(A.get_pod_root_dir(),META_ZIP.format(version_no=version))
	def get_version_meta_archive(B,version):
		A=B.get_version_meta_archive_path(version)
		if os.path.isfile(A):return A
	def get_version_state_archive(B,version):
		A=B.get_version_state_archive_path(version)
		if os.path.isfile(A):return A
def zip_directories(zip_dest,directories):
	B=zip_dest;from localstack.utils.testutil import create_zip_file_python as C
	for A in directories:C(source_path=A,content_root=os.path.basename(A),base_dir=A,zip_file=B,mode='a')
	return B
def add_file_to_archive(archive,entry_name,content):
	with zipfile.ZipFile(archive,'a')as A:A.writestr(entry_name,content)
def read_file_from_archive(archive_path,file_name):
	B=file_name;A=archive_path
	try:
		with zipfile.ZipFile(A)as C:D=json.loads(C.read(B));return json.dumps(D)
	except Exception as E:LOG.debug(f"Could not find {B} in archive {A}: {E}")