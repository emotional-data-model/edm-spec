"""Merge agent group files + MFOEM extraction + Anthropic 171 list into frameworks.json."""
import json, sys, glob, os
fw_dir, mfoem_path, anthropic_path, out = sys.argv[1:5]

# map agent ids -> crosswalk column ids
ALIAS = {
 'ekman_basic_emotions':'ekman','plutchik_wheel':'plutchik','cowen_keltner_2017':'cowen_keltner','goemotions':'goemotions',
 'russell_circumplex':'russell','pad_model':'pad','occ_model':'occ','scherer_cpm_grid_gew':'scherer',
 'barrett_constructed_emotion':'barrett','anthropic_2026_emotion_concepts':'anthropic_2026','hume_expression_measurement':'hume',
 'panksepp_primary_process_emotional_systems':'panksepp','damasio_somatic_marker_and_feeling':'damasio',
 'conway_self_memory_system':'conway','singer_blagov_self_defining_memories':'singer_blagov','pillemer_momentous_events':'pillemer',
 'lazarus_cognitive_appraisal':'lazarus','mcadams_narrative_identity':'mcadams','bruner_narrative_construction':'bruner',
 'booker_seven_basic_plots':'booker','campbell_hero_journey':'campbell','tulving_episodic_semantic_memory':'tulving',
 'ainsworth_attachment':'ainsworth','bartholomew_four_category_attachment':'bartholomew','fiske_relational_models':'fiske',
 'bronfenbrenner_ecological_systems':'bronfenbrenner','gross_process_model_emotion_regulation':'gross',
 'elliot_approach_avoidance_motivation':'elliot','self_determination_theory':'sdt','mayer_salovey_ability_ei':'mayer_salovey',
 'goleman_boyatzis_ei_competencies':'goleman','bar_on_eqi_model':'bar_on',
 'w3c_emotionml_1_0':'emotionml','humaine_earl':'earl','wordnet_affect':'wordnet_affect','nrc_lexicons':'nrc','senticnet_hourglass':'senticnet','snomed_ct_emotion_mood':'snomed',
}
frameworks = []
for f in sorted(glob.glob(os.path.join(fw_dir, 'group_*.json'))):
    for fw in json.load(open(f, encoding='utf-8')):
        fw['agent_id'] = fw['id']
        fw['id'] = ALIAS.get(fw['id'], fw['id'])
        fw['extracted_by'] = os.path.basename(f)
        frameworks.append(fw)

# Anthropic 171 list -> fill the null construct
a = json.load(open(anthropic_path, encoding='utf-8'))
for fw in frameworks:
    if fw['id'] == 'anthropic_2026':
        for c in fw['constructs']:
            if c['id'] == 'anthropic_171_emotion_concepts':
                c['values'] = a['words']; c['value_source'] = 'FETCHED'
                c['notes'] = (c.get('notes') or '') + f" | Full list extracted directly from {a['source_url']} appendix 'Full list of emotions' on {a['accessed']}; count={a['count']}."
        fw['fetched_urls'] = list(dict.fromkeys(fw.get('fetched_urls', []) + [a['source_url']]))
        fw['confidence'] = max(fw.get('confidence', 0), 0.95)

