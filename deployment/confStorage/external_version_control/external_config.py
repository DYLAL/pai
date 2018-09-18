# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os
import sys
import yaml
import logging
import logging.config

from .. import conf_storage_util
from ...paiLibrary.common import template_handler
from ...paiLibrary.common import file_handler

package_directory_kubeinstall = os.path.dirname(os.path.abspath(__file__))


class external_config:

    def __init__(self, **kwargs):

        self.logger = logging.getLogger(__name__)

        # Configuration for local conf
        self.local_conf_path = "{0}/../../sysconf/conf_external_storage.yaml".format(package_directory_kubeinstall)
        if "local_conf_path" in kwargs:
            self.local_conf_path = kwargs["local_conf_path"]

        # Configuration for configmap [Access to k8s through exist kube_config.]
        self.kube_config_path = None
        if "kube_config_path" in kwargs:
            self.kube_config_path = kwargs["kube_conf_path"]

        # Configuration for configmap [Access to k8s through api-server address.]
        # Only support k8s deployed by openPai.
        self.kube_api_server_address = None
        if "kube_api_server_address" in kwargs:
            self.kube_api_server_address = kwargs["kube_api_server_address"]

        self.external_storage_configuration = None



    def load_yaml_config(config_path):
        with open(config_path, "r") as f:
            cluster_data = yaml.load(f)

        return cluster_data



    def load_from_local_conf(self):
        self.external_storage_configuration = self.load_yaml_config(self.local_conf_path)



    def load_from_k8s_configmap(self, KUBE_CONFIG_PATH = None):
        if KUBE_CONFIG_PATH == None:
            KUBE_CONFIG_PATH = self.kube_config_path
        configmap_data_dict = conf_storage_util.get_configmap(KUBE_CONFIG_PATH, "pai-external-storage-conf")
        if configmap_data_dict == None:
            self.logger.error("Unable to get the external storage configuration from k8s cluster.")
            self.logger.error("Please check the configmap named [pai-external-storage] in the namespace [default].")
            sys.exit(1)

        self.external_storage_configuration = yaml.load(configmap_data_dict["external-storage-conf"])



    def get_latest_external_configuration(self):

        if self.kube_config_path != None:
            self.load_from_k8s_configmap()

        if self.kube_api_server_address != None:
            kube_conf_template_path = "{0}/../../k8sPaiLibrary/template/config.template".format(package_directory_kubeinstall)
            kube_conf_template = file_handler.read_template(kube_conf_template_path)
            kube_conf_data = template_handler.generate_from_template_dict(
                kube_conf_template,
                {
                    'clusterconfig' : { 'api-servers-ip': str(self.kube_api_server_address) }
                }
            )
            file_handler.write_generated_file("{0}/config".format(package_directory_kubeinstall), kube_conf_data)
            self.load_from_k8s_configmap(
                KUBE_CONFIG_PATH="{0}/config".format(package_directory_kubeinstall)
            )

        if self.kube_config_path == None and self.kube_api_server_address == None:
            self.load_from_local_conf()

        return self.external_storage_configuration



    def update_latest_external_configuration(self):
        None

