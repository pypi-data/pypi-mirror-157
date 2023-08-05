class HicPlatform(object):
    def create_campaign(self, campaign):
        raise NotImplementedError("Please Implement this method")

    def pause_campaign(self, campaign_id):
        raise NotImplementedError("Please Implement this method")

    def update_campaign(self, campaign):
        raise NotImplementedError("Please Implement this method")

    def get_account_performance(self, account_id):
        raise NotImplementedError("Please Implement this method")

    def get_ad_preview(self, job_id):
        raise NotImplementedError("Please Implement this method")

    def get_ad_manager_url(self, job_id):
        raise NotImplementedError("Please Implement this method")

