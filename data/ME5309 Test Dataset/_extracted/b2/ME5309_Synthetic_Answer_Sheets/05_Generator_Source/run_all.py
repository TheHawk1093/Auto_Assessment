import sys, os, pickle
sys.path.insert(0, '/home/claude')
import build
from students import BATCH1
from gen_students import BATCHES

allst = []
groups = [(1, BATCH1)] + [(b, BATCHES[b]) for b in (2, 3, 4, 5)]
for b, lst in groups:
    d = '/mnt/user-data/outputs/batch%d/answer_sheets' % b
    os.makedirs(d, exist_ok=True)
    for st in lst:
        st['batch'] = b
        fname, nt = build.build_pdf(st, d)
        pm, log = build.marks_for(st)
        st['_pm'], st['_log'], st['_pdf'], st['_typos'] = pm, log, fname, nt
        qs = {q: sum(pm.get(q + p, 0) for p in 'abcd') for q in ['Q1', 'Q2', 'Q3', 'Q4']}
        counted = {q: (0 if q in st['struck'] else qs[q]) for q in qs}
        order = sorted(counted, key=lambda q: -counted[q])[:3]
        best3 = sum(counted[q] for q in order)
        if b > 1:
            note = DESC_NOTE = ''
            if st['struck']:
                unstruck = sorted(qs.values(), reverse=True)[:3]
                note = 'Struck-out %s (raw %.1f) must not count; counted total %.1f vs %.1f if strike ignored. ' % (
                    st['struck'][0], qs[st['struck'][0]], best3, sum(unstruck))
            elif len(st['attempt']) == 4:
                drop = [q for q in qs if q not in order][0]
                note = 'All four attempted: %s (%.1f) is the lowest and must be dropped. ' % (drop, qs[drop])
            elif len(st['attempt']) < 3:
                note = 'Only %d question(s) attempted: remaining counted slot(s) score 0. ' % len(st['attempt'])
            nb = sum(1 for k, v in st['sel'].items() if v == 'bare')
            if nb:
                note += '%d part(s) are bare answers (zero credit). ' % nb
            if any(v in ('ok_2sf', 'ok_nu', 'ok_3sf') for v in st['sel'].values()):
                note += 'Contains unit/significant-figure penalties. '
            if any(v in ('ok_alt', 'ok_approx') for v in st['sel'].values()):
                note += 'Contains a valid alternative answer (should not be penalised). '
            st['tests'] = (note + 'Style: %s.' % ('mixed' if st['arch']=='mixed' else ('verbose' if st['style']=='V' else 'terse'))).strip()
        st['_best3'] = best3
        allst.append(st)
pickle.dump(allst, open('/home/claude/all60.pkl', 'wb'))
tot = [s['_best3'] for s in allst]
print(len(allst), 'sheets; mean', sum(tot)/len(tot), 'min', min(tot), 'max', max(tot))
for s in allst[12:]:
    print(s['id'], s['name'], s['arch'], s['_best3'], 'typos', s['_typos'])
