__author__ = "Philipp D. Rohde"

from SPARQLWrapper import SPARQLWrapper, XML


class SPARQLEndpoint:
    """Implementation of a SPARQL endpoint; having an URL and the ability to run SPARQL queries."""

    class __SPARQLEndpoint:
        """Private class to allow simulation of a Singleton."""
        def __init__(self, endpointURL):
            self.endpointURL = endpointURL
            self.endpoint = SPARQLWrapper(endpointURL)
            #self.endpoint.setReturnFormat(XML)

        def runQuery(self, queryId, queryString):
            print("query id: ", queryId, " - query str: ", queryString)
            # self.endpoint.setQuery(queryString)
            # return self.endpoint.query().convert()
            '''Repository repo = new SPARQLRepository(endPointURL);
            repo.initialize();

            try (RepositoryConnection conn = repo.getConnection()) {
                QueryEvaluation eval = runQuery(conn, queryId, queryString);
                repo.shutDown();
                return eval;'''

        '''private QueryEvaluation runQuery(RepositoryConnection conn, String queryId, String queryString) {
            log.debug("Evaluating query:\n" + queryString);

            TupleQuery tupleQuery = conn.prepareTupleQuery(QueryLanguage.SPARQL, queryString);
            Instant start = Instant.now();
            QueryEvaluation eval = new QueryEvaluation(queryId, queryString, tupleQuery.evaluate(), start);
            eval.iterate();
            return eval;
        }'''

    instance = None

    def __new__(cls, endpointURL):
        if not SPARQLEndpoint.instance:
            SPARQLEndpoint.instance = SPARQLEndpoint.__SPARQLEndpoint(endpointURL)
        return SPARQLEndpoint.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)
