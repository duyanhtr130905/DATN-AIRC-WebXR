import { date, id, integer, MAX_STATES, record, scopedState } from "../live/contracts.ts";
import type { TwinState } from "../live/contracts.ts";
export type Connection = "connecting"|"synchronizing"|"connected"|"stale"|"reconnecting"|"resync_required"|"error";
interface Pending { id:string; watermark:number; chunks:number; total:number; index:number; states:Record<string,TwinState>; targets:Set<string>; bytes:number }
export interface Replica { roomId:string; sequence:number; states:Record<string,TwinState>; status:Connection; pending:Pending|null }
export const initialReplica=(roomId:string):Replica=>({roomId:id(roomId),sequence:0,states:{},status:"connecting",pending:null});
export function consume(replica:Replica,raw:unknown,objects:ReadonlySet<string>):Replica {
  const m=record(raw);
  if(m.schema_version!==2 || id(m.room_id)!==replica.roomId)throw new Error("Protocol/scope mismatch");
  id(m.message_id);date(m.timestamp);const sequence=integer(m.sequence);
  const type=m.type;
  if(type==="resync.required")return {...replica,status:"resync_required",pending:null};
  if(type==="error")return {...replica,status:"error",pending:null};
  if(type==="snapshot.start") {
    if(replica.pending || sequence!==integer(m.watermark))throw new Error("Invalid snapshot start");
    return {...replica,status:"synchronizing",pending:{id:id(m.snapshot_id),watermark:sequence,chunks:integer(m.total_chunks,0,MAX_STATES),total:integer(m.total_states,0,MAX_STATES),index:0,states:{},targets:new Set(),bytes:0}};
  }
  if(type==="snapshot.chunk" || type==="snapshot.end") {
    const p=replica.pending;
    if(!p || id(m.snapshot_id)!==p.id || sequence!==p.watermark || integer(m.watermark)!==p.watermark)throw new Error("Invalid snapshot scope");
    if(type==="snapshot.chunk") {
      if(integer(m.chunk_index)!==p.index || p.index>=p.chunks || !Array.isArray(m.states) || m.states.length<1 || m.states.length>16)throw new Error("Invalid chunk order");
      const states={...p.states};const targets=new Set(p.targets);
      const bytes=p.bytes+new TextEncoder().encode(JSON.stringify(m.states)).byteLength;
      if(bytes>2*1024*1024)throw new Error("Snapshot byte capacity");
      for(const rawState of m.states) {
        const s=scopedState(rawState,replica.roomId,objects);const key=s.target_kind+":"+s.target_id+":"+s.state_type;
        if(states[s.id] || targets.has(key))throw new Error("Duplicate snapshot state");
        states[s.id]=s;targets.add(key);
      }
      if(Object.keys(states).length>p.total)throw new Error("Snapshot capacity");
      return {...replica,pending:{...p,index:p.index+1,states,targets,bytes}};
    }
    if(integer(m.total_chunks)!==p.chunks || integer(m.total_states)!==p.total || p.index!==p.chunks || Object.keys(p.states).length!==p.total)throw new Error("Incomplete snapshot");
    return {...replica,sequence:p.watermark,states:p.states,pending:null,status:"connected"};
  }
  if(replica.pending || replica.status!=="connected")throw new Error("Delta before snapshot end");
  if(type==="heartbeat")return sequence===replica.sequence?replica:{...replica,status:"resync_required"};
  if(type!=="state.updated")throw new Error("Unknown message");
  if(sequence<=replica.sequence)return replica;
  if(sequence!==replica.sequence+1)return {...replica,status:"resync_required"};
  const state=scopedState(m.state,replica.roomId,objects);const previous=replica.states[state.id];
  const sameTarget=Object.values(replica.states).find(s=>s.target_id===state.target_id&&s.state_type===state.state_type);
  if((previous && (state.version!==previous.version+1 || state.target_id!==previous.target_id || state.state_type!==previous.state_type)) || (!previous && (state.version!==1 || sameTarget)))return {...replica,status:"resync_required"};
  return {...replica,sequence,states:{...replica.states,[state.id]:state}};
}
