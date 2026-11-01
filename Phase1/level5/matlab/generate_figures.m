function generate_figures()
%GENERATE_FIGURES Reproduce all nine Phase 1 scientific figure families.
% Requires MATLAB R2020a or later (exportgraphics). Reads retained evidence;
% it does not rerun RTL or train CDM models. MATLAB was unavailable in the
% authoring environment, so this source has not been executed in MATLAB.
base = fileparts(mfilename('fullpath'));
phase = fileparts(fileparts(base));
reference = fullfile(phase,'level5','results','reference');
S = readtable(fullfile(reference,'summary.csv'),'TextType','string');
out = fullfile(phase,'build','matlab_figures');
if ~exist(out,'dir'), mkdir(out); end
policies = ["none","next_line","stride"];
names = unique(S.workload,'sorted');
colors = [102 120 138;237 135 93;22 140 145]/255;
set(groot,'defaultAxesFontName','Arial','defaultAxesFontSize',11);

% Validate the headline formulas against the retained CSV. The denominator
% ends at the final consumed demand response, not speculative quiescence.
assert(all(S.accesses > 0),'Each benchmark must contain demand accesses');
assert(all(abs(S.hits./S.accesses-S.demand_hit_rate) < 1e-12), ...
    'Demand hit rate must equal demand hits / demand accesses');
for i=1:numel(names)
    baseline = select_row(S,names(i),"none");
    for j=1:numel(policies)
        row = select_row(S,names(i),policies(j));
        assert(abs(baseline.completion_cycles/row.completion_cycles-row.speedup) < 1e-12, ...
            'Speedup must use completion cycles with identical end points');
    end
end

% 01-03: Same 13 workloads and values as the published Python gallery.
metrics = ["speedup","demand_hit_rate","mean_accept_to_response_cycles"];
stems = ["01_speedup","02_hit_rate","03_latency"];
titles = ["Completion speedup depends on access pattern", ...
    "Demand hit rate is not execution speedup", ...
    "Response availability includes late-prefetch benefits"];
xlabels = ["No-prefetch completion cycles / policy cycles", ...
    "Demand hits / accepted demand accesses", ...
    "Mean accepted-demand to response-availability cycles"];
for k=1:numel(metrics)
    if k==1, selected=2:3; else, selected=1:3; end
    values = metric_values(S,names,policies(selected),metrics(k));
    f = figure('Color','w','Position',[100 100 1300 780]);
    grouped_horizontal(values,names,policies(selected),colors(selected,:));
    xlabel(xlabels(k)); title(titles(k));
    if k==1, xline(1,'--','Baseline','HandleVisibility','off'); end
    export_family(f,out,stems(k));
end

% 04: Normalize traffic to no-prefetch reads. The four-read pollution baseline
% has a much larger ratio, so show that workload separately in figure 06.
trafficNames = names(names~="pollution_return");
traffic = metric_values(S,trafficNames,policies(2:3),"dram_reads");
baseTraffic = metric_values(S,trafficNames,"none","dram_reads");
traffic = traffic./baseTraffic;
f = figure('Color','w','Position',[100 100 1300 740]);
grouped_horizontal(traffic,trafficNames,policies(2:3),colors(2:3,:));
xline(1,'--','Baseline','HandleVisibility','off');
xlabel('Total DRAM transactions / no-prefetch transactions');
title('Speculation can increase memory traffic');
export_family(f,out,'04_traffic');

% 05: Mutually exclusive stride-prefetch fates after natural quiescence.
fateNames = ["column_stride","phase_shift","tensor_stream", ...
    "three_line_bursts","zero_gap_stream","pollution_return"];
fateFields = ["timely_useful","late_useful","unused_evicted","resident_unconsumed"];
fates = zeros(numel(fateNames),numel(fateFields));
for i=1:numel(fateNames)
    row = select_row(S,fateNames(i),"stride");
    for j=1:numel(fateFields), fates(i,j)=row.(fateFields(j)); end
    assert(sum(fates(i,:))==row.prefetch_issued,'Prefetch fates must conserve');
