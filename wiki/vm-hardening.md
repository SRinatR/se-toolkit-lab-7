# VM hardening

<h2>Table of contents</h2>

- [About the VM hardening](#about-the-vm-hardening)
- [Harden the VM](#harden-the-vm)
  - [Set up `ufw` firewall (REMOTE)](#set-up-ufw-firewall-remote)
  - [Set up `fail2ban` (REMOTE)](#set-up-fail2ban-remote)

## About the VM hardening

VM hardening is the process of securing a [virtual machine](./vm.md#what-is-a-vm) by reducing its attack surface.

Docs:

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)

## Harden the VM

Complete these steps:

<!-- no toc -->
1. [Connect to the VM as the user `<user>` (LOCAL)](./vm-access.md#connect-to-the-vm-as-the-user-user-local).
2. [Set up `ufw` firewall (REMOTE)](#set-up-ufw-firewall-remote).
3. [Set up `fail2ban` (REMOTE)](#set-up-fail2ban-remote).

### Set up `ufw` firewall (REMOTE)

> `ufw` (`Uncomplicated Firewall`) is a simple firewall for [`Linux`](./linux.md#what-is-linux).
>
> By default, `ufw` denies all incoming traffic.
> The steps below create exceptions for the ports your VM needs.

1. To allow [`SSH`](./ssh.md#what-is-ssh),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo ufw allow 22
   ```

   > 🟪 **Important**
   >
   > Always allow `SSH` (port 22) before enabling `ufw`.
   > Otherwise, you will lock yourself out of your VM.

2. To allow the [LMS API port](./lms-api.md#lms-api-port),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo ufw allow <lms-api-host-port>
   ```

   Replace the placeholder [`<lms-api-host-port>`](./lms-api.md#lms-api-port-placeholder).

3. To enable the [firewall](./computer-networks.md#firewall),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo ufw enable
   ```

4. To check the status,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo ufw status
   ```

### Set up `fail2ban` (REMOTE)

`fail2ban` blocks IP addresses that make too many failed login attempts.
Even after password authentication is disabled, `fail2ban` remains useful:

- It rate-limits repeated [`SSH`](./ssh.md#what-is-ssh) connection attempts.
- It can be extended to protect other services.

1. To update the package list,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo apt update
   ```

2. To install `fail2ban`,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo apt install -y fail2ban
   ```

3. To enable the service,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo systemctl enable fail2ban
   ```

4. To start the service,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo systemctl start fail2ban
   ```

5. To check the status,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   sudo systemctl status fail2ban
   ```
