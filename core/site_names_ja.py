"""Wikidata に日本語ラベルが無い世界遺産の和名対訳（WHC 参照番号 → 和名）。

``scripts/build_dataset.py`` が付ける ``name`` は Wikidata の日本語ラベル優先・
無ければ英語名。ここはその英語名フォールバック分を補う。訳語は UNESCO 日本語資料・
日本語版 Wikipedia・世界遺産検定の一覧を突き合わせて選定した標準的な呼称。
``core/data_loader.load_heritage_sites`` が ``site_id`` で引いて ``name`` を差し替える。
"""

from __future__ import annotations

SITE_NAMES_JA: dict[int, str] = {
    12: "ティヤの石碑群",  # Tiya archaeological site
    22: "隊商都市ボスラ",  # Ancient City of Bosra
    32: "ヴィエリチカとボフニャの王立岩塩坑",  # Wieliczka and Bochnia Royal Salt Mines
    36: "チュニスの旧市街",  # Medina of Tunis
    37: "カルタゴの考古遺跡",  # Archaeological site of Carthage
    38: "エル・ジェムの円形闘技場",  # Roman amphitheatre of El Jem
    55: "レーロースの鉱山都市と周辺",  # Røros Mining Town and the Circumference
    65: "アンティグア・グアテマラ",  # Antigua Guatemala
    79: "パフォスの考古遺跡",  # Paphos
    86: "メンフィスのピラミッド地帯",  # Memphis and its Necropolis – the Pyramid Fields from Giza to Dahshur
    95: "ドゥブロヴニクの旧市街",  # Old city (Dubrovnik)
    97: "スプリトのディオクレティアヌス帝の宮殿と歴史的建造物群",  # Historical Complex of Split with the Palace of Diocletian
    124: "オウロ・プレトの歴史都市",  # Historic Town of Ouro Preto
    125: "コトルの文化歴史地域と自然",  # Natural and Culturo-Historical Region of Kotor
    143: "タッタとマクリの歴史的建造物群",  # Historical Monuments at Makli, Thatta
    163: "オランジュの凱旋門、ローマ劇場とその周辺",  # Roman Theatre and its Surroundings and the \"Triumphal Arch\" of Orange
    169: "ヴュルツブルクの司教館と庭園群",  # Würzburg Residence with the Court Gardens and Residence Square
    184: "サブラータの考古遺跡",  # Archaeological Site of Sabratha
    205: "タラマンカ山脈地帯：ラ・アミスタ自然保護区群とラ・アミスタ国立公園",  # Talamanca Range-La Amistad Reserves
    206: "アゾレス諸島の港町アングラ・ド・エロイズモ",  # Centro Histórico de Angra do Heroísmo
    211: "ジャームのミナレットと考古遺跡群",  # Minaret and Archaeological Remains of Jam
    216: "リラの修道院",  # Rila Monastery
    217: "ネセビルの古代都市",  # Ancient City of Nessebar
    229: "ナンシーのスタニスラス広場、カリエール広場、アリアンス広場",  # Place Stanislas, Place de la Carrière and Place d'Alliance in Nancy
    234: "ゴアの聖堂と修道院",  # Churches and Convents of Goa
    258: "ポルト湾：ピアナのカランケ、ジロラッタ湾、スカンドラ保護区",  # Gulf of Porto: Calanche of Piana, Gulf of Girolata, Scandola Reserve
    272: "ハンザ都市リューベック",  # Hanseatic City of Lübeck
    273: "クスコの市街",  # Historic centre of Cusco
    278: "バビロン",  # Babylon
    299: "フェニキア都市ティルス",  # Tyre
    302: "マナ・プールズ国立公園、サピとチュウォールの自然保護区",  # Mana Pools National Park, Sapi and Chewore Safari Areas
    312: "アストゥリアス王国とオビエドの宗教建築物群",  # Monuments of Oviedo and the Kingdom of the Asturias
    318: "マドリードのエル・エスコリアール修道院と王立施設",  # Monastery and Site of the Escurial, Madrid
    332: "古代カルタゴ都市ケルクアンとそのネクロポリス",  # Punic Town of Kerkuane and its Necropolis
    347: "サンティアゴ・デ・コンポステーラ（旧市街）",  # old town of Santiago de Compostela
    348: "アビラの旧市街と城壁外の教会群",  # Old Town of Ávila with its Extra-Muros Churches
    353: "チャコ文化",  # Chaco Culture World Heritage Site
    357: "ギョレメ国立公園とカッパドキアの岩石群",  # Göreme National Park and the Rock Sites of Cappadocia
    361: "エヴォラの歴史地区",  # Centro Histórico de Évora
    362: "ガダーミスの旧市街",  # Old Town of Ghadamès
    370: "ダラム城と大聖堂",  # Durham Castle and Cathedral
    379: "歴史都市トレド",  # Historic City of Toledo
    383: "セビーリャの大聖堂、アルカサル、インディアス古文書館",  # Cathedral, Alcázar and Archivo de Indias in Seville
    384: "カセレスの旧市街",  # old town of Cáceres
    393: "デルフィの考古遺跡",  # archaeological Site of Delphi
    412: "メキシコ・シティの歴史地区とソチミルコ",  # Historic Centre of Mexico City and Xochimilco
    415: "オアハカの歴史地区とモンテ・アルバンの考古遺跡",  # Historic Centre of Oaxaca and Archaeological Site of Monte Albán
    416: "プエブラの歴史地区",  # Historic Centre of Puebla
    417: "イビサ島の生物多様性と文化",  # Ibiza, Biodiversity and Culture
    426: "ウェストミンスター宮殿、ウェストミンスター・アビーとセント・マーガレット教会",  # Palace of Westminster and Westminster Abbey including Saint Margaret's Church
    454: "聖山アトス",  # Mount Athos
    460: "トリニダとロス・インヘニオス渓谷",  # Trinidad and the Valley de los Ingenios
    484: "クサントスとレトーン",  # Xanthos-Letoon
    495: "ストラスブール：グラン・ディルからヌースタットのヨーロッパの都市景観",  # Strasbourg: from Grande-île to Neustadt, a European urban scene
    496: "カンタベリー大聖堂、セント・オーガスティン修道院跡とセント・マーティン教会",  # Canterbury Cathedral, St Augustine's Abbey, and St Martin's Church
    498: "スースの旧市街",  # Medina of Sousse
    535: "クヴェートリンブルクの旧市街と聖堂参事会教会、城",  # Collegiate Church, Castle, and Old Town of Quedlinburg
    549: "カゼルタの18世紀の王宮と庭園、ヴァンヴィテッリの水道橋、サン・レウチョの関連遺産",  # 18th-Century Royal Palace at Caserta with the Park, the Aqueduct of Vanvitelli, and the San Leucio Complex
    555: "ビルカとホヴゴーデン",  # Birka and Hovgården
    569: "ベラトとギロカストラの歴史地区",  # Historic Centres of Berat and Gjirokastër
    578: "シャーク湾",  # Shark Bay
    585: "モレリアの歴史地区",  # Historic Centre of Morelia
    595: "サモス島のピタゴリオンとヘラ神殿",  # Pythagoreion and Heraion of Samos
    601: "ランスのノートル・ダム大聖堂、サン・レミ旧修道院、トー宮",  # Cathedral of Notre-Dame, Former Abbey of Saint-Rémi and Palace of Tau, Reims
    602: "ブハラの歴史地区",  # Historic Centre of Bukhara
    604: "ノヴゴロドと周辺の歴史的建造物群",  # Historic Monuments of Novgorod and Surroundings
    613: "レオン・ビエホの遺跡群",  # Ruínas de León Viejo
    614: "サフランボルの旧市街",  # City of Safranbolu
    617: "チェスキー・クルムロフの歴史地区",  # Historic Centre of Český Krumlov
    618: "バンスカー・シチアウニツァの鉱山都市と近隣の技術遺産",  # Historic Town of Banská Štiavnica and the Technical Monuments in its Vicinity
    621: "テルチの歴史地区",  # Historic Centre of Telč
    634: "コローメンスコエ：昇天教会（ヴォズネセーニエ教会）",  # Church of the Ascension, Kolomenskoye
    648: "パラナ川沿いのイエズス会布教施設群：ラ・サンティシマ・トリニダ・デ・パラナとヘスス・デ・タバランゲ",  # Jesuit Missions of La Santísima Trinidad de Paraná and Jesús de Tavarangüé
    664: "メリダの考古遺跡群",  # Archaeological Ensemble of Mérida
    669: "サンティアゴ・デ・コンポステーラの巡礼路：カミノ・フランセスとスペイン北部の道",  # Routes of Santiago de Compostela: Camino Francés and Routes of Northern Spain
    670: "マテーラの洞窟住居サッシと岩窟教会公園",  # The Sassi and the Park of the Rupestrian Churches of Matera
    676: "サカテカスの歴史地区",  # Historic centre of Zacatecas
    697: "イェリング墳墓、ルーン石碑と教会",  # Jelling Heritage Site
    699: "ルクセンブルク市の旧市街と要塞",  # City of Luxembourg: its Old Quarters and Fortifications
    705: "武当山の道教寺院群",  # Ancient Building Complex in the Wudang Mountains
    709: "上スヴァネチア",  # Upper Svaneti
    723: "シントラの文化的景観",  # Cultural Landscape of Sintra
    728: "エディンバラの旧市街と新市街",  # Old and New Towns of Edinburgh
    731: "ハンザ都市ヴィスビー",  # Hanseatic town of Visby
    733: "ルネサンス都市フェッラーラとポー川のデルタ地帯",  # Ferrara, City of the Renaissance, and its Po Delta
    753: "エッサウィーラ（旧名モガドール）の旧市街",  # Medina of Essaouira
    759: "オランダの水利防衛線群（旧遺産名：アムステルダムの防衛線の要塞）",  # Dutch Water Defence Lines
    765: "カムチャツカ火山群",  # Volcanoes of Kamchatka
    766: "シホテ・アリニ山脈中央部",  # Central Sikhote-Alin
    769: "ウヴス・ヌール盆地",  # Uvs Nuur Basin
    772: "フェルテー（ノイジードル）湖の文化的景観",  # Fertö / Neusiedlersee Cultural Landscape
    773: "ピレネー山脈のペルデュ山",  # Pyrénées – Mont Perdu World Heritage Site
    777: "アフパットとサナインの修道院",  # Monasteries of Haghpat and Sanahin
    779: "峨眉山と楽山大仏",  # Mount Emei Scenic Area, including Leshan Giant Buddha Scenic Area
    786: "シェーンブルン宮殿と庭園",  # Palace and gardens of Schönbrunn
    788: "ラヴェンナの初期キリスト教建造物群",  # Early Christian Monuments of Ravenna
    789: "ピエンツァの歴史地区",  # Historic Centre of the City of Pienza
    790: "パナマ・ビエホの考古遺跡とパナマの歴史地区",  # Archaeological Site of Panamá Viejo and Historic District of Panamá
    792: "ケレタロの歴史的建造物地区",  # Historic Monuments Zone of Querétaro
    793: "ミクナースの旧市街",  # Medina of Meknes
    795: "海事都市グリニッジ",  # Maritime Greenwich
    798: "シュンドルボン",  # Sundarbans Reserved Forest
    804: "バルセロナのカタルーニャ音楽堂とサン・パウ病院",  # Palau de la Música Catalana and Hospital de Sant Pau, Barcelona
    810: "歴史都市トロギール",  # Historic City of Trogir
    812: "平遥の古代都市",  # Ancient City of Ping Yao
    818: "キンデルダイク-エルスハウトの風車群",  # Windmills at Kinderdijk
    820: "ココス島国立公園",  # Cocos Island National Park
    821: "サン・ルイスの歴史地区",  # Historic Centre of São Luís
    826: "ポルトヴェーネレ、チンクエ・テッレと小島群（パルマリア島、ティーノ島、ティネット島）",  # Portovenere, Cinque Terre, and the Islands (Palmaria, Tino and Tinetto)
    827: "モデナ：大聖堂と市民の塔（トッレ・チヴィカ）、グランデ広場",  # Cathedral, Torre Civica and Piazza Grande, Modena
    828: "ウルビーノの歴史地区",  # Historic Centre of Urbino
    837: "テトゥアンの旧市街（旧名ティタウィン）",  # Medina of Tétouan
    842: "チレント・ディアノ渓谷国立公園及び遺跡群と修道院",  # Cilento and Vallo di Diano National Park with the Archeological Sites of Paestum and Velia, and the Certosa di Padula
    860: "クロムニェジーシュの庭園と宮殿",  # Gardens and Castle at Kroměříž
    871: "カールスクローナの軍港",  # Naval City of Karlskrona
    873: "中世市場都市プロヴァン",  # Provins
    876: "アルカラ・デ・エナレスの大学と歴史地区",  # University and Historic Precinct of Alcalá de Henares
    890: "ディアマンティーナの歴史地区",  # Historic Centre of the Town of Diamantina
    895: "歴史的要塞都市カンペチェ",  # Historic Fortified Town of Campeche
    900: "西カフカス山脈",  # Western Caucasus
    905: "カルヴァリア・ゼブジドフスカ：マニエリスム様式の建築と公園に関連する景観と巡礼公園",  # Kalwaria Zebrzydowska park
    933: "ロワール渓谷：シュリー・シュル・ロワールからシャロンヌまで",  # The Loire Valley between Sully-sur-Loire and Chalonnes
    941: "ミケーネとティリンスの考古遺跡",  # Archaeological Sites of Mycenae and Tiryns
    954: "聖カトリーナ修道院地域",  # Saint Catherine Area
    968: "エーランド島南部の農業景観",  # Southern Öland cultural landscape
    973: "バルジェヨウ街並保存地区",  # Bardejov Town Conservation Reserve
    978: "コルフの旧市街",  # Old town of Corfu
    983: "バミューダ諸島：歴史的都市セント・ジョージと関連要塞群",  # St George and Related Fortifications
    984: "ブレナヴォン産業景観",  # Blaenavon Industrial Landscape
    987: "ルーゴのローマの城壁群",  # Roman Walls of Lugo
    988: "ボイ渓谷のカタルーニャ風ロマネスク様式教会群",  # Catalan Romanesque Churches of the Vall de Boí
    993: "ゴイアスの歴史地区",  # Historic Centre of the Town of Goiás
    1001: "青城山と都江堰水利施設",  # Qingchengshan-Dujiangyan National Park
    1002: "安徽省南部の古村落",  # Ancient Villages in Southern Anhui - Xidi and Hongcun
    1016: "アレキパの歴史地区",  # Historic Centre of Arequipa
    1018: "エフェソス",  # Ephesus
    1023: "ウランゲリ島保護区の自然生態系",  # Zapovednik Wrangel Island
    1024: "ヴァル・ディ・ノートの後期バロック様式の都市景観群（シチリア島南東部）",  # Late Baroque Towns of the Val di Noto
    1031: "ギマランイスの歴史地区とコウルス地区",  # Historic Centre of Guimarães and Couros Zone
    1037: "ユングフラウ－アレッチュのスイス・アルプス",  # Jungfrau-Aletsch protected area
    1044: "アランフエスの文化的景観",  # Aranjuez Cultural Landscape
    1058: "マサガン（アル・ジャジーダ）のポルトガル都市",  # Mazagan
    1063: "トカイ地方のワイン産地の歴史的文化的景観",  # Tokaj Wine Region Historic Cultural Landscape
    1070: "デルベントのシタデル、古代都市、要塞建築物群",  # Citadel, old town and fortifications of Derbent
    1073: "ゲベル・バルカルとナパタ地域の遺跡群",  # Gebel Barkal and the Sites of the Napatan Region
    1117: "ピーコ島のブドウ栽培の景観",  # Landscape of the Pico Island Vineyard Culture
    1143: "ヴェガエイヤン：ヴェガ群島",  # Vega Archipelago
    1158: "チェルヴェテリとタルクィニアのエトルリア古代古墳群",  # Etruscan Necropolises of Cerveteri and Tarquinia
    1170: "ヤロスラーヴリの歴史地区",  # historical centre of Yaroslavl
    1189: "城塞歴史都市ハラール・ジュゴル",  # Harar Jugol, the Fortified Historic Town
    1196: "ネスヴィシにあるラジヴィル家の建築と邸宅および文化関連遺産群",  # Architectural, Residential and Cultural Complex of the Radziwill Family at Nesvizh
    1200: "シラクサとパンタリカの岩壁墓地遺跡",  # Syracuse and the Rocky Necropolis of Pantalica
    1202: "シエンフエゴスの歴史地区",  # Historic Centre of Cienfuegos
    1211: "ジェノヴァ：レ・ストラーデ・ヌオーヴェとパラッツィ・デイ・ロッリ制度",  # Genoa: Le Strade Nuove and the system of the Palazzi dei Rolli
    1216: "マルペロ動植物保護区",  # Malpelo Fauna and Flora Sanctuary
    1221: "リドー運河",  # Rideau Canal World Heritage Site
    1222: "ビーソトゥーン",  # Behistun
    1226: "セネガンビアのストーン・サークル遺跡群",  # Stone Circles of Senegambia
    1229: "クラック・デ・シュヴァリエとカラット・サラーフ・アッディーン",  # Crac des Chevaliers and Qal’at Salah El-Din
    1237: "ドロミテ山塊",  # The Dolomites
    1240: "フヴァル島のスターリ・グラード平地",  # Stari Grad Plain
    1245: "サン・マリノの歴史地区とティタノ山",  # San Marino Historic Centre and Mount Titano
    1263: "ソコトラ諸島",  # Socotra Archipelago
    1268: "アガデスの歴史地区",  # Historic Center of Agadez
    1272: "サン・クリストヴァンのサン・フランシスコ広場",  # São Francisco Square
    1274: "サン・ミゲルの要塞都市とアトトニルコにあるナザレのイエスの聖地",  # Protective town of San Miguel and the Sanctuary of Jesús Nazareno de Atotonilco
    1285: "ジョギンズの化石断崖群",  # Joggins Fossil Cliffs
    1302: "ラ・ショー・ド・フォン/ル・ロクル、時計製造都市の都市計画",  # La Chaux-de-Fonds / Le Locle, Watchmaking Town Planning
    1303: "ポントカサステ水路橋と運河",  # Pontcysyllte Aqueduct and Canal
    1308: "パラチーとグランジ島：文化と生物多様性",  # Historical center of Paraty
    1314: "ワッデン海",  # Wadden Sea
    1315: "シューシュタルの歴史的水利システム",  # Shushtar Historical Hydraulic System
    1324: "河回村と良洞村の歴史的集落群",  # Historic Villages of Korea: Hahoe and Yangdong
    1333: "コンソの文化的景観",  # Konso Cultural Landscape
    1334: "杭州にある西湖の文化的景観",  # West Lake Cultural Landscape of Hangzhou
    1336: "メロエ島の考古遺跡",  # Archaeological Sites of the Island of Meroe
    1349: "アムステルダム中心部：ジンフェルグラハト内部の17世紀の環状運河地区",  # Grachtengordel
    1352: "オアハカの中部渓谷にあるヤグルとミトラの先史洞窟",  # Prehistoric Caves of Yagul and Mitla in the Central Valley of Oaxaca
    1356: "ブルー・アンド・ジョン・クロウ山脈",  # Blue and John Crow Mountains
    1360: "ノール＝パ・ドゥ・カレの鉱山地帯",  # northern French coal mining region
    1361: "ジッダの歴史地区：メッカの入口",  # Al-Balad, Jeddah
    1371: "トラムンタナ山脈の文化的景観",  # Cultural Landscape of the Serra de Tramuntana
    1403: "ハミギタン山岳地域野生動物保護区",  # Mount Hamiguitan Range Wildlife Sanctuary
    1411: "タウリカ半島の古代都市とチョーラ",  # Ancient City of Tauric Chersonese and its Chora
    1427: "エトナ山",  # Etna Park
    1430: "ナミブ砂漠",  # Namib Sand Sea
    1431: "ビジャゴス諸島の沿岸・海洋生態系：オマティ・ミンオ",  # Bijagos Archipelago Biosphere Reserve
    1434: "ピュイ山地とリマーニュ断層にある地殻変動地域",  # Chaîne des Puys - Limagne fault tectonic arena
    1444: "ピュー族の古代都市群",  # Pyu Ancient Cities
    1448: "ダウリアの景観群",  # Landscapes of Dauria
    1452: "ブルサとジュマルクズク：オスマン帝国発祥の地",  # Bursa and Cumalıkızık: the Birth of the Ottoman Empire
    1457: "ペルガモンとその周辺：様々な時代からなる文化的景観",  # Pergamon and its Multi-Layered Cultural Landscape
    1461: "ケーン・クラチャン森林関連遺産群",  # Kaeng Krachan Forest Complex
    1466: "サン・アントニオ・ミッションズ",  # San Antonio Missions
    1478: "エルツ山地／クルシュネー鉱業地域",  # Ore Mountain Mining Region
    1492: "パレスチナ：オリーブとブドウの地－南エルサレム、バティールの文化的景観",  # Palestine: Land of Olives and Vines – Cultural Landscape of Southern Jerusalem, Battir
    1499: "アンティグアの海軍造船所と関連考古遺跡群",  # Antigua Naval Dockyard and Related Archaeological Sites
    1500: "ゴーハムの洞窟群",  # Gorham's Cave complex
    1501: "アンテケラの支石墓遺跡",  # Antequera Dolmens Site
    1504: "ステチュツィ：中世の墓碑の残る墓所",  # Q29000652
    1507: "プー・プラバート：ドヴァーラヴァティー時代のセーマ石の伝統の証拠",  # Phu Phrabat, a testimony to the Sīma stone tradition of the Dvaravati period
    1509: "湖北の神農架",  # Hubei Shennongjia
    1519: "アフロディシアス",  # Aphrodisias
    1525: "スヴィヤジツクの集落島にある生神女就寝大聖堂と修道院",  # Sviyazhsk Assumption Monastery
    1528: "メノルカ島のタライオティック文化先史遺跡群",  # Talayotic Culture of Minorca
    1536: "クジャター・グリーンランド：氷冠周縁部におけるノース人とイヌイットの農業地域",  # Kujataa
    1538: "イヴレーア：20世紀の産業都市",  # Ivrea, industrial city of the 20th century
    1539: "タルノフスキェ・グルィの鉛・銀・亜鉛鉱山とその地下水管理システム",  # Tarnowskie Góry Lead-Silver-Zinc Mine and its Underground Water Management System
    1544: "ヤズドの歴史都市",  # Heritage district of Yazd
    1549: "ハーン宮殿のあるシェキの歴史地区",  # Historic Centre of Sheki with the Khan’s Palace
    1550: "アスマラ：アフリカのモダニズム都市",  # Asmara: A Modernist African City
    1551: "アーメダバードの歴史都市",  # Historic City of Ahmadabad
    1558: "ジャテツとザーツ・ホップの景観",  # Žatec and the Landscape of Saaz Hops
    1559: "梵浄山",  # Fanjingshan
    1564: "トロンデック・クロンダイク",  # Tr'ondëk-Klondike
    1570: "テランガナ州にあるカカーティヤ時代のルドレシュワラ（ラマッパ）寺院",  # Ramappa Temple
    1571: "コネリアーノとヴァルドッビアーデネのプロセッコ栽培丘陵群",  # Le Colline del Prosecco di Conegliano e Valdobbiadene
    1573: "マフラの王家の建物：宮殿、バシリカ、女子修道院、セルコ庭園、狩猟公園（タパダ）",  # Royal Building of Mafra
    1581: "1944年のノルマンディー上陸作戦の海岸群",  # Beaches of the D-Day Landings, Normandy, 1944
    1582: "パナマの植民地時代の地峡横断ルート",  # The Colonial Transisthmian Route of Panamá
    1584: "ヒルカニアの森林群",  # Hyrcanian Forests
    1589: "クラドルビ・ナト・ラベムにある式典馬車用の馬の繁殖・訓練地の景観",  # Landscape for Breeding and Training of Ceremonial Carriage Horses at Kladruby nad Labem
    1599: "クシェミオンキにある先史時代の縞状フリント（火打石）採掘地域",  # Krzemionki Prehistoric Striped Flint Mining Region
    1606: "中国の黄海・渤海湾沿岸の渡り鳥保護区群（第1段階）",  # Migratory Bird Sanctuaries along the Coast of Yellow Sea-Bohai Gulf of China (Phase I)
    1608: "ローマ帝国の境界線：ドナウのリーメス（西側部分）",  # Frontiers of the Roman Empire – The Danube Limes (Western Segment)
    1619: "ヒマー地方の岩絵と碑文群",  # Bir Hima Rock Petroglyphs and Inscriptions
    1620: "ロベルト・ブーレ・マルクスの仕事場",  # Sítio Roberto Burle Marx
    1621: "鹿石と関連する青銅器時代の遺跡群",  # Deer Stone Monuments, the Heart of Bronze Age Culture
    1624: "チャンキーヨの天文考古学遺産群",  # Chankillo Archaeoastronomical Complex
    1627: "古代ホタールの文化遺産群",  # Cultural Heritage Sites of Ancient Khuttal
    1633: "ウェールズ北西部の粘板岩の景観",  # The Slate Landscape of Northwest Wales
    1635: "ニース：リヴィエラの冬のリゾート都市",  # Nice, Winter Resort Town of the Riviera
    1636: "シュパイア、ヴォルムス、マインツのユダヤ人関連遺産群",  # ShUM Sites of Speyer, Worms and Mainz
    1641: "ゲデオの文化的景観",  # The Gedeo Cultural Landscape
    1643: "リュブリャナにあるヨジェ・プレチニクの作品群：人間中心の都市デザイン",  # The works of Jože Plečnik in Ljubljana – Human Centred Urban Design
    1647: "ホウラマン/ウラマナトの文化的景観",  # Cultural Landscape of Hawraman/Uramanat
    1648: "コートジボワール北部にあるスーダン様式のモスク群",  # Sudanese style mosques in northern Côte d'Ivoire
    1654: "オネガ湖と白海の岩絵群",  # Petroglyphs of Lake Onega and the White Sea
    1656: "エアフルトの中世ユダヤ関連遺産",  # Jewish-Medieval Heritage of Erfurt
    1657: "プレ山及びマルティニーク島北部の峻峰群の火山と森林",  # Volcanoes and Forests of Mount Pelée and the Pitons of Northern Martinique
    1658: "クルディーガの旧市街",  # Old town of Kuldīga
    1660: "ヴァイキング時代の環状要塞群",  # Viking Age Ring Fortresses
    1661: "モダニズム都市カウナス：楽観主義建築（1919-1939）",  # Modernist Kaunas: Architecture of Optimism, 1919-1939
    1665: "普洱（プーアル）の景邁山古茶林の文化的景観",  # Cultural Landscape of Old Tea Forests of the Jingmai Mountain in Pu’er
    1668: "ペルシアの隊商宿",  # Persian Caravanserai
    1670: "ホイサラ様式の信仰関連遺産群",  # Sacred Ensembles of the Hoysalas
    1673: "ラヴノのヴィエトレニツァ洞窟",  # Vjetrenica
    1676: "人権と自由、和解：ネルソン・マンデラの遺産",  # Human Rights, Liberation and Reconciliation: Nelson Mandela Legacy Sites
    1680: "ヨルサファナの考古学的遺跡：ヨルサファナの入植地とカシポラ・クリークの墓地",  # Jodensavanne
    1686: "アンティコスティ",  # Anticosti
    1688: "ケノゼロ湖の文化的景観",  # Cultural Landscape of Kenozero Lake
    1689: "ホープウェルの儀礼的土塁群",  # Hopewell Ceremonial Earthworks
    1692: "アペニン山脈北部の蒸発岩カルストと洞窟群",  # Evaporitic Karst and Caves of Northern Apennines
    1693: "トゥランの寒冬砂漠群",  # Cold Winter Deserts of Turan
    1694: "中世アナトリアの木造多柱式モスク群",  # Wooden Hypostyle Mosques of Medieval Anatolia
    1696: "キナリグ人の文化的景観と移牧の道「カッチ・ヨル」",  # Cultural Landscape of Khinalig People and “Köç Yolu” Transhumance Route
    1699: "ウルク・バニ・マアリド",  # 'Uruq Bani Ma'arid
    1700: "マリブ：古代サバ王国の代表的遺跡群",  # Landmarks of the Ancient Kingdom of Saba
    1704: "聖地群を経てウィリクタへと至るウィハリカの道（タテウアリ・ウアフイエ）",  # Huichol route to Huiricuta
    1705: "シュヴェリーンの邸宅群",  # Residence Ensemble Schwerin
    1709: "ムルジュガの文化的景観",  # Murujuga National Park
    1711: "モイダム：アホム王朝の墳丘墓・埋葬システム",  # Maidam
    1712: "アル・ファーウ考古地域の文化的景観",  # Qaryat al-Faw
    1713: "ティエベレの王宮",  # Royal Court of Tiébélé
    1714: "北京の中軸線：中国首都の理想的秩序を示す建造物群",  # Central Axis of Beijing
    1715: "グディニャのモダニズム都市中心部",  # Śródmieście
    1718: "ローマ帝国の境界線：ダキア",  # Limes Dacicus
    1719: "オリンポス山周辺地域",  # The wider area of Mount Olympus
    1721: "ウンム・アル・ジマール",  # Umm el-Jimal
    1722: "フロー・カントリー",  # Flow Country
    1724: "ワディ・ウラヤ",  # Wadi Wurayah
    1725: "カルナックとモルビアン沿岸の巨石群",  # Megaliths of Carnac and of the shores of Morbihan
    1726: "バイエルン王ルートヴィヒ2世の宮殿群：ノイシュヴァンシュタイン城、リンダーホーフ城、シャッヘン城、ヘレンキームゼー城",  # The Palaces of King Ludwig II of Bavaria: Neuschwanstein, Linderhof, Schachen and Herrenchiemsee
    1728: "メーンス・クリント",  # Q1517331
    1730: "先史時代のサルディーニャ島の葬送の伝統：ドムス・デ・ヤナス",  # domus de janas
    1731: "サルディスとビン・テペのリュディア墳丘墓",  # Sardis and the Lydian Tumuli of Bin Tepe
    1732: "イエン・トゥー－ヴィン・ニィエム－コン・ソンおよびキエップバックの記念碑と景観の関連遺産群",  # The Complex of Yen Tu Monuments and Landscape
    1734: "セランゴール森林公園マレーシア森林研究所",  # Forest Research Institute Malaysia Forest Park Selangor
    1736: "西夏王陵群",  # Western Xia Mausoleums
    1742: "アカバ海洋保護区",  # Aqaba Marine Reserve
    1743: "シュルガン・タシュ洞窟の岩絵群",  # Kapova Cave
    1745: "マンダラ山脈のディ・ギッド・ビィの文化的景観",  # Diy-Gid-Biy
    1747: "ペルアス川峡谷環境保護区",  # Cavernas do Peruaçu Environmental Protection Area
    1749: "聖ヒラリオン修道院／テル・ウンム・アメル",  # Tell Umm el-'Amr
    1750: "サントメとプリンシペのロサ（農園）群：植民地農業システムと強制移住",  # The Roças of Sao Tome and Principe: Colonial Agricultural System and Forced Migration
    1751: "オケフェノキー国立野生生物保護区",  # Okefenokee National Wildlife Refuge
    1758: "リムフィヨルド西部の硬骨魚類の化石群",  # The Bony Fish Fossils of the Western Limfjord – Evolution and Climate Adaptation in the Earliest Eocene
    1765: "景徳鎮の手工芸磁器産業遺産群",  # Jingdezhen Handicraft Porcelain Industry Sites
    1766: "タシュケントのモダニズム建築：中央アジアにおける近代性と伝統",  # Tashkent Modernist Architecture. Modernity and Tradition in Central Asia
    1774: "アマゾニアの劇場群",  # Amazonia Theaters
    1808: "ボマとバディンギロにおける動物の渡りの景観",  # Boma-Badingilo Migratory Landscape
}
