const group = (category, rows) => rows.map(([emoji, slug, title, words = '']) => ({ emoji, slug, title, keywords: [...new Set([title.toLowerCase(), ...words.split(' ').filter(Boolean)])], category, toneable: category === 'Hands' }));
export const core = [
 ...group('Faces', [
 ['😄','happy','Happy','smile happy joy'],['😂','tears-of-joy','Tears of joy','laugh funny lol'],['😍','heart-eyes','Heart eyes','love adore'],['😎','cool','Cool','sunglasses'],['😉','wink','Wink','joke'],['😘','kiss','Kiss','love'],
 ['😢','sad','Sad','tear'],['😭','crying','Crying','sob tears'],['😠','angry','Angry','mad'],['😮','surprised','Surprised','wow'],['🤔','thinking','Thinking','hmm question'],['😑','unimpressed','Unimpressed','meh'],
 ['😁','grin','Grin','happy teeth'],['🤣','rolling-laughter','Rolling with laughter','rofl funny'],['🥰','love','Love','hearts affection'],['😱','shocked','Shocked','scream fear'],['😴','sleepy','Sleepy','sleep tired'],['😅','phew','Phew','relief sweat']]),
 ...group('Symbols', [['❤️','heart','Heart','love red'],['💔','broken-heart','Broken heart','sad'],['🔥','fire','Fire','hot flame'],['🎉','celebrate','Celebrate','party confetti'],['✅','yes','Yes','check tick correct'],['❌','no','No','cross wrong']]),
 ...group('Hands', [['👍','thumbs-up','Thumbs up','yes good like'],['👎','thumbs-down','Thumbs down','no dislike'],['👋','wave','Wave','hello goodbye'],['👏','clap','Clap','applause'],['🙏','thanks','Thanks','pray please'],['✌️','peace','Peace','victory']])
];
export const expressions = [
 ...group('Faces', [
 ['😀','grinning','Grinning','happy smile'],['🙂','slight-smile','Slight smile','friendly'],['🙃','upside-down','Upside down','silly irony'],['😊','blush','Blush','happy shy'],['😇','innocent','Innocent','angel halo'],['🥳','party-face','Party face','celebrate birthday'],
 ['🤩','star-eyes','Star eyes','excited amazed'],['😋','delicious','Delicious','yum food'],['😛','tongue','Tongue out','playful'],['😜','wink-tongue','Winking tongue','silly cheeky'],['🤪','zany','Zany','crazy silly'],['🤑','money-face','Money face','rich cash'],
 ['🤐','zip-mouth','Zipped mouth','secret quiet'],['🤨','raised-eyebrow','Raised eyebrow','sceptical doubt'],['😐','neutral','Neutral','blank'],['🙄','eye-roll','Eye roll','annoyed'],['😏','smirk','Smirk','knowing'],['😬','grimace','Grimace','awkward teeth'],
 ['😔','pensive','Pensive','sad thoughtful'],['🥺','pleading','Pleading','please puppy eyes'],['😤','huff','Huff','steam frustrated'],['😡','furious','Furious','angry red'],['🤯','mind-blown','Mind blown','exploding amazed'],['🥵','hot-face','Hot face','heat sweat'],
 ['🥶','cold-face','Cold face','frozen ice'],['🤢','nauseated','Nauseated','sick green'],['🤮','vomit','Vomiting','sick'],['🤒','fever','Fever','thermometer sick'],['🤕','bandage','Bandaged head','hurt injury'],['😷','mask','Medical mask','ill health']])
];
export const nature = group('Nature', [
 ['🐶','dog','Dog','puppy pet'],['🐱','cat','Cat','kitten pet'],['🐭','mouse','Mouse','rodent'],['🐹','hamster','Hamster','pet'],['🐰','rabbit','Rabbit','bunny'],['🦊','fox','Fox','animal'],
 ['🐻','bear','Bear','animal'],['🐼','panda','Panda','bear'],['🐨','koala','Koala','animal'],['🐯','tiger','Tiger','cat'],['🦁','lion','Lion','cat'],['🐮','cow','Cow','farm'],
 ['🐷','pig','Pig','farm'],['🐸','frog','Frog','green'],['🐵','monkey','Monkey','animal'],['🐔','chicken','Chicken','bird'],['🐧','penguin','Penguin','bird'],['🦆','duck','Duck','bird'],
 ['🦉','owl','Owl','bird'],['🦋','butterfly','Butterfly','insect'],['🐝','bee','Bee','insect honey'],['🐢','turtle','Turtle','slow'],['🐙','octopus','Octopus','sea'],['🐳','whale','Whale','sea'],
 ['🌻','sunflower','Sunflower','flower'],['🌹','rose','Rose','flower love'],['🌈','rainbow','Rainbow','weather'],['☀️','sun','Sun','sunny weather'],['🌙','moon','Moon','night'],['⭐','star','Star','night favourite']
]);
export const everyday = [
 ...group('Food', [
 ['🍎','apple','Apple','fruit'],['🍌','banana','Banana','fruit'],['🍓','strawberry','Strawberry','fruit'],['🍉','watermelon','Watermelon','fruit'],['🍋','lemon','Lemon','fruit'],['🥑','avocado','Avocado','food'],
 ['🍕','pizza','Pizza','food slice vegetarian veggie mushroom tomato pepper olive onion'],['🍔','burger','Burger','food'],['🍟','fries','Fries','chips food'],['🌮','taco','Taco','food'],['🍿','popcorn','Popcorn','movie snack'],['🍰','cake','Cake','dessert birthday'],
 ['🍩','doughnut','Doughnut','donut dessert'],['🍪','cookie','Cookie','biscuit snack'],['🍦','ice-cream','Ice cream','dessert'],['☕','coffee','Coffee','tea drink'],['🍺','beer','Beer','pint drink'],['🥂','cheers','Cheers','glasses toast']]),
 ...group('Objects', [
 ['🎁','gift','Gift','present birthday'],['💡','idea','Light bulb','idea'],['🔑','key','Key','unlock'],['🔒','lock','Lock','private secure'],['🚀','rocket','Rocket','launch space'],['💻','laptop','Laptop','computer work'],
 ['📱','phone','Phone','mobile'],['📷','camera','Camera','photo'],['🎮','gamepad','Gamepad','game play'],['⚽','football','Football','soccer sport'],['🏆','trophy','Trophy','winner award'],['💩','poop','Poop','shit poo']])
];
export const mascot=group('Nature',[['🫏','crypto-donkey','Donkey','orange donkey crypto cryptodonkey thecryptodonkey cute mascot']]);
export const sacredStone=[{emoji:'🪨',slug:'sacred-stone',title:'Sacred stone',keywords:['rock','stone','sacred','600','600.wtf','600000000000'],category:'Objects',toneable:false}];
export const jumpingSpider=group('Nature',[['🕷️','jumping-spider','Jumping spider','black spider cute littleleap little leap pip jumping fuzzy']]);
export const bitcoin=[{emoji:'₿',slug:'bitcoin',title:'Bitcoin',keywords:['bitcoin','btc','orange','coin','currency'],category:'Symbols',toneable:false,kind:'symbol'}];
export const brands=[
 ['forgesworn','ForgeSworn','png'],['kindred','Kindred','svg'],['kithmoot','KithMoot','svg'],['mysignet','MySignet','svg'],['vitark','Vitark','svg'],['vitark_den','Vitark Den','svg'],['vitark_train','Vitark Train','svg'],['vitark_still','Vitark Still','svg'],['vitark_record','Vitark Record','svg']
].map(([name,title,extension])=>({file:`brands/fs-${name.replaceAll('_','-')}.${extension}`,cols:1,rows:1,preserve:true,entries:[{emoji:`:fs_${name}:`,slug:`fs-${name.replaceAll('_','-')}`,title,keywords:[title.toLowerCase(),'forgesworn','brand','logo',...name.split('_')],category:'forgesworn',toneable:false,kind:'custom'}]}));
// Sunburst's expression rows drifted upward; these measured gutters preserve complete silhouettes.
export const sheets = [{file:'core.png',cols:6,rows:6,entries:core},{file:'expressions.png',cols:6,rows:5,rowEdges:[0,266,506,742,983,1280],entries:expressions},{file:'nature.png',cols:6,rows:5,entries:nature},{file:'everyday.png',cols:6,rows:5,entries:everyday},{file:'crypto-donkey.png',cols:1,rows:1,entries:mascot},{file:'sacred-stone.png',cols:1,rows:1,entries:sacredStone},{file:'jumping-spider.png',cols:1,rows:1,entries:jumpingSpider},{file:'bitcoin.png',cols:1,rows:1,entries:bitcoin},...brands];
export const definitions = sheets.flatMap(sheet => sheet.entries);
