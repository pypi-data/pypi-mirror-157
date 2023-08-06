# -*- coding: utf-8 -*-


from armorblox.api.base_api import BaseApi
from enum import Enum, unique


@unique
class IncidentType(Enum):
    THREAT_INCIDENT_TYPE = 1
    DLP_INCIDENT_TYPE = 2
    ABUSE_INCIDENT_TYPE = 3


class IncidentsApi(BaseApi):
    PATH = 'incidents'
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, config, incident_type=None):
        super().__init__(config)
        self._incident_type = incident_type

    def list(self, page_token=None):
        #   'from_date': '',
        #   'to_date': '',
        params = {
            'orderBy': 'DESC',
            'sortBy': 'DATE',
            'timeFilter': 'allTime'
        }
        if self._incident_type is not None:
            params['incidentTypesFilter'] = self._incident_type.name
        if page_token is not None:
            params['page_token'] = page_token

        response_json, response = self.list_resource(self.PATH, params=params)
        if response_json is None:
            return []
        else:
            next_page_token = response_json.get('next_page_token', None)
            total_count = response_json.get('total_count', 0)
            return response_json.get('incidents', [])

    def get(self, incident_id: int):
        params = {
            'pageSize': 20
        }

        return self.get_resource(self.PATH, str(incident_id), params=params)


class ThreatsApi(IncidentsApi):
    def __init__(self, config):
        super().__init__(config, IncidentType.THREAT_INCIDENT_TYPE)


class DLPIncidentsApi(IncidentsApi):
    def __init__(self, config):
        super().__init__(config, IncidentType.DLP_INCIDENT_TYPE)


class AbuseIncidentsApi(IncidentsApi):
    def __init__(self, config):
        super().__init__(config, IncidentType.ABUSE_INCIDENT_TYPE)

