#!/usr/bin/env python3
"""Execute print-oriented standard-Python notebook cells and retain actual output.
No IPython magics or hidden expression-display emulation. Existing Level 1 is unchanged.
"""
import contextlib,io,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    paths=[ROOT/x for x in ['level2/cache_architecture.ipynb','level3/prefetch_walkthrough.ipynb','level4/rtl_walkthrough.ipynb','level5/results_walkthrough.ipynb','research/cdm/cdm_walkthrough.ipynb']]
    os.chdir(ROOT)
    for path in paths:
        doc=json.loads(path.read_text());scope={'__name__':'__notebook__'};count=0
        for cell in doc['cells']:
            if cell['cell_type']!='code':continue
            count+=1;output=io.StringIO()
            with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
                exec(compile(''.join(cell['source']),path.name,'exec'),scope)
            cell['execution_count']=count;cell['outputs']=[{'output_type':'stream','name':'stdout','text':output.getvalue().splitlines(True)}] if output.getvalue() else []
        path.write_text(json.dumps(doc,indent=1)+'\n');print('Executed',path.relative_to(ROOT),count,'code cells')
if __name__=='__main__':main()
