import json,glob
P={
"shiritsu":{"room":{"perDay":None,"text":"原則は個室（満床のときは大部屋になることも）。差額は公開されていません"},
 "painless":{"ok":True,"cost":None,"text":"2024年度から無痛分娩を始めています（お母様の体の状態によってえらべる）。2人目以降のお母様は計画分娩もできる（34週ごろまでに申し出）。費用は公開されていません"},
 "oiwai":{"ok":True,"cost":None,"text":"生まれて3日目の夜にお祝い膳あり。追加料金かどうかは書かれていません"},
 "_src":[["京都市立病院 入院について","https://www.kch-org.jp/%E5%BD%93%E9%99%A2%E3%81%A7%E5%87%BA%E7%94%A3%E3%82%92%E3%81%8A%E8%80%83%E3%81%88%E3%81%AE%E6%96%B9%E3%81%B8/%E5%85%A5%E9%99%A2%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6"],["京都市立病院 産婦人科","https://www.kch-org.jp/outline/section/sanfujinka"]]},
"yamamoto":{"painless":{"ok":False,"cost":None,"text":"無痛分娩はしていません（病院のよくある質問より）"},"_src":[["山元病院 よくある質問","https://www.yamamoto-hospital.gr.jp/contact/"]]},
"katsura":{"room":{"perDay":16500,"text":"一般個室は1日16,500円（2026年9月から。それまでは13,200円）、特別個室は28,600円"},
 "painless":{"ok":True,"cost":100000,"text":"希望でできる（計画分娩・平日の日中のみ）。100,000円（2026年4月時点）"},
 "oiwai":{"ok":None,"cost":None,"text":"お祝い膳は公開されていません（お祝いのプレゼントあり）"},
 "_src":[["京都桂病院 妊婦健診・分娩費用","https://www.katsura.com/sanfujinka/medical_checkup.html"],["京都桂病院 無痛分娩","https://www.katsura.com/sanfujinka/labor_analgesia.html"]]},
"mihara":{"painless":{"ok":True,"cost":130000,"text":"希望でできる（計画分娩）。平均13〜15万円ほど（かかった時間や薬の量でかわる）"},"_src":[["身原病院 無痛分娩","https://mihara.com/obstetrics/bunben_howto/mutsu/"]]},
"hashii":{"room":{"perDay":5000,"text":"トイレ付きの個室は1日5,000円（普通分娩の費用は5日間で50万円から）"},"_src":[["ハシイ産婦人科 費用","https://hashii-hp.jp/course/course13/"]]},
"fujita":{"painless":{"ok":None,"cost":None,"text":"公開されていません（自然分娩が基本の方針）"},
 "oiwai":{"ok":True,"cost":None,"text":"お祝いの夕食に、ステーキがメインの洋食フルコースあり。追加料金かどうかは書かれていません"},"_src":[["藤田産科・婦人科医院 診療","https://fujita-ladies.jp/medical/"]]},
"uji-tokushukai":{"room":{"perDay":0,"text":"病院の費用の目安（はじめてのお産で約47万円から・税込）に個室代がふくまれています"}},
"tsugumi":{"oiwai":{"ok":None,"cost":None,"text":"お食事はお産の料金にふくまれています（料金はすべて税込）。お祝い膳は公開されていません"}},
"hosoda":{"_extra":["2026年12月下旬までのお産の予約は、しめ切りと案内されています（2026年11月時点）"],"_src":[["細田クリニック 医院案内","https://hosodaclinic.jp/clinicinfo/"]]},
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
    ch=True; print("patched",d["id"])
  if ch: json.dump(L,open(f,"w"),ensure_ascii=False,indent=1)
