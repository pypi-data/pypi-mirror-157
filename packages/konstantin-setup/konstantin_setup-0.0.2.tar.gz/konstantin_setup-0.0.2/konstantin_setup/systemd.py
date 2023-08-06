"""Create systemd service file."""

import getpass
import os

def run(
    service_name: str,
    description: str,
    work_dir: str,
    poetry_bin: str = "/home/admin/.local/bin/poetry",
) -> None:
    """Создать сервис."""
    service = f"""
[Unit]
Description={description}
[Service]
Restart=on-failure
RestartSec=10s
Type=simple
User={getpass.getuser()}
Group={getpass.getuser()}
EnvironmentFile=/etc/environment
WorkingDirectory={work_dir}
ExecStart={poetry_bin} run python start.py
[Install]
WantedBy=multi-user.target"""
    service_file = open(f"scripts/{service_name}", "w")
    service_file.write(service)
    service_file.close()
    os.system(f"sudo mv scripts/{service_name} /etc/systemd/system")
    os.system("sudo systemctl daemon-reload")
