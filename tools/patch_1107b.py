import json,glob
P={
"fukuchiyama-shimin":{"room":{"perDay":5500,"text":"産科の一般個室Aは5,500円（税込）。陣痛からお産まで同じお部屋（LDR）は11,000円、特別個室は16,500円"},"_src":[["市立福知山市民病院 有料個室","https://www.city.fukuchiyama.lg.jp/site/hosp/2962.html"]]},
"hokubu-iryo":{"room":{"perDay":None,"text":"病院の個室料は1日3,480円か4,650円、特別室は13,950円。産科のお部屋がどれにあたるかは書かれていません"},"_src":[["北部医療センター 入院のご案内","https://nmc.kpu-m.ac.jp/doc/kanja/nyuuin.html"]]},
"tamura":{"oiwai":{"ok":True,"cost":None,"text":"お祝い膳あり（病院のブログより）。追加料金かどうかは書かれていません"},"_src":[["田村産婦人科医院 ブログ","https://tamura-hp.com/blog/"]]},
"yamaguchi":{"room":{"perDay":None,"text":"特別室（洗面・トイレ・シャワー付き）、個室（ソファー付き・シャワー付き・一般）、4人部屋、和室あり。差額は公開されていません"},
 "_extra":["赤ちゃんといっしょのお部屋（母子同室）","JR嵯峨野線の馬堀駅から歩いて1分。駐車場あり","週3回、夕食がスペシャルメニュー（和食・イタリアン・フレンチなど）"],
 "_src":[["山口マタニティクリニック 施設","http://www.yamaguchi-mc.jp/yamaguchi_shisestu.html"],["山口マタニティクリニック 食事","http://www.yamaguchi-mc.jp/yamaguchi_meal.html"]]},
"yura":{"room":{"perDay":None,"text":"和室が中心（洋室も相談できる）。お部屋にご家族用の布団あり。差額は公開されていません"},"_src":[["由良産婦人科 施設","https://www.yuraladies.com/facility.html"]]},
"katayama":{"room":{"perDay":None,"text":"個室・4人部屋あり。差額は公開されていません"},"_src":[["片山産婦人科 写真","https://katayama-angel.net/photo"]]},
}
for f in glob.glob("data/data_*.json"):
  L=json.load(open(f)); ch=False
  for d in L:
    p=P.get(d["id"])
    if not p: continue
    for k,v in p.items():
      if k=="_src":
        for s in v:
          if s[1] not in [x[1] for x in d["src"]]: d["src"].append(s)
      elif k=="_extra": d["extra"]=d.get("extra",[])+[e for e in v if e not in d.get("extra",[])]
      else: d[k]=v
    ch=True; print("patched",d["id"], d.get("tachiai"), d.get("days"))
  if ch: json.dump(L,open(f,"w"),ensure_ascii=False,indent=1)
