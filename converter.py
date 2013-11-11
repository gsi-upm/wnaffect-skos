from rdflib import Graph, Literal, Namespace, RDF, URIRef
import json

graph = Graph()
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
dct = Namespace('http://purl.org/dc/terms/#')
wna = Namespace('http://gsi.dit.upm.es/ontologies/wnaffect/ns#')
cc = Namespace('http://creativecommons.org/ns#')
graph.bind('skos', skos)
graph.bind('dct', dct)
graph.bind('cc', cc)
graph.bind('wna', wna)
ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
      'skos': 'http://www.w3.org/2004/02/skos/core#'}

graph.add((URIRef('http://gsi.dit.upm.es'), RDF['type'], dct['Agent']))
graph.add((wna['wn-affect'], RDF['type'], skos['ConceptScheme']))
graph.add((RDF.Description, dct['publisher'], URIRef('http://gsi.dit.upm.es')))
graph.add((RDF.Description, dct['isFormatOf'],
           URIRef('http://wndomains.fbk.eu/wnaffect.html')))
graph.add((RDF.Description, dct['title'],
           Literal('WordNet-Affect taxonomy represented in SKOS.')))
graph.add((RDF.Description, dct['creator'], Literal('Carlo Strapparava')))
graph.add((RDF.Description, dct['creator'], Literal('Alessandro Valitutti')))
graph.add((RDF.Description, cc['license'],
           URIRef('http://creativecommons.org/licenses/by-nc-sa/1.0/')))

wn = open('wn-affect-1.1-hierarchy.txt')
for line in wn.readlines()[2:]:
    label, superconcept = line.strip().split()[1:3]
    graph.add((wna[label], RDF['type'], skos['Concept']))
    graph.add((wna[label], skos['prefLabel'], Literal(label, lang='en')))
    graph.add((wna[label], skos['broaderTransitive'], wna[superconcept]))
#print graph.serialize(format='pretty-xml')

out = file('out.rdf', 'w')
out.write(graph.serialize(format='pretty-xml'))
out.close()


def get_children(node):
    print 'For root %s' % node
    results = graph.query(
        '''SELECT ?pred ?term WHERE{
        ?pred skos:broaderTransitive ?root
        }''', initNs=ns, initBindings={'root': node})
    return [pred[0] for pred in results]


def get_trees(node):
    nametree = {}
    tree = {}
    nametree["name"] = node.title().rsplit('#')[1]
    children = get_children(node)
    print "children %s" % children
    if len(children) > 0:
        nametree["children"] = []
        for leaf in children:
            t = get_trees(leaf)
            nametree["children"].append(t[0])
            tree[leaf] = t[1]
            print nametree["children"]
    return nametree, tree

print wna['root'].rsplit("#")[1]
js = json.dumps(get_trees(wna['root'])[0])

jsonout = file('out.json', 'w')
jsonout.write(js)
jsonout.close()

print "Done"
