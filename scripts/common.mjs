import {readFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const config=JSON.parse(readFileSync(path.join(root,'config/project.json'),'utf8'));
export const abs=p=>path.resolve(root,p);
export function ensure(p){mkdirSync(abs(p),{recursive:true});}
export function run(cmd,args,opts={}){const r=spawnSync(cmd,args,{cwd:root,stdio:'inherit',...opts});if(r.error)throw r.error;if(r.status!==0)throw new Error(cmd+' exited '+r.status);return r;}
export const hf=(...args)=>run(process.execPath,[abs('node_modules/hyperframes/bin/hyperframes.mjs'),...args]);
