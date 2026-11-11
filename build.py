# さんいん手帖 本番用サイトを作るスクリプト
# ドメイン・Amazonのタグ・メールアドレスが決まったら、下の CONFIG を書きかえて
#   python3 build.py
# を実行すると、site/ フォルダにすべてのページができます。
import json, re, os, html, shutil, urllib.parse

CONFIG = {
    "SITE_URL": "https://sanin-techo.jp",   # ← 取ったドメイン（例 https://sanin-techo.jp）
    "AMAZON_TAG": "",                     # ← AmazonアソシエイトのトラッキングID（例 xxxx-22）
    "CONTACT_EMAIL": "info@sanin-techo.jp",                  # ← お問い合わせ用のメールアドレス
    "CONTACT_FORM_URL": "",               # ← Googleフォームなどを使うときのURL（なければ空）
    "COMPANY": "株式会社Bright Future Family",
    "REPRESENTATIVE": "藤川 海美",
    "COMPANY_ADDRESS": "",                # ← 所在地（のせる場合）
    "CHECKED": "2026年11月2日",
}
OUT = "docs"
SITE_NAME = "さんいん手帖 京都"

AREAS = [
 {"slug":"kyoto-shi","label":"京都市","list":["北区","上京区","左京区","中京区","東山区","山科区","下京区","南区","右京区","西京区","伏見区"]},
 {"slug":"otokuni","label":"乙訓","list":["長岡京市","向日市","大山崎町"]},
 {"slug":"uji-joyo","label":"宇治・城陽","list":["宇治市","城陽市","久御山町","宇治田原町","井手町"]},
 {"slug":"yawata-kyotanabe","label":"八幡・京田辺","list":["八幡市","京田辺市"]},
 {"slug":"soraku","label":"相楽","list":["木津川市","精華町","和束町","笠置町","南山城村"]},
 {"slug":"kameoka-nantan","label":"亀岡・南丹","list":["亀岡市","南丹市","京丹波町"]},
 {"slug":"chutan","label":"中丹","list":["福知山市","舞鶴市","綾部市"]},
 {"slug":"tango","label":"丹後","list":["宮津市","京丹後市","与謝野町","伊根町"]},
]
def A(u,t): return f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'
NOTES = {
 "下京区":"2026年11月時点で、区の中でお産ができる産院は確認できませんでした。松本クリニックは2026年10月31日に閉院しています（"+A("https://www.maia-matsumoto.com/news/1034","産院のお知らせ")+"）。",
 "城陽市":"市の中でお産ができる産院は確認できませんでした。あみ助産院は、いまお産をしているかどうか確認中です。",
 "久御山町":"町の中でお産ができる施設は確認できませんでした。京都岡本記念病院は、2007年からお産をしていません（"+A("https://www.okamoto-hp.or.jp/oka2/medical/department/sanfujin.html","病院のページ")+"）。",
 "宇治田原町":"町の中でお産ができる施設は確認できませんでした。",
 "井手町":"町の中でお産ができる施設は確認できませんでした。",
 "宇治市":"曽我産婦人科は、2026年9月末でお産を終えています（"+A("https://www.soga-maternity.jp/news/20260819.html","医院のお知らせ")+"）。",
 "大山崎町":"町の中でお産ができる施設は確認できませんでした。同じ乙訓地域では、長岡京市・向日市の産院でお産ができます。",
 "京田辺市":"京都田辺中央病院は、2025年9月からお産を一時休止しています（妊婦健診と産後ケアは続いています）。",
 "和束町":"町の中でお産ができる施設は確認できませんでした。",
 "笠置町":"町の中でお産ができる施設は確認できませんでした。",
 "南山城村":"村の中でお産ができる施設は確認できませんでした。",
 "京丹波町":"町の中でお産ができる施設は確認できませんでした。",
 "宮津市":"市の中でお産ができる施設は確認できませんでした。",
 "伊根町":"町の中でお産ができる施設は確認できませんでした。",
 "舞鶴市":"舞鶴共済病院は、2026年3月末からお産を一時休止しています（"+A("https://maizuru.kkr.or.jp/common/pdf/news_sanfujin20260203.pdf","病院のお知らせ")+"）。",
 "綾部市":"綾部市立病院は、2022年5月からお産を一時休止しています（"+A("https://www.ayabe-hsp.or.jp/patient/shinryou/sanfujinka.html","病院のページ")+"）。",
}
CITY = "https://www.city.kyoto.lg.jp/hagukumi/cmsfiles/contents/0000168/168986/shisetuichirann.pdf"
OLD_CITY = "https://www.city.kyoto.lg.jp/hagukumi/cmsfiles/contents/0000168/168986/080301.pdf"

# ---------- データ ----------
order = [w for a in AREAS for w in a["list"]]
H = []
for f in ["data/data_core.json","data/data_kita_kamigyo.json","data/data_higashiyama_yamashina.json","data/data_minami_fushimi.json","data/data_nishikyo.json","data/data_uji.json","data/data_nanbu.json","data/data_nantan.json","data/data_hokubu.json"]:
    H += json.load(open(f))
for h in H:
    h["type"] = h["type"].replace("（NICUあり）","")
    for s in h["src"]:
        if s[1] in ("CITY", OLD_CITY): s[1] = CITY
        if s[0].startswith("京都市 スマイルママ") : s[0] = "京都市 スマイルママ・ホッと事業 施設一覧（令和8年8月）"
H.sort(key=lambda h: order.index(h["ward"]))
area_of = {w:a for a in AREAS for w in a["list"]}

esc = lambda s: html.escape(str(s), quote=True)
yen = lambda n: f"{n:,}円"
def man(n): v = round(n/1000)/10; return (f"{v:.1f}".rstrip("0").rstrip(".")) + "万円"

def amazon_url(kw):
    q = urllib.parse.quote(kw)
    tag = CONFIG["AMAZON_TAG"]
    return f"https://www.amazon.co.jp/s?k={q}" + (f"&tag={tag}" if tag else "")

# ---------- 記事 ----------
def read_articles(path):
    arts = []
    for blk in open(path).read().split("===")[1:]:
        first, body = blk.split("\n", 1)
        parts = first.split("|")
        arts.append({"id":parts[0], "title":parts[1], "date":parts[2], "pr": len(parts)>3 and parts[3]=="pr", "body":body.strip()})
    return arts

def gen_painless_article():
    lines = ["京都府で、お母様の希望で無痛分娩ができると公開している産院を、地域ごとにまとめました。無償化のあとも、無痛分娩はじぶんで払う部分になると考えられます。追加の料金も、公開されている分だけのせています。",
             "",
             "ならび順は地域ごとで、おすすめ順ではありません。できる時間（24時間かどうか）や、対象のお母様（2人目以降のみなど）は、産院によってちがいます。かならず産院でたしかめてください。",
             "",
             "## ことばの説明",
             "- 硬膜外麻酔：せなかから細い管を入れて、痛みをやわらげるお薬を入れる方法です。多くの無痛分娩で使われています",
             "- 計画分娩：日にちを決めて入院し、お産をする方法です",
             "- 和痛分娩：痛みをやわらげるお産のことです。病院によって、麻酔をつかう方法をこうよぶこともあれば、注射など別の方法をこうよぶこともあります。ここでは、麻酔（硬膜外麻酔）をつかうものを無痛分娩に入れています",
             "- 医学的に必要なときのみ：お母様の希望ではなく、お体の状態で先生が必要と判断したときだけ行う、という意味です"]
    for a in AREAS:
        hs = [h for h in H if h["ward"] in a["list"] and h["painless"]["ok"] is True]
        if not hs: continue
        lines += ["", f"## {a['label']}"]
        for h in hs:
            lines.append(f"- [{h['name']}](sanin-{h['id']}.html)（{h['ward']}）：{h['painless']['text']}")
    no = [h for h in H if h["painless"]["ok"] is False and "助産所" not in h["type"]]
    lines += ["", "## お母様の希望では、無痛分娩をしていない病院", "医学的に必要なときだけ行う病院や、痛みをやわらげる別の方法（和痛分娩）をしている病院です。"]
    for h in no:
        lines.append(f"- [{h['name']}](sanin-{h['id']}.html)（{h['ward']}）：{h['painless']['text']}")
    unk = [h for h in H if h["painless"]["ok"] is None]
    lines += ["", "## まだ公開されていない産院", f"このほか{len(unk)}か所の産院は、無痛分娩をしているかどうか、または料金が公開されていません。さんいん手帖では、産院に問い合わせて、わかりしだい書きくわえていきます。",
              "", "助産所では、麻酔をつかう無痛分娩はしていません。",
              "", f"（出どころ：厚生労働省「出産なび」、各産院のホームページ。{CONFIG['CHECKED']}に調べました）"]
    return {"id":"mutsu-kyoto","title":"京都府で無痛分娩ができる産院と追加料金（2026年11月）","date":CONFIG["CHECKED"],"pr":False,"body":"\n".join(lines)}

