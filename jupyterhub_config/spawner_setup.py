import os
from dockerspawner import DockerSpawner  

COURSE_DIR = os.environ["COURSE_DIR"]
DATASETS_DIR = os.environ["DATASETS_DIR"]
DATASETS_VOLUME = os.environ["DATASETS_VOLUME"]          # jupyter_hub_test_datasets-vol
DATASETS_MOUNT_PATH = os.environ.get("DATASETS_MOUNT_PATH")


def apply_spawner(c):
    c.JupyterHub.spawner_class = DockerSpawner

    # Single source of truth for the notebook image
    c.DockerSpawner.image = os.environ["DOCKER_JUPYTER_IMAGE"]
    
    c.DockerSpawner.cmd = ["/usr/local/bin/start-singleuser.sh"]

    # Ensure spawned containers join the internal Hub network.
    c.DockerSpawner.network_name = os.environ['JUPYTERHUB_NETWORK']
    c.DockerSpawner.use_internal_ip = True
    c.DockerSpawner.name_template = 'jp-{username}'
    c.DockerSpawner.args = [f"--ServerApp.root_dir={COURSE_DIR}"]

    # Force Jupyter server root to user’s working directory (clean workspace).
    c.DockerSpawner.notebook_dir = COURSE_DIR
    
    
    # for the users security: ensures isolated user volumes & datasets, no shared home dirs
    c.DockerSpawner.volumes = {
        "jHub-{username}": {"bind": "/home/jovyan/work", "mode": "rw"},
        DATASETS_VOLUME: {"bind": DATASETS_MOUNT_PATH, "mode": "ro"},
    }

    
    # Increase shared memory for heavy notebooks   
    c.DockerSpawner.extra_host_config = {
        "shm_size": "4g",
        "dns": ["1.1.1.1", "8.8.8.8"]  
    }
    # Run notebook containers as root to avoid permission issues with volume mounts
    c.DockerSpawner.extra_create_kwargs = {
    "user": "root"
}
    c.DockerSpawner.environment = {
        'CHOWN_HOME': 'yes',
        'CHOWN_HOME_OPTS': '-R',
        'NB_UID': '1000',   
        'NB_GID': '100',    
        'NBGITPULLER_REPO': os.environ["NBGITPULLER_REPO"],
        'NBGITPULLER_BRANCH': os.environ["NBGITPULLER_BRANCH"],
        'NBGITPULLER_TARGET': os.environ["NBGITPULLER_TARGET"],
        'RUNNER_ENABLED': os.environ["RUNNER_ENABLED"],
        'RUNNER_WATCH_DIR': os.environ["RUNNER_WATCH_DIR"],
        'RUNNER_CONFIG': os.environ["RUNNER_CONFIG"],
        'RUNNER_OUTDIR': os.environ["RUNNER_OUTDIR"],
        'COURSE_DIR': os.environ["COURSE_DIR"],
    }
    # Basic resource limits
    c.DockerSpawner.mem_limit="8G"
    
    c.DockerSpawner.cpu_limit=2

    c.Spawner.default_url = '/lab'    

    # Generous timeouts for cold starts/pulls/builds
    c.Spawner.start_timeout = 600
    c.Spawner.http_timeout = 600
    
    c.DockerSpawner.debug = False
    c.DockerSpawner.remove = True
