import json, sys, os
repo = sys.argv[1]; out = sys.argv[2]
domains = ['core','constellation','milky_way','gravity','impulse']
profiles = {}
for p in ['essential','extended','full']:
    s = json.load(open(f'{repo}/schema/edm.v0.8.{p}.schema.json', encoding='utf-8'))
    profiles[p] = {}
    for d in domains:
        v = s['properties'].get(d)
        if v is None: profiles[p][d] = []
        elif '$ref' in v: profiles[p][d] = '*'
        else: profiles[p][d] = list(v['properties'].keys())
kind_map = {
 'core': 'narrative', 'constellation': 'emotion', 'milky_way': 'context', 'gravity': 'salience', 'impulse': 'motivation'}
non_affective = {'milky_way.visibility_context','constellation.media_format','milky_way.associated_people'}
fields = []
for d in domains:
    frag = json.load(open(f'{repo}/schema/fragments/{d}.json', encoding='utf-8'))
    req = set(frag.get('required', []))
    for name, spec in frag['properties'].items():
        path = f'{d}.{name}'
        t = spec.get('type'); 
        if isinstance(t, list): t = [x for x in t if x != 'null']; t = t[0] if len(t)==1 else t
        enum = [e for e in spec.get('enum', []) if e is not None] if 'enum' in spec else None
        canon = spec.get('x-edm-canonical')
        if enum: values, vocab = enum, 'closed_enum'
        elif canon: values, vocab = canon, 'canonical_open'
        elif t == 'boolean': values, vocab = [True, False], 'boolean'
        elif t == 'number': values, vocab = None, 'numeric'
        elif t == 'array': values, vocab = None, 'free_text_list'
        else: values, vocab = None, 'free_text'
        in_profiles = [p for p in profiles if profiles[p][d]=='*' or name in profiles[p][d]]
        fields.append({
          'path': path, 'domain': d, 'field': name, 'json_type': t,
          'nullable': 'null' in (spec.get('type') if isinstance(spec.get('type'), list) else [spec.get('type')]) or (enum is not None and None in spec.get('enum', [])),
          'required_in_fragment': name in req,
          'vocabulary': vocab, 'canonical_values': values,
          'description': spec.get('description'), 'constraints': spec.get('x_constraints'),
          'profiles': in_profiles,
          'edm_kind': 'administrative' if path in non_affective else kind_map[d],
          'items': spec.get('items'), 'minItems': spec.get('minItems'), 'maxItems': spec.get('maxItems'),
        })
summary = {
  'spec_version': '0.8.3', 'generated': '2026-10-17', 'source': 'schema/fragments/{core,constellation,milky_way,gravity,impulse}.json + schema/edm.v0.8.{essential,extended,full}.schema.json',
  'field_count': len(fields),
  'by_domain': {d: sum(1 for f in fields if f['domain']==d) for d in domains},
  'by_vocabulary': {k: sum(1 for f in fields if f['vocabulary']==k) for k in ['closed_enum','canonical_open','free_text','free_text_list','numeric','boolean']},
  'canonical_value_count': sum(len(f['canonical_values']) for f in fields if f['canonical_values'] and f['vocabulary'] in ('closed_enum','canonical_open')),
  'profile_membership': {p: sum(1 for f in fields if p in f['profiles']) for p in profiles},
  'note': 'edm_kind=administrative marks fields in affective domains that carry no affective content (media_format, visibility_context, associated_people).'
}
json.dump({'summary': summary, 'fields': fields}, open(out,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
print(json.dumps(summary, indent=1))