def gen_closure_article():
    lines = ["京都府では、ここ数年で、お産をやめたり、一時休止したりする病院がふえています。お住まいの近くでお産ができるかどうかは、早めにたしかめておくと安心です。",
             "",
             "## お産をやめた・休んでいる病院"]
    stops = [
     ("松本クリニック（京都市下京区）","2026年10月31日に閉院","https://www.maia-matsumoto.com/news/1034"),
     ("曽我産婦人科（宇治市）","2026年9月末でお産を終了","https://www.soga-maternity.jp/news/20260819.html"),
     ("舞鶴共済病院（舞鶴市）","2026年3月末からお産を一時休止","https://maizuru.kkr.or.jp/common/pdf/news_sanfujin20260203.pdf"),
     ("京都田辺中央病院（京田辺市）","2025年9月からお産を一時休止（妊婦健診と産後ケアは続いています。病院のホームページより）",None),
     ("綾部市立病院（綾部市）","2022年5月からお産を一時休止","https://www.ayabe-hsp.or.jp/patient/shinryou/sanfujinka.html"),
     ("京都岡本記念病院（久御山町）","2007年11月からお産をしていません","https://www.okamoto-hp.or.jp/oka2/medical/department/sanfujin.html"),
    ]
    for n,t,u in stops:
        lines.append(f"- {n}：{t}" + (f"（[お知らせ]({u})）" if u else ""))
    lines += ["", "## 中でお産ができる施設が見つからなかった市町村・区"]
    empty = [w for w in order if not any(h["ward"]==w for h in H)]
    lines.append("- " + "、".join(empty))
    lines += ["", "これらの地域にお住まいのお母様は、となりの市町村や京都市内の産院でお産をすることになります。健診に通う時間や、陣痛のときの移動の時間も考えて、産院をえらんでください。",
              "", "## 地域ごとの、いまお産ができる施設の数"]
    for a in AREAS:
        n = sum(1 for h in H if h["ward"] in a["list"])
        lines.append(f"- [{a['label']}](area-{a['slug']}.html)：{n}か所")
    lines += ["", "## 早めにしておきたいこと",
              "- 妊娠がわかったら、お産をする産院の予約がいつまでか、早めに聞いておく（予約の数に限りがある産院もあります）",
              "- 里帰り出産をするときは、何週までに受診が必要かをたしかめる",
              "- 陣痛のときにどうやって産院へ行くか（タクシー・家族の車など）を決めておく",
              "", f"（出どころ：各病院のお知らせ・ホームページ、厚生労働省「出産なび」。{CONFIG['CHECKED']}に調べました）"]
    return {"id":"bunben-kyoto","title":"京都府でお産ができる場所が減っています｜お産をやめた病院と、施設がない市町村（2026年）","date":CONFIG["CHECKED"],"pr":False,"body":"\n".join(lines)}

def gen_room_article():
    lines = ["出産費用の無償化が始まると、お産そのものの費用は産院によるちがいが小さくなります。そのぶん、個室をえらぶかどうかや、個室の料金が、じぶんで払う部分として大きくなります。京都府の産院の個室の料金を、地域ごとにまとめました。",
             "",
             "ならび順は地域ごとで、おすすめ順ではありません。金額は、公開されている1日あたりの追加の料金（差額）です。お部屋のタイプによって金額がちがう産院では、いちばん低い金額を目安にのせ、くわしくは各産院のページに書いています。",
             "",
             "## 見かたのポイント",
             "- 個室代の目安：5日入院すると、1日の差額 × 5日ぶんがかかります。たとえば1日5,000円なら、5日で25,000円です",
             "- 「お部屋代がお産の料金にふくまれています」と書いてある産院は、個室でも追加がかからないか、お産の料金の中に入っています",
             "- 全室個室の産院でも、お部屋のタイプによって追加の料金がちがうことがあります",
             "- 無償化のあと、個室の料金がどのようにあつかわれるかは、まだ決まっていない部分があります"]
    for a in AREAS:
        hs = [h for h in H if h["ward"] in a["list"]]
        if not hs: continue
        lines += ["", f"## {a['label']}"]
        for h in hs:
            r = h["room"]; pd = r.get("perDay")
            head = "追加なし" if pd == 0 else ((f"1日{yen(pd)}から" + ("（税込の目安）" if "税別" in r["text"] else "")) if pd else "金額は公開されていません")
            if pd is None and "公開されていません" in r["text"]: head = ""
            lines.append(f"- [{h['name']}](sanin-{h['id']}.html)（{h['ward']}）：" + (head + "。" if head else "") + r["text"])
    known = sum(1 for h in H if h["room"].get("perDay") is not None)
    lines += ["", "## まだ公開されていない産院", f"{len(H)}か所のうち、個室の追加の料金がわかっているのは{known}か所です。のこりの産院は、さんいん手帖から問い合わせて、わかりしだい書きくわえていきます。",
              "", f"（出どころ：厚生労働省「出産なび」、各産院のホームページ、産院への問い合わせ。{CONFIG['CHECKED']}〜2026年11月11日に調べました）"]
    return {"id":"koshitsu-kyoto","title":"京都府の産院の個室代（1日あたりの追加料金）まとめ｜無償化のあとはじぶんで払う部分（2026年11月）","date":"2026年11月11日","pr":False,"body":"\n".join(lines)}

def gen_oiwai_article():
    lines = ["お産のあとに出る「お祝い膳」は、産院ごとにちがいが大きいところです。追加の料金がかかるかどうかもふくめて、公開されている情報と、産院に問い合わせてわかったことを地域ごとにまとめました。",
             "",
             "ならび順は地域ごとで、おすすめ順ではありません。メニューや出る日は変わることがあるので、かならず産院でたしかめてください。"]
    for a in AREAS:
        hs = [h for h in H if h["ward"] in a["list"] and h["oiwai"]["ok"] is True]
        if not hs: continue
        lines += ["", f"## {a['label']}"]
        for h in hs:
            c = h["oiwai"].get("cost")
            head = "追加料金なし" if c == 0 else ((f"{yen(c)}" + ("（税込の目安）" if "税別" in h["oiwai"]["text"] else "")) if c else "")
            if head and ("追加料金なし" in h["oiwai"]["text"] or "無料" in h["oiwai"]["text"] or "円" in h["oiwai"]["text"]): head = "" if c == 0 else head
            lines.append(f"- [{h['name']}](sanin-{h['id']}.html)（{h['ward']}）：" + (head + "。" if head else "") + h["oiwai"]["text"])
    no = [h for h in H if h["oiwai"]["ok"] is False]
    if no:
        lines += ["", "## お祝い膳はないと案内している産院"]
        for h in no:
            lines.append(f"- [{h['name']}](sanin-{h['id']}.html)（{h['ward']}）：{h['oiwai']['text']}")
    unk = [h for h in H if h["oiwai"]["ok"] is None]
    lines += ["", "## まだ公開されていない産院", f"このほか{len(unk)}か所の産院は、お祝い膳があるかどうかが公開されていません。さんいん手帖では、産院に問い合わせて、わかりしだい書きくわえていきます。",
              "", f"（出どころ：厚生労働省「出産なび」、各産院のホームページ、産院への問い合わせ。{CONFIG['CHECKED']}〜2026年11月11日に調べました）"]
    return {"id":"oiwai-kyoto","title":"京都府の産院のお祝い膳まとめ｜追加料金はかかる？（2026年11月）","date":"2026年11月11日","pr":False,"body":"\n".join(lines)}

