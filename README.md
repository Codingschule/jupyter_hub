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
# =============================================================================
# JUPYTERHUB KONFIGURATION
# =============================================================================

# --- Grundlegende JupyterHub-Einstellungen ---
JUPYTERHUB_VERSION=5.1.0                     # Festgelegte Hub-Version, um unerwartete Änderungen zu vermeiden
JUPYTERHUB_PORT=8111                         # Port, an dem der Hub öffentlich zugänglich ist
PYTHONPATH=/srv/jupyterhub                   # Python-Pfad für JupyterHub

# --- Docker-Konfiguration ---
DOCKER_JUPYTER_IMAGE=my-datascience-singleuser:5.1.0  # Standard Single-User Notebook Image für DockerSpawner
JUPYTERHUB_EXT_NETWORK=hub-public                     # Vorher erstelltes Docker-Netzwerk für öffentlichen Hub-Zugriff
JUPYTERHUB_NETWORK=hub-backend                        # Internes Docker-Netzwerk für Spawner und Services

# --- Datenbank-Konfiguration ---
POSTGRES_DB=jupyterhub                       # Datenbankname für Hub-Status
POSTGRES_USER=jupyteruser                    # Datenbankbenutzer für Hub-Verbindungen
POSTGRES_PASSWORD=userpassword               # Passwort für den DB-Benutzer
DB_HOST=postgres                             # Hostname des PostgreSQL-Dienstes
DB_PORT=5432                                 # PostgreSQL-Port im internen Netzwerk

# --- Benutzerverwaltung ---
JUPYTERHUB_AUTO_APPROVE=false                # Automatische Genehmigung von Anmeldungen deaktiviert
JUPYTERHUB_ADMIN_USERS=admin,techmanager     # Administratoren mit vollen Hub-Rechten
JUPYTERHUB_ALLOWED_USERS=admin,techmanager   # Beschränkung der Anmeldung auf diese E-Mails (plus Tools-Ergänzungen)
JUPYTERHUB_SUBADMIN_USERS=techmanager        # Benutzer mit "user-admin"-Rolle (ohne volle Admin-Rechte)

# --- Benutzersynchronisierung ---
USERS_FILE=/srv/jupyterhub/users.json        # Pfad für externe Benutzer/Gruppen
USERSYNC_INTERVAL=10                         # Sekunden zwischen Prüfungen auf users.json-Änderungen
USERSYNC_PRUNE=false                         # Benutzer, die nicht in users.json sind, nicht bei Sync entfernen

# --- Anmeldung und Registrierung ---
JUPYTERHUB_SIGNUP_BOOTSTRAP_FLAG=/srv/jupyterhub/.signup_bootstrap_done
JUPYTERHUB_OPEN_SIGNUP=false                 # Öffentliche Registrierung geschlossen (außer beim ersten Start)
EDIT_LOGIN_PASSWORD=pas12345                 # Client-seitiges Passwort für den statischen Editor-Zugang
EDIT_TARGET_URL=/hub/static/edit/editUser.html  # Zielseite für JSON-Editor nach Client-Login

# =============================================================================
# INHALTE UND KURSE
# =============================================================================

# --- New York Taxi Beispiel ---
COURSE_DIR=/home/jovyan/work/NewYorkTaxi     # Verzeichnis für den New York Taxi Kurs

# --- Git-Integration ---
NBGITPULLER_REPO=https://github.com/Codingschule/NewYorkTaxi.git
NBGITPULLER_BRANCH=main
NBGITPULLER_TARGET=workbooks

# --- Benutzereinstellungen ---
NB_USER=jovyan                               # Standard-Benutzername
NB_UID=1000                                  # Benutzer-ID
NB_GID=100                                   # Gruppen-ID

# =============================================================================
# RUNNER-KONFIGURATION
# =============================================================================

RUNNER_ENABLED=1                             # Runner aktiviert (1=ja, 0=nein)
RUNNER_WATCH_DIR=${COURSE_DIR}               # Zu überwachendes Verzeichnis
RUNNER_CONFIG=${COURSE_DIR}/runner.yml       # Konfigurationsdatei für den Runner
RUNNER_OUTDIR=/home/jovyan/work/.runner      # Ausgabeverzeichnis des Runners
RUNNER_TEMPLATE=python                       # Template-Typ für den Runner

# =============================================================================
# DATASETS-KONFIGURATION
# =============================================================================

DATASETS_DIR=/shared/data                    # Verzeichnis für Datasets
DATASETS_VOLUME=jupyter_hub_test_datasets-vol # Name des Docker-Volumes für Datasets
DATASETS_MOUNT_PATH=/shared/data             # Mountpunkt für Datasets im Container
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