function generate_deep_analysis()
% Measured RTL figures and analytical tradeoff views. Base MATLAB operations
% only; also executed with GNU Octave. No Statistics Toolbox or fitted model.
root=fileparts(fileparts(mfilename('fullpath')));
d=fullfile(root,'analysis','data');out=fullfile(root,'plots');
if ~exist(out,'dir'),mkdir(out);end
cases=lines_of(fullfile(d,'cases.txt'));variants=lines_of(fullfile(d,'variants.txt'));
families=lines_of(fullfile(d,'families.txt'));meta=dlmread(fullfile(d,'meta.csv'),',');
S=loadmatrix(d,'speedup');D=loadmatrix(d,'dram_ratio');C=loadmatrix(d,'completion_cycles');
reads=loadmatrix(d,'dram_reads');H=loadmatrix(d,'demand_hit_rate');HB=loadmatrix(d,'service_hit_rate');
T=loadmatrix(d,'timely_useful');L=loadmatrix(d,'late_useful');W=loadmatrix(d,'unused_evicted');R=loadmatrix(d,'resident_unconsumed');
issued=loadmatrix(d,'prefetch_issued');P95=loadmatrix(d,'p95_offer_latency');
assert(all(all(abs(S-repmat(C(:,1),1,7)./C)<1e-12)),'Speedup mismatch');
assert(all(all(abs(D-reads./repmat(reads(:,1),1,7))<1e-12)),'Traffic mismatch');
assert(all(all(issued==T+L+W+R)),'Prefetch fate conservation mismatch');
colors=[.38 .46 .55;.91 .48 .31;.38 .46 .78;.59 .40 .65;.52 .65 .33;.00 .52 .55;.15 .30 .42];
set(0,'defaultfigurevisible','off','defaultaxesfontname','Arial','defaultaxesfontsize',11,'defaulttextfontname','Arial','defaultaxesgridcolor',[.86 .88 .89],'defaultaxesposition',[.22 .22 .72 .66]);
held=meta(:,1)==2;valid=meta(:,1)==1;allcases=true(size(held));
% 01: Frozen validation selection and its untouched held-out outcome.
g=zeros(2,7);traffic=zeros(2,7);
for k=1:7,g(1,k)=balanced(S(:,k),meta,valid);g(2,k)=balanced(S(:,k),meta,held);traffic(1,k)=balanced(D(:,k),meta,valid);traffic(2,k)=balanced(D(:,k),meta,held);end
f=canvas(1350,650);plot(1:7,g(1,:),'o-','Color',colors(1,:),'LineWidth',1.5);hold on;plot(1:7,g(2,:),'s-','Color',colors(6,:),'LineWidth',1.5);
set(gca,'XTick',1:7,'XTickLabel',pretty(variants));ylabel('Family balanced geometric mean speedup');
title('Validation choice and held out performance');plotkey({'Validation','Held out'},colors([1 6],:));ylim([.96 1.11]);grid on;
savefigs(f,out,'01_validation_and_held_out');
% 02: No single tested variant dominates every objective. Labels are evidence.
f=canvas(1100,680);hold on;
for k=[1 2 4 5 6],plot(traffic(2,k),g(2,k),'o','MarkerSize',9,'MarkerFaceColor',colors(k,:),'Color',colors(k,:));end
text(.72,1.045,'Victim buffer','Color',colors(4,:));text(1.55,1.062,'Next line','Color',colors(2,:));text(1.09,1.023,'Region and feedback coincide','Color',colors(6,:));text(1.015,1.005,'Stride and global buffer coincide','Color',colors(5,:));text(.94,.998,'None','Color',colors(1,:));
plot([min(traffic(2,:)) 1.65],[1 1],'k:');xlabel('Family balanced memory transaction ratio');ylabel('Family balanced completion speedup');
title('Held out time and traffic tradeoff');xlim([.65 1.8]);ylim([.995 1.075]);grid on;savefigs(f,out,'02_held_out_pareto');
% 03: Every primary case and variant remains visible, including slowdowns.
f=canvas(1450,1550);imagesc(log2(S));colormap(diverging());cb=colorbar;
set(gca,'XTick',1:7,'XTickLabel',pretty(variants),'YTick',1:numel(cases),'YTickLabel',strrep(cases,'_',' '),'FontSize',8);
set(gca,'Position',[.34 .12 .53 .80]);set(cb,'Position',[.91 .15 .025 .70]);title('All 55 cases log2 completion speedup positive means faster');caxis([-1 1]);savefigs(f,out,'03_all_case_heatmap');
% 04: Five held-out families receive equal aggregate weight.
ids=unique(meta(held,2));familyValues=zeros(numel(ids),7);
for j=1:numel(ids),for k=1:7,familyValues(j,k)=gm(S(held&meta(:,2)==ids(j),k));end,end
f=canvas(1350,700);b=barh(familyValues);stylebars(b,colors);set(gca,'YTick',1:numel(ids),'YTickLabel',pretty(families(ids)));xlabel('Geometric mean speedup');title('Held out families favor different mechanisms');plotkey(pretty(variants),colors);grid on;savefigs(f,out,'04_held_out_families');
% 05: ECDF represents finite cases. It is not a population confidence interval.
f=canvas(1200,650);hold on;
for k=2:7,x=sort(S(:,k));stairs(x,(1:numel(x))/numel(x),'LineWidth',1.5,'Color',colors(k,:));end
plot([1 1],[0 1],'k:');xlabel('Completion speedup');ylabel('Fraction of the 55 declared cases');title('Gain and regression distribution');plotkey(pretty(variants(2:7)),colors(2:7,:));grid on;savefigs(f,out,'05_case_speedup_distribution');
% 06: Per-run request p95, nearest-rank estimator, normalized to paired reference.
rat=P95./repmat(P95(:,1),1,7);v=zeros(numel(ids),7);
for j=1:numel(ids),for k=1:7,v(j,k)=gm(rat(held&meta(:,2)==ids(j),k));end,end
f=canvas(1350,700);b=barh(v);stylebars(b,colors);set(gca,'YTick',1:numel(ids),'YTickLabel',pretty(families(ids)));xlabel('Geometric mean of per case p95 offered latency ratios');title('Tail latency of requests in each replay');plotkey(pretty(variants),colors);grid on;savefigs(f,out,'06_p95_offered_latency');
% 07: Main cache hits and immediate subsystem service have distinct definitions.
ix=find(strcmp(cases,'legacy_interleaved_conflicting'));f=canvas(1250,650);b=bar([H(ix,:)' HB(ix,:)']);stylebars(b,colors([1 6],:));set(gca,'XTick',1:7,'XTickLabel',pretty(variants));ylabel('Demand fraction');title('Conflicting streams main cache versus immediate buffer service');plotkey({'Main cache hit rate','Cache plus timely buffer hit rate'},colors([1 6],:));ylim([0 1]);grid on;savefigs(f,out,'07_cache_and_service_hits');
% 08: Fates conserve only after the declared natural quiescent drain.
chosen={'legacy_column_stride','legacy_interleaved_conflicting','legacy_three_line_bursts','legacy_zero_gap_stream','legacy_pollution_return'};
ix=case_indices(cases,chosen);f=canvas(1250,650);b=barh([T(ix,7) L(ix,7) W(ix,7) R(ix,7)],'stacked');stylebars(b,colors([6 1 2 5],:));set(gca,'YTick',1:numel(ix),'YTickLabel',pretty(chosen));xlabel('Issued prefetch transactions');title('Context feedback prefetch outcomes');plotkey({'Timely','Late','Unused replaced','Resident unresolved'},colors([6 1 2 5],:));grid on;savefigs(f,out,'08_prefetch_fates');
% 09: Absolute values avoid exaggerating ratios from a four-read baseline.
ix=find(strcmp(cases,'legacy_pollution_return'));f=canvas(1350,600);
panel(1,2,1);barh(C(ix,:),'FaceColor',colors(6,:));set(gca,'YTick',1:7,'YTickLabel',pretty(variants),'FontSize',8);xlabel('Completion cycles');title('Hot line pollution probe');grid on;
panel(1,2,2);barh(reads(ix,:),'FaceColor',colors(2,:));set(gca,'YTick',1:7,'YTickLabel',pretty(variants),'FontSize',8);xlabel('Total memory line reads');title('Four demanded lines with speculative interference');grid on;savefigs(f,out,'09_pollution_repair');
% 10: Region history has both a benefit and a retraining cost.
chosen={'legacy_interleaved_conflicting','legacy_two_stream_disjoint_sets','legacy_column_stride','boundary_crossing_g0_l48'};ix=case_indices(cases,chosen);
f=canvas(1350,700);b=barh(S(ix,[3 4 5 6 7]));stylebars(b,colors([3 4 5 6 7],:));set(gca,'YTick',1:numel(ix),'YTickLabel',pretty(chosen));xlabel('Completion speedup');title('Region separation and boundary counterexamples');plotkey(pretty(variants([3 4 5 6 7])),colors([3 4 5 6 7],:));grid on;savefigs(f,out,'10_context_counterexamples');
% 11: Stress matrix describes this service model, not physical DRAM bandwidth.
ix=find(meta(:,1)==4);f=canvas(1350,750);imagesc(S(ix,[2 3 4 5 6 7]));colorbar;colormap(diverging());caxis([.5 1.5]);set(gca,'XTick',1:6,'XTickLabel',pretty(variants(2:7)),'YTick',1:numel(ix),'YTickLabel',pretty(cases(ix)));title('Declared latency gap and boundary stress cases');savefigs(f,out,'11_timing_and_boundary_stress');
% 12: Completed mature outcomes and unresolved residents are different signals.
path=fullfile(d,'legacy_pollution_return__context_feedback.csv');q=dlmread(path,',',1,0);baseq=dlmread(fullfile(d,'legacy_pollution_return__region_buffer.csv'),',',1,0);
f=canvas(1300,720);panel(2,1,1);stairs(q(:,1),q(:,6),'Color',colors(7,:),'LineWidth',1.5);ylim([-.1 3.2]);ylabel('Global quality counter');title('Observed feedback state on the pollution replay');grid on;
panel(2,1,2);plot(q(:,1),q(:,7),'Color',colors(7,:),'LineWidth',1.5);hold on;plot(baseq(:,1),baseq(:,7),'Color',colors(6,:),'LineWidth',1.5);plot(q(:,1),q(:,8),'Color',colors(2,:),'LineWidth',1.5);xlabel('Accepted demand index');ylabel('Cumulative count');plotkey({'Feedback issued','Region issued','Feedback suppressed'},colors([7 6 2],:));grid on;savefigs(f,out,'12_feedback_state_and_issues');
% 13: Two declared costs. Lambda is a preference, not a memory energy model.
lambdas=linspace(0,60,121);cost=zeros(numel(lambdas),7);
for j=1:numel(lambdas),J=C+lambdas(j)*reads;for k=1:7,cost(j,k)=balanced(J(:,1)./J(:,k),meta,held);end,end
f=canvas(1250,650);hold on;for k=2:7,plot(lambdas,cost(:,k),'Color',colors(k,:),'LineWidth',1.5);end
xlabel('Assumed penalty lambda in cycles per line transaction');ylabel('Family balanced geometric mean J reference / J variant');title('Analytical sensitivity J equals cycles plus lambda times transactions');plotkey(pretty(variants(2:7)),colors(2:7,:));grid on;savefigs(f,out,'13_declared_transaction_cost_sensitivity');
% 14: Sensitivity is validation-only and never changes the sealed threshold.
ps=dlmread(fullfile(d,'probe_sensitivity.csv'),',');values=zeros(3,2);
intervals=[8 16 32];
for j=1:3,mask=ps(:,2)==intervals(j);values(j,:)=[gm(ps(mask,3)) gm(ps(mask,4))];end
f=canvas(1100,600);b=bar(values);stylebars(b,colors([6 2],:));set(gca,'XTick',1:3,'XTickLabel',{'8','16 frozen','32'});xlabel('Recovery probe interval');title('Validation only probe interval sensitivity');plotkey({'Speedup geometric mean','Traffic ratio geometric mean'},colors([6 2],:));grid on;savefigs(f,out,'14_probe_sensitivity');
% 15: Dataset coverage records provenance classes, not diversity guarantees.
counts=zeros(numel(families),4);for j=1:numel(families),for k=1:4,counts(j,k)=sum(meta(:,2)==j&meta(:,1)==k);end,end
f=canvas(1300,650);b=barh(counts,'stacked');stylebars(b,colors([6 3 1 2],:));set(gca,'YTick',1:numel(families),'YTickLabel',pretty(families));xlabel('Replay cases');title('Declared dataset coverage and split counts');plotkey({'Validation','Held out','Legacy regression','Stress'},colors([6 3 1 2],:));grid on;savefigs(f,out,'15_dataset_coverage');
% 16: Scalar aggregates never replace mechanism-level ablations.
chosen={'legacy_interleaved_conflicting','legacy_pollution_return','legacy_three_line_bursts','legacy_column_stride'};ix=case_indices(cases,chosen);
gain=[C(ix,3)-C(ix,5),C(ix,5)-C(ix,6),C(ix,6)-C(ix,7)];
f=canvas(1350,680);b=barh(gain);stylebars(b,colors([5 6 7],:));set(gca,'YTick',1:numel(ix),'YTickLabel',pretty(chosen));xlabel('Paired completion cycles saved positive is improvement');title('Incremental buffer region and feedback contributions');plotkey({'Stride to global buffer','Global to region buffer','Region to feedback'},colors([5 6 7],:));grid on;savefigs(f,out,'16_incremental_ablation');
% 17: Actual signal samples from independent memory simulation.
path=fullfile(d,'fsm_wave.csv');
if exist(path,'file')
 q=dlmread(path,',',1,0);mask=q(:,1)>=5&q(:,1)<=100;q=q(mask,:);f=canvas(1350,780);
 panel(3,1,1);stairs(q(:,1),q(:,2),'LineWidth',1.5,'Color',colors(7,:));set(gca,'YTick',[0 1 2],'YTickLabel',{'IDLE','SEND','WAIT'});ylim([-.2 2.3]);title('Independent simulation FSM and memory handshake');grid on;
 panel(3,1,2);stairs(q(:,1),q(:,7),'Color',colors(6,:));hold on;stairs(q(:,1),q(:,8)+1.3,'Color',colors(2,:));set(gca,'YTick',[0 1 1.3 2.3],'YTickLabel',{'valid0','valid1','ready0','ready1'});ylabel('Request channel');grid on;
 panel(3,1,3);stairs(q(:,1),q(:,9),'Color',colors(3,:));hold on;stairs(q(:,1),q(:,10)+1.3,'Color',colors(5,:));set(gca,'YTick',[0 1 1.3 2.3],'YTickLabel',{'valid0','valid1','ready0','ready1'});ylabel('Response channel');xlabel('Simulation cycle');grid on;savefigs(f,out,'17_fsm_handshake_trace');
