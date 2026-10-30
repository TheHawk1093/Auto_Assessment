# -*- coding: utf-8 -*-
import random, sys
sys.path.insert(0, '/home/claude')
from content import VAR, MAX
from students import S, BATCH1

NAMES = {
    2: ['Aditya Verma', 'Kavya Menon', 'Siddharth Joshi', 'Nisha Kulkarni', 'Harsh Agarwal', 'Pooja Bhat',
        'Manish Yadav', 'Lakshmi Narayanan', 'Tanvi Deshmukh', 'Gaurav Singh', 'Shreya Pillai', 'Nikhil Rao'],
    3: ['Ritika Chopra', 'Varun Malhotra', 'Aishwarya Hegde', 'Suresh Babu', 'Neha Kapoor', 'Dev Choudhary',
        'Anjali Mishra', 'Pranav Deshpande', 'Swati Jain', 'Imran Sheikh', 'Tejas Naik', 'Bhavna Rathore'],
    4: ['Kunal Thakur', 'Divya Sethi', 'Mohit Saxena', 'Ramya Chandran', 'Ayush Tiwari', 'Sana Qureshi',
        'Yash Bhatt', 'Ishaan Kohli', 'Gayatri Joshi', 'Abhishek Nair', 'Fatima Khan', 'Rajat Mukherjee'],
    5: ['Pallavi Shetty', 'Karan Oberoi', 'Meghna Ghosh', 'Arvind Krishnamurthy', 'Trisha Dutta', 'Zoya Ansari',
        'Harini Sundaram', 'Omkar Patil', 'Naveen Kumar', 'Shalini Pandey', 'Vivek Rao', 'Ankita Sinha'],
}

COMP = {
    2: ['topper', 'strong', 'strong', 'average', 'average', 'average', 'weak', 'weak', 'bare', 'two_q', 'strike', 'all4'],
    3: ['topper', 'strong', 'strong', 'average', 'average', 'average', 'weak', 'units', 'chatty', 'two_q', 'strike', 'all4'],
    4: ['strong', 'strong', 'average', 'average', 'average', 'weak', 'weak', 'bare', 'chatty', 'mixed', 'strike', 'one_q'],
    5: ['topper', 'strong', 'average', 'average', 'average', 'weak', 'units', 'bare', 'chatty', 'mixed', 'strike', 'all4'],
}

DESC = {
    'topper': 'Topper: complete, well-organised answers; at most one tiny slip',
    'strong': 'Strong: mostly correct with a couple of slips',
    'average': 'Average: several calculation/sign/unit mistakes, partial credit in many parts',
    'weak': 'Weak: conceptual misunderstandings in most parts',
    'bare': 'Minimal-working student: several parts are final answers only (no formula)',
    'two_q': 'Attempted only two questions (third counted question scores 0)',
    'strike': 'Attempted all four and struck out one question',
    'all4': 'Attempted all four, no strike-out (best three must be picked)',
    'units': 'Careless with units / significant figures (instructions 6-7)',
    'chatty': 'Chatty, rambling and wordy, with self-doubt and filler text',
    'mixed': 'Inconsistent: some parts long, some one-liners',
    'one_q': 'Attempted only one question (two counted slots score 0)',
}
ERR_P = {'topper': 0.04, 'strong': 0.22, 'average': 0.55, 'weak': 0.85, 'bare': 0.4, 'two_q': 0.35,
         'strike': 0.35, 'all4': 0.35, 'units': 0.3, 'chatty': 0.45, 'mixed': 0.45, 'one_q': 0.45}
TYPO = {'topper': 0.05, 'strong': 0.10, 'average': 0.25, 'weak': 0.40, 'bare': 0.40, 'two_q': 0.20,
        'strike': 0.20, 'all4': 0.15, 'units': 0.30, 'chatty': 0.30, 'mixed': 0.25, 'one_q': 0.25}

CH_PRE = {
    'Q1': ["Okay Q1 first, seems doable. Writing everything out slowly.", "Let me think... camera question, I did something like this in the tutorial.", "Starting with this one because it looks the shortest."],
    'Q2': ["Hmm pendulum question again. Lets see what we can do.", "I think I know the first two parts, the third one is tricky.", "Alright, joint model. Writing the given values first."],
    'Q3': ["Observer question. I remember the idea from class, hope I get the algebra right.", "This looks long but I will try.", "OK last attempt at the observer, let me be careful with signs."],
    'Q4': ["Last question, not much time left so I might rush.", "Integral action, this one I actually like.", "Hmm, the first part looks easy, second part is a bit weird."],
}
CH_POST = ["(not sure about this, moving on)", "I think this is right but will recheck if time permits.",
           "Sorry if the handwriting is bad here, please read carefully.", "Skipping the check, running out of time. Hope partial marks are given for method.",
           "Honestly not 100% confident about the last step."]
