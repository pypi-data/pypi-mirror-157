# -*- coding: utf-8 -*-


from urllib.parse import urlparse


class Config:
    BASE_INSTANCE_URL = 'https://{}.armorblox.io/'
    BASE_API_PATH = 'api/{}/organizations/{}/'

    def __init__(
            self, api_key: str, instance_name: str = None, instance_url: str = None,
            sdk_version: str = 'Unspecified'):
        """

        Args:
            api_key: string
            instance_name: string
            instance_url: string
            sdk_version: string

        Raises:
            Exception:
        """
        self._sdk_version = sdk_version
        self._api_key = api_key
        if instance_url:
            self._instance_url = instance_url
            if not instance_url.endswith('/'):
                self._instance_url += '/'
            if instance_name:
                self._instance_name = instance_name
            else:
                self._instance_name = urlparse(instance_url).netloc.split('.')[0]
        elif instance_name:
            self._instance_url = self.BASE_INSTANCE_URL.format(instance_name)
            self._instance_name = instance_name
        else:
            raise Exception('At least one of instance_url or instance_name should be provided')
        self._base_api_url = self._instance_url + self.BASE_API_PATH.format('{}', self._instance_name)

    @property
    def sdk_version(self):
        return self._sdk_version

    @property
    def api_key(self):
        return self._api_key

    @property
    def instance_url(self):
        return self._instance_url

    @property
    def instance_name(self):
        return self._instance_name

    @property
    def base_api_url(self):
        return self._base_api_url
