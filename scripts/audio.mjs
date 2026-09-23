import {writeFileSync} from 'node:fs';
import {config,abs,ensure} from './common.mjs';
export function makeAudio(){
 const sr=config.audioSampleRate,N=Math.round(sr*config.duration),pcm=Buffer.alloc(N*4);
 const notes=[[.7,523.25,.08],[1.12,659.25,.06],[1.46,783.99,.055],[2.55,1046.5,.035],[3.45,880,.045],[4.25,1046.5,.07],[4.44,1318.51,.055],[4.66,1567.98,.04]];
 for(let i=0;i<N;i++){let x=0,t=i/sr;for(const [start,f,g] of notes){const dt=t-start;if(dt>=0&&dt<1.2)x+=g*(1-Math.exp(-dt*90))*Math.exp(-dt*5)*(Math.sin(2*Math.PI*f*dt)+.25*Math.sin(2*Math.PI*f*2.01*dt));}x*=Math.min(1,(config.duration-t)/.35);const v=Math.round(Math.max(-1,Math.min(1,x))*32767);pcm.writeInt16LE(v,i*4);pcm.writeInt16LE(v,i*4+2);}
 const h=Buffer.alloc(44);h.write('RIFF');h.writeUInt32LE(36+pcm.length,4);h.write('WAVEfmt ',8);h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(2,22);h.writeUInt32LE(sr,24);h.writeUInt32LE(sr*4,28);h.writeUInt16LE(4,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(pcm.length,40);
 ensure('assets/audio');writeFileSync(abs('assets/audio/snake_chimes.wav'),Buffer.concat([h,pcm]));
}
