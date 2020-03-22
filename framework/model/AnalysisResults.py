class AnalysisResults:
    """
    This class aggregates several different information pieces provided by the
    log-analysis facility, to make access easier
    """
    def __init__(self):
        self.leaked_uuids = {}
        self.leaked_service_uuids = {}
        self.leaked_characteristic_uuids = {}
        self.leaked_descriptor_uuids = {}
        self.leaked_categorized_misc_uuids= {}
        self.call_paths = []
        self.dump_paths = []
