import {writeFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {config,abs,ensure,run} from './common.mjs';
export function validateMedia(p,c){
 const errors=[];const v=p.streams.find(s=>s.codec_type==='video'),a=p.streams.find(s=>s.codec_type==='audio');
 if(!v)return ['Missing video'];
 const [n,d]=String(v.avg_frame_rate).split('/').map(Number);
 if(v.width!==c.width||v.height!==c.height)errors.push('resolution');
 if(!Number.isFinite(n/d)||Math.abs(n/d-c.fps)>.001)errors.push('fps');
 if(!Number.isFinite(Number(p.format?.duration))||Math.abs(Number(p.format.duration)-c.duration)>1/c.fps+.001)errors.push('duration');
 if(Number(v.nb_frames)!==Math.round(c.duration*c.fps))errors.push('frame count');
 if(v.codec_name!=='h264')errors.push('video codec');
 if(a?.codec_name!=='aac')errors.push('audio codec');
 if(Number(a?.sample_rate)!==c.audioSampleRate)errors.push('audio sample rate');
 return errors;
}
export function qc(){
 const p=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',abs(config.outputPaths.final)],{stdio:'pipe',encoding:'utf8'}).stdout);
 const errors=validateMedia(p,config);ensure('outputs');
 writeFileSync(abs('outputs/qc.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',checkedAt:new Date().toISOString(),errors,probe:p},null,2));
 if(errors.length)throw Error('QC failed: '+errors.join(', '));
 console.log('PASS: 1080p / '+config.fps+' fps / '+config.duration+' s / H.264 / AAC / 48 kHz');
 return p;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)qc();
