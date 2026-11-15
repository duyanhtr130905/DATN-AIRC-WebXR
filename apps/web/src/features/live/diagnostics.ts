// Test build only. Bounded synthetic diagnostics; no visitor persistence/network logging.
export interface Diagnostic { kind:string; at:number; [key:string]:unknown }
interface Probe { events:Diagnostic[]; lastDelta:unknown; disconnect?:()=>void; inject?:(raw:unknown)=>void }
declare global { interface Window { __AIRC_TEST__?:Probe } }
const enabled=import.meta.env?.VITE_TEST_DIAGNOSTICS==="1";
function probe():Probe|undefined {
  if(!enabled || typeof window==="undefined")return;
  return window.__AIRC_TEST__??(window.__AIRC_TEST__={events:[],lastDelta:null});
}
export function diagnostic(kind:string,fields:Record<string,unknown>={}){
  const p=probe();if(!p)return;p.events.push({kind,at:performance.now(),...fields});if(p.events.length>512)p.events.splice(0,p.events.length-512);
}
export function lastDelta(raw:unknown){const p=probe();if(p)p.lastDelta=raw;}
export function testControls(disconnect:()=>void,inject:(raw:unknown)=>void){
  const p=probe();if(!p)return()=>{};p.disconnect=disconnect;p.inject=inject;
  return()=>{if(p.inject===inject){delete p.disconnect;delete p.inject;}};
}
