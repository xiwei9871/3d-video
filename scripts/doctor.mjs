import {existsSync,accessSync,constants} from 'node:fs';
import {config,abs,ensure,run,hf} from './common.mjs';
const rows=[];
for(const [cmd,args] of [[process.execPath,['--version']],['ffmpeg',['-version']],['ffprobe',['-version']],[process.env.BLENDER_BIN||'blender',['--version']]]){const s=run(cmd,args,{stdio:'pipe',encoding:'utf8'}).stdout.split('\n')[0];rows.push(s);}
if(Number(process.versions.node.split('.')[0])<22)throw Error('Node 22+ required');
for(const key of ['width','height','fps','duration','audioSampleRate'])if(!Number.isFinite(config[key])||config[key]<=0)throw Error('Invalid config '+key);
for(const file of ['assets/reference/zodiac_base_reference.png','assets/fonts/zodiac-serif.ttf','node_modules/hyperframes/bin/hyperframes.mjs'])if(!existsSync(abs(file)))throw Error('Missing '+file);
for(const dir of ['outputs','generated','work']){ensure(dir);accessSync(abs(dir),constants.W_OK);}
hf('--version');
run(process.env.BLENDER_BIN||'blender',['-b','--factory-startup','--python-exit-code','1','--python',abs('scripts/doctor-render.py')],{stdio:'inherit'});
if(!existsSync(abs('work/doctor.png')))throw Error('Blender headless render failed');
console.log(rows.join('\n')+'\nPASS: project config, reference, fonts, output permissions, Blender headless render');
