#!/usr/bin/env bash
set -euo pipefail

# ========= basic =========
export PATH="/opt/conda/bin:$PATH"

# UID/GID for the notebook user 
NB_USER="${NB_USER}"
NB_UID="${NB_UID}"
NB_GID="${NB_GID}"

# Directory to be used as base for course material
BASEWORK="/home/${NB_USER}/work"
COURSE_DIR="${COURSE_DIR:-${BASEWORK}/NewYorkTaxi}"

mkdir -p "${BASEWORK}" "${BASEWORK}/.runner"

# fix-permissions is available in the jupyterhub/k8s images 
if command -v fix-permissions >/dev/null 2>&1; then
  chown -R "${NB_UID}:${NB_GID}" "/home/${NB_USER}" || true
  fix-permissions "/home/${NB_USER}" || true
else
  chown -R "${NB_UID}:${NB_GID}" "/home/${NB_USER}" || true
  find "/home/${NB_USER}" -type d -exec chmod 775 {} \; || true
  find "/home/${NB_USER}" -type f -exec chmod 664 {} \; || true
fi

# ========= 2) Gitpuller optional =========
NBGITPULLER_REPO="${NBGITPULLER_REPO:-}"
NBGITPULLER_BRANCH="${NBGITPULLER_BRANCH:-main}"
NBGITPULLER_TARGET="${NBGITPULLER_TARGET:-.}"
RUNNER_OUTDIR="${RUNNER_OUTDIR:-${BASEWORK}/.runner}"

# Create Folder for course and runner output 
mkdir -p "${COURSE_DIR}" "${RUNNER_OUTDIR}"
chown -R "${NB_UID}:${NB_GID}" "${COURSE_DIR}" "${RUNNER_OUTDIR}" || true


if [[ -n "${NBGITPULLER_REPO}" ]]; then
  su -s /bin/bash -c "
    set -e
    export PATH=/opt/conda/bin:\$PATH
    cd '${COURSE_DIR}'
    gitpuller '${NBGITPULLER_REPO}' '${NBGITPULLER_BRANCH}' '${NBGITPULLER_TARGET}' \
      > '${RUNNER_OUTDIR}/gitpuller.log' 2>&1 || true
  " "${NB_USER}"
fi


# ========= 2b) join shared data (optional) =========
if [[ -d "/shared/data" ]]; then
  ln -sfn /shared/data "${COURSE_DIR}/data"
  chown -h "${NB_UID}:${NB_GID}" "${COURSE_DIR}/data" || true
fi

# ========= 3) Runner (optional) =========
RUNNER_ENABLED="${RUNNER_ENABLED:-0}"
RUNNER_WATCH_DIR="${RUNNER_WATCH_DIR:-${COURSE_DIR}}"
RUNNER_CONFIG="${RUNNER_CONFIG:-${COURSE_DIR}/runner.yml}"
RUNNER_OUTDIR="${RUNNER_OUTDIR:-${BASEWORK}/.runner}"

if [[ "${RUNNER_ENABLED}" = "1" ]]; then
  export RUNNER_WATCH_DIR RUNNER_CONFIG RUNNER_OUTDIR
  mkdir -p "${RUNNER_OUTDIR}"
  chown -R "${NB_UID}:${NB_GID}" "${RUNNER_OUTDIR}" || true

  # Run in background as NB_USER
  su -s /bin/bash -c "export PATH=/opt/conda/bin:\$PATH; nohup python3 -u /usr/local/bin/jhub_runner.py > '${RUNNER_OUTDIR}/runner.log' 2>&1 &" "${NB_USER}" || true
fi


# ========= 4) link datasets  =========
DATASETS_MOUNT_PATH="${DATASETS_MOUNT_PATH:-/shared/data}"
COURSE_DIR="${COURSE_DIR:-/home/${NB_USER}/work/NewYorkTaxi}"

mkdir -p "${COURSE_DIR}"
if [ -d "${DATASETS_MOUNT_PATH}" ]; then
  ln -sfn "${DATASETS_MOUNT_PATH}" "${COURSE_DIR}/data"
fi

# Finally, launch the notebook server as NB_USER
exec su -s /bin/bash -c "export PATH=/opt/conda/bin:\$PATH; start-singleuser.py" "${NB_USER}"
