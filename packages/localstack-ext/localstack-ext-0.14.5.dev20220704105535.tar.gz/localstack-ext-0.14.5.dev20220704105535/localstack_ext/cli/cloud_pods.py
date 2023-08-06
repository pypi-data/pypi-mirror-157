_M='--reset/--no-reset'
_L='--inject/--no-inject'
_K='Injects the state from a version into the application runtime'
_J='--remote'
_I='--message'
_H='--version'
_G='-v'
_F=False
_E='name'
_D='Name of the cloud pod'
_C='--name'
_B='-n'
_A=True
import json,sys,traceback
from typing import Any,List,Mapping,Tuple
import click
from click import Context
from localstack.cli import console
from localstack.utils.analytics.cli import publish_invocation
from localstack_ext.cli.tree_view import TreeRenderer
class PodsCmdHandler(click.Group):
	def invoke(self,ctx):
		try:return super(PodsCmdHandler,self).invoke(ctx)
		except Exception as exc:
			click.echo(f"Error: {exc}")
			if ctx.parent and ctx.parent.params.get('debug'):click.echo(traceback.format_exc())
			ctx.exit(1)
def required_if_not_cached(option_key):
	class PodConfigContext(click.Option):
		def handle_parse_result(self,ctx,opts,args):
			from localstack_ext.bootstrap import pods_client;is_present=self.name in opts
			if not is_present:
				config_cache=pods_client.get_pods_config();pod_name=config_cache.get(option_key)
				if pod_name is None:raise click.MissingParameter(f"Parameter `--{option_key}` unspecified. Call with `--{option_key}` or set the parameter with `set-context`")
				opts[self.name]=pod_name
			return super().handle_parse_result(ctx,opts,args)
	return PodConfigContext
def _cloud_pod_initialized(pod_name):
	from localstack_ext.bootstrap import pods_client
	if not pods_client.is_initialized(pod_name=pod_name):console.print(f"[red]Error:[/red] Could not find local CloudPods instance '{pod_name}'");return _F
	return _A
@click.group(name='pod',help='Manage the state of your instance via local Cloud Pods',cls=PodsCmdHandler)
def pod():
	from localstack_ext.bootstrap.licensing import is_logged_in
	if not is_logged_in():console.print('[red]Error:[/red] not logged in, please log in first');sys.exit(1)
@pod.command(name='set-context',help='Sets the context for all the pod commands')
@click.option(_B,_C,help='Name of the cloud pod to set in the context',required=_A)
@publish_invocation
def cmd_pod_set_context(name):from localstack_ext.bootstrap import pods_client;options=dict(locals());del options['pods_client'];pods_client.save_pods_config(options=options)
@pod.command(name='delete',help='Deletes the specified cloud pod. By default only locally')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@click.option('-r',_J,help='Whether the Pod should also be deleted remotely.',is_flag=_A,default=_F)
@publish_invocation
def cmd_pod_delete(name,remote):
	from localstack_ext.bootstrap import pods_client;result=pods_client.delete_pod(pod_name=name,remote=remote)
	if result:console.print(f"Successfully deleted {name}")
	else:console.print(f"[yellow]{name} not available locally[/yellow]")
