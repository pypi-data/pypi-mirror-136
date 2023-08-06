import subprocess
import json
from pathlib import Path
import time


class Tf:
    def __init__(self, region, ssh_key_name, aws_access_key_id, aws_secret_access_key):
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.ssh_key_name = ssh_key_name
        self.dir = Path(__file__).parent

    def init(self):
        cmds = ['terraform', 'init']
        resp = subprocess.run(cmds, cwd=self.dir, capture_output=True)
        assert resp.returncode == 0, 'Terraform initialization failed'
        return True

    def init_validate(self):
        cmds = ['terraform', 'init', '-var', 'backend=false']
        resp = subprocess.run(cmds, cwd=self.dir, capture_output=False)
        assert resp.returncode == 0, 'Terraform initialization failed'
        return True

    def validate(self):
        cmds = ['terraform', 'validate']
        resp = subprocess.run(cmds, cwd=self.dir, capture_output=False)
        assert resp.returncode == 0, 'Terraform validation failed'
        return True

    def build(self):
        cmds = self._add_vars(['terraform', 'apply', '-auto-approve'])
        resp = subprocess.run(cmds, cwd=self.dir, capture_output=False)
        assert resp.returncode == 0, 'Terraform build failed'
        return True

    def outputs(self):
        resp = subprocess.run(['terraform', 'output', '-json'],
                              cwd=self.dir, capture_output=True)
        assert resp.returncode == 0, 'Terraform output failed'
        outputs = json.loads(resp.stdout.decode())
        return {
            'cluster_id': outputs['cluster_id']['value'],
            'instance_id': outputs['ec2_instance_id']['value'],
            'vpc_id': outputs['vpc_id']['value']
        }

    def destroy(self):
        cmds = self._add_vars(['terraform', 'destroy', '-auto-approve'])
        resp = subprocess.run(cmds, cwd=self.dir, capture_output=False)
        assert resp.returncode == 0, 'Terraform destroy failed'
        return True

    def _add_vars(self, cmds):
        vars = {"region": self.region, "ssh_key_name": self.ssh_key_name,
                "aws_access_key_id": self.aws_access_key_id, 'aws_secret_access_key': self.aws_secret_access_key}
        for var, value in vars.items():
            cmds.append('-var')
            cmds.append(f'{var}={value}')
        return cmds

    def _clean_up(self):
        cmds = ['rm', '-r', '.terraform']
        resp = subprocess.run(cmds, cwd=self.dir, capture_output=False)
        assert resp.returncode == 0, 'Terraform clean up failed'
        return True


class tfstateFileNotFoundError(Exception):
    pass