ARTICLES = read_articles("content/articles.md") + read_articles("content/articles_data_static.md") + [gen_painless_article(), gen_room_article(), gen_oiwai_article(), gen_closure_article()] + read_articles("content/articles_junbi.md")
for a in ARTICLES:
    a["body"] = a["body"].replace("さんいん手帖の「京都の産院をくらべる」ページ", "さんいん手帖の「[京都の産院をくらべる](kuraberu.html)」ページ").replace("記事「京都市の産後ケア（スマイルママ・ホッと事業）の使い方と料金」","記事「[京都市の産後ケア（スマイルママ・ホッと事業）の使い方と料金](yomimono-sangocare.html)」")

def inline(t):
    out = ""; pos = 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", t):
        out += esc(t[pos:m.start()])
        label, url = m.group(1), m.group(2)
        if url.startswith("amazon:"):
            out += f'<a class="aff" href="{esc(amazon_url(url[7:]))}" target="_blank" rel="sponsored noopener">{esc(label)}</a>'
        elif url.startswith("http"):
            out += f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'
        else:
            out += f'<a href="{esc(url)}">{esc(label)}</a>'
        pos = m.end()
    return out + esc(t[pos:])

def md(text):
    out = []; lst = None; para = []
    def fp():
        nonlocal para
        if para: out.append("<p>"+inline("".join(para))+"</p>"); para = []
    def fl():
        nonlocal lst
        if lst: out.append(f"</{lst}>"); lst = None
    for l in text.split("\n"):
        if l.startswith("## "): fp(); fl(); out.append("<h2>"+inline(l[3:])+"</h2>")
        elif l.startswith("- "):
            fp()
            if lst != "ul": fl(); out.append("<ul>"); lst = "ul"
            out.append("<li>"+inline(l[2:])+"</li>")
        elif re.match(r"^\d+\. ", l):
            fp()
            if lst != "ol": fl(); out.append("<ol>"); lst = "ol"
            out.append("<li>"+inline(re.sub(r"^\d+\. ","",l))+"</li>")
        elif not l.strip(): fp(); fl()
        elif l.startswith("（出どころ"): fp(); fl(); out.append('<p class="src">'+inline(l)+"</p>")
        else: fl(); para.append(l)
    fp(); fl()
    return "\n".join(out)

