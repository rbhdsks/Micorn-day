#!/usr/bin/env python3
"""Explain accepted-line predictor state; this is not a cycle or cache simulator."""
import argparse
import json
from dataclasses import dataclass

MAX_LINE=(1<<28)-1
@dataclass
class Predictor:
    policy: str='stride'
    seen: bool=False
    last_line: int=0
    stride: int=0
    confidence: int=0
    def __post_init__(self):
        if self.policy not in ('stride','next_line'):raise ValueError('unknown policy')
    def observe(self,line,enable=True):
        if type(line) is not int or not 0<=line<=MAX_LINE:raise ValueError('line outside 28-bit space')
        before={'seen':self.seen,'last_line':self.last_line,'stride':self.stride,'confidence':self.confidence}
        candidate=None;delta=None;action='same_line_ignored'
        if not self.seen or line!=self.last_line:
            if self.policy=='next_line':
                action='next_line'
                if enable and line<MAX_LINE:candidate=line+1
            elif not self.seen:
                self.stride=0;self.confidence=0;action='first_line'
            else:
                delta=line-self.last_line
                if delta==self.stride and delta!=0:
                    predicted=line+self.stride
                    if enable and self.confidence>=1 and 0<=predicted<=MAX_LINE:candidate=predicted
                    self.confidence=min(3,self.confidence+1);action='matching_delta'
                else:self.stride=delta;self.confidence=1;action='new_stride'
            self.seen=True;self.last_line=line
        return {'line':line,'before':before,'delta':delta,'action':action,'candidate':candidate,
                'after':{'seen':self.seen,'last_line':self.last_line,'stride':self.stride,'confidence':self.confidence}}

def walk(lines,policy='stride'):
    p=Predictor(policy);return [p.observe(x) for x in lines]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy',choices=['stride','next_line'],default='stride')
    parser.add_argument('--lines',nargs='+',type=lambda s:int(s,0))
    parser.add_argument('--demo',action='store_true');parser.add_argument('--json',action='store_true');parser.add_argument('--output')
    a=parser.parse_args();records=walk(a.lines or [100,100,104,108,112,90,68],a.policy)
    text=json.dumps(records,indent=2) if a.json else '\n'.join(f"line={r['line']:>9} delta={str(r['delta']):>7} confidence={r['after']['confidence']} candidate={str(r['candidate']):>9} {r['action']}" for r in records)
    if a.output:
        from pathlib import Path
        Path(a.output).write_text(text+'\n')
    print(text)
if __name__=='__main__':main()
