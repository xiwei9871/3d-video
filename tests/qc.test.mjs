import test from 'node:test';
import assert from 'node:assert/strict';
import {validateMedia} from '../scripts/qc.mjs';
const config={width:1920,height:1080,fps:30,duration:5.8,audioSampleRate:48000};
const good=()=>({streams:[{codec_type:'video',codec_name:'h264',width:1920,height:1080,avg_frame_rate:'30/1',duration:'5.8',nb_frames:'174'},{codec_type:'audio',codec_name:'aac',sample_rate:'48000'}],format:{duration:'5.8'}});
test('accepts specified delivery media',()=>assert.deepEqual(validateMedia(good(),config),[]));
test('rejects undefined framerate',()=>{const p=good();p.streams[0].avg_frame_rate='0/0';assert.ok(validateMedia(p,config).includes('fps'))});
test('rejects undefined duration',()=>{const p=good();p.format.duration='N/A';assert.ok(validateMedia(p,config).includes('duration'))});
for(const [label,mutate] of Object.entries({resolution:p=>p.streams[0].width=1280,fps:p=>p.streams[0].avg_frame_rate='24/1',duration:p=>p.format.duration='8',video:p=>p.streams[0].codec_name='vp9',audio:p=>p.streams.pop(),sampleRate:p=>p.streams[1].sample_rate='44100',frames:p=>p.streams[0].nb_frames='170'})){
 test('rejects wrong '+label,()=>{const p=good();mutate(p);assert.ok(validateMedia(p,config).length>0)});
}