# ---------- 共通のわく ----------
NAV = [("index.html","トップ","top"),("kuraberu.html","産院をくらべる","kuraberu"),("area.html","エリアでさがす","area"),("yomimono.html","読みもの","yomimono"),("junbi.html","出産じゅんび","junbi")]
CSS_EXTRA = """
.aff{font-weight:700}
/* hero */
.hero-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:40px;align-items:center}
@media (max-width:820px){.hero-grid{grid-template-columns:1fr;gap:24px}}
.hero h1 .nb{display:inline-block}
.hero-art{display:grid;justify-items:end;align-content:center}
.hero-illust{width:min(280px,72%);height:auto;margin:0 30px -18px 0;position:relative;z-index:0;filter:drop-shadow(0 8px 18px rgba(40,50,46,.10))}
.hero-art .receipt{position:relative;z-index:1}
@media (max-width:820px){.hero-art{justify-items:center}.hero-illust{width:min(230px,64%);margin:0 0 -10px}}
.logo{align-items:center}
.logo-mark{width:28px;height:28px;flex:none}
@media (min-width:821px){.hero-grid .hero-text h1{font-size:clamp(2rem,3.3vw,2.6rem)}}
.receipt{background:var(--paper);border:1px solid var(--line);border-top:5px solid var(--beni);border-radius:6px 6px 10px 10px;padding:18px 20px 16px;box-shadow:0 10px 30px -18px rgba(40,50,46,.35);font-variant-numeric:tabular-nums;max-width:420px;width:100%;justify-self:end}
@media (max-width:820px){.receipt{justify-self:stretch;max-width:none}}
.rc-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap;padding-bottom:10px;border-bottom:2px solid var(--ink)}
.rc-head b{font-family:var(--display);font-size:1.15rem;letter-spacing:.08em}
.rc-head span{font-size:.75rem;color:var(--sub)}
.receipt ul{list-style:none;margin:0;padding:0}
.receipt li{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:11px 0;border-bottom:1px dashed var(--line);font-size:.95rem}
.receipt li b{font-size:.82rem;border-radius:999px;padding:2px 10px;white-space:nowrap}
.receipt b.ins{background:var(--ai-soft);color:var(--ai)}
.receipt b.self{background:var(--beni-soft);color:var(--beni)}
.receipt b.city{background:var(--mute);color:var(--sub)}
.rc-foot{margin-top:12px;font-family:var(--display);font-weight:700;font-size:1rem}
.rc-foot b{color:var(--beni)}
.rc-note{font-size:.75rem;color:var(--sub);margin:.4em 0 0}
/* nav on phone */
@media (max-width:640px){
 header.top .wrap{padding-block:10px 0;gap:6px}
 nav.menu{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;width:100%;gap:0 18px;padding-bottom:10px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
 nav.menu::-webkit-scrollbar{display:none}
 nav.menu a{padding:4px 0}
}
/* cards / table switch */
.cards{display:grid;gap:12px;margin-top:16px}
@media (min-width:760px){.narrow-only{display:none!important}}
@media (max-width:759px){.wide-only{display:none!important}}
.hcard{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:10px}
.hc-top{display:grid;gap:2px}
.hc-name{font-family:var(--display);font-weight:700;font-size:1.1rem;color:var(--ink);text-decoration:none}
.hc-name:hover{text-decoration:underline}
.hc-ward{font-size:.8rem;color:var(--sub)}
.hc-mine{background:var(--beni-soft);border-radius:8px;padding:10px 12px;display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}
.hc-mine span{font-size:.78rem;color:var(--sub);width:100%}
.hc-mine b{font-family:var(--display);font-size:1.35rem;font-variant-numeric:tabular-nums}
.hc-mine em{font-style:normal;font-size:.72rem;font-weight:700;border-radius:3px;padding:0 6px}
.hc-mine em.unk{color:var(--warn);background:var(--warn-soft)}
.hc-mine em.no{color:var(--sub);background:var(--mute)}
dl.hc-pills{display:grid;gap:6px;margin:0}
dl.hc-pills>div{display:grid;grid-template-columns:5.5em 1fr;align-items:center;gap:8px}
dl.hc-pills dt{font-size:.82rem;color:var(--sub);font-weight:700}
dl.hc-pills dd{margin:0}
.pl{display:inline-block;font-size:.85rem;font-weight:700;border-radius:999px;padding:2px 10px;line-height:1.6}
.pl.ok{background:var(--ai-soft);color:var(--ai)}
.pl.no{background:var(--mute);color:var(--sub)}
.pl.unk{background:var(--warn-soft);color:var(--warn)}
.hc-more{margin:0;font-size:.9rem;text-align:right}
.hc-more a{font-weight:700}
.hc-more a::after{content:" →"}
.hsum{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 24px}
@media (min-width:760px){.hsum dl.hc-pills{grid-template-columns:repeat(3,1fr)}.hsum dl.hc-pills>div{grid-template-columns:auto 1fr}}
.prnote{font-size:.92rem;background:var(--warn-soft);border:1px solid var(--warn);border-radius:8px;padding:10px 14px;color:var(--ink);margin:10px 0 18px}
.prnote b{color:var(--warn)}
.prtag{display:inline-block;font-size:.72rem;font-weight:700;color:var(--paper);background:var(--sub);border-radius:3px;padding:0 6px;margin-left:6px;vertical-align:middle}
footer nav{display:flex;flex-wrap:wrap;gap:4px 16px}
footer nav a{color:var(--sub)}
.legal{max-width:40em}
.legal h2{font-size:1.15rem;margin:1.6em 0 .4em}
.copy{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px}
.copy code{background:var(--mute);padding:6px 10px;border-radius:6px;font-size:1rem;user-select:all}
.hlist{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:14px}
.hlist a.box{text-decoration:none;color:var(--ink);display:block}
.hlist a.box:hover h3{text-decoration:underline}
.hlist .who{margin-bottom:2px}
.hlist p{font-size:.85rem;color:var(--sub);margin:.3em 0 0}
"""
def page(fname, title, desc, body, nav="", crumbs=None, preview=False):
    canon = CONFIG["SITE_URL"].rstrip("/") + "/" + ("" if fname=="index.html" else fname)
    full_title = title if fname=="index.html" else f"{title}｜{SITE_NAME}"
    navhtml = "".join(f'<a href="{u}"{" aria-current=\"page\"" if k==nav else ""}>{t}</a>' for u,t,k in NAV)
    ld = ""
    if crumbs:
        items = [{"@type":"ListItem","position":i+1,"name":n,"item":CONFIG["SITE_URL"].rstrip("/")+"/"+u} for i,(n,u) in enumerate(crumbs)]
        ld = '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items},ensure_ascii=False)+'</script>'
        body = '<div class="crumb">' + " ／ ".join(f'<a href="{u}">{esc(n)}</a>' if i < len(crumbs)-1 else esc(n) for i,(n,u) in enumerate(crumbs)) + '</div>' + body
    head = f"""<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canon)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{"website" if fname=="index.html" else "article"}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary">
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=Noto+Sans+JP:wght@400;500;700&display=swap">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect x='10' y='6' width='44' height='52' rx='8' fill='%23b8475f'/><rect x='10' y='6' width='9' height='52' rx='4' fill='%239c3a50'/><path d='M42 6 v18 l5 -4 l5 4 V6 z' fill='%23f6e3e7'/><path d='M34 46 C24 39 22 33 25.5 29.5 C28.5 26.5 32.5 27.5 34 31 C35.5 27.5 39.5 26.5 42.5 29.5 C46 33 44 39 34 46 Z' fill='%23fff'/></svg>">
{ld}"""
    content = f"""<header class="top"><div class="wrap">
  <a class="logo" href="index.html"><svg class="logo-mark" viewBox="0 0 64 64" aria-hidden="true"><rect x="10" y="6" width="44" height="52" rx="8" fill="#b8475f"/><rect x="10" y="6" width="9" height="52" rx="4" fill="#9c3a50"/><path d="M42 6 v18 l5 -4 l5 4 V6 z" fill="#f6e3e7"/><path d="M34 46 C24 39 22 33 25.5 29.5 C28.5 26.5 32.5 27.5 34 31 C35.5 27.5 39.5 26.5 42.5 29.5 C46 33 44 39 34 46 Z" fill="#fff"/></svg>さんいん手帖<small>京都</small></a>
  <nav class="menu" aria-label="サイトのメニュー">{navhtml}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
  <nav aria-label="サイトについて"><a href="about.html">運営者・このサイトについて</a><a href="ad-policy.html">広告について</a><a href="privacy.html">プライバシーポリシー</a><a href="contact.html">お問い合わせ</a></nav>
  <div>{SITE_NAME}｜運営：{CONFIG["COMPANY"]}</div>
  <div>情報の出どころ：厚生労働省「出産なび」、各産院のホームページ、京都府内の市町村の資料。調べた日：{CONFIG["CHECKED"]}。</div>
  <div>料金やサービスは変わることがあります。かならず産院にご確認ください。このサイトは医療のアドバイスをするものではありません。</div>
</div></footer>"""
    if preview:
        return head + "\n" + content
    return f"""<!doctype html>
<html lang="ja"><head>
<meta charset="utf-8">
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-5V88ZQWV"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());</script>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{head}
</head><body>
{content}
</body></html>"""

# ---------- 各ページ ----------
pages = {}   # fname -> (title, desc, body, nav, crumbs)
def add(fname, title, desc, body, nav="", crumbs=None): pages[fname] = (title, desc, body, nav, crumbs)

count = len(H)
cards = lambda arts: '<div class="yomi">' + "".join(f'<a class="box" href="yomimono-{a["id"]}.html"><span class="date">{a["date"]}</span><h3>{esc(a["title"])}{"<span class=prtag>PR</span>" if a["pr"] else ""}</h3></a>' for a in arts) + '</div>'
main_arts = [a for a in ARTICLES if not a["id"].startswith("junbi")]
junbi_arts = [a for a in ARTICLES if a["id"].startswith("junbi")]

def area_buttons():
    out = []
    for a in AREAS:
        n = sum(1 for h in H if h["ward"] in a["list"])
        out.append(f'<a class="area" href="area-{a["slug"]}.html">{a["label"]}<i>{n}か所</i></a>')
    return '<div class="areas">' + "".join(out) + '</div>'

