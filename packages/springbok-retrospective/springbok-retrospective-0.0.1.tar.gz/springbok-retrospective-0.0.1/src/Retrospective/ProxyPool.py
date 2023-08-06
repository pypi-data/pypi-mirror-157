"""
This project seeks to create a 'retrospective' of Google News top hits.
Copyright (C) Springbok LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import random
import time

# TODO: Replace use of boto with boto3
# http://boto.cloudhackers.com/en/latest/
import boto.ec2

# https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
import boto3
import requests
import subprocess

USERNAME = "ubuntu"
KEY_FILENAME = "~/.ssh/tinyproxy-01.pem"

logger = logging.getLogger(__name__)


# TODO: Need a key to make instances unique
class ProxyPool:
    def __init__(
        self,
        region_name="us-east-1",
        image_id="ami-05e8288885ee0c2d5",  # tinyproxy-03
        security_group_id="sg-04ae83dffd0e19255",  # tinyproxy-01
        security_group_rule_ids={
            "ralatsdc": "sgr-0a777fb7a78973c66",
            "spearw": "sgr-0b892e4e6efd4befa",
        },
        target_count=3,
        key_name="tinyproxy-01",
        security_groups=["tinyproxy-01"],
        instance_type="t2.micro",
        sleep_stp=10,
        sleep_max=60,
        **kwargs,
    ):
        self.region_name = region_name
        self.image_id = image_id
        self.security_group_id = security_group_id
        self.security_group_rule_ids = security_group_rule_ids
        self.target_count = target_count
        self.key_name = key_name
        self.security_groups = security_groups
        self.instance_type = instance_type
        self.sleep_stp = sleep_stp
        self.sleep_max = sleep_max
        self.connection = boto.ec2.connect_to_region(self.region_name, **kwargs)
        self.client = boto3.client("ec2")
        self.instances = self._get_instances()

    def maintain_pool(self):
        self.instances = self._get_instances()
        current_count = len(self.instances)
        logger.info("Current count: {0}".format(current_count))
        if current_count < self.target_count:
            self.add_to_pool(self.target_count - current_count)
        elif current_count > self.target_count:
            self.remove_from_pool(current_count - self.target_count)
        self._wait_for_pool(self.target_count)

    def add_to_pool(self, count):
        logger.info("Add count: {0}".format(count))
        self.instances = self._get_instances()
        self.connection.run_instances(
            self.image_id,
            min_count=count,
            max_count=count,
            key_name=self.key_name,
            security_groups=self.security_groups,
            instance_type=self.instance_type,
        )
        self._wait_for_pool(len(self.instances) + count)

    def remove_from_pool(self, count):
        logger.info("Remove count: {0}".format(count))
        self.instances = self._get_instances()
        instance_ids = []
        for i in self.instances:
            instance_ids.append(i.id)
            if len(instance_ids) == count:
                break
        self.connection.stop_instances(instance_ids)
        self._wait_for_pool(len(self.instances) - count)

    def restart_pool(self):
        self.terminate_pool()
        self.maintain_pool()

    def terminate_pool(self):
        self.instances = self._get_instances()
        for i in self.instances:
            logger.info("Terminating instance: {0}".format(i.id))
            i.terminate()
        self._wait_for_pool(0)

    def get_random_proxy_instance(self):
        return random.choice(self.instances)

    def _get_instances(self):
        instances = []
        reservations = self.connection.get_all_reservations()
        for r in reservations:
            for i in r.instances:
                # TODO: Use a key to identify this pool instance
                if (
                    i.image_id == self.image_id
                    and i.instance_type == self.instance_type
                    and i.state == "running"
                ):
                    instances.append(i)
        return instances

    def _wait_for_pool(self, count):
        sleep = 0
        while sleep < self.sleep_max:
            self.instances = self._get_instances()
            if len(self.instances) == count:
                break
            else:
                logger.info("Sleeping {0}".format(self.sleep_stp))
                time.sleep(self.sleep_stp)
                sleep += self.sleep_stp
        self._modify_security_group_rules()

    def _modify_security_group_rules(self):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.modify_security_group_rul
        # Get user's github username
        cp = subprocess.run(
            "git config -l | grep remote.origin.url | cut -d ':' -f 2 | cut -d '/' -f 1",
            shell=True,
            capture_output=True,
        )
        username = cp.stdout.decode("utf-8").strip()

        # Get user's public IP address
        ip = requests.get("https://api.ipify.org").text

        # Modify security group rule to permit access by user's IP address
        response = self.client.modify_security_group_rules(
            GroupId=self.security_group_id,
            SecurityGroupRules=[
                {
                    "SecurityGroupRuleId": self.security_group_rule_ids[username],
                    "SecurityGroupRule": {
                        "IpProtocol": "TCP",
                        "FromPort": 8888,
                        "ToPort": 8888,
                        "CidrIpv4": f"{ip}/32",
                        "Description": "ralatsdc",
                    },
                },
            ],
        )
        return response


def main():
    return ProxyPool()


if __name__ == "__main__":
    proxyPool = main()
