import { id, integer, object, record, room, state } from "../features/live/contracts.ts";
import type { CatalogObject, Room, TwinState } from "../features/live/contracts.ts";
export type FailureKind = "cancelled" | "timeout" | "unavailable" | "not_found" | "contract" | "network";
export class CatalogError extends Error { kind: FailureKind; constructor(kind: FailureKind) { super(kind); this.kind=kind; } }
export async function getJson(path: string, signal?: AbortSignal, fetcher: typeof fetch=fetch, timeoutMs=4000): Promise<unknown> {
  const controller=new AbortController();let reader:ReadableStreamDefaultReader<Uint8Array>|undefined;
  let rejectDeadline:(reason:CatalogError)=>void=()=>{};
  const deadline=new Promise<never>((_resolve,reject)=>{rejectDeadline=reject;});
  const stop=(kind:FailureKind)=>{controller.abort();void reader?.cancel().catch(()=>{});rejectDeadline(new CatalogError(kind));};
  const abort=()=>stop("cancelled");signal?.addEventListener("abort",abort,{once:true});
  const timer=setTimeout(()=>stop("timeout"),timeoutMs);
  if(signal?.aborted)abort();
  const work=async()=>{
    const response=await fetcher(path,{signal:controller.signal,credentials:"omit"});
    if(!response.ok)throw new CatalogError(response.status===503?"unavailable":response.status>=500?"network":response.status===404?"not_found":"contract");
    reader=response.body?.getReader();if(!reader)throw new CatalogError("contract");
    const chunks:Uint8Array[]=[];let size=0;
    try {while(true){const item=await reader.read();if(item.done)break;size+=item.value.byteLength;
      if(size>2*1024*1024){void reader.cancel().catch(()=>{});throw new CatalogError("contract");}chunks.push(item.value);}
    }finally{reader.releaseLock();reader=undefined;}
    const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
    return JSON.parse(new TextDecoder().decode(bytes)) as unknown;
  };
  try{return await Promise.race([work(),deadline]);}
  catch(error){if(error instanceof CatalogError)throw error;throw new CatalogError(signal?.aborted?"cancelled":error instanceof SyntaxError?"contract":"network");}
  finally{clearTimeout(timer);signal?.removeEventListener("abort",abort);}
}

async function pages<T extends {id:string}>(path:string, parse:(raw:unknown)=>T, signal?:AbortSignal, fetcher:typeof fetch=fetch):Promise<T[]> {
  try {
  const result:T[]=[]; const ids=new Set<string>();const cursors=new Set<string>();let cursor:string|null=null;
  for(let page=0;page<32;page++) {
    const raw=record(await getJson(path+"?limit=25"+(cursor?"&cursor="+encodeURIComponent(cursor):""),signal,fetcher));
    const meta=record(raw.meta); if(meta.schema_version!==1 || !Array.isArray(raw.data) || raw.data.length>25)throw new CatalogError("contract");
    for(const item of raw.data){const value=parse(item);if(ids.has(value.id))throw new CatalogError("contract"); ids.add(value.id);result.push(value);}
    if(result.length>512)throw new CatalogError("contract");
    if(meta.next_cursor===null)return result;
    if(typeof meta.next_cursor!=="string" || !meta.next_cursor || meta.next_cursor.length>400 || cursors.has(meta.next_cursor) || raw.data.length===0)throw new CatalogError("contract");
    cursor=meta.next_cursor;cursors.add(cursor);
  } throw new CatalogError("contract");
  } catch(error){if(error instanceof CatalogError)throw error;throw new CatalogError("contract");}
}
export const readRooms=(signal?:AbortSignal,fetcher?:typeof fetch):Promise<Room[]>=>pages("/api/v1/rooms",room,signal,fetcher);
export async function readObjects(roomId:string,signal?:AbortSignal,fetcher?:typeof fetch):Promise<CatalogObject[]> {
  const scope=id(roomId);const rows=await pages(`/api/v1/rooms/${scope}/objects`,object,signal,fetcher);
  if(rows.some(row=>row.room_id!==scope))throw new CatalogError("contract");return rows;
}
export async function readObject(objectId:string,signal?:AbortSignal,fetcher?:typeof fetch):Promise<CatalogObject> {
  const key=id(objectId);const raw=record(await getJson(`/api/v1/objects/${key}`,signal,fetcher));
  if(record(raw.meta).schema_version!==1)throw new CatalogError("contract");const result=object(raw.data);if(result.id!==key)throw new CatalogError("contract");return result;
}
export async function readStates(kind:"rooms"|"objects",targetId:string,signal?:AbortSignal,fetcher?:typeof fetch):Promise<TwinState[]> {
  const key=id(targetId);const rows=await pages(`/api/v1/${kind}/${key}/states`,state,signal,fetcher);
  if(rows.some(row=>kind==="rooms"?row.room_id!==key:row.target_id!==key))throw new CatalogError("contract");
  rows.forEach(row=>integer(row.version,1));return rows;
}