top = f"""
<div class="hero">
 <div class="hero-grid">
  <div class="hero-text">
  <div class="eyebrow">出産費用の無償化にそなえる、京都府の産院えらび</div>
  <h1><span class="nb">ふつうのお産は、</span><span class="nb">保険で。</span><br><span class="nb">これからは</span><span class="nb"><em>「じぶん払い」</em>で</span><br><span class="nb">産院をえらぶ</span><span class="nb">時代へ。</span></h1>
  <p>2028年6月ごろまでに、ふつうのお産の費用は、国の保険でまかなわれる予定です。産院ごとにちがいが出るのは、個室やお祝い膳、無痛分娩など、じぶんで払うところ。さんいん手帖は、それを京都府の産院ごとにならべて、くらべられるサイトです。</p>
  <div class="actions"><a class="btn main" href="kuraberu.html">京都の産院をくらべる</a><a class="btn line" href="yomimono-mushouka.html">無償化はいつから？</a></div>
  </div>
  <div class="hero-art">
  <img class="hero-illust" src="illust.webp" width="640" height="640" alt="赤ちゃんをだっこするお母様のイラスト" decoding="async">
  <aside class="receipt" aria-label="お産の明細のイメージ">
    <div class="rc-head"><b>お産の明細</b><span>無償化のあと・イメージ</span></div>
    <ul>
      <li><span>分娩費（ふつうのお産）</span><b class="ins">保険で</b></li>
      <li><span>個室（1日あたり）</span><b class="self">じぶん払い</b></li>
      <li><span>お祝い膳</span><b class="self">じぶん払い</b></li>
      <li><span>無痛分娩</span><b class="self">じぶん払い＊</b></li>
      <li><span>退院後の産後ケア</span><b class="city">市町村の料金</b></li>
    </ul>
    <div class="rc-foot">産院ごとにちがうのは、<b>じぶん払い</b>のところ。</div>
    <p class="rc-note">＊無痛分娩のあつかいは、これから決まります。</p>
  </aside>
  </div>
 </div>
  <div class="facts">
    <div class="fact"><b>{count}か所</b><span>さんいん手帖で調べた、京都府内でお産ができる産院・助産所</span></div>
    <div class="fact"><b>差額なし〜1日17,000円</b><span>個室の追加料金（金額を公開している産院）</span></div>
    <div class="fact"><b>7万〜15万円</b><span>無痛分娩の追加料金（金額を公開している産院）</span></div>
  </div>
</div>
<section id="seido">
  <span class="tag">きほん</span>
  <h2>無償化で、なにが変わるの？</h2>
  <p class="lead">2026年5月に法律が決まりました。ふつうのお産には全国おなじ金額がきめられ、その分は保険から払われる予定です。</p>
  <div class="split">
    <div class="box"><div class="who">国（保険）が払う部分</div><h3>ふつうのお産そのもの</h3>
      <ul><li>正常分娩の費用は、全国おなじ金額に</li><li>お母様の持ち出しを、おさえるしくみになる予定</li><li>すべての妊婦さんに、じゅんび用のお金（定額）も出る予定</li></ul></div>
    <div class="box pay"><div class="who">じぶんで払う部分</div><h3>産院ごとにちがうところ</h3>
      <ul><li>個室やランクの高いお部屋</li><li>お祝い膳などのサービス</li><li>無痛分娩など（くわしくはこれから決まります）</li><li>帝王切開は、いまと同じく原則3割</li></ul></div>
    <div class="box"><div class="who">まだ決まっていないこと</div><h3>これから発表されます</h3>
      <ul><li>全国一律の金額がいくらになるか</li><li>産院ごとに、いつから新しいしくみになるか</li><li>決まりしだい、このサイトを書きかえます</li></ul></div>
  </div>
</section>
<section>
  <span class="tag">ものさし</span>
  <h2>くらべるのは、この5つ</h2>
  <p class="lead">無償化のあとは、ここで差がつきます。どれを大切にするかは、ご家族しだいです。</p>
  <div class="rulers">
    <div class="ruler"><b>お部屋</b><span>大部屋・個室・特別室。1日いくら？</span></div>
    <div class="ruler"><b>お食事</b><span>お祝い膳はある？ ふだんの食事は？</span></div>
    <div class="ruler"><b>無痛分娩</b><span>できる？ 24時間？ いくら足される？</span></div>
    <div class="ruler"><b>ご家族</b><span>立ち会い、上のお子様の面会、泊まり</span></div>
    <div class="ruler"><b>産後ケア</b><span>退院後に泊まれる？ 1泊いくら？</span></div>
  </div>
  <div class="actions"><a class="btn main" href="kuraberu.html">京都の産院で計算してみる</a></div>
</section>
<section>
  <span class="tag">エリア</span>
  <h2>エリアでさがす</h2>
  <p class="lead">京都府ぜんたいの、お産ができる産院・助産所をのせています。</p>
  {area_buttons()}
</section>
<section>
  <span class="tag">読みもの</span>
  <h2>知っておきたいこと</h2>
  {cards(main_arts)}
</section>
<section>
  <span class="tag">じゅんび</span>
  <h2>出産までに、そろえるもの</h2>
  {cards(junbi_arts)}
</section>
<section>
  <span class="tag">やくそく</span>
  <h2>さんいん手帖の4つのやくそく</h2>
  <ul class="promise">
    <li><b>ランキングはつけません</b>どの産院がいいかは、ご家族ごとにちがうからです。</li>
    <li><b>口コミ・体験談はのせません</b>のせるのは、金額とサービスの「事実」だけです。</li>
    <li><b>情報の出どころと、調べた日をかきます</b>金額が変わることがあるので、行く前に産院へご確認ください。</li>
    <li><b>お金をいただいたものには「広告」「PR」とかきます</b>ふつうの情報と、まざらないようにします。</li>
  </ul>
</section>
<section id="faq">
  <span class="tag">しつもん</span>
  <h2>よくある質問</h2>
  <details><summary>いつから無料になりますか？</summary><p>2028年6月ごろまでに始まる予定です。じゅんびのできた産院から順番に新しいしくみになるので、産院ごとに時期がちがうことがあります。</p></details>
  <details><summary>帝王切開も無料ですか？</summary><p>帝王切開は、いまと同じく保険で原則3割の負担になる予定です。くわしくは、決まりしだいお知らせします。</p></details>
  <details><summary>出産育児一時金（50万円）はどうなりますか？</summary><p>産院の判断で、しばらくは今のしくみが続くこともあると発表されています。お使いになる産院でご確認ください。</p></details>
  <details><summary>のっている「いまの総額」は、無償化のあとも同じですか？</summary><p>いいえ。いまの総額は、国の「出産なび」の2025年4〜9月の実績です。無償化のあとは、ふつうのお産の分は保険になり、じぶんで払うのは個室などの分になる予定です。</p></details>
  <details><summary>「産院に確認」と出るのはなぜ？</summary><p>産院が金額を公開していない項目です。さんいん手帖では、産院に問い合わせて、わかりしだい書きくわえていきます。</p></details>
</section>
<section>
  <div class="forclinic">
    <h3>産院・病院のみなさまへ</h3>
    <p>個室やお祝い膳、産後ケアなどの料金を、まちがいなくのせたいと考えています。料金表の確認や、情報の直しは、<a href="contact.html">お問い合わせ</a>からご連絡ください。（現在、掲載は無料です）</p>
  </div>
</section>"""
add("index.html", "さんいん手帖 京都｜出産費用の無償化にそなえる産院えらび", f"出産費用の無償化のあとは、個室・お祝い膳・無痛分娩・産後ケアなど「じぶんで払う部分」で産院をえらぶ時代に。京都府の産院{count}か所の料金とサービスを、出どころつきでくらべられます。", top, "top")

# くらべる（計算つき）
kdata = [{k:h[k] for k in ("id","ward","name","type","total","days","room","painless","oiwai","tachiai")} for h in H]
kuraberu_body = f"""
<section style="border-top:0">
  <span class="tag">くらべる</span>
  <h1 class="ph">京都の産院、じぶんで払う分はいくら？</h1>
  <p class="lead">希望をえらぶと、産院ごとに「じぶん払い」の目安を計算します。個室は、それぞれの産院の入院日数のまん中の値でかけ算しています。</p>
  <div class="sim" role="group" aria-label="希望をえらぶ">
    <div class="row"><span class="label">希望</span>
      <label class="chk"><input type="checkbox" id="opt-room" checked> 個室をつかう</label>
      <label class="chk"><input type="checkbox" id="opt-painless"> 無痛分娩をえらぶ</label>
      <label class="chk"><input type="checkbox" id="opt-oiwai"> お祝い膳を食べたい</label>
    </div>
    <div class="row"><span class="label">エリア</span><select id="area-sel" class="pill" aria-label="エリアをえらぶ"></select></div>
  </div>
  <div id="notes"></div>
  <div id="cards" class="cards narrow-only"></div>
  <div class="tablebox wide-only">
    <table>
      <thead><tr><th>産院</th><th>じぶん払いの目安</th><th>お部屋</th><th>無痛分娩</th><th>お祝い膳</th><th>立ち会い</th><th>いまの総額（参考）</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
  <details><summary>ことばの説明（計画分娩・硬膜外麻酔など）</summary><p>計画分娩：日にちを決めて入院し、お産をする方法です。<br>硬膜外麻酔：せなかから細い管を入れて、痛みをやわらげるお薬を入れる方法です。<br>和痛分娩：痛みをやわらげるお産のことです。病院によって、麻酔をつかう方法をこうよぶこともあれば、注射など別の方法をこうよぶこともあります。<br>医学的に必要なときのみ：お母様の希望ではなく、お体の状態で先生が必要と判断したときだけ行う、という意味です。<br>LDR：陣痛からお産、お産のあとまで、同じお部屋ですごせるお部屋です。<br>母子同室・母子別室：入院中、赤ちゃんとお母様が同じお部屋か、別のお部屋かのちがいです。</p></details>
  <p class="note">ならび順は地域ごとで、おすすめ順ではありません。個室の金額がいくつかある産院は、いちばん安い個室で計算しています。「いまの総額」は国の「出産なび」の2025年4〜9月の実績の平均で、無償化の前の金額です。金額は{CONFIG["CHECKED"]}に調べたもので、変わることがあります。</p>
</section>
<script>
const H={json.dumps(kdata,ensure_ascii=False)};
const AREAS={json.dumps([{"label":a["label"],"list":a["list"]} for a in AREAS],ensure_ascii=False)};
const NOTES={json.dumps(NOTES,ensure_ascii=False)};
</script>
<script src="kuraberu.js"></script>"""
add("kuraberu.html", "京都の産院をくらべる｜個室・無痛分娩・お祝い膳のじぶん払い", f"京都府の産院{count}か所について、個室・無痛分娩・お祝い膳をえらんだときの「じぶん払い」の目安を計算できます。", kuraberu_body, "kuraberu", [("トップ","index.html"),("京都の産院をくらべる","kuraberu.html")])