@pod.command(name='rename',help='Renames the pod. If the pod is remotely registered, change is also propagated to remote')
@click.option(_B,_C,help='Current Name of the cloud pod',required=_A)
@click.option('-nn','--new-name',help='New name of the cloud pod',required=_A)
@publish_invocation
def cmd_pod_rename(name,new_name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.rename_pod(current_pod_name=name,new_pod_name=new_name)
	if result:console.print(f"Successfully renamed {name} to {new_name}")
	else:console.print(f"[red]Error:[/red] Failed to rename {name} to {new_name}")
@pod.command(name='commit',help='Commits the current expansion point and creates a new (empty) revision')
@click.option('-m',_I,help='Add a comment describing the revision')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_commit(message,name):from localstack_ext.bootstrap import pods_client;pods_client.commit_state(pod_name=name,message=message);console.print('Successfully committed the current state')
@pod.command(name='push',help='Creates a new version by using the state files in the current expansion point (latest commit)')
@click.option('--register/--no-register',default=_A,help='Registers a local Cloud Pod instance with platform')
@click.option('-m',_I,help='Add a comment describing the version')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@click.option('-s','--services',help='List of services to push in the pods. It pushes all, if not specified',multiple=_A,default=[])
@publish_invocation
def cmd_pod_push(message,name,register,services):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.push_state(pod_name=name,comment=message,register=register,services=services);console.print('Successfully pushed the current state')
	if register:
		if result:console.print(f"Successfully registered {name} with remote!")
		else:console.print(f"[red]Error:[/red] Pod with name {name} is already registered")
@pod.command(name='push-overwrite',help='Overwrites a version with the content from the latest commit of the currently selected version')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@click.option(_G,_H,type=int)
@click.option('-m',_I,required=_F)
@publish_invocation
def cmd_pod_push_overwrite(version,message,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.push_overwrite(version=version,pod_name=name,comment=message)
	if result:console.print('Successfully overwritten state of version ')
@pod.command(name='inject',help=_K)
@click.option('--merge',is_flag=_A,default=_F,help='For each service in the application state, its backend is merged with the backend specified by the given pod and version, or added if missing.')
@click.option(_G,_H,default='-1',type=int,help='Loads the state of the specified version - Most recent one by default')
@click.option('--reset',is_flag=_A,default=_F,help='Will reset the application state before injecting')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_inject(merge,version,reset,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.inject_state(pod_name=name,version=version,reset_state=reset,merge=merge)
	if result:console.print('[green]Successfully Injected Pod State[/green]')
	else:console.print('[red]Failed to Inject Pod State[/red]')
@click.option(_L,default=_A,help='Whether the latest version of the pulled pod should be injected')
@click.option(_M,default=_A,help='Whether the current application state should be reset after the pod has been pulled')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@click.option('--lazy/--eager',default=_A,help='Will only fetch references to existing versions, i.e. version state is only downloaded when required')
@pod.command(name='pull',help=_K)
@publish_invocation
def cmd_pod_pull(name,inject,reset,lazy):from localstack_ext.bootstrap import pods_client;pods_client.pull_state(pod_name=name,inject_version_state=inject,reset_state_before=reset,lazy=lazy)
@pod.command(name='list',help='Lists all pods and indicates which pods exist locally and, by default, which ones are managed remotely')
@click.option(_J,'-r',is_flag=_A,default=_F)
@publish_invocation
def cmd_pod_list_pods(remote):
	from localstack_ext.bootstrap import pods_client;pods=pods_client.list_pods(remote=remote)
	if not pods:console.print(f"[yellow]No pods available {'locally'if not remote else''}[/yellow]")
	else:console.print('\n'.join(pods))
@pod.command(name='versions',help='Lists all available version numbers')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_versions(name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	version_list=pods_client.get_version_summaries(pod_name=name);result='\n'.join(version_list);console.print(result)
@pod.command(name='metamodel',help='Displays the content metamodel as json')
@click.option(_G,_H,type=int,default=-1,help='Latest version by default')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_version_metamodel(version,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	metamodel=pods_client.get_version_metamodel(version=version,pod_name=name)
	if metamodel:console.print_json(json.dumps(metamodel))
	else:console.print(f"[red]Could not find metamodel for pod {name} with version {version}[/red]")
@pod.command(name='set-version',help='Set HEAD to a specific version')
@click.option(_G,_H,required=_A,type=int,help='The version the state should be set to')
@click.option(_L,default=_A,help='Whether the state should be directly injected into the application runtime after changing version')
@click.option(_M,default=_A,help='Whether the current application state should be reset before changing version')
@click.option('--commit-before',is_flag=_F,help='Whether the current application state should be committed to the currently selected version before changing version')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_set_version(version,inject,reset,commit_before,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	pods_client.set_version(version=version,inject_version_state=inject,reset_state=reset,commit_before=commit_before,pod_name=name)
@pod.command(name='commits',help='Shows the commit history of a version')
@click.option(_H,_G,default=-1)
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_commits(version,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	commits=pods_client.list_version_commits(version=version,pod_name=name);result='\n'.join(commits);console.print(result)
@pod.command(name='commit-diff',help='Shows the changes made by a commit')
@click.option(_H,_G,required=_A)
@click.option('--commit','-c',required=_A)
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@publish_invocation
def cmd_pod_commit_diff(version,commit,name):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	commit_diff=pods_client.get_commit_diff(version=version,commit=commit,pod_name=name)
	if commit_diff:console.print_json(json.dumps(commit_diff))
	else:console.print(f"[red]Error:[/red] Commit {commit} not found for version {version}")
@pod.command(name='inspect',help='Inspect the contents of a pod')
@click.option(_B,_C,help=_D,cls=required_if_not_cached(_E))
@click.option('-f','--format',help='Format (curses, rich, json)',default='curses')
@publish_invocation
def cmd_pod_inspect(name,format):
	from localstack_ext.bootstrap import pods_client
	if not _cloud_pod_initialized(pod_name=name):return
	result=pods_client.get_version_metamodel(pod_name=name,version=-1);skipped_services=['cloudwatch']
	for (account,details) in result.items():result[account]={k:v for(k,v)in details.items()if k not in skipped_services}
	TreeRenderer.get(format).render_tree(result)