# MFOEM
m = json.load(open(mfoem_path, encoding='utf-8'))
cs = [c for c in m['classes'] if c['id'].startswith('MFOEM:') and not c['deprecated']]
def pairs(pred): return sorted(f"{c['id']}|{c['label']}" for c in cs if pred(c))
mfoem = {
 'id':'mfoem','agent_id':'mfoem_emotion_ontology','name':'MFOEM Emotion Ontology (OBO)','family':'machine',
 'citation':{'authors':'Hastings, J., Ceusters, W., Smith, B., Mulligan, K. et al.','year':2011,
   'title':'Dispositions and processes in the Emotion Ontology (MFOEM); ontology file version 2025-07-31',
   'venue':'OBO Foundry / ICBO 2011','url':'http://purl.obolibrary.org/obo/mfoem.owl','doi':None,'accessed':'2026-10-17'},
 'source_status':'FETCHED','confidence':1.0,
 'fetched_urls':[m['summary']['source'], m['summary']['version_iri']],
 'summary':'OWL ontology of affective phenomena built on BFO and the Ontology of Mental Functioning (MF). Emotions are processes (subclasses of MFOEM:000001 emotion process); it also models moods, subjective affective feelings, appraisals, physiological responses, action tendencies, expressive behaviour, and valence as a process profile.',
 'identifier_scheme':'OBO PURL, e.g. http://purl.obolibrary.org/obo/MFOEM_000034 (CURIE MFOEM:000034, label "joy")',
 'constructs':[
  {'id':'emotion_process_subclasses','label':'emotion process (MFOEM:000001) and subclasses','type':'hierarchy','uri_or_code':'MFOEM:000001','values':pairs(lambda c: c['is_emotion_process']),'value_source':'FETCHED','notes':'English rdfs:label; the OWL also carries de/fr/es/it/ja labels'},
  {'id':'mood_process_subclasses','label':'mood process (MFOEM:000193) and subclasses','type':'hierarchy','uri_or_code':'MFOEM:000193','values':pairs(lambda c: c['is_mood']),'value_source':'FETCHED','notes':''},
  {'id':'subjective_affective_feelings','label':'subjective affective feeling (MFOEM:000006) and subclasses','type':'hierarchy','uri_or_code':'MFOEM:000006','values':pairs(lambda c: c['is_affective_process'] and not c['is_emotion_process'] and not c['is_mood']),'value_source':'FETCHED','notes':''},
  {'id':'affective_appraisals','label':'affective appraisal (MFOEM:000005) and subclasses','type':'appraisal','uri_or_code':'MFOEM:000005','values':pairs(lambda c: c['label'] and (c['label'].startswith('appraisal') or c['label'].startswith('evaluation as'))),'value_source':'FETCHED','notes':'GRID/CPM-derived appraisal checks'},
  {'id':'physiological_processes','label':'physiological process involved in an emotion (MFOEM:000003) and subclasses','type':'hierarchy','uri_or_code':'MFOEM:000003','values':pairs(lambda c: 'physiological process involved in an emotion' in c['parent_labels'] or c['label'] in ('perspiring (hands)','perspiring (whole body)','experiencing heat in cheeks or chest','experiencing warm sensation in whole body')),'value_source':'FETCHED','notes':''},
  {'id':'behavioural_processes','label':'emotional behavioural process (MFOEM:000004) and subclasses','type':'hierarchy','uri_or_code':'MFOEM:000004','values':pairs(lambda c: any(p in c['parent_labels'] for p in ('emotional behavioural process','facial expression behaviour','emotional bodily movement behaviour','emotional speaking behaviour','canonical emotional facial expression','canonical emotional voice utterances','aggression'))),'value_source':'FETCHED','notes':''},
  {'id':'dispositions_and_valence','label':'emotion disposition, love/hate, valence, action tendency','type':'hierarchy','uri_or_code':None,'values':pairs(lambda c: c['label'] in ('emotion disposition','love','hate','companionate love','passionate love','valence','positive valence','negative valence','emotional action tendency','emotional personality trait','affective process','affective appraisal process','affective appraisal')),'value_source':'FETCHED','notes':''},
 ],
 'verification_notes':f"OWL downloaded via OBO PURL (resolves to GitHub jannahastings/emotion-ontology master). version IRI {m['summary']['version_iri']}. {m['summary']['total_classes']} classes total, {m['summary']['mfoem_classes']} non-deprecated MFOEM classes, {m['summary']['emotion_process_subclasses']} emotion-process subclasses. No 'intensity' or 'duration' quality classes; no 'mixed valence'; no classes for wonder, awe, reverence, gratitude, longing, relief, tenderness or frustration.",
}
frameworks.append(mfoem)

by_fam = {}
for fw in frameworks: by_fam[fw['family']] = by_fam.get(fw['family'], 0) + 1
status = {}
for fw in frameworks: status[fw['source_status']] = status.get(fw['source_status'], 0) + 1
doc = {
 'generated':'2026-10-17','purpose':'Reference set for the EDM v0.8.3 ontology crosswalk (discovery only).',
 'legend':{'source_status':{'FETCHED':'primary/official source fetched and constructs read from it','FETCHED_SECONDARY':'official abstract / distributor / encyclopedia / open-access secondary source fetched; construct lists verified against it (see constructs[].verified_against) or, where that key is absent, partly from knowledge','KNOWLEDGE':'no fetch succeeded; constructs from model knowledge, see confidence','NOT_FOUND':'no such publication located'},
           'value_source':'per-construct flag: FETCHED = values read from a fetched page, or verified item by item against an accessible secondary source recorded in verified_against (verification_level: secondary; sources/verification_2026-10-17.json); KNOWLEDGE = from model knowledge, unverified ([KNOWLEDGE] in the report)',
           'verified_against':'per-construct record of the 2026-10-17 verification pass: status VERIFIED / PARTIAL / CONTRADICTED / UNVERIFIED, url, title, kind (open_access_paper, open_access_review, handbook_chapter, university_page, author_page, official_site, wikipedia, other), quote, corrections'},
 'summary':{'framework_count':len(frameworks),'by_family':by_fam,'by_source_status':status,
            'construct_count':sum(len(f['constructs']) for f in frameworks)},
 'frameworks':frameworks,
}
json.dump(doc, open(out,'w',encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(doc['summary'], indent=1))
print([f['id'] for f in frameworks])
