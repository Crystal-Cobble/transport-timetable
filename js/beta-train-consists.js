(()=>{'use strict';
const MAX_PAIR_DISTANCE_METERS=160,MAX_PAIR_SPEED_DIFFERENCE=3,MAX_PAIR_BEARING_DIFFERENCE=30,MAX_PAIR_LATERAL_DISTANCE=22,PAIR_CONFIRMATION_MS=25000,PAIR_CONFIRMATION_REPORTS=3,MAX_REPORT_GAP_MS=45000,MAX_CONFIRMED_ABSENCE_MS=300000;
const labelKey=value=>String(value||'').trim().toUpperCase().replace(/\s+/g,'');
function isTrainUnit(value){return/^AMP\d{3,4}$/.test(labelKey(value))}
function hasChargingPort(value){return/^AMP\d{4}$/.test(labelKey(value))}
function distanceMeters(a,b){const lat=(a.lat+b.lat)/2*Math.PI/180,dx=(b.lng-a.lng)*111320*Math.cos(lat),dy=(b.lat-a.lat)*110540;return{distance:Math.hypot(dx,dy),dx,dy}}
function bearingDifference(a,b){const difference=Math.abs(a-b)%360;return Math.min(difference,360-difference)}
function followingCandidate(a,b){
  if(a.id==null||b.id==null||a.id===b.id||!isTrainUnit(a.label)||!isTrainUnit(b.label)||labelKey(a.label)===labelKey(b.label))return null;
  if(a.outOfService===b.outOfService)return null;
  if(![a.lat,a.lng,b.lat,b.lng,a.speed,b.speed,a.bearing,b.bearing].every(Number.isFinite)||a.speed<1.5||b.speed<1.5)return null;
  if(a.timestamp&&b.timestamp&&Math.abs(a.timestamp-b.timestamp)>30)return null;
  if(a.tripId&&b.tripId&&a.tripId!==b.tripId)return null;
  if(a.routeId&&b.routeId&&a.routeId!==b.routeId)return null;
  if(Math.abs(a.speed-b.speed)>MAX_PAIR_SPEED_DIFFERENCE||bearingDifference(a.bearing,b.bearing)>MAX_PAIR_BEARING_DIFFERENCE)return null;
  const vector=distanceMeters(a,b),bearing=a.bearing*Math.PI/180,longitudinal=vector.dx*Math.sin(bearing)+vector.dy*Math.cos(bearing),lateral=Math.abs(vector.dx*Math.cos(bearing)-vector.dy*Math.sin(bearing));
  if(vector.distance>MAX_PAIR_DISTANCE_METERS||Math.abs(longitudinal)<25||lateral>MAX_PAIR_LATERAL_DISTANCE)return null;
  if(a.outOfService!==b.outOfService){
    const active=a.outOfService?b:a,outOfService=a.outOfService?a:b,leadToFollower=distanceMeters(active,outOfService),activeBearing=active.bearing*Math.PI/180,behind=leadToFollower.dx*Math.sin(activeBearing)+leadToFollower.dy*Math.cos(activeBearing);
    if(behind>=-25)return null
  }
  return{a,b,distance:vector.distance};
}
function followingPairs(vehicles){
  const edges=[],degree=new Map;
  for(let i=0;i<vehicles.length;i++)for(let j=i+1;j<vehicles.length;j++){
    const edge=followingCandidate(vehicles[i],vehicles[j]);
    if(!edge)continue;
    edges.push(edge);
    degree.set(edge.a.id,(degree.get(edge.a.id)||0)+1);
    degree.set(edge.b.id,(degree.get(edge.b.id)||0)+1);
  }
  return edges.filter(edge=>degree.get(edge.a.id)===1&&degree.get(edge.b.id)===1).map(edge=>[edge.a,edge.b]);
}
function createTracker(){
  const candidates=new Map,confirmed=new Map,lastVehicles=new Map;
  return{
    observe(vehicles,now=Date.now()){
      const byId=new Map;
      for(const vehicle of vehicles)if(vehicle&&vehicle.id!=null){const id=String(vehicle.id);byId.set(id,vehicle);lastVehicles.set(id,vehicle)}
      const nextCandidates=new Set;
      for(const [a,b] of followingPairs(vehicles)){
        if(a.outOfService===b.outOfService)continue;
        const ids=[a.id,b.id].map(String).sort(),key=ids.join('|'),previous=candidates.get(key);
        nextCandidates.add(key);
        const observation=previous&&now-previous.lastSeen<=MAX_REPORT_GAP_MS?{startedAt:previous.startedAt,reports:previous.reports+1,lastSeen:now}:{startedAt:now,reports:1,lastSeen:now,ids};
        candidates.set(key,observation);
        if(observation.reports>=PAIR_CONFIRMATION_REPORTS&&now-observation.startedAt>=PAIR_CONFIRMATION_MS)confirmed.set(key,{ids,lastSeen:now});
      }
      for(const key of candidates.keys())if(!nextCandidates.has(key))candidates.delete(key);
      for(const [key,record] of confirmed){
        if(record.ids.some(id=>byId.has(id)))record.lastSeen=now;
        else if(now-record.lastSeen>MAX_CONFIRMED_ABSENCE_MS){confirmed.delete(key);for(const id of record.ids)lastVehicles.delete(id)}
      }
      return[...confirmed.values()].map(({ids})=>ids.map(id=>byId.get(id)||lastVehicles.get(id)).filter(Boolean)).filter(pair=>pair.length===2);
    }
  };
}
window.ATTrainConsists={labelKey,isTrainUnit,hasChargingPort,followingPairs,createTracker};
})();
