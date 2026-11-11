
(function(){
const state={room:true,painless:false,oiwai:false,ward:"すべて",sort:"area"};
try{const s=JSON.parse(localStorage.getItem("sanin-sim")||"null");if(s)Object.assign(state,s);}catch(e){}
const WARDS=AREAS.flatMap(a=>a.list);
if(state.ward!=="すべて"&&!WARDS.includes(state.ward)&&!AREAS.some(a=>"@"+a.label===state.ward))state.ward="すべて";
const save=()=>{try{localStorage.setItem("sanin-sim",JSON.stringify(state))}catch(e){}};
const yen=n=>n.toLocaleString("ja-JP")+"円";
const man=n=>(Math.round(n/1000)/10).toFixed(1).replace(/\.0$/,"")+"万円";
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const inArea=(w,key)=>key==="すべて"||w===key||(key.startsWith("@")&&(AREAS.find(a=>"@"+a.label===key)||{list:[]}).list.includes(w));
function mine(h){let sum=0;const unk=[],no=[];
 if(state.room){if(h.room.perDay===null)unk.push("個室");else if(h.days===null)unk.push("入院日数");else sum+=h.room.perDay*h.days;}
 if(state.painless){if(h.painless.ok===false)no.push("無痛分娩");else if(h.painless.cost===null)unk.push("無痛分娩");else sum+=h.painless.cost;}
 if(state.oiwai){if(h.oiwai.ok===false)no.push("お祝い膳");else if(h.oiwai.cost===null)unk.push("お祝い膳");else sum+=h.oiwai.cost;}
 return {sum,unk,no};}
function cell(h){if(!state.room&&!state.painless&&!state.oiwai)return '<td class="mine">希望をえらぶと出ます</td>';
 const m=mine(h);let s='<b>'+(m.unk.length?"わかる分 ":"")+yen(m.sum)+'</b>';
 m.unk.forEach(u=>s+='<br><span class="unk">'+u+'は産院に確認</span>');m.no.forEach(u=>s+='<br><span class="no">'+u+'はできません</span>');
 return '<td class="mine">'+s+'</td>';}
const sel=document.getElementById("area-sel");
const opt=(v,t)=>'<option value="'+v+'"'+(state.ward===v?" selected":"")+'>'+t+'</option>';
sel.innerHTML=opt("すべて","京都府ぜんたい")+AREAS.map(a=>'<optgroup label="'+a.label+'">'+opt("@"+a.label,a.label+"ぜんたい")+a.list.filter(w=>H.some(h=>h.ward===w)).map(w=>opt(w,w)).join("")+'</optgroup>').join("");
["room","painless","oiwai"].forEach(k=>document.getElementById("opt-"+k).checked=state[k]);
function draw(){
 let list=H.filter(h=>inArea(h.ward,state.ward));
 if(state.sort==="mine"){const k=h=>{const m=mine(h);return (m.no.length?2e9:0)+(m.unk.length?1e9:0)+m.sum;};list=list.slice().sort((a,b)=>k(a)-k(b));}
 if(state.sort==="total"){const k=h=>h.total?h.total.avg:9e9;list=list.slice().sort((a,b)=>k(a)-k(b));}
 document.getElementById("rows").innerHTML=list.map(h=>'<tr><th><a href="sanin-'+h.id+'.html">'+esc(h.name)+'</a><small>'+h.ward+'・'+esc(h.type)+'</small></th>'+cell(h)+'<td>'+esc(h.room.text)+'</td><td>'+esc(h.painless.text)+'</td><td>'+esc(h.oiwai.text)+'</td><td>'+esc(h.tachiai)+'</td><td class="num">'+(h.total?"平均 "+man(h.total.avg)+(h.days?"<br>入院 約"+h.days+"日":""):"出産なびに記載なし")+'</td></tr>').join("")||'<tr><td colspan="7">このエリアでは、お産ができる施設が確認できませんでした。</td></tr>';
 const pl=h=>{const r=h.room.perDay,p=h.painless,o=h.oiwai;
  const a=r===null?["公開されていない","unk"]:(r===0?["差額なし","ok"]:["1日"+r.toLocaleString("ja-JP")+"円から","ok"]);
  const b=p.ok===null?["公開されていない","unk"]:(p.ok===false?["希望ではできない","no"]:[p.cost?"できる・"+p.cost.toLocaleString("ja-JP")+"円":"できる・料金は未公開","ok"]);
  const c=o.ok===null?["公開されていない","unk"]:(o.ok===false?["なし","no"]:[o.cost===0?"あり・無料":"あり","ok"]);
  return '<dl class="hc-pills"><div><dt>個室</dt><dd><span class="pl '+a[1]+'">'+a[0]+'</span></dd></div><div><dt>無痛分娩</dt><dd><span class="pl '+b[1]+'">'+b[0]+'</span></dd></div><div><dt>お祝い膳</dt><dd><span class="pl '+c[1]+'">'+c[0]+'</span></dd></div></dl>';};
 const mineBox=h=>{if(!state.room&&!state.painless&&!state.oiwai)return "";const m=mine(h);let s='<div class="hc-mine"><span>じぶん払いの目安</span><b>'+(m.unk.length?"わかる分 ":"")+yen(m.sum)+'</b>';m.unk.forEach(u=>s+='<em class="unk">'+u+'は産院に確認</em>');m.no.forEach(u=>s+='<em class="no">'+u+'はできません</em>');return s+'</div>';};
 document.getElementById("cards").innerHTML=list.map(h=>'<article class="hcard"><div class="hc-top"><a class="hc-name" href="sanin-'+h.id+'.html">'+esc(h.name)+'</a><span class="hc-ward">'+h.ward+'・'+esc(h.type)+'</span></div>'+mineBox(h)+pl(h)+'<p class="hc-more"><a href="sanin-'+h.id+'.html">くわしく見る</a></p></article>').join("")||'<p class="wardnote">このエリアでは、お産ができる施設が確認できませんでした。</p>';
 const ns=Object.keys(NOTES).filter(w=>inArea(w,state.ward));
 document.getElementById("notes").innerHTML=state.ward==="すべて"?'<div class="wardnote">お産ができる施設が見つからなかった市町村もあります。エリアをえらぶと、近くの産院の案内が出ます。</div>':ns.map(w=>'<div class="wardnote"><b>'+w+'について</b><br>'+NOTES[w]+'</div>').join("");
}
document.addEventListener("change",e=>{const m={"opt-room":"room","opt-painless":"painless","opt-oiwai":"oiwai"};
 if(m[e.target.id]){state[m[e.target.id]]=e.target.checked;save();draw();}
 if(e.target.id==="area-sel"){state.ward=e.target.value;save();draw();}
 if(e.target.id==="sort-sel"){state.sort=e.target.value;save();draw();}});
document.getElementById("sort-sel").value=state.sort||"area";
draw();
})();
