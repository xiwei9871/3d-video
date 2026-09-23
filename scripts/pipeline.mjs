import {existsSync,readdirSync,writeFileSync,readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {config,abs,ensure,run,hf} from './common.mjs';
import {compose} from './compose.mjs';
import {qc} from './qc.mjs';
const command=process.argv[2],preview=process.argv.includes('--preview');
function blender(script,args=[]){run(process.env.BLENDER_BIN||'blender',['-b','--factory-startup','--python-exit-code','1','--python',abs('blender/scripts/'+script),'--',...args]);}
function prepare(){
 const dir=preview?config.renderPaths.previewFrames:config.renderPaths.frames;
 const frames=Math.round(config.fps*config.duration);
 const hash=createHash('sha256');for(const f of ['config/project.json','blender/scripts/build_scene.py'])hash.update(readFileSync(abs(f)));
 const expectedHash=hash.digest('hex');let manifest;try{manifest=JSON.parse(readFileSync(abs(dir+'/manifest.json')))}catch{}
 if(manifest?.sourceHash!==expectedHash||!existsSync(abs(dir))||readdirSync(abs(dir)).filter(s=>/^frame_\d{6}\.png$/.test(s)).length!==frames)blender('render_scene.py',preview?['--preview']:[]);
 for(let n=1;n<=frames;n++)if(!existsSync(abs(dir+'/frame_'+String(n).padStart(6,'0')+'.png')))throw Error('Missing frame '+n);
 ensure('generated/composition/media');
 run('ffmpeg',['-hide_banner','-loglevel','warning','-y','-framerate',String(config.fps),'-start_number','1','-i',abs(dir+'/frame_%06d.png'),'-frames:v',String(frames),'-c:v','libvpx-vp9','-pix_fmt','yuva420p','-b:v','0','-crf','18','-deadline','good','-cpu-used','4','-row-mt','1','-threads','4','-auto-alt-ref','0',abs('generated/composition/media/snake-alpha.webm')]);
 compose(preview);
}
if(command==='blender-build')blender('build_scene.py');
else if(command==='blender-render')blender('render_scene.py',process.argv.slice(3));
else if(command==='prepare')prepare();
else if(command==='preview'){if(!existsSync(abs('generated/composition/index.html')))prepare();hf('preview',abs('generated/composition'),'--port','5174');}
else if(command==='render'){
 const started=Date.now();prepare();ensure('generated/hyperframes');ensure('outputs/preview');ensure('outputs/final');
 hf('lint',abs('generated/composition'));
 hf('render',abs('generated/composition'),'-o',abs(config.outputPaths.composition),'--fps',String(config.fps),'--workers','1','--quality',preview?'draft':'delivery','--strict','--no-best-effort');
 const output=preview?config.outputPaths.preview:config.outputPaths.final;
 run('ffmpeg',['-hide_banner','-loglevel','warning','-y','-i',abs(config.outputPaths.composition),'-map','0:v:0','-map','0:a:0','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',String(config.fps),'-c:a','aac','-b:a','192k','-ar',String(config.audioSampleRate),'-t',String(config.duration),'-movflags','+faststart',abs(output)]);
 if(!preview){qc();run('ffmpeg',['-hide_banner','-loglevel','warning','-y','-ss',String(config.duration-.5),'-i',abs(output),'-frames:v','1','-update','1',abs(config.outputPaths.poster)]);writeFileSync(abs('outputs/final/build.json'),JSON.stringify({builtAt:new Date().toISOString(),buildSeconds:(Date.now()-started)/1000,...config,codec:'H.264 / AAC'},null,2));}
 console.log('Output: '+abs(output));
}else if(!['blender-build','blender-render','prepare','preview'].includes(command))throw Error('Unknown command '+command);
