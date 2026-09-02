# Assignment 1: SJSU Ansible Web Server

This folder contains the Ansible code for deploying and undeploying a simple Nginx web server on two Ubuntu Multipass virtual machines.

## Objective

The objective of this assignment is to use Ansible from a Mac control node to manage two Ubuntu servers and deploy a web service that listens on port 8080. Each server displays a different page:

- VM1: `Hello World from SJSU-1`
- VM2: `Hello World from SJSU-2`

## Environment

| Component | Description |
|---|---|
| Control node | macOS host running Ansible |
| Managed node 1 | Ubuntu Multipass VM `vm1` |
| Managed node 2 | Ubuntu Multipass VM `vm2` |
| Web server | Nginx |
| Port | 8080 |

Current VM inventory:

```ini
[webservers]
vm1 ansible_host=192.168.252.2 ansible_user=ubuntu server_id=1
vm2 ansible_host=192.168.252.3 ansible_user=ubuntu server_id=2
```

## Folder Structure

```text
Assignment 1/
├── README.md
├── DEMO.md
├── ansible.cfg
├── inventory.ini
├── site.yml
└── templates/
    ├── index.html.j2
    └── nginx.conf.j2
```

## Files

- `inventory.ini`: Defines the two Ubuntu managed nodes.
- `ansible.cfg`: Stores project-local Ansible defaults for this assignment.
- `site.yml`: Contains both deploy and undeploy plays.
- `templates/index.html.j2`: Creates the custom Hello World page using `server_id`.
- `templates/nginx.conf.j2`: Configures Nginx to listen on port 8080.

## Connectivity Test

Run the Ansible ping module to verify that the Mac control node can reach both VMs:

```bash
ansible all -i inventory.ini -m ping
```

Expected result:

```text
vm1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}

vm2 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## Deploy

Run the deploy tag:

```bash
ansible-playbook -i inventory.ini site.yml --tags deploy
```

The deploy play installs Nginx, deploys the custom HTML page, configures Nginx to listen on port 8080, and starts/enables the service.

## Verify Deployment

Open the following URLs in a browser:

```text
http://192.168.252.2:8080
http://192.168.252.3:8080
```

Expected output:

- `http://192.168.252.2:8080` shows `Hello World from SJSU-1`
- `http://192.168.252.3:8080` shows `Hello World from SJSU-2`

You can also verify with curl:

```bash
curl http://192.168.252.2:8080
curl http://192.168.252.3:8080
```

## Undeploy

Run the undeploy tag:

```bash
ansible-playbook -i inventory.ini site.yml --tags undeploy
```

The undeploy play stops/disables Nginx, removes the deployed custom web page, and removes the Nginx package.

## Verify Undeployment

After undeployment, the browser or curl should fail to connect on port 8080:

```bash
curl http://192.168.252.2:8080
curl http://192.168.252.3:8080
```

Expected result:

```text
Failed to connect
```

## Submission Note

The Word report contains screenshots and written explanation. This GitHub folder contains the Ansible code and scripts submitted separately.
