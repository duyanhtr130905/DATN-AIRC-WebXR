/** Pure experiment navigation. Horizontal points use Three X/Z, metres. */
export type Point = [number, number];
export type Proxy = {id:string; kind:string; cluster?:string; polygon:Point[]; bottom_z:number; top_z:number; orientation_deg:number};
export type RecordEntry = {id:string; status:string; survey_transform:Record<string,unknown>; authored_bounds_survey:number[]|null};
export type Manifest = {schema_version:number; unit:string; axis_conversion:string; model_sha256:string; model_bytes:number; source_sha:string; checkout_sha:string; survey_baseline:{width_x:number;length_y:number;height_z:number;source:string}; virtual_dimensions:{width_x:number;length_y:number;height_z:number;source:string;rights?:string}; instances:RecordEntry[]; collision_proxies:Proxy[]; floor:{walkable_rect_survey:number[]}; occupied_use:{chair_pullback_m:number}};
export const PLAYER = {radius:.30,height:1.80,eye:1.65,speed:1.2,maxDelta:.05};
export const SPAWN:Point = [1.25,-7.415];
export const surveyToThree = ([x,y,z]:number[]) => [x,z,-y];
export function check(value:unknown,message:string):asserts value { if(!value) throw new Error(message); }
export function validateManifest(m:Manifest) {
  check(m.schema_version===1 && m.unit==='metre' && m.axis_conversion.includes('(x,z,-y)'), 'Unsupported manifest schema/unit/axes');
  const s=m.survey_baseline,v=m.virtual_dimensions;
  check(s.width_x===6 && s.length_y===8.1 && s.height_z===3.5 && s.source==='USER_REPORTED','Survey baseline mismatch');
  check(v.width_x===6.9 && v.length_y===9.315 && v.height_z===3.5 && v.source==='OWNER_APPROVED_VIRTUAL_ADAPTATION','Virtual dimensions mismatch');
  const ids=m.instances.map(i=>i.id),placed=m.instances.filter(i=>i.status!=='UNPLACED');
  check(ids.length===123 && new Set(ids).size===123 && placed.length===121,'Duplicate/missing logical IDs');
  check(m.collision_proxies.length===121 && new Set(m.collision_proxies.map(p=>p.id)).size===121,'Invalid proxy IDs');
  check(placed.every(i=>m.collision_proxies.some(p=>p.id===i.id)),'Missing collision mapping');
  check(['P507-CHAIR-C-09','P507-CHAIR-C-10'].every(id=>m.instances.find(i=>i.id===id)?.status==='UNPLACED'),'Unplaced chairs changed');
  check(m.occupied_use.chair_pullback_m===.15,'Occupied-use assumption changed');
  for(const p of m.collision_proxies) check(p.polygon.length>=3 && p.polygon.every(v=>v.length===2 && v.every(Number.isFinite)) && Number.isFinite(p.bottom_z) && Number.isFinite(p.top_z) && p.top_z>p.bottom_z && (p.orientation_deg===undefined || Number.isFinite(p.orientation_deg)),'Invalid oriented proxy '+p.id);
  return m;
}
export type Collider={id:string;polygon:Point[];bottom:number;top:number};
export function colliders(m:Manifest):Collider[] {
  return m.collision_proxies.flatMap(p=>{
    const original:Collider={id:p.id,polygon:p.polygon.map(([x,y])=>[x,-y]),bottom:p.bottom_z,top:p.top_z};
    if(p.kind!=='chair') return [original];
    const a=p.orientation_deg*Math.PI/180,pull=m.occupied_use.chair_pullback_m;
    // Union of static and occupied envelopes conservatively covers pullback sweep.
    const shifted=original.polygon.map(([x,z])=>[x+pull*Math.sin(a),z+pull*Math.cos(a)] as Point);
    return [original,{...original,polygon:shifted}];
  });
}
const sub=(a:Point,b:Point):Point=>[a[0]-b[0],a[1]-b[1]];
const cross=(a:Point,b:Point)=>a[0]*b[1]-a[1]*b[0];
function pointSegment(p:Point,a:Point,b:Point) {
  const d=sub(b,a),v=sub(p,a),t=Math.max(0,Math.min(1,(v[0]*d[0]+v[1]*d[1])/(d[0]*d[0]+d[1]*d[1]||1)));
  return Math.hypot(p[0]-a[0]-t*d[0],p[1]-a[1]-t*d[1]);
}
function segmentsTouch(a:Point,b:Point,c:Point,d:Point) {
  const ab=sub(b,a),cd=sub(d,c),den=cross(ab,cd);
  if(Math.abs(den)<1e-12) return Math.min(pointSegment(a,c,d),pointSegment(b,c,d),pointSegment(c,a,b),pointSegment(d,a,b))<1e-9;
  const t=cross(sub(c,a),cd)/den,u=cross(sub(c,a),ab)/den;
  return t>=0&&t<=1&&u>=0&&u<=1;
}
function inside(p:Point,poly:Point[]) {
  const signs=poly.map((a,i)=>cross(sub(poly[(i+1)%poly.length],a),sub(p,a)));
  return signs.every(s=>s>=-1e-9)||signs.every(s=>s<=1e-9);
}
export function sweptCircle(a:Point,b:Point,poly:Point[],radius:number) {
  if(inside(a,poly)||inside(b,poly)) return true;
  return poly.some((c,i)=>{const d=poly[(i+1)%poly.length];return segmentsTouch(a,b,c,d)||Math.min(pointSegment(a,c,d),pointSegment(b,c,d),pointSegment(c,a,b),pointSegment(d,a,b))<=radius+1e-6;});
}
export class Navigation {
  obstacles:Collider[];
  rect:number[];
  radius:number; height:number;
  constructor(m:Manifest,radius=PLAYER.radius,height=PLAYER.height) {
    this.radius=radius;this.height=height;
    check(Number.isFinite(radius)&&radius>0&&Number.isFinite(height)&&height>0 && height<=3.5,'Invalid player dimensions');
    this.obstacles=colliders(m).filter(p=>p.bottom<height && p.top>0);
    const [x0,y0,x1,y1]=m.floor.walkable_rect_survey;
    this.rect=[x0,-y1,x1,-y0];
  }
  blocked(a:Point,b:Point):string|null {
    if(![...a,...b].every(Number.isFinite)) return 'INVALID_POSITION';
    const [x0,z0,x1,z1]=this.rect,r=this.radius;
    if([a,b].some(([x,z])=>x<=x0+r||x>=x1-r||z<=z0+r||z>=z1-r)) return 'ROOM_BOUNDARY_OUTSIDE_UNSURVEYED';
    return this.obstacles.find(p=>sweptCircle(a,b,p.polygon,r))?.id??null;
  }
  move(a:Point,delta:Point) {
    const b:Point=[a[0]+delta[0],a[1]+delta[1]],reason=this.blocked(a,b);
    // Stop entire requested step: no unverified slide, teleport or corner cutting.
    return {position:reason?a:b,reason};
  }
}
export function displacement(forward:number,strafe:number,yaw:number,dt:number):Point {
  if(!Number.isFinite(dt)||dt<0) return [0,0];
  const distance=PLAYER.speed*Math.min(dt,PLAYER.maxDelta),n=Math.max(1,Math.hypot(forward,strafe));
  return [(-Math.sin(yaw)*forward+Math.cos(yaw)*strafe)*distance/n,(-Math.cos(yaw)*forward-Math.sin(yaw)*strafe)*distance/n];
}
export function logicalId(node:{userData:Record<string,unknown>;parent:any}|null,known:Set<string>):string|null {
  for(let at=node;at;at=at.parent) {const id=at.userData.survey_instance_id;if(typeof id==='string'&&known.has(id)) return id;}
  return null;
}
export class InputState {
  keys=new Set<string>(); active=false;
  clear(){this.keys.clear();this.active=false;}
  lock(locked:boolean){this.clear();this.active=locked;}
  key(code:string,down:boolean){if(!this.active)return; if(down)this.keys.add(code);else this.keys.delete(code);}
  axes():Point{return [Number(this.keys.has('KeyW'))-Number(this.keys.has('KeyS')),Number(this.keys.has('KeyD'))-Number(this.keys.has('KeyA'))];}
}
export function summarize(raw:number[]) {
  const sorted=raw.slice().sort((a,b)=>a-b),q=(p:number)=>sorted[Math.max(0,Math.ceil(sorted.length*p)-1)]??null;
  return {raw,sampleCount:raw.length,p50:q(.5),p95:q(.95),min:sorted[0]??null,max:sorted.at(-1)??null,fps:raw.length?1000*raw.length/raw.reduce((a,b)=>a+b,0):null,over33_33:raw.filter(t=>t>33.33).length};
}
