import logging
import requests

logger = logging.getLogger('sotaog_public_api_client')


class Client_Exception(Exception):
  pass


class Client():
  def __init__(self, url: str, client_id: str, client_secret: str, customer_id: str = None):
    self.session = requests.Session()
    self.url = url.rstrip('/')
    self.customer_id = customer_id
    logger.info(f'Initializing Sotaog API client for {url}')
    logger.debug(f'Authenticating to API: {url}')
    data = {
        'grant_type': 'client_credentials'
    }
    result = self.session.post(f'{self.url}/v1/authenticate', data=data, auth=(client_id, client_secret))
    if result.status_code == 200:
      self.token = result.json()['access_token']
      logger.debug(f'Token: {self.token}')
    else:
      raise Client_Exception('Unable to authenticate to API')

  def _get_headers(self):
    headers = {
        'authorization': 'Bearer {}'.format(self.token)
    }
    if self.customer_id:
      headers['x-sotaog-customer-id'] = self.customer_id
    return headers

  def get_alarm_services(self):
    logger.debug(f'Getting alarm services')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/alarm-services', headers=headers)
    if result.status_code == 200:
      alarm_services = result.json()
      logger.debug(f'Alarm Services: {alarm_services}')
      return alarm_services
    else:
      raise Client_Exception(f'Unable to retrieve alarm services')

  def get_alarm_service(self, alarm_service_id: str):
    logger.debug(f'Getting alarm service {alarm_service_id}')
    headers = self._get_headers()
    url = f'{self.url}/v1/alarm-services/{alarm_service_id}'
    result = self.session.get(url, headers=headers)
    if result.status_code == 200:
      alarm_service = result.json()
      logger.debug(f'Alarm Service: {alarm_service}')
      return alarm_service
    else:
      raise Client_Exception(f'Unable to retrieve alarm service {alarm_service_id}')

  def get_alarms(self):
    logger.debug(f'Getting alarms')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/alarms', headers=headers)
    if result.status_code == 200:
      alarms = result.json()
      logger.debug(f'Alarms: {alarms}')
      return alarms
    else:
      raise Client_Exception(f'Unable to retrieve alarms')

  def get_alarm(self, asset_id: str, datatype: str = None):
    logger.debug(f'Getting alarms for {asset_id}')
    headers = self._get_headers()
    url = f'{self.url}/v1/alarms/{asset_id}'
    if datatype:
      url += f'/{datatype}'
    result = self.session.get(url, headers=headers)
    if result.status_code == 200:
      alarm = result.json()
      logger.debug(f'Alarm: {alarm}')
      return alarm
    else:
      raise Client_Exception(f'Unable to retrieve alarms for {asset_id}')

  def get_facilities(self):
    logger.debug(f'Getting facilities')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/facilities', headers=headers)
    if result.status_code == 200:
      facilities = result.json()
      logger.debug(f'Facilities: {facilities}')
      return facilities
    else:
      raise Client_Exception(f'Unable to retrieve facilities')

  def get_facility(self, facility_id: str):
    logger.debug(f'Getting facility: {facility_id}')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/facilities/{facility_id}', headers=headers)
    if result.status_code == 200:
      facility = result.json()
      logger.debug(f'Facility: {facility}')
      return facility
    else:
      raise Client_Exception(f'Unable to retrieve facility {facility_id}')

  def get_asset(self, asset_id, type: str = 'assets'):
    logger.debug(f'Getting asset {asset_id} of type: {type}')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/{type}/{asset_id}', headers=headers)
    if result.status_code == 200:
      asset = result.json()
      logger.debug(f'Asset: {asset}')
      return asset
    else:
      raise Client_Exception(f'Unable to retrieve asset {asset_id} of type {type}')

  def get_assets(self, type: str = 'assets', facility: str = None, asset_type: str = None):
    logger.debug(f'Getting assets of type: {type}')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/{type}', headers=headers)
    if result.status_code == 200:
      assets = result.json()
      if facility:
        assets = [asset for asset in assets if 'facility' in asset and asset['facility'] == facility]
      if asset_type:
        assets = [asset for asset in assets if 'asset_type' in asset and asset['asset_type'] == asset_type]
      logger.debug(f'Assets: {assets}')
      return assets
    else:
      raise Client_Exception(f'Unable to retrieve assets of type {asset_type}')

  def get_datatypes(self, group_by='asset'):
    logger.debug('Getting datatypes')
    headers = self._get_headers()
    params = {}
    if group_by:
      params['group_by']: group_by
    result = self.session.get(f'{self.url}/v1/datatypes', headers=headers, params=params)
    if result.status_code == 200:
        return result.json()
    else:
        raise Client_Exception('Unable to get datatypes')

  def get_datatype(self, datatype_id):
    logger.debug(f'Getting datatype {datatype_id}')
    headers = self._get_headers()
    params = {'group_by': 'asset'}
    result = self.session.get(f'{self.url}/v1/datatypes/{datatype_id}', headers=headers, params=params)
    if result.status_code == 200:
        return result.json()
    else:
        raise Client_Exception(f'Unable to get datatype {datatype_id}')

  def get_datapoints(self, asset_datatypes: dict, start_ts: int = None, end_ts: int = None, sort: str = 'desc', limit: int = 100):
    logger.debug(f'Getting datapoints for asset_datatypes: {asset_datatypes}')
    headers = self._get_headers()
    body = {
        'asset_datatypes': asset_datatypes
    }
    if start_ts:
      body['start_ts'] = start_ts
    if end_ts:
      body['end_ts'] = end_ts
    if sort:
      body['sort'] = sort
    if limit:
      body['limit'] = limit
    result = self.session.post(f'{self.url}/v1/datapoints', headers=headers, json=body)
    if result.status_code == 200:
      datapoints = result.json()
      logger.debug(f'Datapoints: {datapoints}')
      return datapoints
    else:
      logger.debug(result.json())
      raise Client_Exception('Unable to get datapoints')

  def get_asset_datapoints(self, asset_id: str, datatypes: [str] = [], start_ts: int = None, end_ts: int = None, sort: str = 'desc', limit: int = 100):
    logger.debug(f'Getting datapoints for asset: {asset_id}')
    headers = self._get_headers()
    params = {}
    if datatypes:
      params['datatypes'] = datatypes
    if start_ts:
      params['start_ts'] = start_ts
    if end_ts:
      params['end_ts'] = end_ts
    if sort:
      params['sort'] = sort
    if limit:
      params['limit'] = limit
    result = self.session.get(f'{self.url}/v1/datapoints/{asset_id}', headers=headers, params=params)
    if result.status_code == 200:
      datapoints = result.json()
      logger.debug(f'Datapoints: {datapoints}')
      return datapoints
    else:
      raise Client_Exception('Unable to get datapoints')

  def get_swd_networks(self, facility: str = None):
    logger.debug(f'Getting SWD networks')
    headers = self._get_headers()
    result = self.session.get(f'{self.url}/v1/swd-networks', headers=headers)
    if result.status_code == 200:
      swd_networks = result.json()
      logger.debug(f'SWD Networks: {swd_networks}')
      if facility:
        swd_networks = [swd_network for swd_network in swd_networks if facility in swd_network['facilities']]
      logger.debug(f'SWD Networks: {swd_networks}')
      return swd_networks
    else:
      raise Client_Exception(f'Unable to retrieve SWD networks')

  def get_truck_tickets(self, facility: str = None, type: str = None, start_ts: int = None, end_ts: int = None):
    logger.debug(f'Getting truck tickets')
    headers = self._get_headers()
    params = {}
    if start_ts:
      params['start_ts'] = start_ts
    if end_ts:
      params['end_ts'] = end_ts
    if type:
      params['type'] = type
    if facility:
      params['facility'] = facility
    result = self.session.get(f'{self.url}/v1/truck-tickets', headers=headers, params=params)
    if result.status_code == 200:
      truck_tickets = result.json()
      logger.debug(f'Truck tickets: {truck_tickets}')
      return truck_tickets
    else:
      raise Client_Exception(f'Unable to retrieve truck tickets')

  def post_datapoints(self, asset_id, datapoints):
    logger.debug(f'Posting datapoints')
    headers = self._get_headers()
    result = self.session.post(f'{self.url}/v1/datapoints/{asset_id}', headers=headers, json=datapoints)
    if result.status_code != 202:
      logger.exception(result.json())
      raise Exception('Unable to post datapoints')
