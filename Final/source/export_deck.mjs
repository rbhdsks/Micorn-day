// Run with the bundled artifact-tool runtime; environment paths are explicit.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {buildDeck} from './build_deck.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const moduleRoot=process.env.RUNTIME_NODE_MODULES,skill=process.env.PRESENTATION_SKILL_DIR,python=process.env.RUNTIME_PYTHON;
if(!moduleRoot||!skill||!python)throw new Error('Set RUNTIME_NODE_MODULES, PRESENTATION_SKILL_DIR and RUNTIME_PYTHON from the workspace runtime');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(moduleRoot,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const data=JSON.parse(await fs.readFile(path.join(root,'Final/source/evidence.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});const spec=await buildDeck(p,data);
for(const s of p.slides.items)for(const c of s.charts.items)applyPresentationChartFont(c,{fontFamily:'Arial'});
const out=path.join(root,'Phase2/build/presentation');await fs.mkdir(out,{recursive:true});
const draft=path.join(out,'candidate.pptx');await (await PresentationFile.exportPptx(p)).save(draft);
const finalPath=path.join(root,'Final/Hackathon_Presentation.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:draft,finalPath,pythonExecutable:python,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...spec.tableOwners.flatMap(i=>['--require-native-table-slide',String(i)])],
 requiredNativeTableOwnerSlides:spec.tableOwners,requiredNativeChartOwnerSlides:spec.chartOwners,
 fontPolicy:{basis:'design',families:['Arial']},materializeLiteralChartWorkbooks:true,
 verifyArtifactToolImport:true,receiptPath:path.join(out,'validation.json')});
console.log(JSON.stringify({slideCount:spec.slideCount,finalPath,result}));
