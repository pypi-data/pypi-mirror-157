class Base:

    def __init__(self, stage, key):
        self.key = key
        self.headers = {'X-API-KEY': self.key}

        if stage == 'develop':
            self.url = "https://test-api.dcentralab.com/"
        if stage == 'staging':
            self.url = "https://staging-api.dcentralab.com/"