end
f = figure('Color','w','Position',[100 100 1300 650]);
b = barh(fates,'stacked');
fateColors = [22 140 145;102 120 138;237 135 93;215 220 217]/255;
for j=1:numel(b), b(j).FaceColor=fateColors(j,:); end
set(gca,'YTick',1:numel(fateNames),'YTickLabel',workload_labels(fateNames),'YDir','reverse');
xlabel('Issued stride-prefetch transactions'); title('Useful predictions may arrive late');
legend('Timely','Late','Unused evicted','Resident unconsumed','Location','southoutside','Orientation','horizontal');
grid on; box off; export_family(f,out,'05_prefetch_fates');

% 06: Absolute pollution costs keep the tiny baseline visible and auditable.
f = figure('Color','w','Position',[100 100 1300 560]);
plotMetrics = ["completion_cycles","dram_reads"];
plotTitles = ["Completion cycles","Total DRAM transactions"];
for k=1:2
    subplot(1,2,k);
    v = metric_values(S,"pollution_return",policies,plotMetrics(k));
    b = bar(v,'FaceColor','flat'); b.CData=colors;
    set(gca,'XTick',1:3,'XTickLabel',{'None','Next-line','Stride'});
    ylim([0 max(v)*1.22]); title(plotTitles(k)); grid on; box off;
    for j=1:3
        text(j,v(j)+max(v)*.035,sprintf('%d',v(j)), ...
            'HorizontalAlignment','center','FontSize',11);
    end
end
sgtitle('A wrong prefetch displaces a hot demand line');
export_family(f,out,'06_pollution');

% 07: Read the archived analysis at the actual 16-byte RTL line geometry.
footprint = zeros(numel(names),1);
for i=1:numel(names)
    path = fullfile(reference,'analysis',char(names(i)+".summary.json"));
    analysis = jsondecode(fileread(path));
    assert(analysis.line_size_bytes==16,'Footprint must use 16-byte lines');
    footprint(i)=analysis.unique_cache_lines;
end
f = figure('Color','w','Position',[100 100 1300 740]);
barh(footprint,'FaceColor',colors(3,:));
set(gca,'YTick',1:numel(names),'YTickLabel',workload_labels(names),'YDir','reverse');
xline(64,'--','64 cache slots','Color',colors(2,:));
xlabel('Distinct touched 16-byte lines');
title('Trace footprint spans reuse and streaming regimes'); grid on; box off;
export_family(f,out,'07_workload_footprint');

% 08: Chai/Coffee/Juice supplied INITIAL factors, not trained models/cache data.
T={[.2;.4;.1],[.2 .1;.4 .2;.1 .3],[.2 .1 .3;.4 .2 .1;.1 .3 .2]};
C={[.3;.5;.2],[.3 .2;.5 .1;.2 .4],[.3 .2 .1;.5 .1 .4;.2 .4 .2]};
sets={ [1 2],[1 2],[1 2],[1 3],[2 3],[1 2 3]}; chosen=[1 1 2 3 2 2];
P=zeros(6,3);
for r=1:3
    M=T{r}*C{r}';
    for k=1:6
        available=sets{k}; score=zeros(size(available));
        for j=1:numel(available)
            others=available(available~=available(j));
            score(j)=sum(M(available(j),others));
        end
        q=exp(score-max(score)); q=q/sum(q); % numerically stable softmax
        P(k,r)=q(available==chosen(k));
    end
end
meanNLL=-mean(log(P),1);
f = figure('Color','w','Position',[100 100 1050 580]);
b = plot(1:6,P,'o-','LineWidth',1.5);
cdmColors = [22 140 145;35 60 82;237 135 93]/255;
for j=1:3, b(j).Color=cdmColors(j,:); end
ylim([0 1]); xticks(1:6); xlabel('Observation in the supplied six-choice example');
ylabel('Probability assigned to observed choice');
title('CDM initial-factor arithmetic'); legend('Rank 1','Rank 2','Rank 3'); grid on; box off;
export_family(f,out,'08_cdm_probabilities');