end
% 18: Generic synthesis compares common tool and scripts, not FPGA LUTs.
path=fullfile(d,'generic_cells.csv');
if exist(path,'file')
 q=dlmread(path,',');f=canvas(1200,650);b=bar(q);stylebars(b,colors([6 1],:));set(gca,'XTick',1:5,'XTickLabel',{'Stride','Victim','Global buffer','Region buffer','Feedback'});ylabel('Common tool generic cells');title('Functional core and exposed debug instrumentation');plotkey({'Functional counters pruned','Instrumented'},colors([6 1],:));grid on;savefigs(f,out,'18_generic_synthesis_cost');
end
% Independent aggregate export permits direct comparison against Python CSV.
dlmwrite(fullfile(out,'matlab_aggregate_checks.csv'),[g traffic],',','precision','%.17g');
fprintf('Completed measured and analytical figures with %s\n',version);
end
function a=loadmatrix(d,name),a=dlmread(fullfile(d,[name '.csv']),',');end
function v=gm(x),assert(~isempty(x)&&all(x>0));v=exp(mean(log(x)));end
function v=balanced(x,meta,mask)
 ids=unique(meta(mask,2));z=zeros(size(ids));for j=1:numel(ids),z(j)=gm(x(mask&meta(:,2)==ids(j)));end;v=gm(z);
