from SPARQLWrapper import SPARQLWrapper, JSON

def get_wikipedia_links(topic):
    # Define the DBpedia SPARQL endpoint
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    
    # Define the SPARQL query
    query = f"""
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    
    SELECT ?wikiLink WHERE {{
      ?subject dbo:wikiPageWikiLink dbr:{topic} .
      ?subject foaf:isPrimaryTopicOf ?wikiLink .
    }}
    """
    
    # Set the query and return format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and collect results
    results = sparql.query().convert()
    
    # Extract links from results
    links = [result["wikiLink"]["value"] for result in results["results"]["bindings"]]
    
    return links

# Example usage
topic = "Sherlock_Holmes"
links = get_wikipedia_links(topic)

for link in links:
    print(link)

print(len(links))
