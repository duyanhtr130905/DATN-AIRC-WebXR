import { test } from "node:test";
import assert from "node:assert/strict";
import { consume, initialReplica } from "../src/features/realtime/reducer.ts";
import { object, state } from "../src/features/live/contracts.ts";
import { getJson, CatalogError, readObjects, readRooms } from "../src/api/catalog.ts";
import { sceneFromCatalog } from "../src/features/catalog/adapter.ts";
import { socketUrl, subscribe } from "../src/features/realtime/client.ts";
const room="10000000-0000-4000-8000-000000000001", target="20000000-0000-4000-8000-000000000001", sid="30000000-0000-4000-8000-000000000001",mid="40000000-0000-4000-8000-000000000001";
const stamp="2026-11-15T00:00:00Z";
function dto(version=1){return {id:sid,room_id:room,target_id:target,target_kind:"object",state_type:"equipment_status",value:{status:version===1?"available":"maintenance"},source_kind:"synthetic",version,source_observed_at:null,committed_at:stamp};}
function frame(type:string,extra:Record<string,unknown>={}):Record<string,any>{return {type,schema_version:2,message_id:mid,snapshot_id:mid,room_id:room,sequence:1,watermark:1,timestamp:stamp,...extra};}
const objects=new Set([target]);
function snapshot(){let r=initialReplica(room);r=consume(r,frame("snapshot.start",{total_chunks:1,total_states:1}),objects);r=consume(r,frame("snapshot.chunk",{chunk_index:0,states:[dto()]}),objects);return consume(r,frame("snapshot.end",{total_chunks:1,total_states:1}),objects);}
test("snapshot stages atomically; delta versions, duplicate, gap, authoritative replacement",()=>{
 let r=initialReplica(room);r=consume(r,frame("snapshot.start",{total_chunks:1,total_states:1}),objects);r=consume(r,frame("snapshot.chunk",{chunk_index:0,states:[dto()]}),objects);assert.deepEqual(r.states,{});
 r=consume(r,frame("snapshot.end",{total_chunks:1,total_states:1}),objects);assert.equal(r.states[sid].version,1);
 const next=consume(r,frame("state.updated",{sequence:2,state:dto(2)}),objects);assert.equal(next.states[sid].value.status,"maintenance");
 assert.equal(consume(next,frame("state.updated",{sequence:2,state:dto(1)}),objects),next);
 assert.equal(consume(next,frame("state.updated",{sequence:4,state:dto(3)}),objects).status,"resync_required");
 assert.equal(consume(next,frame("state.updated",{sequence:3,state:dto(1)}),objects).status,"resync_required");
 let replacement=consume(next,frame("snapshot.start",{total_chunks:0,total_states:0}),objects);replacement=consume(replacement,frame("snapshot.end",{total_chunks:0,total_states:0}),objects);assert.deepEqual(replacement.states,{});
});
for(const fault of ["missing","duplicate","order","watermark","room","schema","unsafe","totals","target","source"]){test("reject malformed snapshot: "+fault,()=>{
 let r=consume(initialReplica(room),frame("snapshot.start",{total_chunks:1,total_states:1}),objects);
 const chunk=frame("snapshot.chunk",{chunk_index:0,states:[dto()]});
 if(fault==="missing")assert.throws(()=>consume(r,frame("snapshot.end",{total_chunks:1,total_states:1}),objects));
 else {if(fault==="order")chunk.chunk_index=1;if(fault==="watermark")chunk.watermark=3;if(fault==="room")chunk.room_id=target;if(fault==="schema")chunk.schema_version=1;if(fault==="unsafe")chunk.sequence=2**53;
 if(fault==="target")chunk.states=[{...dto(),target_id:room}];if(fault==="source")chunk.states=[{...dto(),source_kind:"real_verified"}];
 if(fault==="duplicate"||fault==="totals"){r=consume(r,chunk,objects);assert.throws(()=>consume(r,fault==="duplicate"?chunk:frame("snapshot.end",{total_chunks:1,total_states:2}),objects));}
 else assert.throws(()=>consume(r,chunk,objects));}assert.deepEqual(r.states,{});
 });}