# エリア
def pills(h):
    r=h["room"]["perDay"]; p=h["painless"]; o=h["oiwai"]
    room = ("公開されていない","unk") if r is None else (("差額なし","ok") if r==0 else (f"1日{r:,}円から","ok"))
    pain = ("公開されていない","unk") if p["ok"] is None else (("希望ではできない","no") if p["ok"] is False else ((f"できる・{p['cost']:,}円" if p["cost"] else "できる・料金は未公開"),"ok"))
    oi = ("公開されていない","unk") if o["ok"] is None else (("なし","no") if o["ok"] is False else (("あり・無料" if o["cost"]==0 else "あり"),"ok"))
    return f'<dl class="hc-pills"><div><dt>個室</dt><dd><span class="pl {room[1]}">{room[0]}</span></dd></div><div><dt>無痛分娩</dt><dd><span class="pl {pain[1]}">{pain[0]}</span></dd></div><div><dt>お祝い膳</dt><dd><span class="pl {oi[1]}">{oi[0]}</span></dd></div></dl>'
def hcards(hs):
    return '<div class="cards narrow-only">' + "".join(f'<article class="hcard"><div class="hc-top"><a class="hc-name" href="sanin-{h["id"]}.html">{esc(h["name"])}</a><span class="hc-ward">{h["ward"]}・{esc(h["type"])}</span></div>{pills(h)}<p class="hc-more"><a href="sanin-{h["id"]}.html">くわしく見る</a></p></article>' for h in hs) + '</div>'
def htable(hs):
    rows = "".join(f'<tr><th><a href="sanin-{h["id"]}.html">{esc(h["name"])}</a><small>{h["ward"]}・{esc(h["type"])}</small></th><td>{esc(h["room"]["text"])}</td><td>{esc(h["painless"]["text"])}</td><td>{esc(h["oiwai"]["text"])}</td><td class="num">{("平均 "+man(h["total"]["avg"])+("<br>入院 約"+str(h["days"])+"日" if h["days"] else "")) if h["total"] else "出産なびに記載なし"}</td></tr>' for h in hs)
    return hcards(hs) + f'<div class="tablebox wide-only"><table><thead><tr><th>産院</th><th>お部屋</th><th>無痛分娩</th><th>お祝い膳</th><th>いまの総額（参考）</th></tr></thead><tbody>{rows}</tbody></table></div>'
area_index = '<section style="border-top:0"><span class="tag">エリア</span><h1 class="ph">エリアでさがす</h1><p class="lead">京都府を8つの地域に分けて、お産ができる産院・助産所をのせています。</p>'
for a in AREAS:
    hs = [h for h in H if h["ward"] in a["list"]]
    chips = "".join((f'<span class="area">{w}<i>{sum(1 for h in hs if h["ward"]==w)}か所</i></span>' if any(h["ward"]==w for h in hs) else f'<span class="area">{w}<i>なし</i></span>') for w in a["list"])
    area_index += f'<h2 style="margin-top:1.4em"><a href="area-{a["slug"]}.html">{a["label"]}</a>（{len(hs)}か所）</h2><div class="areas" style="margin-top:6px">{chips}</div>'
    notes = "".join(f'<div class="wardnote"><b>{w}について</b><br>{NOTES[w]}</div>' for w in a["list"] if w in NOTES)
    body = f'<section style="border-top:0"><span class="tag">エリア</span><h1 class="ph">{a["label"]}の産院・助産所（{len(hs)}か所）</h1><p class="lead">{"・".join(a["list"])}で、いまお産ができる施設です。ならび順は市区町村ごとで、おすすめ順ではありません。</p>{notes}{htable(hs)}<div class="actions"><a class="btn main" href="kuraberu.html">じぶん払いの目安を計算する</a><a class="btn line" href="area.html">ほかのエリア</a></div></section>'
    add(f"area-{a['slug']}.html", f"{a['label']}の産院・助産所（{len(hs)}か所）の個室・無痛分娩・お祝い膳", f"京都府{a['label']}（{'・'.join(a['list'])}）でお産ができる産院・助産所{len(hs)}か所の、個室・無痛分娩・お祝い膳・立ち会いのちがいを出どころつきでまとめました。", body, "area", [("トップ","index.html"),("エリアでさがす","area.html"),(a["label"],f"area-{a['slug']}.html")])
area_index += '<p class="note">「なし」は、その市町村の中でお産ができる施設が確認できなかったところです。</p></section>'
add("area.html", "エリアでさがす｜京都府の産院・助産所", "京都府を8つの地域に分けて、お産ができる産院・助産所をのせています。", area_index, "area", [("トップ","index.html"),("エリアでさがす","area.html")])

