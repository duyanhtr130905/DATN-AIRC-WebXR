/** Actual frozen manifest navigation evidence; synthetic math tests are separate. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {Navigation,SPAWN,validateManifest} from '../../apps/web/src/p507-e1/core.ts';
const m=validateManifest(JSON.parse(fs.readFileSync(new URL('../../.local/p507-e0-e1/artifact/asset-manifest.json',import.meta.url),'utf8'))),nav=new Navigation(m);
assert.equal(nav.blocked(SPAWN,SPAWN),null);
// Explicit west route, chosen conservatively from manifest, no central passage.
const route=[[1.25,-7.415],[.95,-7.415],[.95,-5.9],[.95,-5.2]];
const segments=route.slice(1).map((p,i)=>({from:route[i],to:p,reason:nav.blocked(route[i],p)}));
console.log(JSON.stringify({routeSegments:segments},null,2));
assert(segments.every(s=>!s.reason),'West route segment blocked (do not shrink capsule)');
const blocked=[];
for(const [id,from,to] of [
 ['west continuation',[.95,-5.2],[.95,-3.9]],
 ['wall',[.95,-7.415],[-1,-7.415]],
 ['desk',[1.25,-7.415],[4,-7.415]],
 ['chair',[1.25,-6.12],[2.175,-6.12]],
 ['cabinet',[1,-8.2],[1,-9]],
 ['A-B gap',[1.2,-5.63],[5.5,-5.63]],
 ['B-C gap',[1.2,-2.85],[5.5,-2.85]],
 ['open outward door',[1.25,-7.415],[-1,-7.415]],
 ['large jump',[1.25,-7.415],[6,-7.415]],
]){const reason=nav.blocked(from,to);assert(reason,id+' must block');blocked.push({case:id,from,to,reason});}
const result={result:'PASS',capsule:{radius:.3,height:1.8},route,segments,blocked,policy:'Static plus .15m occupied chair envelope; full swept segment; stop, no slide. No outside corridor.'};
fs.writeFileSync(new URL('../../.local/p507-e0-e1/navigation-report.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
