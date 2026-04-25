# MathPuzzle - Comprehensive VPS Deployment Plan (K3s)

This document is the definitive guide for deploying MathPuzzle to a budget-friendly VPS using **K3s (Lightweight Kubernetes)**. It combines strategic infrastructure choices with technical implementation steps.

---

## 🏗️ Part 1: Infrastructure Architecture

### Current Stack Compatibility: ✅ FULLY COMPATIBLE
- **Runtime**: Python 3.11-slim (Gunicorn + Threading)
- **Database**: PostgreSQL 15-Alpine (Deployed in-cluster)
- **Orchestration**: K3s (managed via `kubectl` and `helm`)
- **Ingress/SSL**: Traefik + Cert-Manager (Let's Encrypt)
- **Automation**: GitHub Actions (Build) + Local Bash Scripts (Deploy)

---

## 💰 Part 2: VPS Provider Selection

### Recommended EU VPS Providers
| Provider | Starting Price | Best For | GDPR | Notes |
|----------|---|---|---|---|
| **Hetzner** 🏆 | €4.50/mo | **BEST VALUE** | ✅ | CPX11 (2 vCPU, 4GB RAM) is the "Sweet Spot" |
| **OVHcloud** | €3.50/mo | Budget | ✅ | Mature EU platform |
| **Oracle Cloud**| $0.00 | Free Forever | ✅ | 4 ARM Cores, 24GB RAM (If available) |
| **DigitalOcean**| $6.00 | Simplicity | ✅ | Great documentation and marketplace |

**Recommended Specs for K3s**:
- **CPU**: 2 cores minimum
- **RAM**: 4GB recommended (K3s + App + DB run comfortably here)
- **OS**: Ubuntu 22.04 LTS

---

## 🌐 Part 3: Domain Strategy

### Option A: Professional Domain (Recommended)
- **Registrars**: Namecheap (€0.88/yr), Ionos (€1/yr), or Porkbun.
- **Setup**: Point an **A Record** from your domain (e.g., `math.com`) to your VPS IP.

### Option B: The "No Domain" Hack (Immediate HTTPS)
- **Service**: **sslip.io**
- **How**: Use `YOUR_IP.sslip.io` as your domain. 
- **Benefit**: Let's Encrypt issues real certificates for these, enabling the **PWA Install Icon** without buying a domain.

---

## 🚀 Part 4: Technical Setup & Deployment

### 0. Hetzner Server Creation (SSH Setup)
When creating your server in the Hetzner Cloud Console:
1.  **SSH Keys Section**: Click **"Add SSH Key"** and paste your public key (usually from `cat ~/.ssh/id_ed25519.pub` or `id_rsa.pub`).
2.  **Selection**: Ensure your key is **selected** (checked) before clicking "Create & Buy". This ensures the root password is never sent and your key is pre-installed.

### 1. VPS Initial Setup
Connect via SSH using your Public IP (IPv4 or IPv6):

**For IPv4**:
```bash
ssh root@your-vps-ip
```

**For IPv6** (If you see an address like `2a01:4f8:...`):
```bash
ssh root@your-vps-ipv6
```

**⚠️ CRITICAL (For IPv6-only servers)**: 
GitHub and Docker Hub do not support IPv6 yet. You must use a NAT64 gateway to download K3s and images:

**Temporary (will reset on reboot)**:
```bash
echo "nameserver 2a00:1098:2c::1" > /etc/resolv.conf
echo "nameserver 2a01:4f8:c2c:123b::1" >> /etc/resolv.conf
```

**Permanent (Ubuntu 22.04 Netplan)**:
```bash
sudo nano /etc/netplan/00-installer-config.yaml
```
Add under the network interface:
```yaml
nameservers:
  addresses: [2a00:1098:2c::1, 2a01:4f8:c2c:123b::1]
```
Then apply:
```bash
sudo netplan apply
```

**Verify NAT64 is working**:
```bash
ping -c 1 8.8.8.8  # Should work (Ping Google DNS via NAT64)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 -I  # Should get HTTP 200
```

Once connected, install K3s:
```bash
curl -sfL https://get.k3s.io | sh -
# Verify: sudo kubectl get nodes

# Enable K3s config for Helm/Kubectl
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc

### 2. Clone Repository
Get the code and deployment manifests onto the server:
```bash
# If you are on IPv6-only, ensure NAT64 is set (Step 1)
git clone https://github.com/bindalmax/AIHandsOn.git
cd AIHandsOn
```

### 3. Install Infrastructure (Helm & Cert-Manager)
```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Cert-Manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --set installCRDs=true
```

### 4. Deploy MathPuzzle
Follow the automated sequence using the provided scripts:

1.  **Configure Secrets**:
    ```bash
    cp k8s/secrets.example.yaml k8s/secrets.yaml
    # Edit keys and passwords in k8s/secrets.yaml
    ```
2.  **Run Setup Script**:
    ```bash
    ./scripts/k8s-setup.sh
    ```
    ```

---

## 🚨 Part 5: Troubleshooting & Maintenance

### The Database Password Trap
**Issue**: Changing `POSTGRES_PASSWORD` in `secrets.yaml` does not update an existing database.
**Fix**:
1. Run `./scripts/k8s-nuke.sh` (Warning: Deletes data).
2. Correct the password in `secrets.yaml`.
3. Run `./scripts/k8s-setup.sh`.

### Common Commands
- **Logs**: `kubectl logs -l app=mathpuzzle-web -n mathpuzzle -f`
- **Restart**: `kubectl rollout restart deployment/mathpuzzle-web -n mathpuzzle`
- **SSL Check**: `kubectl get certificate -n mathpuzzle`

---

## 🛡️ Part 6: Post-Deployment Checklist

- [ ] **Backups**: Set up a CRON job on the VPS to run `kubectl exec` and `pg_dump` daily.
- [ ] **Security**: Ensure the VPS firewall (UFW) only allows ports 22, 80, and 443.
- [ ] **PWA Check**: Access the app via HTTPS and verify the "Install" icon appears.
- [ ] **Resource Monitoring**: Use `kubectl top nodes` to ensure the 4GB RAM is sufficient.

---

**Plan Created**: April 21, 2026
**Status**: ACTIVE DEPLOYMENT SOURCE OF TRUTH
