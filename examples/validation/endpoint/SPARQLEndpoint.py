class SPARQLEndpoint:
    def __init__(self, endPointURL):
        self.endPointURL = endPointURL

    def runQuery(self, queryId, queryString):
        print("query id: ", queryId, " - query str: ", queryString)
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