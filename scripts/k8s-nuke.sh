#!/bin/bash
# k8s-nuke.sh: Delete all MathPuzzle resources from Kubernetes

NAMESPACE="mathpuzzle"

# Determine paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
K8S_DIR="$PROJECT_ROOT/k8s"

echo "☢️  Nuking MathPuzzle resources in namespace: $NAMESPACE..."

# Delete in reverse order of creation
kubectl delete ingress mathpuzzle-ingress -n $NAMESPACE --ignore-not-found
kubectl delete service mathpuzzle-service -n $NAMESPACE --ignore-not-found
kubectl delete deployment mathpuzzle-web -n $NAMESPACE --ignore-not-found

kubectl delete clusterissuer letsencrypt-prod --ignore-not-found
kubectl delete service postgres-service -n $NAMESPACE --ignore-not-found
kubectl delete deployment postgres -n $NAMESPACE --ignore-not-found

# Critical: Delete the PVC to ensure DB password can be reset on next run
echo "🧹 Deleting Persistent Volume Claim (this erases all DB data)..."
kubectl delete pvc postgres-pvc -n $NAMESPACE --ignore-not-found

# Also try to delete by file to catch any naming mismatches
kubectl delete -f "$K8S_DIR/secrets.yaml" --ignore-not-found 2>/dev/null
kubectl delete -f "$K8S_DIR/namespace.yaml" --ignore-not-found 2>/dev/null

echo "✅ Nuke complete. Cluster is clean."
