class Base:
    headers = {}

    def __init__(self, stage, key):
        headers = {'X-API-KEY': self.key}

        if stage == 'develop':
            self.url = "https://test-api.dcentralab.com/"
            self.key = key
        if stage == 'staging':
            self.url = "https://staging-api.dcentralab.com/"
