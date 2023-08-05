""" SSH Secret Type """
from dataclasses import dataclass
from pathlib import Path

from kubernetes import client

from mcli.objects.secrets import MCLIMountedSecret
from mcli.serverside.job.mcli_k8s_job import MCLIK8sJob

COMPOSER_SFTP_KEY_ENV = 'COMPOSER_SFTP_KEY_FILE'


@dataclass
class MCLISSHSecret(MCLIMountedSecret):
    """Secret class for ssh private keys that will be mounted to run pods as a file
    """

    def add_to_job(self, kubernetes_job: MCLIK8sJob, permissions: int = 256) -> bool:
        return super().add_to_job(kubernetes_job=kubernetes_job, permissions=permissions)


@dataclass
class MCLIGitSSHSecret(MCLISSHSecret):
    """Secret class for git-related ssh private keys

    The ssh key will be mounted to a file and the environment variable GIT_SSH_COMMAND
    will be pointed toward it
    """

    def add_to_job(self, kubernetes_job: MCLIK8sJob, permissions: int = 256) -> bool:
        super().add_to_job(kubernetes_job=kubernetes_job, permissions=permissions)
        assert self.mount_path is not None
        git_ssh_command_var = client.V1EnvVar(
            name='GIT_SSH_COMMAND',
            value=f'ssh -o StrictHostKeyChecking=no -i {Path(self.mount_path) / "secret"}',
        )
        kubernetes_job.add_env_var(git_ssh_command_var)
        return True


@dataclass
class MCLISFTPSecret(MCLISSHSecret):
    """Secret class for sftp-related ssh private keys

    The sftp ssh key will be mounted to a file and the environment variable COMPOSER_SFTP_KEY_FILE
    will be pointed toward it
    """

    def add_to_job(self, kubernetes_job: MCLIK8sJob, permissions: int = 256) -> bool:
        super().add_to_job(kubernetes_job=kubernetes_job, permissions=permissions)
        assert self.mount_path is not None
        kubernetes_job.add_env_var(client.V1EnvVar(
            name=COMPOSER_SFTP_KEY_ENV,
            value=self.mount_path,
        ))
        return True
