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

You can deploy using the automated scripts or follow the manual sequence.

### Path A: Quick Setup (Recommended)
1.  **Configure Secrets**:
    ```bash
    cp k8s/secrets.example.yaml k8s/secrets.yaml
    # Edit k8s/secrets.yaml with your actual passwords
    ```
2.  **Run Setup Script**:
    ```bash
    ./scripts/k8s-setup.sh
    ```

### Path B: Manual Sequence
If you prefer to run commands manually, follow this **exact order**:

1.  **Namespace & Secrets**:
    ```bash
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/secrets.yaml
    ```
2.  **Wait for Cert-Manager Readiness**:
    ```bash
    kubectl get pods -n cert-manager
    # Wait until all pods show "Running"
    ```
3.  **Infrastructure & App**:
    ```bash
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/issuer.yaml
    kubectl apply -f k8s/app.yaml
    kubectl apply -f k8s/ingress.yaml
    ```

---

## 🚨 Troubleshooting: The Database Password Trap

If you see `FATAL: password authentication failed for user "mathuser"`, it is usually because the PostgreSQL volume was created with an old password. **Changing the Secret does NOT update the password in an existing volume.**

### How to Fix (The Nuke & Reset):
1.  **Nuke everything** (Warning: This deletes all DB data):
    ```bash
    ./scripts/k8s-nuke.sh
    ```
2.  **Correct your password** in `k8s/secrets.yaml`.
3.  **Setup again**:
    ```bash
    ./scripts/k8s-setup.sh
    ```


---

## 🧪 Local Testing with k3d

To test the Kubernetes setup on your local machine:

1.  **Install k3d**:
    ```bash
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    ```
2.  **Create Cluster with Port Forwarding**:
    You **must** map your local ports to the cluster load balancer:
    ```bash
    k3d cluster create math-test -p "80:80@loadbalancer" -p "443:443@loadbalancer"
    ```
3.  **Configure for Local Access**:
    - Update `k8s/ingress.yaml` to use host: `127.0.0.1.sslip.io`.
    - **Note**: For local testing, comment out the `traefik.ingress.kubernetes.io/router.entrypoints: websecure` annotation in `ingress.yaml` to avoid 403 errors if SSL is not set up locally.
4.  **Deploy**:
    Follow the **exact sequence** in Step 3 above. 
5.  **Access**:
    Open `http://127.0.0.1.sslip.io` in your browser.

### 🆘 Emergency Access (Bypass Ingress)
If you cannot reach the app via the domain, you can tunnel directly to the service:
```bash
kubectl port-forward service/mathpuzzle-service 8080:80 -n mathpuzzle
```
Then access via `http://localhost:8080`.


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