POOL_POST = {
    'Q1': ["Sanity check: a 160 mm field of view across 1280 pixels is plausible for a 400 mm standoff and a 16 mm lens.",
           "Note: a longer lens would shrink the field of view in proportion (FOV ∝ 1/f)."],
    'Q2': ["Note: K<sub>d</sub> does not influence the steady-state angle because §t = 0 there.",
           "Remark: the sag of a PD loop under gravity shrinks as K<sub>p</sub> is increased."],
    'Q3': ["Note: observer poles are usually placed several times faster than the controller poles.",
           "Sampling at 1 kHz is fast compared with the 10 rad/s observer bandwidth, so discretisation effects are small."],
    'Q4': ["Note: the integrator adds one state, so the loop becomes third order.",
           "Remark: with integral action the exact value of N<sub>ff</sub> matters less because the integrator enforces tracking."],
}
POOL_POST = {k: [t for t in v] for k, v in POOL_POST.items()}


def keys_for(q, p):
    return [k for (qq, pp, k) in VAR if qq == q and pp == p]


def pick_error(q, p, rng, weak=False):
    ks = [k for k in keys_for(q, p) if not k.startswith('ok') and k != 'bare']
    if not ks:
        return None
    if weak:
        w = [(MAX[(q, p)] - VAR[(q, p, k)]['m']) + 0.3 for k in ks]
        return rng.choices(ks, weights=w)[0]
    return rng.choice(ks)


def make_student(idx, name, arch, rng):
    sid = 'S%02d' % idx
    roll = 'ME25M%03d' % idx
    qs = ['Q1', 'Q2', 'Q3', 'Q4']
    if arch in ('strike', 'all4'):
        attempt = qs[:]
    elif arch == 'two_q':
        attempt = sorted(rng.sample(qs, 2))
    elif arch == 'one_q':
        attempt = [rng.choice(qs)]
    else:
        attempt = sorted(rng.sample(qs, 3))
    style = {'topper': 'V', 'weak': 'T', 'bare': 'T', 'units': 'T', 'chatty': 'V', 'strike': 'V', 'all4': 'V'}.get(
        arch, rng.choice(['V', 'T']))
    sel = {}
    nerr = 0
    struck = [rng.choice(attempt)] if arch == 'strike' else []
    for q in attempt:
        for p in 'abcd':
            if (q, p) not in MAX:
                continue
            k = q + p
            ks = keys_for(q, p)
            choice = 'ok'
            if arch == 'bare' and 'bare' in ks and rng.random() < 0.75:
                choice = 'bare'
            elif arch == 'units' and rng.random() < 0.7 and any(x in ks for x in ('ok_2sf', 'ok_nu', 'ok_3sf')):
                choice = [x for x in ('ok_2sf', 'ok_nu', 'ok_3sf') if x in ks][0]
            elif rng.random() < ERR_P[arch]:
                e = pick_error(q, p, rng, weak=(arch == 'weak'))
                if e:
                    choice = e
            elif arch in ('strong', 'topper', 'average') and 'ok_alt' in ks and rng.random() < 0.3:
                choice = 'ok_alt'
            elif arch in ('strong', 'average') and 'ok_approx' in ks and rng.random() < 0.3:
                choice = 'ok_approx'
            if arch == 'mixed' and choice == 'ok':
                choice = rng.choice(['ok_T', 'ok_V'])
            if choice not in ('ok',) and not choice.startswith('ok'):
                nerr += 1
            sel[k] = choice
    # non-toppers get at least one real error
    counted_err = sum(1 for k, v in sel.items() if not v.startswith('ok') and v != 'bare' and k[:2] not in struck)
    if arch != 'topper' and counted_err == 0:
        for q in [x for x in attempt if x not in struck]:
            p = rng.choice('abcd')
            if (q, p) in MAX:
                e = pick_error(q, p, rng)
                if e:
                    sel[q + p] = e
                    break
    pre, post = {}, {}
    if arch == 'chatty':
        for q in attempt:
            pre[q] = [rng.choice(CH_PRE[q])]
            if rng.random() < 0.7:
                post[q] = [rng.choice(CH_POST)]
    elif style == 'V' and arch in ('topper', 'strong', 'all4', 'strike', 'two_q', 'average', 'mixed'):
        for q in rng.sample(attempt, min(len(attempt), rng.choice([1, 2]))):
            post[q] = [rng.choice(POOL_POST[q])]
    if struck:
        post.setdefault(struck[0], []).append("(Cancelled - please do not evaluate this question.)")
    st = S(sid, name, roll, DESC[arch], style, TYPO[arch], attempt, struck, sel, '', pre, post)
    st['arch'] = arch
    return st


def build_batches():
    out = {}
    idx = 13
    for b in (2, 3, 4, 5):
        rng = random.Random(1000 + b)
        lst = []
        for name, arch in zip(NAMES[b], COMP[b]):
            lst.append(make_student(idx, name, arch, rng))
            idx += 1
        out[b] = lst
    return out


BATCHES = build_batches()
if __name__ == '__main__':
    seen = set()
    allst = [s for b in BATCHES.values() for s in b]
    for s in allst:
        sig = tuple(sorted(s['sel'].items())) + tuple(s['attempt']) + tuple(s['struck'])
        assert sig not in seen
        seen.add(sig)
    print(len(allst), 'students, all distinct')
    for s in allst:
        print(s['id'], s['name'], s['arch'], s['style'], s['attempt'], s['struck'])
