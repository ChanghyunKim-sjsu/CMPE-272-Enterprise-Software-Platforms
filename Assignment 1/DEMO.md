# Assignment 1 Demo Script

Use this short sequence for the assignment demo.

## 1. Show the VM Environment

```bash
multipass list
```

Explain that the Mac is the Ansible control node and `vm1` and `vm2` are Ubuntu managed nodes.

## 2. Show Ansible Installation

```bash
ansible --version
```

Explain that Ansible is installed on the Mac control node.

## 3. Verify Connectivity

```bash
ansible all -i inventory.ini -m ping
```

Point out that both VMs return `SUCCESS` and `ping: pong`.

## 4. Explain the Playbook

```bash
cat site.yml
```

Mention:

- The deploy play installs Nginx.
- The HTML page is generated from a Jinja2 template.
- Nginx is configured to listen on port 8080.
- The undeploy play removes the web server resources.

## 5. Deploy the Web Servers

```bash
ansible-playbook -i inventory.ini site.yml --tags deploy
```

Point out the final play recap:

```text
unreachable=0
failed=0
```

## 6. Verify in Browser

Open:

```text
http://192.168.252.2:8080
http://192.168.252.3:8080
```

Expected pages:

- VM1: `Hello World from SJSU-1`
- VM2: `Hello World from SJSU-2`

## 7. Undeploy

```bash
ansible-playbook -i inventory.ini site.yml --tags undeploy
```

Explain that the playbook stops Nginx, removes the custom web page, and removes Nginx.

## 8. Verify Undeployment

Refresh the browser pages or run:

```bash
curl http://192.168.252.2:8080
curl http://192.168.252.3:8080
```

Expected result: the connection fails because Nginx is no longer running.

## Optional Final Reset for Live Demo

If the instructor may ask to see the working website again, redeploy at the end:

```bash
ansible-playbook -i inventory.ini site.yml --tags deploy
```
