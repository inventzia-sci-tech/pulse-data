#!/usr/bin/env bash
set -e

# ----------------------------
# Configuration
# ----------------------------
ENV_PATH="/home/magrino_bini/env/pulse-py-3-11"   # <-- change this to your actual conda env path
AIRFLOW_HOME="$HOME/airflow"
AIRFLOW_VERSION="2.10.2"

# ----------------------------
# Helper function
# ----------------------------
activate_env() {
    if [[ -z "$CONDA_DEFAULT_ENV" || "$CONDA_DEFAULT_ENV" != *"pulse-py-3-10"* ]]; then
        echo "🔹 Activating conda environment: $ENV_PATH"
        # shellcheck disable=SC1091
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate "$ENV_PATH"
    else
        echo "✅ Conda environment already active: $CONDA_DEFAULT_ENV"
    fi
}

# ----------------------------
# Activate environment
# ----------------------------
activate_env

# ----------------------------
# Verify Airflow is installed
# ----------------------------
if ! command -v airflow &> /dev/null; then
    echo "❌ Airflow not found in the environment!"
    echo "Installing Apache Airflow..."
    pip install "apache-airflow[postgres]==${AIRFLOW_VERSION}"
fi

# ----------------------------
# Setup Airflow home
# ----------------------------
mkdir -p "$AIRFLOW_HOME"
export AIRFLOW_HOME="$AIRFLOW_HOME"
echo "Airflow home set to $AIRFLOW_HOME"

# ----------------------------
# Initialize Airflow DB
# ----------------------------
echo "Initializing Airflow metadata database..."
airflow db init

# ----------------------------
# Create admin user if not exists
# ----------------------------
echo "Creating admin user..."
airflow users create \
    --username admin \
    --firstname admin \
    --lastname user \
    --role Admin \
    --email magrino.bini@schlossbergco.com \
    --password admin || true

# ----------------------------
# Start Airflow services
# ----------------------------
echo "Starting Airflow webserver and scheduler..."
nohup airflow webserver --port 8080 > "$AIRFLOW_HOME/webserver.log" 2>&1 &
nohup airflow scheduler > "$AIRFLOW_HOME/scheduler.log" 2>&1 &

echo "✅ Airflow setup complete!"
echo "🌐 Access the web UI at: http://localhost:8080"
