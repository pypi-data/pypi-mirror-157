import requests
from Base import Base


class EventPolling(Base):

    def get_collection(self, collection_name):
        url = self.url + "event_polling/collection"
        headers = {'X-API-KEY': self.key}
        data = {
            "collection_name": collection_name
        }
        response = requests.post(url, json=data, headers=headers)
        return response.json()