end
function x=lines_of(path),fid=fopen(path);assert(fid>=0);c=textscan(fid,'%s','Delimiter','\n');fclose(fid);x=c{1};end
function x=pretty(x),for j=1:numel(x),x{j}=strrep(x{j},'_',' ');end,end
function ix=case_indices(cases,chosen),ix=zeros(numel(chosen),1);for j=1:numel(chosen),k=find(strcmp(cases,chosen{j}));assert(numel(k)==1,['Missing case ' chosen{j}]);ix(j)=k;end,end
function f=canvas(w,h)
 f=figure('Color','w','Position',[40 40 w h]);
 % Homebrew Octave may reset its default toolkit at figure creation. Select
 % the export toolkit on this figure explicitly; MATLAB never enters here.
 if exist('OCTAVE_VERSION','builtin'),graphics_toolkit(f,'gnuplot');end
end
function stylebars(b,c),for j=1:numel(b),set(b(j),'FaceColor',c(j,:));end,end
function c=diverging(),a=[.84 .37 .25];b=[.98 .98 .96];z=[.00 .50 .55];c=[a+(b-a).*(linspace(0,1,64)');b+(z-b).*(linspace(0,1,64)')];end
function savefigs(f,out,name)
 fprintf('Exporting %s\n',name);
 layout=getappdata(f,'panel_layout');for k=1:size(layout,1),set(layout{k,1},'Position',layout{k,2});end
 set(f,'PaperPositionMode','auto');drawnow;
 print(f,fullfile(out,[name '.png']),'-dpng','-r160');
 print(f,fullfile(out,[name '.pdf']),'-dpdf','-bestfit');close(f);
