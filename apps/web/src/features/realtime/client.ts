import { diagnostic, lastDelta, testControls } from "../live/diagnostics.ts";
import { consume, initialReplica } from "./reducer.ts";
import type { Replica } from "./reducer.ts";
import { id } from "../live/contracts.ts";
export function socketUrl(roomId:string,location:Pick<Location,"href">):string {
  const url=new URL("/ws/v1/state",location.href);url.protocol=url.protocol==="https:"?"wss:":"ws:";
  url.searchParams.set("room_id",id(roomId));url.searchParams.set("protocol","2");return url.href;
}
export function subscribe(roomId:string,objects:ReadonlySet<string>,notify:(state:Replica)=>void, options:{url?:string;factory?:(url:string)=>WebSocket;random?:()=>number}={}) {
  let replica=initialReplica(roomId);let stopped=false;let generation=0;let attempts=0;
  let socket:WebSocket|undefined;let retry:ReturnType<typeof setTimeout>|undefined;let deadline:ReturnType<typeof setTimeout>|undefined;
  let clearControls=()=>{};
  const emit=()=>{if(!stopped){diagnostic("connection",{roomId,status:replica.status,sequence:replica.sequence});notify(replica);}};
  const random=options.random??Math.random;
  function open() {
    if(stopped)return;attempts++;const token=++generation;
    replica={...replica,pending:null,status:attempts===1?"connecting":"reconnecting"};emit();
    const fail=()=>{
      if(stopped || token!==generation)return;
      generation++;clearTimeout(deadline);socket?.close();
      replica={...replica,pending:null,status:"stale"};emit();
      if(attempts>=12){replica={...replica,status:"error"};emit();return;}
      const delay=Math.min(8000,300*2**Math.min(attempts-1,5))*(0.75+random()*0.5);
      retry=setTimeout(open,delay);
    };
    const arm=()=>{clearTimeout(deadline);deadline=setTimeout(fail,10000);};
    try { socket=(options.factory??(url=>new WebSocket(url)))(options.url??socketUrl(roomId,window.location)); }
    catch {fail();return;}
    arm();
    socket.onopen=()=>{if(stopped||token!==generation)return;replica={...replica,status:"synchronizing"};emit();arm();};
    socket.onmessage=event=>{
      if(stopped||token!==generation)return;
      try {
        if(typeof event.data!=="string" || new TextEncoder().encode(event.data).byteLength>32*1024)throw new Error("Frame capacity");
        const raw=JSON.parse(event.data);
        diagnostic("received",{roomId,type:raw.type,sequence:raw.sequence,version:raw.state?.version,objectId:raw.state?.target_id});
        const previous=replica.sequence;replica=consume(replica,raw,objects);
        if(raw.type==="state.updated" && replica.sequence>previous && replica.status==="connected")lastDelta(raw);
        emit();
        if(["resync_required","error"].includes(replica.status)){fail();return;}arm();
      } catch {replica={...replica,pending:null,status:"resync_required"};emit();fail();}
    };
    socket.onclose=fail;socket.onerror=fail;
    clearControls();clearControls=testControls(()=>socket?.close(),raw=>{if(!stopped&&token===generation)socket?.onmessage?.call(socket,new MessageEvent("message",{data:JSON.stringify(raw)}));});
  }
  open();
  return ()=>{clearControls();stopped=true;generation++;clearTimeout(retry);clearTimeout(deadline);if(socket){socket.onmessage=null;socket.onclose=null;socket.onerror=null;socket.onopen=null;socket.close();}};
}
