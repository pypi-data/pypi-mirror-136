import json

from ankorstore_api_client.utils import urljoin

class ResourcePool:
    def __init__(self, endpoint, session):
        """Initialize the ResourcePool to the given endpoint. Eg: products"""
        self._endpoint = endpoint
        self._session = session

    def get_url(self):
        return self._endpoint

class CreatableResource:
    def create_item(self, item):
        res = self._session.post(self._endpoint, data=json.dumps(item))
        return res

class GettableResource:
    def fetch_item(self, code):
        url = urljoin(self._endpoint, code)
        res = self._session.get(url)
        return res

class ListableResource:
    def fetch_list(self, args=None):
        res = self._session.get(self._endpoint, params=args)
        return res

class SearchableResource:
    def search(self, query):
        params = {
            'query': query
        }
        res = self._session.get(self._endpoint, params=params)
        return res

class UpdatableResource:
    def update_create_item(self, item, code=None):
        if code is None:
            code = item.get('id')
        url = urljoin(self._endpoint, code)
        res = self._session.put(url, data=json.dumps(item))
        return res

class DeletableResource:
    def delete_item(self, code):
        url = urljoin(self._endpoint, code)
        res = self._session.delete(url)
        return res


# Pools
#  Account Pool
class AccountPool(ResourcePool):
    @property
    def orders(self):
        return AccountOrderPool(
            urljoin(self._endpoint, 'orders'), self._session
        )
    
    @property
    def products(self):
        return AccountProductPool(
            urljoin(self._endpoint, 'products'), self._session
        )

class AccountProductPool(ResourcePool, GettableResource, UpdatableResource, CreatableResource, ListableResource):
    pass

class AccountOrderPool(ResourcePool):
    @property
    def export(self):
        return OrderExportPool(
            urljoin(self._endpoint, 'export'), self._session
        )

    def shipping_label(self, code):
        return OrderShippingLabelPool(
            urljoin(self._endpoint, code, 'shipping_label'), self._session
        )

class OrderShippingLabelPool(ResourcePool, GettableResource, ListableResource, CreatableResource):
    pass

class OrderExportPool(ResourcePool, ListableResource):
    def fetch_list(self, status_key='all'):
        res = self._session.get(self._endpoint, params={'status_key': status_key})
        return res

# Brand Pool

class BrandPool(ResourcePool):
    @property
    def products(self):
        return BrandProductPool(
            urljoin(self._endpoint, 'products'), self._session
        )

# Brand Product Pool

class BrandProductPool(ResourcePool, ListableResource, GettableResource, UpdatableResource):
    
    @property
    def mass_action(self):
        return BrandProductMassActionPool(
            urljoin(self._endpoint, 'mass-action'), self._session
        )

class BrandProductMassActionPool(ResourcePool, CreatableResource):
    pass        

# Order Pool
class OrderPool(ResourcePool, GettableResource, ListableResource):
    def pickup(self, code):
        return OrderPickupPool(
            urljoin(self._endpoint, code, 'pickup'), self._session
        )
    
    def action(self, code):
        return OrderActionPool(
            urljoin(self._endpoint, code, 'action'), self._session
        )

    def parcels(self, code):
        return OrderParcelPool(
            urljoin(self._endpoint, code, 'parcels'), self._session
        ) 

    def items(self, code):
        return OrderItemsPool(
            urljoin(self._endpoint, code, 'items'), self._session
        )         


class OrderItemsPool(ResourcePool, CreatableResource):
    pass

class OrderActionPool(ResourcePool, CreatableResource):
    pass

class OrderParcelPool(ResourcePool, CreatableResource):
    pass

class OrderPickupPool(ResourcePool, CreatableResource, UpdatableResource):
    pass

# Product Pool

class ProductPool(ResourcePool, GettableResource):
    pass

# Conversation Pool

class ConversationPool(ResourcePool, CreatableResource):
    pass