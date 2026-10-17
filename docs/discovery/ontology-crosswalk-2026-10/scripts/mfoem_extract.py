import xml.etree.ElementTree as ET, json, sys, re
src, out = sys.argv[1], sys.argv[2]
ns = {'owl':'http://www.w3.org/2002/07/owl#','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#','rdfs':'http://www.w3.org/2000/01/rdf-schema#','obo':'http://purl.obolibrary.org/obo/','oboInOwl':'http://www.geneontology.org/formats/oboInOwl#'}
RDF='{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
tree = ET.parse(src); root = tree.getroot()
version = root.find('owl:Ontology/owl:versionIRI', ns).get(RDF+'resource')
classes = {}
for c in root.findall('owl:Class', ns):
    iri = c.get(RDF+'about')
    if not iri: continue
    XML='{http://www.w3.org/XML/1998/namespace}lang'
    labs = c.findall('rdfs:label', ns)
    label = next((l for l in labs if l.get(XML) in (None,'en')), labs[0] if labs else None)
    other_labels = {l.get(XML): l.text for l in labs if l.get(XML) not in (None,'en')}
    defn = c.find('obo:IAO_0000115', ns)
    parents = [p.get(RDF+'resource') for p in c.findall('rdfs:subClassOf', ns) if p.get(RDF+'resource')]
    syns = [s.text for s in c.findall('oboInOwl:hasExactSynonym', ns)+c.findall('oboInOwl:hasRelatedSynonym', ns)+c.findall('oboInOwl:hasBroadSynonym', ns)+c.findall('oboInOwl:hasNarrowSynonym', ns) if s.text]
    dep = c.find('owl:deprecated', ns)
    classes[iri] = {'iri': iri, 'id': iri.rsplit('/',1)[-1].replace('_',':'), 'label': label.text if label is not None else None, 'definition': defn.text.strip() if defn is not None and defn.text else None, 'parents': parents, 'synonyms': syns, 'labels_other_lang': other_labels, 'deprecated': dep is not None and dep.text=='true'}
def lab(i): return classes.get(i,{}).get('label') or i.rsplit('/',1)[-1]
for c in classes.values(): c['parent_labels'] = [lab(p) for p in c['parents']]
# ancestry helper
def ancestors(iri, seen=None):
    seen = seen or set()
    for p in classes.get(iri,{}).get('parents',[]):
        if p not in seen: seen.add(p); ancestors(p, seen)
    return seen
for c in classes.values():
    anc = [lab(a) for a in ancestors(c['iri'])]
    c['is_emotion_process'] = 'emotion process' in anc or c['label']=='emotion process'
    c['is_mood'] = 'mood process' in anc or c['label']=='mood process'
    c['is_affective_process'] = 'affective process' in anc
prefixes = {}
for c in classes.values():
    pre = c['id'].split(':')[0]; prefixes[pre] = prefixes.get(pre,0)+1
mf = [c for c in classes.values() if c['id'].startswith('MFOEM:') and not c['deprecated']]
summary = {'source': 'http://purl.obolibrary.org/obo/mfoem.owl', 'version_iri': version, 'accessed': '2026-10-17', 'total_classes': len(classes), 'by_prefix': prefixes,
  'mfoem_classes': len(mf), 'emotion_process_subclasses': sum(1 for c in mf if c['is_emotion_process']), 'mood_subclasses': sum(1 for c in mf if c['is_mood']), 'affective_process_subclasses': sum(1 for c in mf if c['is_affective_process'])}
json.dump({'summary': summary, 'classes': sorted(classes.values(), key=lambda c: c['id'])}, open(out,'w',encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(summary, indent=1))
# print top-level affective structure
for c in mf:
    if c['label'] in ('affective process','emotion process','mood process','emotion','appraisal process','action tendency','physiological response to emotion process','subjective emotional feeling','emotional behavioural process','affective representation','bodily feeling','affective state'):
        print(c['id'], '|', c['label'], '| parents:', c['parent_labels'])
