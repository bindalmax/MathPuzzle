# Application Deployment Plan

This document outlines various options and considerations for deploying the MathPuzzle application to a production server.

## 1. General Deployment Steps (Common to All Options)

Before deploying, ensure the following:

*   **Dependencies File:** Create a `requirements.txt` file by running `pip freeze > requirements.txt` in your activated virtual environment.
*   **Debug Mode:** Change `app.run(debug=True)` to `app.run(debug=False)` or remove it entirely in `app.py` for production. Debug mode is a security risk.
*   **WSGI Server:** Use a production-ready WSGI (Web Server Gateway Interface) server (e.g., Gunicorn, uWSGI) to run your Flask application. Flask's built-in server is for development only.
*   **Reverse Proxy (Recommended):** Consider using a web server like Nginx or Apache as a reverse proxy. It handles static files, SSL/TLS, and can improve performance and security.
*   **Process Management:** Implement a process manager (e.g., systemd, Supervisor) to ensure your WSGI server runs continuously and restarts automatically if it crashes.

## 2. Key Consideration: `highscores.json`

Your application currently stores high scores in `highscores.json` on the filesystem. This has significant implications for deployment:

*   **Persistence:** Data is tied to the specific server instance. If the server is replaced or the application redeployed without careful handling, data can be lost.
*   **Scalability:** It's not suitable for scaling to multiple application instances, as each instance would have its own `highscores.json` file, leading to inconsistent data.

For a truly robust and scalable solution, **migrating to a proper database (e.g., PostgreSQL, SQLite with persistent storage)** is highly recommended.

## 3. Deployment Options

### Option A: Virtual Private Server (VPS) - Recommended for Current Data Model

This is the most straightforward option if you wish to keep `highscores.json` as is, but requires manual server management.

*   **Description:** Provision a Linux-based VPS (e.g., DigitalOcean, AWS EC2, Linode, Google Cloud Compute Engine) and manually set up the environment.
*   **Pros:**
    *   Full control over the server.
    *   Directly supports `highscores.json` on the filesystem.
    *   Cost-effective for single-instance deployments.
*   **Cons:**
    *   Requires manual setup and maintenance (OS, Python, WSGI, Nginx, systemd).
    *   `highscores.json` data needs manual backup/restore if the server changes.
    *   Not scalable for multiple application instances without further data migration.
*   **Key Technologies:** Gunicorn (WSGI), Nginx (Reverse Proxy), systemd (Process Management).

### Option B: Platform as a Service (PaaS) - Requires Database Migration

PaaS providers simplify deployment but typically have ephemeral filesystems.

*   **Description:** Deploy to a platform like Heroku, Render, Google App Engine, or AWS Elastic Beanstalk.
*   **Pros:**
    *   Extremely easy deployment and scaling.
    *   No server management required.
    *   Built-in CI/CD, logging, and monitoring.
*   **Cons:**
    *   **Requires migrating `highscores.json` to a proper database (e.g., PostgreSQL, managed SQLite) before deployment.**
    *   Less control over the underlying infrastructure.
    *   Can be more expensive at scale.
*   **Key Technologies:** PaaS-specific buildpacks/runtimes, Managed Database Services.

### Option C: Containerization (Docker) - Advanced, Benefits from Database Migration

Docker packages your application and its dependencies into portable containers.

*   **Description:** Create a `Dockerfile` for your application, build a Docker image, and deploy it to a container orchestration platform (e.g., Kubernetes, AWS ECS, Google Cloud Run) or a Docker-enabled VPS.
*   **Pros:**
    *   Highly portable and reproducible deployments.
    *   Consistent environments across development and production.
    *   Scalable with container orchestration.
*   **Cons:**
    *   Adds complexity (learning Docker, writing Dockerfiles).
    *   `highscores.json` persistence still needs careful handling (e.g., Docker volumes for single host, or a shared database for multi-instance).
    *   Still highly recommended to migrate to a database for multi-instance scalability.
*   **Key Technologies:** Docker, Gunicorn, Container Orchestration (Kubernetes, ECS, etc.).

## 4. Recommendation

*   **For immediate deployment with the current `highscores.json` file:** Start with **Option A (VPS)**. This will get your application live with minimal code changes.
*   **For a long-term, robust, and scalable solution:** Plan to **migrate your `highscores.json` data to a proper database (e.g., PostgreSQL)**. Once this is done, **Option B (PaaS)** or **Option C (Docker)** will provide much easier management and better scalability.
