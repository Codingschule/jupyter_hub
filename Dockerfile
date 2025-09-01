ARG JUPYTERHUB_VERSION=5.1.0
FROM jupyterhub/jupyterhub:${JUPYTERHUB_VERSION}  
#Pin Hub base image to the same version as .env

ARG JUPYTERLAB_VERSION=4.2.5
ARG NATIVEAUTH_VERSION=1.3.0
ARG DOCKERSPAWNER_VERSION=14.0.0
ARG PG_PKG="psycopg[binary]==3.1.18"

# Install Hub-side Python packages (Lab, Authenticator, Spawner, psycopg).
RUN python3 -m pip install --no-cache-dir --upgrade pip \
 && python3 -m pip install --no-cache-dir \
      jupyterlab==${JUPYTERLAB_VERSION} \
      jupyterhub-nativeauthenticator==${NATIVEAUTH_VERSION} \
      dockerspawner==${DOCKERSPAWNER_VERSION} \
      "${PG_PKG}" \
  && python3 -m pip check \
 && rm -rf /root/.cache/pip ~/.cache/pip /tmp/*
 # Clean pip caches and temp files to reduce final image size.

# Ship the small helper that generates config.js for your static editor.
COPY jupyterhub_config/gen-edit-config.sh /usr/local/bin/gen-edit-config.sh
# Make the generator script executable at runtime.
RUN chmod +x /usr/local/bin/gen-edit-config.sh