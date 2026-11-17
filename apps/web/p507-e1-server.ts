/** Serve only the E1 neutral assets during Vite DEV; never copy them to dist. */
import type {Plugin} from 'vite';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
export function p507ExperimentAssets():Plugin {
  return {name:'p507-e1-dev-assets',apply:'serve',configureServer(server){
    server.middlewares.use('/p507-e1-assets/',async(req,res)=>{
      const name=req.url?.split('?')[0]?.replace(/^\//,'');
      if(!name || !['P507_G1_G2_PROVISIONAL.glb','asset-manifest.json','asset-lock.json'].includes(name)){res.statusCode=404;res.end('Unknown E1 asset');return;}
      try{const data=await readFile(fileURLToPath(new URL('../../.local/p507-e0-e1/served/'+name,import.meta.url)));res.setHeader('Content-Type',name.endsWith('.glb')?'model/gltf-binary':'application/json');res.setHeader('Cache-Control','no-store');res.end(data);}
      catch{res.statusCode=404;res.end('Run E0 validate_asset.py --prepare first');}
    });
  }};
}
