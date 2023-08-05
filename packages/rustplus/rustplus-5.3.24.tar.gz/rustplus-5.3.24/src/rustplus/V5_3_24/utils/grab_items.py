import requests
import json

item_ids = {
    "-2139580305": "Auto Turret",
    "-2124352573": "Acoustic Guitar",
    "-2123125470": "Advanced Healing Tea",
    "-2107018088": "Shovel Bass",
    "-2103694546": "Sunglasses",
    "-2099697608": "Stones",
    "-2097376851": "Nailgun Nails",
    "-2094954543": "Wood Armor Helmet",
    "-2086926071": "Potato",
    "-2084071424": "Potato Seed",
    "-2072273936": "Bandage",
    "-2069578888": "M249",
    "-2067472972": "Sheet Metal Door",
    "-2058362263": "Small Candle Set",
    "-2049214035": "Pressure Pad",
    "-2047081330": "Movember Moustache",
    "-2040817543": "Pan Flute",
    "-2025184684": "Shirt",
    "-2022172587": "Diving Tank",
    "-2012470695": "Improvised Balaclava",
    "-2002277461": "Road Sign Jacket",
    "-2001260025": "Instant Camera",
    "-1999722522": "Furnace",
    "-1997698639": "Sunglasses",
    "-1997543660": "Horse Saddle",
    "-1994909036": "Sheet Metal",
    "-1992717673": "Large Furnace",
    "-1985799200": "Rug",
    "-1982036270": "High Quality Metal Ore",
    "-1978999529": "Salvaged Cleaver",
    "-1973785141": "Fogger-3000",
    "-1966748496": "Mace",
    "-1962971928": "Mushroom",
    "-1961560162": "Firecracker String",
    "-1958316066": "Scientist Suit",
    "-1950721390": "Concrete Barricade",
    "-1941646328": "Can of Tuna",
    "-1938052175": "Charcoal",
    "-1916473915": "Chinese Lantern",
    "-1904821376": "Orange Roughy",
    "-1903165497": "Bone Helmet",
    "-1899491405": "Glue",
    "-1884328185": "ScrapTransportHeliRepair",
    "-1880870149": "Red Keycard",
    "-1880231361": "Flatbed Vehicle Module",
    "-1878764039": "Small Trout",
    "-1878475007": "Satchel Charge",
    "-1863559151": "Water Barrel",
    "-1861522751": "Research Table",
    "-1850571427": "Silencer",
    "-1848736516": "Cooked Chicken",
    "-1841918730": "High Velocity Rocket",
    "-1832422579": "One Sided Town Sign Post",
    "-1824943010": "Jack O Lantern Happy",
    "-1819763926": "Wind Turbine",
    "-1819233322": "Medium Wooden Sign",
    "-1815301988": "Water Pistol",
    "-1812555177": "LR-300 Assault Rifle",
    "-1802083073": "High Quality Valves",
    "-1800345240": "Speargun Spear",
    "-1785231475": "Surgeon Scrubs",
    "-1780802565": "Salvaged Icepick",
    "-1779183908": "Paper",
    "-1779180711": "Water",
    "-1778897469": "Button",
    "-1778159885": "Heavy Plate Pants",
    "-1776128552": "Green Berry Seed",
    "-1773144852": "Hide Skirt",
    "-1772746857": "Heavy Scientist Suit",
    "-1768880890": "Small Shark",
    "-1759188988": "Hab Repair",
    "-1758372725": "Thompson",
    "-1754948969": "Sleeping Bag",
    "-1736356576": "Reactive Target",
    "-1729415579": "Adv. Anti-Rad Tea",
    "-1709878924": "Raw Human Meat",
    "-1698937385": "Herring",
    "-1695367501": "Shorts",
    "-1693832478": "Large Flatbed Vehicle Module",
    "-1691396643": "HV Pistol Ammo",
    "-1685290200": "12 Gauge Buckshot",
    "-1679267738": "Graveyard Fence",
    "-1677315902": "Pure Healing Tea",
    "-1673693549": "Empty Propane Tank",
    "-1671551935": "Direct Torpedo",
    "-1667224349": "Decorative Baubels",
    "-1663759755": "Land Mine",
    "-1654233406": "Sardine",
    "-1651220691": "Pookie Bear",
    "-1647846966": "Two Sided Ornate Hanging Sign",
    "-1622660759": "Large Present",
    "-1622110948": "Bandit Guard Gear",
    "-1621539785": "Beach Parasol",
    "-1615281216": "Armored Passenger Vehicle Module",
    "-1614955425": "Strengthened Glass Window",
    "-1607980696": "Work Bench Level 3",
    "-1588628467": "Computer Station",
    "-1583967946": "Stone Hatchet",
    "-1581843485": "Sulfur",
    "-1579932985": "Horse Dung",
    "-1569700847": "Headset",
    "-1557377697": "Empty Tuna Can",
    "-1553999294": "Red Boomer",
    "-1549739227": "Boots",
    "-1539025626": "Miners Hat",
    "-1538109120": "Violet Volcano Firework",
    "-1535621066": "Stone Fireplace",
    "-1530414568": "Cassette Recorder",
    "-1520560807": "Raw Bear Meat",
    "-1519126340": "Drop Box",
    "-1518883088": "Night Vision Goggles",
    "-1517740219": "Speargun",
    "-1511285251": "Pumpkin Seed",
    "-1509851560": "Cooked Deer Meat",
    "-1507239837": "HBHF Sensor",
    "-1506417026": "Ninja Suit",
    "-1506397857": "Salvaged Hammer",
    "-1501451746": "Cockpit Vehicle Module",
    "-1488398114": "Composter",
    "-1486461488": "Red Roman Candle",
    "-1478445584": "Tuna Can Lamp",
    "-1478212975": "Wolf Headdress",
    "-1478094705": "Boogie Board",
    "-1469578201": "Longsword",
    "-1448252298": "Electrical Branch",
    "-1442559428": "Hobo Barrel",
    "-1440987069": "Raw Chicken Breast",
    "-1432674913": "Anti-Radiation Pills",
    "-1429456799": "Prison Cell Wall",
    "-1423304443": "Medium Neon Sign",
    "-1408336705": "Sunglasses",
    "-1405508498": "Muzzle Boost",
    "-1379835144": "Festive Window Garland",
    "-1379036069": "Canbourine",
    "-1370759135": "Portrait Picture Frame",
    "-1368584029": "Sickle",
    "-1367281941": "Waterpipe Shotgun",
    "-1336109173": "Wood Double Door",
    "-1331212963": "Star Tree Topper",
    "-1330640246": "Junkyard Drum Kit",
    "-1321651331": "Explosive 5.56 Rifle Ammo",
    "-1316706473": "Camera",
    "-1306288356": "Green Roman Candle",
    "-1305326964": "Green Berry Clone",
    "-1302129395": "Pickaxe",
    "-1293296287": "Small Oil Refinery",
    "-1286302544": "OR Switch",
    "-1284169891": "Water Pump",
    "-1273339005": "Bed",
    "-1266045928": "Bunny Onesie",
    "-1262185308": "Binoculars",
    "-1252059217": "Hatchet",
    "-1234735557": "Wooden Arrow",
    "-1215753368": "Flame Thrower",
    "-1215166612": "A Barrel Costume",
    "-1211268013": "Basic Horse Shoes",
    "-1211166256": "5.56 Rifle Ammo",
    "-1199897172": "Metal Vertical embrasure",
    "-1199897169": "Metal horizontal embrasure",
    "-1184406448": "Basic Max Health Tea",
    "-1183726687": "Wooden Window Bars",
    "-1167031859": "Spoiled Wolf Meat",
    "-1166712463": "Fluid Splitter",
    "-1163532624": "Jacket",
    "-1162759543": "Cooked Horse Meat",
    "-1157596551": "Sulfur Ore",
    "-1138208076": "Small Wooden Sign",
    "-1137865085": "Machete",
    "-1130709577": "Pump Jack",
    "-1130350864": "Raw Horse Meat",
    "-1123473824": "Multiple Grenade Launcher",
    "-1117626326": "Chainlink Fence",
    "-1113501606": "Boom Box",
    "-1112793865": "Door Key",
    "-1108136649": "Tactical Gloves",
    "-1104881824": "Rug Bear Skin",
    "-1102429027": "Heavy Plate Jacket",
    "-1101924344": "Wetsuit",
    "-1100422738": "Spinning wheel",
    "-1100168350": "Large Water Catcher",
    "-1078639462": "Skull Spikes",
    "-1073015016": "Skull Spikes",
    "-1049881973": "Cowbell",
    "-1044468317": "RF Broadcaster",
    "-1043618880": "Ghost Costume",
    "-1039528932": "Small Water Bottle",
    "-1036635990": "12 Gauge Incendiary Shell",
    "-1023374709": "Wood Shutters",
    "-1023065463": "High Velocity Arrow",
    "-1022661119": "Baseball Cap",
    "-1021495308": "Metal Spring",
    "-1018587433": "Animal Fat",
    "-1009359066": "SAM Site",
    "-1004426654": "Bunny Ears",
    "-1002156085": "Gold Egg",
    "-1000573653": "Frog Boots",
    "-996920608": "Blueprint",
    "-996185386": "XL Picture Frame",
    "-992286106": "White Berry Seed",
    "-989755543": "Burnt Bear Meat",
    "-985781766": "High Ice Wall",
    "-979951147": "Jerry Can Guitar",
    "-979302481": "Easter Door Wreath",
    "-967648160": "High External Stone Wall",
    "-961457160": "New Year Gong",
    "-956706906": "Prison Cell Gate",
    "-946369541": "Low Grade Fuel",
    "-939424778": "Flasher Light",
    "-932201673": "Scrap",
    "-930193596": "Fertilizer",
    "-929092070": "Basic Healing Tea",
    "-924959988": "Skull Trophy",
    "-912398867": "Cassette - Medium",
    "-904863145": "Semi-Automatic Rifle",
    "-888153050": "Halloween Candy",
    "-886280491": "Hemp Clone",
    "-858312878": "Cloth",
    "-855748505": "Simple Handmade Sight",
    "-854270928": "Dragon Door Knocker",
    "-852563019": "M92 Pistol",
    "-851988960": "Salmon",
    "-850982208": "Key Lock",
    "-845557339": "Landscape Picture Frame",
    "-819720157": "Metal Window Bars",
    "-810326667": "Work Cart",
    "-804769727": "Plant Fiber",
    "-803263829": "Coffee Can Helmet",
    "-798293154": "Laser Detector",
    "-796583652": "Shop Front",
    "-784870360": "Electric Heater",
    "-781014061": "Sprinkler",
    "-778875547": "Corn Clone",
    "-778367295": "L96 Rifle",
    "-769647921": "Skull Trophy",
    "-765183617": "Double Barrel Shotgun",
    "-761829530": "Burlap Shoes",
    "-751151717": "Spoiled Chicken",
    "-746647361": "Memory Cell",
    "-746030907": "Granola Bar",
    "-742865266": "Rocket",
    "-733625651": "Paddling Pool",
    "-727717969": "12 Gauge Slug",
    "-722241321": "Small Present",
    "-702051347": "Bandana Mask",
    "-700591459": "Can of Beans",
    "-699558439": "Roadsign Gloves",
    "-697981032": "Inner Tube",
    "-695978112": "Smart Alarm",
    "-695124222": "Giant Candy Decor",
    "-692338819": "Small Rechargeable Battery",
    "-691113464": "High External Stone Gate",
    "-690968985": "Blocker",
    "-690276911": "Glowing Eyes",
    "-682687162": "Burnt Human Meat",
    "-656349006": "Green Boomer",
    "-649128577": "Basic Wood Tea",
    "-629028935": "Electric Fuse",
    "-626174997": "Taxi Vehicle Module",
    "-592016202": "Explosives",
    "-587989372": "Catfish",
    "-586784898": "Mail Box",
    "-586342290": "Blueberries",
    "-583379016": "Megaphone",
    "-582782051": "Snap Trap",
    "-575744869": "Party Hat",
    "-575483084": "Santa Hat",
    "-568419968": "Grub",
    "-567909622": "Pumpkin",
    "-566907190": "RF Pager",
    "-563624462": "Splitter",
    "-560304835": "Space Suit",
    "-559599960": "Sandbag Barricade",
    "-557539629": "Pure Wood Tea",
    "-555122905": "Sofa",
    "-544317637": "Research Paper",
    "-542577259": "Minnows",
    "-541206665": "Advanced Wood Tea",
    "-520133715": "Yellow Berry Seed",
    "-515830359": "Blue Roman Candle",
    "-502177121": "Door Controller",
    "-496584751": "Rad. Removal Tea",
    "-493159321": "Medium Quality Spark Plugs",
    "-489848205": "Large Candle Set",
    "-487356515": "Anti-Rad Tea",
    "-484206264": "Blue Keycard",
    "-465682601": "SUPER Stocking",
    "-463122489": "Watch Tower",
    "-458565393": "Root Combiner",
    "-454370658": "Red Volcano Firework",
    "-395377963": "Raw Wolf Meat",
    "-384243979": "SAM Ammo",
    "-369760990": "Small Stash",
    "-365097295": "Powered Water Purifier",
    "-363689972": "Snowball",
    "-343857907": "Sound Light",
    "-335089230": "High External Wooden Gate",
    "-333406828": "Sled",
    "-324675402": "Reindeer Antlers",
    "-321733511": "Crude Oil",
    "-321431890": "Beach Chair",
    "-316250604": "Wooden Ladder",
    "-295829489": "Test Generator",
    "-282113991": "Simple Light",
    "-280223496": "Violet Boomer",
    "-277057363": "Salt Water",
    "-265876753": "Gun Powder",
    "-265292885": "Fluid Combiner",
    "-262590403": "Salvaged Axe",
    "-253079493": "Scientist Suit",
    "-242084766": "Cooked Pork",
    "-239306133": "Surface torpedo",
    "-237809779": "Hemp Seed",
    "-216999575": "Counter",
    "-216116642": "Skull Door Knocker",
    "-211235948": "Xylobone",
    "-209869746": "Decorative Plastic Candy Canes",
    "-196667575": "Flashlight",
    "-194953424": "Metal Facemask",
    "-194509282": "Butcher Knife",
    "-187031121": "Solo Submarine",
    "-180129657": "Wood Storage Box",
    "-176608084": "Sunglasses",
    "-173268132": "Rustig\u00e9 Egg - Blue",
    "-173268131": "Rustig\u00e9 Egg - Purple",
    "-173268129": "Rustig\u00e9 Egg - Red",
    "-173268126": "Rustig\u00e9 Egg - Ivory",
    "-173268125": "Rustig\u00e9 Egg - Green",
    "-156748077": "Skull Trophy",
    "-151838493": "Wood",
    "-151387974": "Deluxe Christmas Lights",
    "-148794216": "Garage Door",
    "-148229307": "Metal Shop Front",
    "-144417939": "Wire Tool",
    "-143132326": "Huge Wooden Sign",
    "-135252633": "Sled",
    "-132516482": "Weapon Lasersight",
    "-132247350": "Small Water Catcher",
    "-129230242": "Decorative Pinecones",
    "-126305173": "Painted Egg",
    "-119235651": "Water Jug",
    "-113413047": "Diving Mask",
    "-110921842": "Locker",
    "-99886070": "Violet Roman Candle",
    "-97956382": "Tool Cupboard",
    "-97459906": "Jumpsuit",
    "-92759291": "Wooden Floor Spikes",
    "-89874794": "Low Quality Spark Plugs",
    "-78533081": "Burnt Deer Meat",
    "-75944661": "Eoka Pistol",
    "-48090175": "Snow Jacket",
    "-44876289": "Igniter",
    "-44066823": "Medium Chassis",
    "-44066790": "Large Chassis",
    "-44066600": "Small Chassis",
    "-41896755": "Work Bench Level 2",
    "-41440462": "Spas-12 Shotgun",
    "-33009419": "Pure Anti-Rad Tea",
    "-25740268": "Skull Spikes",
    "-23994173": "Boonie Hat",
    "-22883916": "Dragon Mask",
    "-20045316": "Mobile Phone",
    "-17123659": "Smoke Rocket WIP!!!!",
    "-8312704": "Beach Towel",
    "-7270019": "Orange Boomer",
    "-4031221": "Metal Ore",
    "3222790": "Hide Halterneck",
    "3380160": "Card Movember Moustache",
    "14241751": "Fire Arrow",
    "15388698": "Stone Barricade",
    "20489901": "Purple Sunglasses",
    "21402876": "Burlap Gloves",
    "23352662": "Large Banner Hanging",
    "23391694": "Bunny Hat",
    "28201841": "M39 Rifle",
    "37122747": "Green Keycard",
    "39600618": "Microphone Stand",
    "42535890": "Medium Animated Neon Sign",
    "51984655": "Incendiary Pistol Bullet",
    "60528587": "Roadsign Horse Armor",
    "62577426": "Photograph",
    "69511070": "Metal Fragments",
    "73681876": "Tech Trash",
    "95950017": "Metal Pipe",
    "98508942": "XXL Picture Frame",
    "99588025": "High External Wooden Wall",
    "121049755": "Tall Picture Frame",
    "122783240": "Black Berry Clone",
    "143803535": "F1 Grenade",
    "170758448": "Cockpit With Engine Vehicle Module",
    "171931394": "Stone Pickaxe",
    "174866732": "16x Zoom Scope",
    "176787552": "Rifle Body",
    "177226991": "Scarecrow",
    "185586769": "Inner Tube",
    "190184021": "Kayak",
    "196700171": "Hide Vest",
    "198438816": "Vending Machine",
    "200773292": "Hammer",
    "204391461": "Coal :(",
    "204970153": "Wrapped Gift",
    "215754713": "Bone Arrow",
    "223891266": "T-Shirt",
    "237239288": "Pants",
    "254522515": "Large Medkit",
    "261913429": "White Volcano Firework",
    "263834859": "Basic Scrap Tea",
    "268565518": "Storage Vehicle Module",
    "271048478": "Rat Mask",
    "273172220": "Plumber's Trumpet",
    "273951840": "Scarecrow Suit",
    "277730763": "Mummy Suit",
    "282103175": "Giant Lollipop Decor",
    "286193827": "Pickles",
    "286648290": "Disco Floor",
    "296519935": "Diving Fins",
    "304481038": "Flare",
    "317398316": "High Quality Metal",
    "342438846": "Anchovy",
    "349762871": "40mm HE Grenade",
    "352130972": "Rotten Apple",
    "352321488": "Sunglasses",
    "352499047": "Shotgun Trap",
    "359723196": "Chippy Arcade Game",
    "363163265": "Hose Tool",
    "363467698": "Chocolate Bar",
    "390728933": "Yellow Berry Clone",
    "418081930": "Wood Chestplate",
    "442289265": "Holosight",
    "442886268": "Rocket Launcher",
    "443432036": "Fluid Switch & Pump",
    "476066818": "Cassette - Long",
    "479143914": "Gears",
    "479292118": "Large Loot Bag",
    "492357192": "RAND Switch",
    "524678627": "Advanced Scrap Tea",
    "528668503": "Flame Turret",
    "553270375": "Large Rechargeable Battery",
    "553887414": "Skull Fire Pit",
    "559147458": "Survival Fish Trap",
    "567235583": "8x Zoom Scope",
    "567871954": "Secret Lab Chair",
    "573676040": "Coffin",
    "573926264": "Semi Automatic Body",
    "576509618": "Portable Boom Box",
    "588596902": "Handmade Shell",
    "593465182": "Table",
    "596469572": "RF Transmitter",
    "602741290": "Burlap Shirt",
    "603811464": "Advanced Max Health Tea",
    "605467368": "Incendiary 5.56 Rifle Ammo",
    "609049394": "Battery - Small",
    "613961768": "Bota Bag",
    "621915341": "Raw Pork",
    "634478325": "CCTV Camera",
    "642482233": "Sticks",
    "649912614": "Revolver",
    "656371026": "High Quality Carburetor",
    "656371027": "Medium Quality Carburetor",
    "656371028": "Low Quality Carburetor",
    "657352755": "Beach Table",
    "665332906": "Timer",
    "671063303": "Riot Helmet",
    "671706427": "Reinforced Glass Window",
    "674734128": "Festive Doorway Garland",
    "680234026": "Yellow Perch",
    "696029452": "Paper Map",
    "699075597": "Wooden Cross",
    "722955039": "Water Gun",
    "756517185": "Medium Present",
    "762289806": "Siren Light",
    "785728077": "Pistol Bullet",
    "794356786": "Hide Boots",
    "794443127": "Christmas Tree",
    "795236088": "Torch",
    "795371088": "Pump Shotgun",
    "803222026": "Repair Bench",
    "803954639": "Blue Berry Seed",
    "809199956": "Gravestone",
    "809942731": "Scarecrow Wrap",
    "813023040": "Cooked Wolf Meat",
    "818733919": "Industrial Door",
    "818877484": "Semi-Automatic Pistol",
    "826309791": "Two Sided Town Sign Post",
    "830839496": "Red Berry Seed",
    "832133926": "Wood Armor Pants",
    "833533164": "Large Wood Box",
    "838831151": "Blue Berry Clone",
    "844440409": "Bronze Egg",
    "850280505": "Bucket Helmet",
    "853471967": "Laser Light",
    "854447607": "White Berry",
    "858486327": "Green Berry",
    "866332017": "Large Neon Sign",
    "866889860": "Wooden Barricade",
    "878301596": "Generic vehicle module",
    "882559853": "Spider Webs",
    "884424049": "Compound Bow",
    "888415708": "RF Receiver",
    "895374329": "Passenger Vehicle Module",
    "915408809": "40mm Smoke Grenade",
    "926800282": "Medium Quality Valves",
    "935692442": "Longsleeve T-Shirt",
    "936496778": "Floor grill",
    "946662961": "Car Key",
    "952603248": "Weapon flashlight",
    "963906841": "Rock",
    "968019378": "Clatter Helmet",
    "968421290": "Connected Speaker",
    "971362526": "Skull Trophy",
    "980333378": "Hide Poncho",
    "988652725": "Smart Switch",
    "989925924": "Raw Fish",
    "996293980": "Human Skull",
    "998894949": "Corn Seed",
    "999690781": "Geiger Counter",
    "1015352446": "Duo Submarine",
    "1052926200": "Mining Quarry",
    "1055319033": "40mm Shotgun Round",
    "1058261682": "Christmas Lights",
    "1072924620": "High Quality Spark Plugs",
    "1079279582": "Medical Syringe",
    "1081315464": "Nest Hat",
    "1081921512": "Card Table",
    "1090916276": "Pitchfork",
    "1094293920": "Wrapping Paper",
    "1099314009": "Barbeque",
    "1103488722": "Snowball Gun",
    "1104520648": "Chainsaw",
    "1110385766": "Metal Chest Plate",
    "1112162468": "Blue Berry",
    "1121925526": "Candy Cane",
    "1142993169": "Ceiling Light",
    "1149964039": "Storage Monitor",
    "1153652756": "Large Wooden Sign",
    "1158340331": "Medium Quality Crankshaft",
    "1158340332": "High Quality Crankshaft",
    "1158340334": "Low Quality Crankshaft",
    "1159991980": "Code Lock",
    "1160881421": "Hitch & Trough",
    "1171735914": "AND Switch",
    "1177596584": "Elevator",
    "1181207482": "Heavy Plate Helmet",
    "1186655046": "Fuel Tank Vehicle Module",
    "1189981699": "Crate Costume",
    "1199391518": "Road Signs",
    "1205084994": "Large Photo Frame",
    "1205607945": "Two Sided Hanging Sign",
    "1221063409": "Armored Double Door",
    "1230323789": "SMG Body",
    "1234878710": "Telephone",
    "1234880403": "Sewing Kit",
    "1242482355": "Jack O Lantern Angry",
    "1242522330": "Cursed Cauldron",
    "1248356124": "Timed Explosive Charge",
    "1258768145": "Sunglasses",
    "1259919256": "Mixing Table",
    "1263920163": "Smoke Grenade",
    "1266491000": "Hazmat Suit",
    "1272194103": "Red Berry",
    "1272430949": "Wheelbarrow Piano",
    "1272768630": "Spoiled Human Meat",
    "1293102274": "XOR Switch",
    "1305578813": "Small Neon Sign",
    "1315082560": "Ox Mask",
    "1318558775": "MP5A4",
    "1319617282": "Small Loot Bag",
    "1324203999": "Champagne Boomer",
    "1326180354": "Salvaged Sword",
    "1327005675": "Short Ice Wall",
    "1330084809": "Low Quality Valves",
    "1346158228": "Pumpkin Bucket",
    "1353298668": "Armored Door",
    "1358643074": "Snow Machine",
    "1366282552": "Leather Gloves",
    "1367190888": "Corn",
    "1371909803": "Tesla Coil",
    "1373240771": "Wooden Barricade Cover",
    "1373971859": "Python Revolver",
    "1376065505": "Rear Seats Vehicle Module",
    "1381010055": "Leather",
    "1382263453": "Barbed Wooden Barricade",
    "1390353317": "Sheet Metal Double Door",
    "1391703481": "Burnt Pork",
    "1397052267": "Supply Signal",
    "1400460850": "Saddle bag",
    "1401987718": "Duct Tape",
    "1409529282": "Door Closer",
    "1413014235": "Fridge",
    "1414245162": "Note",
    "1414245522": "Rope",
    "1422530437": "Raw Deer Meat",
    "1424075905": "Water Bucket",
    "1426574435": "MC repair",
    "1443579727": "Hunting Bow",
    "1451568081": "Chainlink Fence Gate",
    "1478091698": "Muzzle Brake",
    "1480022580": "Basic Ore Tea",
    "1488979457": "Jackhammer",
    "1491189398": "Paddle",
    "1512054436": "Potato Clone",
    "1516985844": "Netting",
    "1521286012": "Double Sign Post",
    "1523195708": "Targeting Computer",
    "1523403414": "Cassette - Short",
    "1524187186": "Work Bench Level 1",
    "1525520776": "Building Plan",
    "1533551194": "White Berry Clone",
    "1534542921": "Chair",
    "1536610005": "Cooked Human Meat",
    "1540934679": "Wooden Spear",
    "1542290441": "Single Sign Post",
    "1545779598": "Assault Rifle",
    "1548091822": "Apple",
    "1553078977": "Bleach",
    "1557173737": "Sunglasses",
    "1559779253": "Engine Vehicle Module",
    "1568388703": "Diesel Fuel",
    "1569882109": "Handmade Fishing Rod",
    "1581210395": "Large Planter Box",
    "1588298435": "Bolt Action Rifle",
    "1588492232": "Drone",
    "1601468620": "Blue Jumpsuit",
    "1602646136": "Stone Spear",
    "1608640313": "Tank Top",
    "1629293099": "Snowman",
    "1638322904": "Incendiary Rocket",
    "1643667218": "Large Animated Neon Sign",
    "1655650836": "Metal Barricade",
    "1655979682": "Empty Can Of Beans",
    "1658229558": "Lantern",
    "1659114910": "Gas Mask",
    "1659447559": "Wooden Horse Armor",
    "1660145984": "Yellow Berry",
    "1668129151": "Cooked Fish",
    "1668858301": "Small Stocking",
    "1675639563": "Beenie Hat",
    "1686524871": "Decorative Gingerbread Men",
    "1696050067": "Modular Car Lift",
    "1697996440": "Landscape Photo Frame",
    "1711033574": "Bone Club",
    "1712070256": "HV 5.56 Rifle Ammo",
    "1712261904": "Pure Max Health Tea",
    "1714496074": "Candle Hat",
    "1719978075": "Bone Fragments",
    "1722154847": "Hide Pants",
    "1723747470": "Tree Lights",
    "1729120840": "Wooden Door",
    "1729374708": "Pure Ore Tea",
    "1729712564": "Portrait Photo Frame",
    "1735402444": "Disco Floor",
    "1744298439": "Blue Boomer",
    "1746956556": "Bone Armor",
    "1751045826": "Hoodie",
    "1757265204": "Silver Egg",
    "1770475779": "Worm",
    "1770744540": "Generic vehicle chassis",
    "1771755747": "Black Berry",
    "1776460938": "Blood",
    "1783512007": "Cactus Flesh",
    "1784406797": "Sousaphone",
    "1789825282": "Candy Cane Club",
    "1796682209": "Custom SMG",
    "1803831286": "Garry's Mod Tool Gun",
    "1814288539": "Bone Knife",
    "1827479659": "Burnt Wolf Meat",
    "1835946060": "Cable Tunnel",
    "1840570710": "Above Ground Pool",
    "1840822026": "Beancan Grenade",
    "1849887541": "Small Generator",
    "1850456855": "Road Sign Kilt",
    "1856217390": "Egg Basket",
    "1873897110": "Cooked Bear Meat",
    "1874610722": "Armored Cockpit Vehicle Module",
    "1877339384": "Burlap Headwrap",
    "1882709339": "Metal Blade",
    "1883981798": "Low Quality Pistons",
    "1883981800": "High Quality Pistons",
    "1883981801": "Medium Quality Pistons",
    "1885488976": "Spooky Speaker",
    "1895235349": "Disco Ball",
    "1898094925": "Pumpkin Plant Clone",
    "1899610628": "Medium Loot Bag",
    "1903654061": "Small Planter Box",
    "1905387657": "Pure Rad. Removal Tea",
    "1911552868": "Black Berry Seed",
    "1917703890": "Burnt Horse Meat",
    "1931713481": "Black Raspberries",
    "1946219319": "Camp Fire",
    "1948067030": "Ladder Hatch",
    "1950721418": "Salvaged Shelves",
    "1951603367": "Switch",
    "1953903201": "Nailgun",
    "1965232394": "Crossbow",
    "1973165031": "Birthday Cake",
    "1973684065": "Burnt Chicken",
    "1975934948": "Survey Charge",
    "1983621560": "Floor triangle grill",
    "1989785143": "High Quality Horse Shoes",
    "1992974553": "Burlap Trousers",
    "2009734114": "Christmas Door Wreath",
    "2019042823": "Tarp",
    "2021351233": "Advanced Rad. Removal Tea",
    "2023888403": "Medium Rechargeable Battery",
    "2024467711": "Pure Scrap Tea",
    "2040726127": "Combat Knife",
    "2041899972": "Triangle Ladder Hatch",
    "2048317869": "Wolf Skull",
    "2052270186": "Inner Tube",
    "2063916636": "Advanced Ore Tea",
    "2070189026": "Large Banner on pole",
    "2087678962": "Search Light",
    "2090395347": "Large Solar Panel",
    "2100007442": "Audio Alarm",
    "2104517339": "Strobe Light",
    "2106561762": "Decorative Tinsel",
    "2114754781": "Water Purifier",
    "2126889441": "Santa Beard",
    "2133269020": "Red Berry Clone",
    "-1843426638": "MLRS Rocket",
    "343045591": "MLRS Aiming Module",
}


def translate_id_to_stack(value_id: int) -> str:
    global item_ids
    try:
        return item_ids[str(value_id)]
    except KeyError:
        return "Not Found"


def grab_items() -> None:
    data = {}

    for line in (
        requests.get(
            "https://raw.githubusercontent.com/OrangeWulf/Rust-Docs/master/Items.md"
        )
        .content.decode()
        .splitlines(False)[4:]
    ):
        if len(line) == 0:
            continue

        item = line.split("|")[1:-1]

        if item[1] == "":
            continue

        data[int(item[-1])] = item[1]

    with open("rust_items.json", "w") as output:
        json.dump(data, output, indent=4, sort_keys=True)


if __name__ == "__main__":
    grab_items()
