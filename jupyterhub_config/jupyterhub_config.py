# type: ignore
import os

from traitlets.config import Config
from user_mgmt import configure_users_and_roles
from hub_setup import get_db_env
from auth_setup import apply_auth
from spawner_setup import apply_spawner

c = get_config()  # type: ignore

users_file = os.environ["USERS_FILE"]
sync_interval = int(os.environ["USERSYNC_INTERVAL"])
prune = os.environ["USERSYNC_PRUNE"]

# Run a managed Hub service that reconciles users/groups from users.json
c.JupyterHub.services = [
    {
        "name": "usersync",
        "admin": True,  
        "command": ["python", "/srv/jupyterhub/usersync.py"],
        "environment": {
            "USERS_FILE": users_file,
            "USERSYNC_INTERVAL": str(sync_interval),
            "USERSYNC_PRUNE": prune,
        },
    }
]

apply_auth(c, users_file=users_file)

# ------------------------
# URLs Hub
# ------------------------
c.JupyterHub.bind_url = "http://:8000"
c.JupyterHub.hub_bind_url = "http://0.0.0.0:8081"
c.JupyterHub.hub_connect_url = "http://jupyterhub:8081"


# ------------------------
# Config users & roles
# ------------------------
configure_users_and_roles(c)


# ------------------------
# DB configuration
# ------------------------
db_name, db_host, db_port, db_user, db_pass = get_db_env()
c.JupyterHub.db_url = f'postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'


# ------------------------
# Spawner configuration
# ------------------------
apply_spawner(c)

c.JupyterHub.log_level = "INFO"

# for the users security: keep secret outside git repo, never expose this file
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/secret/jupyterhub_cookie_secret"

# Adjusts UI timeout threshold for slow container spawns.
c.JupyterHub.tornado_settings = {
    "slow_spawn_timeout": 60,
}

datasets_volume = os.environ.get("DATASETS_VOLUME", "jupyter_hub_test_datasets-vol")
datasets_mount  = os.environ.get("DATASETS_MOUNT_PATH", "/shared/data")
COURSE_DIR      = os.environ.get("COURSE_DIR", "/home/jovyan/work/NewYorkTaxi")

current_vols = getattr(c.DockerSpawner, "volumes", {}) or {}
current_vols.update({
    datasets_volume: {"bind": datasets_mount, "mode": "ro"},
})
c.DockerSpawner.volumes = current_vols

async def _post_spawn_hook(spawner, auth_state):
    cmd = f"bash -lc 'mkdir -p {COURSE_DIR} && ln -sfn {datasets_mount} {COURSE_DIR}/data'"
    try:
        await spawner.run_command(cmd, timeout=20)
        spawner.log.info("Symlink de datasets creado correctamente.")
    except Exception as e:
        spawner.log.warning(f"No se pudo crear symlink de datasets: {e}")
