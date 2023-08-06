from neo4j import GraphDatabase

def get_session(endpoint, db, user, pwd):
    # TODO: static driver to share with all
    driver = GraphDatabase.driver(endpoint, auth=(user, pwd))
    return driver.session(database=db)

# example or helper
# build into test at some point
def do_it_all(host,port,db,user,pwd):
    # e.g.
    # host = "my-neo4j.host.com"
    # port = 7687  # bolt
    # db = "my-db"
    # user = "bob"
    # pass = "password123"
    session = get_session(f'bolt://{host}:{port}', db, user, pwd)

    file_id = "gov.noaa.ncdc:C00708"
    #file_id = "gov.*"

    # parameterize! sanitize! for safe travels
    query = f'match (d:Dataset) WHERE d.fileId = $file_id return *'
    params = { 'file_id': event["graph_metadata"]["file_id"]}
    
    response = session.run(query,parameters=params)
    # maybe handle errors here?

    nodes = [ { k:v for k,v in r["d"].items() } 
            for r in response ]
    return nodes
