#!/usr/bin/env python3
"""Common-tool generic cost comparison, functional and instrumented views."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
REPO=Path(__file__).resolve().parents[3]
OUT=REPO/'Phase2/build/synthesis'
CONFIG={'stride':None,'global_buffer':(0,0,0),'region_buffer':(1,0,0),'context_feedback':(1,1,0),'victim_buffer':(0,0,1)}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--yosys',default=os.environ.get('YOSYS','yosys'));a=p.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 sources=[*sorted((REPO/'Phase1/level4/rtl').glob('*.sv')),*sorted((REPO/'Phase2/level4/rtl').glob('*.sv'))]
 wrapper=REPO/'Phase2/level4/vivado/fpga_cache_top.sv';sources.append(wrapper)
 version=subprocess.check_output([a.yosys,'-V'],text=True).strip();records=[]
 for name,config in CONFIG.items():
  for view in ['functional','instrumented']:
   stem=f'{name}_{view}';script=OUT/f'{stem}.ys';stats=OUT/f'{stem}.json';log=OUT/f'{stem}.log'
   commands=['read_verilog -sv '+' '.join(json.dumps(str(s)) for s in sources)]
   if config is None:
    if view=='functional':
     # Same functional port list, debug statistics unconnected.
     text=wrapper.read_text();start=text.index(' ai_cache_context #(');end=text.index('\nendmodule')
     inst=' ai_cache #(.INDEX_BITS(INDEX_BITS),.PREFETCH_POLICY(1)) cache(\n'
     inst+='  .clk(clk),.rst(rst),.prefetch_enable(prefetch_enable),\n'
     for port in ['cpu_req_valid','cpu_req_ready','cpu_req_addr','cpu_rsp_valid','cpu_rsp_ready','cpu_rsp_data','mem_req_valid','mem_req_ready','mem_req_addr','mem_rsp_valid','mem_rsp_ready','mem_rsp_data']:
      inst+=f'  .{port}({port}),\n'
     inst+='  .stat_access(),.stat_hit(),.stat_miss(),.stat_pf_issued(),.stat_pf_useful(),.stat_pf_unused());'
     generated=OUT/'baseline_cost_top.sv';generated.write_text(text[:start].replace('fpga_cache_top','baseline_cost_top')+inst+text[end:])
     commands+=['read_verilog -sv '+json.dumps(str(generated))];top='baseline_cost_top'
    else:top='ai_cache'
   else:
    top='fpga_cache_top' if view=='functional' else 'ai_cache_context'
    for key,value in zip(['REGION_ENABLE','FEEDBACK_ENABLE','VICTIM_ENABLE'],config):commands.append(f'chparam -set {key} {value} {top}')
   commands += [f'hierarchy -check -top {top}',f'synth -top {top}','check -assert','tee -o '+json.dumps(str(stats))+' stat -json']
   script.write_text('\n'.join(commands)+'\n')
   run=subprocess.run([a.yosys,'-l',str(log),'-s',str(script)],cwd=REPO,capture_output=True,text=True)
   (OUT/f'{stem}.console.log').write_text(run.stdout+run.stderr);run.check_returncode()
   data=json.loads(stats.read_text());design=data.get('design',data['modules']['\\'+top])
   records.append({'variant':name,'view':view,'generic_cells':design['num_cells'],'wire_bits':design['num_wire_bits'],'check_problems':0})
   print('PASS',stem,design['num_cells'],'generic cells',flush=True)
 result={'tool':version,'command':'synth -top TOP; check -assert; stat -json','measurements':records,
  'source_sha256':{str(s.relative_to(REPO)):hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},
  'limits':['Generic mapped cells are tool-dependent, not FPGA LUTs or process area','Functional wrappers disconnect debug counters; instrumented view retains all counters','No target timing, placement, power or bitstream result']}
 (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
