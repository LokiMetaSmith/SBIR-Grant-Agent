# Proxmox LXC Deployment Guide for SBIR Grant Agent

This guide provides instructions on how to deploy the SBIR Grant Agent application into a new LXC container on your Proxmox VE host using a single automated script.

## Overview

The `deploy_lxc.sh` script is self-contained and automates the following tasks:
1.  **Create a new LXC container** from a Debian or Ubuntu template.
2.  **Configure the container's** resources (CPU, memory, storage).
3.  **Archive the local project files** and push them into the new container.
4.  **Update the container** and install necessary dependencies (Python, pip).
5.  **Create a dedicated non-root user** to run the application.
6.  **Set up a Python virtual environment** and install all required packages from `requirements.txt`.
7.  **Create and enable a `systemd` service** to ensure the application server starts automatically on boot.

## Prerequisites

- A running Proxmox VE host with SSH access.
- At least one LXC container template (e.g., Debian 12 or Ubuntu 24.04) downloaded on your Proxmox host. You can download templates via the Proxmox web UI under `local` storage -> `CT Templates`.
- The complete SBIR Grant Agent project directory downloaded or cloned onto your Proxmox host.

## Step 1: Place the Script

Ensure the `deploy_lxc.sh` script is located in the **root directory** of the SBIR Grant Agent project on your Proxmox host. The script needs to be in the same directory as `server.py` and `requirements.txt` to bundle the files correctly.

## Step 2: Customize the Deployment Script (Optional)

Before running the script, you may want to customize the configuration variables at the top of the `deploy_lxc.sh` file.

Open the script with a text editor:
```bash
nano deploy_lxc.sh
```

Key variables you might want to change:
- `CT_ID`: A unique ID for your new container. **Ensure this ID is not already in use.**
- `CT_PASSWORD`: The root password for the new container. **It is highly recommended to change this.**
- `PROXMOX_STORAGE`: The Proxmox storage pool where the container's disk will be created (e.g., `local-lvm`).
- `PROXMOX_BRIDGE`: The network bridge the container should use (e.g., `vmbr0`).

## Step 3: Run the Deployment Script

1.  Navigate to the root of the project directory.

2.  Make the script executable:
    ```bash
    chmod +x deploy_lxc.sh
    ```

3.  Run the script as root:
    ```bash
    sudo ./deploy_lxc.sh
    ```

The script will now archive the project, create the container, push the files, and provision the environment. This process may take several minutes.

## Step 4: Final Configuration (Required)

After the script finishes, you must add your API keys to the `.env` file inside the new container for the application to be fully functional. The script uses the `.env.example` file as a template.

1.  Log into your Proxmox host.

2.  Enter the newly created container's console using `pct enter`. If you used the default `CT_ID`, this will be:
    ```bash
    pct enter 199
    ```

3.  Once inside the container, copy the example `.env` file:
    ```bash
    cp /opt/sbir-agent/.env.example /opt/sbir-agent/.env
    ```

4.  Open the new `.env` file with a text editor like `nano`:
    ```bash
    nano /opt/sbir-agent/.env
    ```

5.  Add your API keys for your chosen LLM provider(s) and for `sam.gov`. Save the file and exit the editor (`Ctrl+X`, then `Y`, then `Enter` in nano).

6.  Restart the application service to apply the new environment variables:
    ```bash
    systemctl restart sbir-agent
    ```

## Accessing the Application

Your SBIR Grant Agent is now running. The script will print the container's IP address at the end of the setup process. You can access the web interface by navigating to:

`http://<CONTAINER_IP_ADDRESS>:5000/sbir_agent.html`

## Troubleshooting

-   **Service Status:** To check if the application server is running correctly, use the following command inside the container:
    ```bash
    systemctl status sbir-agent
    ```
-   **Server Logs:** To view the Flask server's logs, you can use `journalctl`:
    ```bash
    journalctl -u sbir-agent -f
    ```
-   **Network Issues:** If the script fails to get an IP address, ensure your Proxmox network and DHCP server are configured correctly. You may need to restart the container (`pct stop 199 && pct start 199`) after it has been created.