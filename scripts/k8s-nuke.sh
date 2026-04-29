#!/bin/bash
# k8s-nuke.sh: Delete all MathPuzzle resources from Kubernetes

NAMESPACE="mathpuzzle"

# Determine paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
K8S_DIR="$PROJECT_ROOT/k8s"

echo "☢️  Nuking MathPuzzle resources..."

# Delete using Kustomize (Prod overlay covers all base resources)
kubectl delete -k "$PROJECT_ROOT/k8s/overlays/prod" --ignore-not-found

# Also delete secrets specifically
kubectl delete -f "$K8S_DIR/secrets.yaml" --ignore-not-found 2>/dev/null

echo "✅ Nuke complete. Cluster is clean."
