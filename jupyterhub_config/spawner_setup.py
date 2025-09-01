import os
from dockerspawner import DockerSpawner  


def apply_spawner(c):
    c.JupyterHub.spawner_class = DockerSpawner

    # Single source of truth for the notebook image
    c.DockerSpawner.image = os.environ.get("DOCKER_JUPYTER_IMAGE", "jupyter/datascience-notebook:latest")
    c.DockerSpawner.cmd = ["start-singleuser.py"]
    # Ensure spawned containers join the internal Hub network.
    c.DockerSpawner.network_name = os.environ['JUPYTERHUB_NETWORK']
    c.DockerSpawner.use_internal_ip = True
    c.DockerSpawner.remove = False
    c.DockerSpawner.name_template = 'jupyter-{username}'
    c.Spawner.args = ["--ServerApp.root_dir=/home/jovyan/work"]

    # Force Jupyter server root to user’s working directory (clean workspace).
    c.Spawner.notebook_dir = "/home/jovyan/work"
    
    
    # for the users security: ensures isolated user volumes, no shared home dirs
    c.DockerSpawner.volumes = {'JHub-{username}': '/home/jovyan/work'}
    
    # Increase shared memory for heavy notebooks   
    c.DockerSpawner.extra_host_config = {"shm_size": "1g"}
    
    c.DockerSpawner.environment = {
        'CHOWN_HOME': 'yes',
        'CHOWN_HOME_OPTS': '-R',
        'NB_UID': '1000',   
        'NB_GID': '100',    
    }
    # Basic resource limits
    c.Spawner.mem_limit="4G"
    
    c.Spawner.cpu_limit=2

    c.Spawner.default_url = '/lab'    

    # Generous timeouts for cold starts/pulls/builds
    c.Spawner.start_timeout = 600
    c.Spawner.http_timeout = 600
    
    c.DockerSpawner.debug = False