test("scope, validation and deterministic UUID scene layout20objects",()=>{
 assert.throws(()=>state({...dto(),version:0}));assert.throws(()=>state({...dto(),source_kind:"unknown"}));
 assert.throws(()=>consume(snapshot(),frame("heartbeat",{room_id:target}),objects));
 const rows=Array.from({length:20},(_,i)=>object({id:`20000000-0000-4000-8000-${String(i+1).padStart(12,"0")}`,room_id:room,name:"Synthetic",type:"demo",source_kind:"synthetic",metadata:{label:"SYNTHETIC"},created_at:stamp,updated_at:stamp}));
 const a=sceneFromCatalog(room,rows,{}),b=sceneFromCatalog(room,[...rows].reverse(),{});assert.deepEqual(a,b);assert.equal(a.objects.length,20);
 assert.throws(()=>sceneFromCatalog(target,rows,{}));assert.throws(()=>sceneFromCatalog(room,[rows[0],rows[0]],{}));
 assert.equal(socketUrl(room,{href:"https://test.example/a"}),`wss://test.example/ws/v1/state?room_id=${room}&protocol=2`);
});
test("real pagination, repeated cursor guard, invalid UUID/scope/source",async()=>{
 const base={id:room,code:"DEMO",name:"DEMO",source_kind:"synthetic",metadata:{},created_at:stamp,updated_at:stamp};let calls=0;
 const fetcher=(async()=>new Response(JSON.stringify({data:[{...base,id:calls++===0?room:target}],meta:{schema_version:1,next_cursor:calls===1?"next":null}}))) as typeof fetch;
 assert.equal((await readRooms(undefined,fetcher)).length,2);
 const repeated=(async()=>new Response(JSON.stringify({data:[base],meta:{schema_version:1,next_cursor:"same"}}))) as typeof fetch;
 await assert.rejects(readRooms(undefined,repeated));await assert.rejects(readObjects("invalid",undefined,fetcher));
 const hidden=(async()=>new Response(JSON.stringify({data:[{...base,source_kind:"unknown"}],meta:{schema_version:1,next_cursor:null}}))) as typeof fetch;await assert.rejects(readRooms(undefined,hidden));
});
test("socket disposal prevents stale callbacks; no client writes",()=>{
 let socket:any;let updates=0;const stop=subscribe(room,objects,()=>updates++,{url:"ws://example.test",factory:()=>{socket={close(){},onmessage:null,onopen:null,onclose:null,onerror:null};return socket as WebSocket;}});
 const callback=socket.onmessage;stop();const old=updates;callback({data:JSON.stringify(frame("snapshot.start",{total_chunks:0,total_states:0}))});assert.equal(updates,old);assert.equal(socket.onmessage,null);
});


test("Catalog deadline covers a stalled body even if transport ignores abort",async()=>{
 let aborted=false;
 const fetcher=(async(_url,options)=>{options?.signal?.addEventListener("abort",()=>{aborted=true;});return new Response(new ReadableStream({start(){}}));}) as typeof fetch;
 const result=await Promise.race([getJson("/api/test",undefined,fetcher,10).then(()=>"unexpected",error=>error),new Promise(resolve=>setTimeout(()=>resolve("hung"),100))]);
 assert.ok(result instanceof CatalogError && result.kind==="timeout");assert.equal(aborted,true);
});


test("public metadata permits backend-valid empty/null optional strings",()=>{
 const base={id:target,room_id:room,name:"Demo",type:"demo",source_kind:"synthetic",created_at:stamp,updated_at:stamp};
 assert.deepEqual(object({...base,metadata:{description:"",label:null}}).metadata,{description:"",label:null});
 assert.throws(()=>object({...base,metadata:{evidence_ref:"private"}}));
});
test("Catalog cancellation settles stalled transport and stops use of response",async()=>{
 const controller=new AbortController();const fetcher=(()=>new Promise(()=>{})) as typeof fetch;
 const request=getJson("/api/test",controller.signal,fetcher,1000);controller.abort();
 await assert.rejects(request,(error:unknown)=>error instanceof CatalogError&&error.kind==="cancelled");
});


test("reconnect FSM is bounded, marks stale, and ignores old socket callbacks",(t)=>{
 t.mock.timers.enable({apis:["setTimeout"]});
 const sockets:any[]=[];const statuses:string[]=[];
 const stop=subscribe(room,objects,r=>statuses.push(r.status),{url:"ws://test.invalid",random:()=>0,factory:()=>{const s:any={close(){},onmessage:null,onopen:null,onclose:null,onerror:null};sockets.push(s);return s as WebSocket;}});
 const oldMessage=sockets[0].onmessage;
 sockets[0].onclose();assert.ok(statuses.includes("stale"));t.mock.timers.tick(300);assert.equal(sockets.length,2);
 const before=statuses.length;oldMessage({data:JSON.stringify(frame("snapshot.start",{total_chunks:0,total_states:0}))});assert.equal(statuses.length,before);
 for(let index=1;index<12;index++){sockets.at(-1).onclose();t.mock.timers.tick(8000);}
 assert.equal(sockets.length,12);assert.equal(statuses.at(-1),"error");t.mock.timers.tick(100000);assert.equal(sockets.length,12);stop();
});
