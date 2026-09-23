import {readFileSync,writeFileSync,copyFileSync} from 'node:fs';
import {config,abs,ensure} from './common.mjs';
import * as layers from '../src/snake-demo/layers.mjs';
import {makeAudio} from './audio.mjs';
export function compose(preview=false){
 ensure('generated/composition/media');makeAudio();
 for(const [s,t] of [['node_modules/gsap/dist/gsap.min.js','gsap.min.js'],['assets/fonts/zodiac-serif.ttf','zodiac-serif.ttf'],['assets/audio/snake_chimes.wav','snake_chimes.wav']])copyFileSync(abs(s),abs('generated/composition/media/'+t));
 const w=preview?config.previewWidth:config.width,h=preview?config.previewHeight:config.height;
 const css=readFileSync(abs('src/snake-demo/style.css'),'utf8');
 const js=readFileSync(abs('src/snake-demo/timeline.js'),'utf8');
 const body=layers.background()+layers.zodiac()+layers.snake(config)+layers.fx()+layers.titles()+layers.audio(config);
 const html='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>十二生肖 · 蛇宝宝</title><script src="media/gsap.min.js"></script><style>'+css+'</style></head><body><div id="snake-demo" data-composition-id="snake-demo" data-width="'+w+'" data-height="'+h+'" data-duration="'+config.duration+'" data-fps="'+config.fps+'"><div style="position:absolute;width:1920px;height:1080px;transform-origin:top left;transform:scale('+(w/1920)+')">'+body+'</div></div><script>'+js+'</script></body></html>';
 writeFileSync(abs('generated/composition/index.html'),html);
 writeFileSync(abs('generated/composition/hyperframes.json'),JSON.stringify({name:config.name,width:w,height:h,fps:config.fps,duration:config.duration},null,2));
}
