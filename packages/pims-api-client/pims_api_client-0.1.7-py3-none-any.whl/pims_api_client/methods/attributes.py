from pims_api_client.schemas import AttributeFilter, AttributeListItem, BaseAttribute
from pims_api_client.schemas import PagedListResponse
from typing import Optional
from .base_executor import BaseExecutor

class AttributeMethodsExecutor(BaseExecutor):

    async def fetch_attributes(self, params: AttributeFilter = AttributeFilter()):
        response = await self.client.get('pim/api/v1/attribute', params=params.dict(by_alias=True))
        return PagedListResponse[AttributeListItem].parse_obj(response)

    async def fetch_attribute(self, uid: str):
        response = await self.client.get(f'pim/api/v1/attribute/{uid}')
        return AttributeListItem.parse_obj(response)

    async def create_attribute(self, data: BaseAttribute):
        return await self.client.post('pim/api/v1/attribute', data=data.dict())