# 産院ページ
for h in H:
    a = area_of[h["ward"]]
    srcs = "".join((f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a></li>' if u else f'<li>{esc(t)}</li>') for t,u in h["src"])
    tot = (f'<dl class="spec"><dt>総額の平均</dt><dd>{yen(h["total"]["avg"])}</dd><dt>総額のまん中の値</dt><dd>{yen(h["total"]["med"]) if h["total"]["med"] else "記載なし"}</dd><dt>入院日数</dt><dd>{"約"+str(h["days"])+"日" if h["days"] else "記載なし"}</dd></dl>' if h["total"] else "<p>国の「出産なび」には、まだ総額のデータがありません。</p>")
    extra = ('<ul style="margin-top:14px">' + "".join(f"<li>{esc(x)}</li>" for x in h["extra"]) + "</ul>") if h["extra"] else ""
    same = [x for x in H if x["ward"] in a["list"] and x["id"] != h["id"]]
    samehtml = ('<section><h2>同じ地域の産院</h2><div class="hlist">' + "".join(f'<a class="box" href="sanin-{x["id"]}.html"><div class="who">{x["ward"]}</div><h3>{esc(x["name"])}</h3></a>' for x in same) + '</div></section>') if same else ""
    note = f'<div class="wardnote"><b>{h["ward"]}について</b><br>{NOTES[h["ward"]]}</div>' if h["ward"] in NOTES else ""
    body = f"""
<div class="hhead">
  <span class="eyebrow">{h["ward"]}</span>
  <h1>{esc(h["name"])}</h1>
  <div class="meta"><span>{esc(h["type"])}</span><span>調べた日 {CONFIG["CHECKED"]}</span></div>
</div>
{note}
<div class="hsum">{pills(h)}</div>
<section style="border-top:0;padding-top:0">
  <h2>じぶんで払う部分</h2>
  <dl class="spec">
    <dt>お部屋</dt><dd>{esc(h["room"]["text"])}</dd>
    <dt>無痛分娩</dt><dd>{esc(h["painless"]["text"])}</dd>
    <dt>お祝い膳・食事</dt><dd>{esc(h["oiwai"]["text"])}</dd>
    <dt>立ち会い</dt><dd>{esc(h["tachiai"])}</dd>
    <dt>ご家族・面会</dt><dd>{esc(h["family"])}</dd>
    <dt>産後ケア</dt><dd>{esc(h["care"])}</dd>
  </dl>
</section>
<section>
  <h2>いまの出産費用（無償化の前・参考）</h2>
  {tot}
  {extra}
  <p class="note">総額は国の「出産なび」の2025年4〜9月の実績です。出産育児一時金（50万円）を引く前の金額です。</p>
</section>
<section>
  <h2>情報の出どころ</h2>
  <ul class="srcs">{srcs}</ul>
  <p class="note">料金やサービスは変わることがあります。かならず産院にご確認ください。まちがいを見つけたら、<a href="contact.html">お問い合わせ</a>からお知らせください。</p>
  <div class="actions"><a class="btn line" href="kuraberu.html">ほかの産院とくらべる</a></div>
</section>
{samehtml}"""
    desc = f"{h['ward']}の{h['name']}の、個室・無痛分娩・お祝い膳・立ち会い・産後ケアと、いまの出産費用を出どころつきでまとめました（{CONFIG['CHECKED']}調べ）。"
    add(f"sanin-{h['id']}.html", f"{h['name']}（{h['ward']}）の個室・無痛分娩・お祝い膳", desc, body, "kuraberu", [("トップ","index.html"),(a["label"],f"area-{a['slug']}.html"),(h["name"],f"sanin-{h['id']}.html")])

# 読みもの
PRNOTE = '<p class="prnote"><b>【広告】</b>この記事には広告（アフィリエイトリンク）がふくまれます。リンク先で商品が買われると、さんいん手帖に紹介料が入ることがあります。紹介する商品は、産院の情報とは関係なくえらんでいます。Amazonのアソシエイトとして、' + CONFIG["COMPANY"] + '（さんいん手帖 京都）は適格販売により収入を得ています。</p>'
for art in ARTICLES:
    nav = "junbi" if art["id"].startswith("junbi") else "yomimono"
    parent = ("出産じゅんび","junbi.html") if nav=="junbi" else ("読みもの","yomimono.html")
    first_para = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", art["body"].split("\n")[0])[:110]
    body = f'<article class="post"><span class="eyebrow">{art["date"]}</span><h1>{esc(art["title"])}</h1>{PRNOTE if art["pr"] else ""}{md(art["body"])}<div class="actions"><a class="btn main" href="kuraberu.html">京都の産院をくらべる</a><a class="btn line" href="{parent[1]}">ほかの記事</a></div></article>'
    add(f"yomimono-{art['id']}.html", art["title"], first_para, body, nav, [("トップ","index.html"),parent,(art["title"],f"yomimono-{art['id']}.html")])
add("yomimono.html", "読みもの｜無償化・産後ケア・産院えらび", "出産費用の無償化、京都府の産後ケア、無痛分娩ができる産院など、産院えらびの前に知っておきたいことをまとめています。", f'<section style="border-top:0"><span class="tag">読みもの</span><h1 class="ph">知っておきたいこと</h1>{cards(main_arts)}</section>', "yomimono", [("トップ","index.html"),("読みもの","yomimono.html")])
add("junbi.html", "出産じゅんび｜入院バッグ・ベビー用品・内祝い", "入院バッグの中身、ベビー用品の準備、出産内祝いのきほんをまとめています。", f'<section style="border-top:0"><span class="tag">じゅんび</span><h1 class="ph">出産までに、そろえるもの</h1><p class="lead">このページの記事には、広告（アフィリエイトリンク）がふくまれます。</p>{cards(junbi_arts)}</section>', "junbi", [("トップ","index.html"),("出産じゅんび","junbi.html")])

# サイトについて・広告・プライバシー・問い合わせ
addr = f"<dt>所在地</dt><dd>{esc(CONFIG['COMPANY_ADDRESS'])}</dd>" if CONFIG["COMPANY_ADDRESS"] else ""
about = f"""<div class="legal"><h1 class="ph">運営者・このサイトについて</h1>
<h2>運営者</h2>
<dl class="spec"><dt>運営</dt><dd>{CONFIG["COMPANY"]}</dd><dt>代表</dt><dd>{CONFIG["REPRESENTATIVE"]}</dd>{addr}<dt>お問い合わせ</dt><dd><a href="contact.html">お問い合わせページ</a></dd></dl>
<h2>このサイトでしていること</h2>
<p>2028年6月ごろまでに、ふつうのお産の費用は国の保険でまかなわれる予定です。そのあとは、個室、お祝い膳、無痛分娩、産後ケアなど、ご家族がじぶんで選んで払う部分で、産院ごとのちがいが出てきます。さんいん手帖は、京都府の産院ごとに、その「じぶんで払う部分」をならべて、くらべられるようにするサイトです。</p>
<h2>情報の調べ方</h2>
<ul><li>厚生労働省の「出産なび」、各産院のホームページ、市町村の公開資料をもとにしています</li><li>産院のページには、出どころと、調べた日をかならず書いています</li><li>公開されていない金額は「公開されていません」と書き、推測ではうめません</li><li>のせる前に、出どころともう一度照らし合わせて確認しています</li></ul>
<h2>4つのやくそく</h2>
<ul><li>ランキングや「おすすめ」はつけません</li><li>口コミ・体験談はのせません</li><li>情報の出どころと、調べた日を書きます</li><li>お金をいただいたものには「広告」「PR」と書きます</li></ul>
<h2>情報のまちがいについて</h2>
<p>料金やサービスは変わることがあります。まちがいを見つけたときや、産院の方で内容の直しがあるときは、<a href="contact.html">お問い合わせ</a>からお知らせください。確認のうえ、なるべく早く直します。</p>
<h2>医療についての注意</h2>
<p>このサイトは、医療のアドバイスをするものではありません。お体のことや、お産の方法については、かかりつけの先生や助産師さんにご相談ください。</p>
<h2>免責事項</h2>
<p>このサイトの情報は、調べた日の時点で公開されていたものです。正確な情報をのせるよう努めていますが、内容が変わっていることがあります。産院を選ぶときは、かならず産院に直接ご確認ください。このサイトの情報を使ったことで生じた損害について、運営者は責任を負いかねます。</p></div>"""
add("about.html", "運営者・このサイトについて", "さんいん手帖 京都の運営者、情報の調べ方、やくそくについて。", about, "", [("トップ","index.html"),("運営者・このサイトについて","about.html")])

adp = f"""<div class="legal"><h1 class="ph">広告について</h1>
<h2>紹介料（アフィリエイト）について</h2>
<p>さんいん手帖の一部の記事（出産じゅんびの記事など）には、Amazonなどの商品へのリンクがあります。リンク先で商品が買われると、さんいん手帖に紹介料が入ることがあります。こうしたリンクがある記事には、記事の最初に「広告がふくまれます」と書き、記事の一覧には「PR」と表示しています。</p>
<p>Amazonのアソシエイトとして、{CONFIG["COMPANY"]}（さんいん手帖 京都）は適格販売により収入を得ています。</p>
<h2>産院の情報と広告は分けています</h2>
<ul><li>産院のページ、くらべる表、エリアのページの内容は、紹介料や広告とは関係なく、公開されている情報をもとに作っています</li><li>現在、産院・病院から掲載料はいただいていません</li><li>今後、産院から広告や掲載料をいただくことになった場合は、そのページにはっきり「広告」と書き、ならび順や目立たせ方は変えません</li><li>医療広告ガイドラインにそって、ランキング、口コミ・体験談、ほかの産院より優れていると思わせる書き方はしません</li><li>掲載料をいただく場合は、医療広告ガイドラインの決まり（自由診療の料金をのせるときに、内容・費用・リスクなどもあわせて書く「限定解除」の条件）を満たして掲載します</li></ul></div>"""
add("ad-policy.html", "広告について", "さんいん手帖 京都の広告・紹介料（アフィリエイト）についての考え方。", adp, "", [("トップ","index.html"),("広告について","ad-policy.html")])

priv = f"""<div class="legal"><h1 class="ph">プライバシーポリシー</h1>
<p>{CONFIG["COMPANY"]}（以下「当社」）は、さんいん手帖 京都（以下「このサイト」）での個人情報の取り扱いについて、次のとおり定めます。</p>
<h2>1. 集める情報</h2>
<ul><li>お問い合わせのときにいただく、お名前・メールアドレス・お問い合わせの内容</li><li>アクセス解析ツールによる、閲覧したページ・使っている端末やブラウザなどの情報（個人を特定するものではありません）</li></ul>
<h2>2. 使う目的</h2>
<ul><li>お問い合わせへのお返事のため</li><li>サイトの内容をよくするため（よく読まれているページの分析など）</li><li>掲載している情報の確認・修正のため</li></ul>
<h2>3. 第三者への提供</h2>
<p>法令にもとづく場合をのぞき、ご本人の同意なく、個人情報を第三者に提供することはありません。</p>
<h2>4. アクセス解析について</h2>
<p>このサイトでは、Googleによるアクセス解析ツール「Googleアナリティクス」を使います。Googleアナリティクスは、Cookieを使って、個人を特定しない形で利用状況を集めます。集めた情報は、Googleに送られます。Cookieはブラウザの設定で無効にできます。また、<a href="https://tools.google.com/dlpage/gaoptout?hl=ja" target="_blank" rel="noopener">Googleアナリティクス オプトアウト アドオン</a>を使うと、情報が集められないようにできます。くわしくは、<a href="https://policies.google.com/technologies/partner-sites?hl=ja" target="_blank" rel="noopener">Googleのポリシー</a>をごらんください。</p>
<h2>5. 広告（アフィリエイト）について</h2>
<p>このサイトは、Amazonアソシエイト・プログラムなどのアフィリエイトプログラムに参加しています。リンク先のサイトでは、Cookieが使われることがあります。リンク先での個人情報の取り扱いは、それぞれのサイトのポリシーによります。</p>
<h2>6. 安全のための取り組み</h2>
<p>いただいた個人情報は、必要な人だけが見られるようにし、パスワードなどで守って管理します。使い終わった情報は、適切に消します。</p>
<h2>7. 開示・訂正・利用停止のご請求</h2>
<p>ご本人から、ご自身の個人情報の開示・訂正・削除・利用停止などのご請求があったときは、ご本人であることをたしかめたうえで、法令にしたがって対応します。手数料はいただきません。ご請求は、<a href="contact.html">お問い合わせページ</a>の窓口からお願いいたします。</p>
<h2>8. 事業者</h2>
<p>{CONFIG["COMPANY"]}　代表 {CONFIG["REPRESENTATIVE"]}{("　" + CONFIG["COMPANY_ADDRESS"]) if CONFIG["COMPANY_ADDRESS"] else ""}</p>
<h2>9. お問い合わせ</h2>
<p>個人情報の取り扱いについてのお問い合わせは、<a href="contact.html">お問い合わせページ</a>からお願いいたします。</p>
<h2>10. 見直し</h2>
<p>このポリシーは、必要に応じて見直すことがあります。</p>
<p class="note">制定日：{CONFIG["CHECKED"]}</p></div>"""
add("privacy.html", "プライバシーポリシー", "さんいん手帖 京都のプライバシーポリシー。", priv, "", [("トップ","index.html"),("プライバシーポリシー","privacy.html")])

if CONFIG["CONTACT_FORM_URL"]:
    how = f'<p><a class="btn main" href="{esc(CONFIG["CONTACT_FORM_URL"])}" target="_blank" rel="noopener">お問い合わせフォームをひらく</a></p>'
elif CONFIG["CONTACT_EMAIL"]:
    how = f'<p>下のメールアドレスあてに、お送りください。</p><div class="copy"><code id="mail">{esc(CONFIG["CONTACT_EMAIL"])}</code><button type="button" class="btn line" id="copybtn">コピー</button></div><script>document.getElementById("copybtn").addEventListener("click",function(){{var t=document.getElementById("mail").textContent;var b=this;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){{b.textContent="コピーしました"}}).catch(function(){{var r=document.createRange();r.selectNodeContents(document.getElementById("mail"));var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent="選びました。コピーしてください"}})}});</script>'
else:
    how = '<p class="wardnote">お問い合わせ先は、じゅんび中です。</p>'
contact = f"""<div class="legal"><h1 class="ph">お問い合わせ</h1>
<p>情報のまちがい、産院の方からの内容の直し、そのほかのご質問は、こちらからお願いいたします。</p>
{how}
<h2>産院・病院のみなさまへ</h2>
<p>個室・お食事・無痛分娩・産後ケアなどの料金の確認や、直しのご連絡をお待ちしています。現在、掲載は無料です。</p>
<h2>お返事について</h2>
<p>お返事には、数日いただくことがあります。医療についてのご相談には、お答えできません。</p></div>"""
add("contact.html", "お問い合わせ", "さんいん手帖 京都へのお問い合わせ。", contact, "", [("トップ","index.html"),("お問い合わせ","contact.html")])

# ---------- 書き出し ----------
KJS = r"""
(function(){
const state={room:true,painless:false,oiwai:false,ward:"すべて"};
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
 const list=H.filter(h=>inArea(h.ward,state.ward));
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
 if(e.target.id==="area-sel"){state.ward=e.target.value;save();draw();}});
draw();
})();
"""

def build(preview=False):
    out = OUT if not preview else "site_preview"
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(out)
    css = open("static/site_style.css").read() + CSS_EXTRA + "\nh1.ph{font-family:var(--display);font-weight:900;font-size:clamp(1.5rem,4.4vw,2.1rem);line-height:1.4;margin:.3em 0 .6em;text-wrap:balance}\n"
    if not preview:
        css = "*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0}img{max-width:100%}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}\n" + css
    open(f"{out}/style.css","w").write(css)
    open(f"{out}/kuraberu.js","w").write(KJS)
    for f in ("logo.svg","illust.webp","illust.png"):
        if os.path.exists("static/"+f): shutil.copy("static/"+f, out)
    if not preview:
        open(f"{out}/CNAME","w").write("sanin-techo.jp\n")
        open(f"{out}/.nojekyll","w").write("")
        open(f"{out}/google398b3a66555b760f.html","w").write("google-site-verification: google398b3a66555b760f.html")
    for fname,(title,desc,body,nav,crumbs) in pages.items():
        open(f"{out}/{fname}","w").write(page(fname,title,desc,body,nav,crumbs,preview=(preview and fname=="index.html")))
    if not preview:
        base = CONFIG["SITE_URL"].rstrip("/")
        urls = "".join(f"<url><loc>{base}/{'' if f=='index.html' else f}</loc></url>" for f in pages)
        open(f"{out}/sitemap.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
        open(f"{out}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    return out

if __name__ == "__main__":
    build()
    json.dump(H, open("data/sanin_data_all.json","w"), ensure_ascii=False, indent=1)
    open("content/articles_all.md","w").write("\n\n".join(f"==={a['id']}|{a['title']}|{a['date']}{'|pr' if a['pr'] else ''}\n{a['body']}" for a in ARTICLES))
    print(len(pages), "pages")
