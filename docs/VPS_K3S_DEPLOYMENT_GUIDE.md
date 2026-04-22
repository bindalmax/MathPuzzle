# VPS Deployment Guide: K3s on Hetzner

This guide outlines the process of deploying the MathPuzzle application to a single-node Kubernetes cluster using **K3s** on a budget-friendly VPS like **Hetzner**.

## 🏗️ Architecture Overview

- **Node**: 1x Hetzner Cloud VPS (e.g., CPX11 - 2 vCPU, 4GB RAM).
- **Orchestration**: K3s (Lightweight Kubernetes).
- **Ingress**: Traefik (Built-in K3s).
- **SSL**: Cert-Manager + Let's Encrypt.
- **Database**: PostgreSQL (StatefulSet/Deployment with PersistentVolume).
- **CI/CD**: GitHub Actions + GitHub Container Registry (GHCR).

---

## 🚀 Step 1: VPS Setup

1.  **Rent a VPS**: Choose Hetzner, DigitalOcean, or Oracle Cloud.
2.  **Connect via SSH**:
    ```bash
    ssh root@your-vps-ip
    ```
3.  **Install K3s**:
    ```bash
    curl -sfL https://get.k3s.io | sh -
    # Check status
    sudo kubectl get nodes
    ```

---

## 📦 Step 2: Infrastructure Components

### 1. Install Helm
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 2. Install Cert-Manager
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --set installCRDs=true
```

---

## 🛠️ Step 3: Deploy Application

Deploy resources in this **exact order** to avoid errors.

### 1. Create Namespace & Secrets
First, establish the environment:
```bash
# Create the namespace
kubectl apply -f k8s/namespace.yaml

# Copy and edit the secrets template
cp k8s/secrets.example.yaml k8s/secrets.yaml
# (Edit k8s/secrets.yaml with your actual passwords/keys)

# Apply secrets
kubectl apply -f k8s/secrets.yaml
```

### 2. Wait for Cert-Manager Readiness
Before applying the Issuer, ensure cert-manager is fully running:
```bash
kubectl get pods -n cert-manager
# Wait until all pods show "Running" (approx 30-60 seconds)
```

### 3. Deploy Infrastructure (DB & SSL Issuer)
Once cert-manager is ready:
```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy SSL Issuer (requires cert-manager)
kubectl apply -f k8s/issuer.yaml
```

### 4. Deploy Application & Ingress
```bash
# Update k8s/app.yaml with your GHCR image name
# Update k8s/ingress.yaml with your domain (or YOUR_IP.sslip.io)

kubectl apply -f k8s/app.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## 🧪 Local Testing with k3d

To test the Kubernetes setup on your local machine:

1.  **Install k3d**:
    ```bash
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    ```
2.  **Create Cluster**:
    ```bash
    k3d cluster create math-test -p "80:80@loadbalancer" -p "443:443@loadbalancer"
    ```
3.  **Deploy**:
    Follow the **exact sequence** in Step 3 above. For local testing, use `127.0.0.1.sslip.io` as your domain.


---

## 💰 Cost Comparison (per Month)

| Feature | AWS Managed | VPS (K3s) |
| :--- | :--- | :--- |
| **Control Plane** | $72.00 | **$0.00** |
| **Compute Node** | $30.00 | **$5.00** |
| **Database** | $15.00 | **$0.00** |
| **Load Balancer** | $16.00 | **$0.00** |
| **Total** | **~$133.00** | **~$5.00** |

---

## 🔧 Maintenance

- **Update App**: `kubectl rollout restart deployment/mathpuzzle-web -n mathpuzzle`.
- **Check Logs**: `kubectl logs -l app=mathpuzzle-web -n mathpuzzle`.
- **Check SSL**: `kubectl get certificate -n mathpuzzle`.
