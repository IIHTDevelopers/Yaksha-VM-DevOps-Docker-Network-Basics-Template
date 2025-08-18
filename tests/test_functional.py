import unittest
import subprocess
from tests.TestUtils import TestUtils

class TestDockerNetwork(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_obj = TestUtils()
        cls.container_name = "app1"
        cls.target_container = "app2"

    def run_command(self, cmd):
        """Helper to run shell commands safely"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            print(f"⚠️ Exception while running command: {e}")
            return "", str(e), 1

    def run_command(self, cmd):
        """Helper function to run shell commands"""
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode("utf-8"), err.decode("utf-8"), process.returncode

    # Testcase 1: Check if mynetwork is created
    def test_network_created(self):
        try:
            out, err, code = self.run_command("docker network ls --filter name=mynetwork --format '{{.Name}}'")
            if "mynetwork" in out.strip():
                self.test_obj.yakshaAssert("TestNetworkCreated", True, "functional")
                print("TestNetworkCreated = Passed")
            else:
                self.test_obj.yakshaAssert("TestNetworkCreated", False, "functional")
                print("TestNetworkCreated = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("TestNetworkCreated", False, "functional")
            print(f"TestNetworkCreated = Failed with Exception: {e}")

    # Testcase 2: Ensure app1 and app2 exist
    def test_containers_exist(self):
        try:
            out, err, code = self.run_command("docker ps -a --format '{{.Names}}'")
            if "app1" in out and "app2" in out:
                self.test_obj.yakshaAssert("TestContainersExist", True, "functional")
                print("TestContainersExist = Passed")
            else:
                self.test_obj.yakshaAssert("TestContainersExist", False, "functional")
                print("TestContainersExist = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("TestContainersExist", False, "functional")
            print(f"TestContainersExist = Failed with Exception: {e}")

    # Testcase 3: Check if app1 and app2 are connected to mynetwork
    def test_containers_connected_to_network(self):
        try:
            # Run inspect commands properly as list
            out1, _, _ = self.run_command([
                "docker", "inspect", "-f", "{{json .NetworkSettings.Networks}}", "app1"
            ])
            out2, _, _ = self.run_command([
                "docker", "inspect", "-f", "{{json .NetworkSettings.Networks}}", "app2"
            ])

            import json
            networks1 = json.loads(out1)
            networks2 = json.loads(out2)

            if "mynetwork" in networks1 and "mynetwork" in networks2:
                self.test_obj.yakshaAssert("TestContainersConnectedToNetwork", True, "functional")
                print("TestContainersConnectedToNetwork = Passed")
            else:
                self.test_obj.yakshaAssert("TestContainersConnectedToNetwork", False, "functional")
                print("TestContainersConnectedToNetwork = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("TestContainersConnectedToNetwork", False, "functional")
            print(f"TestContainersConnectedToNetwork = Failed with Exception: {e}")

    def test_ping_app2(self):
        try:
            cmd = ["docker", "exec", self.container_name, "ping", "-c", "2", self.target_container]
            out, err, code = self.run_command(cmd)

            if code == 0 and "0% packet loss" in out:
                self.test_obj.yakshaAssert("TestPingApp2", True, "functional")
                print("TestPingApp2 = Passed")
            else:
                self.test_obj.yakshaAssert("TestPingApp2", False, "functional")
                print(f"TestPingApp2 = Failed\nOutput:\n{out}\nError:\n{err}")
        except Exception as e:
            self.test_obj.yakshaAssert("TestPingApp2", False, "functional")
            print(f"TestPingApp2 = Failed with Exception: {e}")
    # Testcase: Check DNS resolution within mynetwork
    def test_dns_resolution(self):
        try:
            # Step 1: Try to resolve app2 from app1 using nslookup
            out, err, code = self.run_command("docker exec app1 nslookup app2")

            if "Name:" in out and "Address:" in out:
                self.test_obj.yakshaAssert("TestDNSResolution", True, "functional")
                print("TestDNSResolution = Passed")
            else:
                self.test_obj.yakshaAssert("TestDNSResolution", False, "functional")
                print("TestDNSResolution = Failed")
        except Exception as e:
            self.test_obj.yakshaAssert("TestDNSResolution", False, "functional")
            print(f"TestDNSResolution = Failed with Exception: {e}")


if __name__ == "__main__":
    unittest.main()
