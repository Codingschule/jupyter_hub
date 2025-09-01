# JupyterHub with DockerSpawner and PostgreSQL

[![JupyterHub](https://img.shields.io/badge/Powered%20by-JupyterHub-orange.svg)](https://jupyter.org/hub)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://www.postgresql.org/)

This project provides a containerized JupyterHub 5.1.0 environment for multiple users.
It uses DockerSpawner to run each user in an isolated container, PostgreSQL as Hub database, and a JSON-based sync service for managing users and groups.

## 🚀 Key Features

- **Isolated Environments**: Each user gets their own Docker container, ensuring security and reproducible environments
- **Persistent Storage**: User notebooks and data are stored in named Docker volumes, persisting even after a container is stopped or removed
- **Centralized Authentication**: Uses `NativeAuthenticator` with auto-approval for users listed in users.json.
- **Scalable**: This setup provides a solid foundation for running JupyterHub for small to medium-sized teams
- **DockerSpawner**: Launches a dedicated container per user (my-datascience-singleuser:5.1.0)
- **PostgreSQL backend**: Stores Hub and user metadata
- **NativeAuthenticator**: integrated login, approval flow, and roles (admin / subadmin / allowed)
- **JSON-based user & Group Sync**: external users.json managed by usersync service
- **Custom Web UI**: lightweight HTML tool for editing users.json with password-protected access
- **Persistent Volumes**: each user mapped to its own named Docker volume "JHub-{username}"
- **Resource Limits**: single-user containers capped at 2 CPU and 4 GB RAM
- Ready for local LAN or single-server deployment

## 📋 Prerequisites

- Docker
- Docker Compose

## 🛠️ Setup

### 1. Configure Environment Variables

1. Copy the `.env.dummy` file to a new file named `.env`:
```shell script
cp .env.dummy .env
```

2. Edit the `.env` file and adjust the following values:
```
JUPYTERHUB_VERSION=5.1.0
JUPYTERHUB_PORT=8000                           # Hub external port
DOCKER_JUPYTER_IMAGE=my-datascience-singleuser:5.1.0  # Single-user image tag

JUPYTERHUB_NETWORK=hub-backend                 # Docker network name used by compose

POSTGRES_DB=jupyterhub                         # PostgreSQL database name
POSTGRES_USER=jupyteruser                      # PostgreSQL user
POSTGRES_PASSWORD=jupyterhubpass               # PostgreSQL password
DB_HOST=postgres                               # PostgreSQL service hostname (compose)
DB_PORT=5432                                   # PostgreSQL port

JUPYTERHUB_AUTO_APPROVE=false                  # Do not auto-approve unknown signups
JUPYTERHUB_OPEN_SIGNUP=false                   # Signup closed unless first boot flag

JUPYTERHUB_ADMIN_USERS=admin,techmanager       # Comma-separated list of admin users
JUPYTERHUB_ALLOWED_USERS=admin,techmanager     # Allowed users whitelist
JUPYTERHUB_SUBADMIN_USERS=techmanager          # Limited management role

USERS_FILE=/path.../users.json                 # Source file for user/group sync
USERSYNC_INTERVAL=5                            # Seconds between sync checks
USERSYNC_PRUNE=false                           # Do not remove extras during sync

EDIT_LOGIN_PASSWORD=somePassword
EDIT_TARGET_URL=/path/editUser.html
```

### 3. Build and Start Containers

```shell script
docker-compose up -d --build
```

## 🖥️ Usage

1. Access JupyterHub in your browser at `http://localhost:8000` (or the port configured in `.env`)
2. Log in with a username/password (must exist in users.json or be allowed).
3. Users listed in `JUPYTERHUB_ADMIN_USERS` will have administrator privileges
4. After logging in, you will be redirected to your personal Jupyter notebook server
5. The usersync service updates users, groups, and admins from users.json
6. To edit users/groups, open /hub/static/edit/login.html (password from .env).

## ⚙️ Configuration

- **Hub**: `jupyterhub_config.py` ties together auth, DB, spawner, and services.
- **Authentication**: `auth_setup.py` extends NativeAuthenticator with auto-approve for allowed users.
- **Users & Roles**: Defined in `users.json` and managed by `user_mgmt.py` + `usersync.py`.
- **Spawner**: `spawner_setup.py` configures DockerSpawner, volumes, limits, and default URL /lab.
- **Database**: PostgreSQL settings come from `.env`.
- **Static Editor**: static_edit/ provides a small UI (login.html + editUser.html) to edit users.json.

## 🔧 Troubleshooting

- **Containers won't start**: Check `JUPYTERHUB_NETWORK` network exist and if environment variables are set properly.
- **Auth issues**: Ensure usernames in `users.json` match login credentials.
- **Database connection problems**: Verify the DB settings in the `.env` file.
- **Static editor fails**: Ensure `EDIT_LOGIN_PASSWORD` is set and config.js is generated.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).