end

function plotkey(labels,colors)
 ax=gca;f=gcf;p=get(ax,'Position');set(ax,'Position',[p(1) max(p(2),.20) p(3) min(p(4),.72)]);
 kax=axes('Parent',f,'Position',[.12 .005 .84 .10]);axis(kax,[0 1 0 1]);axis(kax,'off');hold(kax,'on');
 n=numel(labels);columns=min(4,n);rows=ceil(n/columns);
 for j=1:n,x=mod(j-1,columns)/columns;y=1-(floor((j-1)/columns)+.5)/rows;plot(kax,[x x+.025],[y y],'LineWidth',4,'Color',colors(j,:));text(kax,x+.035,y,labels{j},'FontSize',10,'Interpreter','none');end
 axes(ax);
end

function ax=panel(rows,columns,i)
 % Explicit post-creation positions avoid a toolkit subplot-overlap issue.
 ax=axes('Parent',gcf);
 if columns==2,positions=[.20 .20 .28 .68;.69 .20 .28 .68];
 elseif rows==3,positions=[.18 .75 .76 .17;.18 .45 .76 .17;.18 .15 .76 .17];
 else,positions=[.18 .59 .76 .30;.18 .20 .76 .29];end
 set(ax,'Position',positions(i,:));
 f=gcf;layout=getappdata(f,'panel_layout');if isempty(layout),layout=cell(0,2);end;layout(end+1,:)={ax,positions(i,:)};setappdata(f,'panel_layout',layout);
end