% 09: Float64 parameter-only storage; not identifiable degrees of freedom,
% process RSS, gradients, optimizer state or dense temporary matrices.
n=[250 500 1000 2000 3000 5000]; entries=[n.^2;2*n;4*n;6*n]';
miB=8*entries/2^20;
f = figure('Color','w','Position',[100 100 1050 580]);
b = loglog(n,miB,'o-','LineWidth',1.5);
storageColors = [35 60 82;22 140 145;237 135 93;142 136 173]/255;
for j=1:4, b(j).Color=storageColors(j,:); end
xlabel('Alternatives n'); ylabel('Float64 parameter storage (MiB)');
title('Low-rank factors reduce parameter storage');
legend('Full n squared','Rank 1: 2 n r','Rank 2: 2 n r','Rank 3: 2 n r','Location','northwest');
grid on; box off; export_family(f,out,'09_cdm_storage');

% Companion tables contain the same input measurements or explicit arithmetic.
writetable(S,fullfile(out,'benchmark_summary.csv'));
writetable(table((1:3)',meanNLL','VariableNames',{'rank','initial_factor_mean_NLL'}), ...
    fullfile(out,'cdm_initial_nll.csv'));
writetable(table((1:6)',P(:,1),P(:,2),P(:,3), ...
    'VariableNames',{'observation','rank1_probability','rank2_probability','rank3_probability'}), ...
    fullfile(out,'cdm_chosen_probabilities.csv'));
writetable(table(n',entries(:,1),entries(:,2),entries(:,3),entries(:,4), ...
    miB(:,1),miB(:,2),miB(:,3),miB(:,4), ...
    'VariableNames',{'alternatives','full_entries','rank1_entries','rank2_entries','rank3_entries', ...
    'full_float64_MiB','rank1_float64_MiB','rank2_float64_MiB','rank3_float64_MiB'}), ...
    fullfile(out,'cdm_parameter_storage.csv'));
fprintf('Wrote nine PNG/PDF figure families and companion CSV tables to %s\n',out);
end

function row = select_row(S,name,policy)
row = S(S.workload==name & S.policy==policy,:);
assert(height(row)==1,'Each workload must have exactly one row per policy');
end

function values = metric_values(S,names,policies,metric)
values = zeros(numel(names),numel(policies));
for i=1:numel(names)
    for j=1:numel(policies)
        row=select_row(S,names(i),policies(j)); values(i,j)=row.(metric);
    end
end
end

function grouped_horizontal(values,names,policies,colors)
b=barh(values,'grouped');
for j=1:numel(b), b(j).FaceColor=colors(j,:); end
set(gca,'YTick',1:numel(names),'YTickLabel',workload_labels(names),'YDir','reverse');
legend(strrep(policies,'_',' '),'Location','southoutside','Orientation','horizontal');
grid on; box off;
end

function labels = workload_labels(names)
keys = ["column_stride","embedding_gather","interleaved_conflicting", ...
    "modelled_matmul_ijk_ab_reads","modelled_matmul_ikj_ab_reads","phase_shift", ...
    "pollution_return","same_line","tensor_stream","three_line_bursts", ...
    "tiled_reuse","two_stream_disjoint_sets","zero_gap_stream"];
values = ["Column stride","Irregular gather","Conflicting streams", ...
    "Matmul ijk A/B","Matmul ikj A/B","Phase shift","Hot-line pollution", ...
    "Same-line reuse","Dense words","Three-line bursts","Tile reuse", ...
    "Disjoint streams","Zero compute gap"];
labels = strings(size(names));
for i=1:numel(names)
    index=find(keys==names(i),1);
    if isempty(index), labels(i)=strrep(names(i),'_',' '); else, labels(i)=values(index); end
end
end

function export_family(fig,out,stem)
exportgraphics(fig,fullfile(out,char(string(stem)+".png")),'Resolution',200);
exportgraphics(fig,fullfile(out,char(string(stem)+".pdf")),'ContentType','vector');
close(fig);
end
