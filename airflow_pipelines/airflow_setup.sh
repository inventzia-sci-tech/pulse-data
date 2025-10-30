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
# Verify system Graphviz installation
# ----------------------------
if ! command -v dot &> /dev/null; then
    echo "Installing Graphviz system package..."
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y graphviz
    # For other distros, adjust package manager (yum, pacman, etc.)
else
    echo "✅ Graphviz system package already installed"
fi

# ----------------------------
# Verify Airflow is installed
# ----------------------------
if ! command -v airflow_pipelines &> /dev/null; then
    echo "❌ Airflow not found in the environment!"
    echo "Installing Apache Airflow..."
    pip install "apache-airflow[postgres]==${AIRFLOW_VERSION}"
fi
pip install graphviz
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
airflow_pipelines db init

# ----------------------------
# Create admin user if not exists
# ----------------------------
echo "Creating admin user..."
airflow_pipelines users create \
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
# Start Airflow webserver if not running
if ! pgrep -f "airflow webserver" > /dev/null; then
    echo "Starting Airflow webserver..."
    nohup airflow_pipelines webserver --port 8080 > "$AIRFLOW_HOME/webserver.log" 2>&1 &
else
    echo "Airflow webserver is already running. Not restarting."
fi
# Start Airflow scheduler if not running
if ! pgrep -f "airflow scheduler" > /dev/null; then
    echo "Starting Airflow scheduler..."
    nohup airflow_pipelines scheduler > "$AIRFLOW_HOME/scheduler.log" 2>&1 &
else
    echo "Airflow scheduler is already running. Not restarting."
fi

echo "✅ Airflow setup complete!"
echo "🌐 Access the web UI at: http://localhost:8080"
