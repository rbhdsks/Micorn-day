#!/usr/bin/env python3
"""Reproduce Notes sections4.4-4.6 arithmetic, not cache policy performance."""
import math,json,csv
from pathlib import Path
FACTORS={
 1:([[.2],[.4],[.1]],[[.3],[.5],[.2]]),
 2:([[.2,.1],[.4,.2],[.1,.3]],[[.3,.2],[.5,.1],[.2,.4]]),
 3:([[.2,.1,.3],[.4,.2,.1],[.1,.3,.2]],[[.3,.2,.1],[.5,.1,.4],[.2,.4,.2]])}
OBSERVATIONS=[([0,1],0),([0,1],0),([0,1],1),([0,2],2),([1,2],1),([0,1,2],1)]

def probabilities(target,context,available):
    if not available or len(set(available))!=len(available):raise ValueError('choice set must be nonempty and unique')
    n=len(target)
    if n!=len(context) or not n or any(not 0<=i<n for i in available):raise ValueError('invalid alternatives')
    r=len(target[0])
    if r<1 or any(len(x)!=r for x in target+context):raise ValueError('inconsistent factors')
    scores={x:sum(sum(a*b for a,b in zip(target[x],context[z])) for z in available if z!=x) for x in available}
    maximum=max(scores.values());weights={x:math.exp(s-maximum) for x,s in scores.items()};total=sum(weights.values())
    return {x:w/total for x,w in weights.items()}

def evaluate():
    records=[]
    for rank,(t,c) in FACTORS.items():
        chosen=[probabilities(t,c,s)[y] for s,y in OBSERVATIONS]
        records.append({'rank':rank,'chosen_probabilities':chosen,'mean_nll':-sum(math.log(p) for p in chosen)/len(chosen),
                        'interpretation':'illustrative initial factors from supplied Notes, not fitted models or cache results'})
    return records

def main():
    out=Path(__file__).resolve().parent/'results';out.mkdir(exist_ok=True)
    records=evaluate();(out/'illustrative_choices.json').write_text(json.dumps(records,indent=2)+'\n')
    with (out/'chosen_probabilities.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['observation','choice_set','chosen','rank_1','rank_2','rank_3'])
        for i,(s,y) in enumerate(OBSERVATIONS):w.writerow([i+1,','.join('ABJ'[x] for x in s),'ABJ'[y],*[r['chosen_probabilities'][i] for r in records]])
    with (out/'parameter_storage.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['items','model','rank','trainable_entries','float64_mib','kind'])
        for n in [250,500,1000,2000,3000,5000]:
            for rank in [0,1,2,3]:
                entries=n*n if rank==0 else 2*n*rank
                w.writerow([n,'full' if rank==0 else f'rank_{rank}',rank,entries,8*entries/2**20,'analytic storage, not measured process memory'])
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
