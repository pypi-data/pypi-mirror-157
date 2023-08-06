class EsRequest:
    search_term: str
    resources: list[str]
    filters: list[str]
    aggregation: bool
    page: int
    size: int
    analytics: bool

    def __init__(self, search_term: str, resources: list[str] = None, filters: list[str] = None,
                 aggregation: bool = False, page: int = 1, size: int = 10, analytics: bool = False):
        """
        A class used to wrap all necessary input for the search endpoint.

        Parameters
        ----------
        search_term : str
            a query which follows Lucene syntax
        resources : list[str], default=None
            a list of resources to search on
        filters : list[str], default=None
            a list of filters applied on the query
        aggregation : bool, default=False
            indicate if the result should be aggregated or not
        page : int, default=1
            page number
        size : int, default=10
            number of items per page
        analytics : bool, default=False
        """
        self.search_term = search_term
        self.resources = resources
        self.filters = filters
        self.aggregation = aggregation
        self.page = page
        self.size = size
        self.analytics = analytics

