#!/bin/bash
# k8s-setup.sh: Create all MathPuzzle resources in correct sequence

NAMESPACE="mathpuzzle"

# Determine paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
K8S_DIR="$PROJECT_ROOT/k8s"

echo "🚀 Starting MathPuzzle Kubernetes Setup..."

# 1. Namespace
echo "📁 Creating namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"

# 2. Secrets
if [ ! -f "$K8S_DIR/secrets.yaml" ]; then
    echo "❌ Error: $K8S_DIR/secrets.yaml not found!"
    echo "Please create $K8S_DIR/secrets.yaml (copy from secrets.example.yaml) and edit it first."
    exit 1
fi
echo "🔐 Applying secrets..."
kubectl apply -f "$K8S_DIR/secrets.yaml"

# 3. Cert-Manager (Check if installed)
if ! kubectl get crd clusterissuers.cert-manager.io > /dev/null 2>&1; then
    echo "⚠️  Cert-Manager CRDs not found. Please install Cert-Manager first (see guide)."
    exit 1
fi

# 4. Wait for Cert-Manager pods to be ready
echo "⏳ Waiting for cert-manager to be ready..."
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=90s

# Determine environment (default to prod)
ENV=${1:-prod}
if [[ ! "$ENV" =~ ^(local|prod)$ ]]; then
    echo "❌ Error: Invalid environment '$ENV'. Use 'local' or 'prod'."
    exit 1
fi

# 5. Infrastructure & App
echo "🌐 Deploying MathPuzzle ($ENV)..."
kubectl apply -k "$PROJECT_ROOT/k8s/overlays/$ENV"

echo "✅ Setup complete! Check status with: kubectl get pods -n $NAMESPACE"
