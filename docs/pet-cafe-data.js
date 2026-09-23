/* Paw & Pour — shared café data and static render helpers.
   Identical on both the vulnerable and patched pages; only the
   security-relevant logic differs between them. */

const CAFE = {
  name: 'Paw & Pour',
  tagline: 'Coffee, pastries, and a room full of good dogs (and cats, and one very opinionated rabbit).',
  address: '118 Hollow Creek Road, Maple Hollow',
  hours: 'Tue–Sun · 8:00 AM–7:00 PM · Closed Mondays',
  phone: '(555) 240-7761',
};

const STAFF = [
  { username: 'staff_manager', password: 'Marigold@2024', name: 'Priya (Manager)' },
  { username: 'staff_barista', password: 'PourOver!88', name: 'Alex (Barista)' },
];

const PETS = [
  { name: 'Biscuit', species: 'dog', emoji: '🐶', color: '#caa06a', breed: 'Golden Retriever mix', age: '4 yrs', note: 'Loves belly rubs, terrible at fetch.', status: 'Available for cuddles' },
  { name: 'Nimbus', species: 'cat', emoji: '🐱', color: '#9aa3ad', breed: 'Grey tabby', age: '2 yrs', note: 'Naps in the pastry case sunbeam every afternoon.', status: 'Napping' },
  { name: 'Clover', species: 'rabbit', emoji: '🐰', color: '#d9c2a6', breed: 'Holland Lop', age: '1 yr', note: 'Will steal your napkin if you look away.', status: 'Available for cuddles' },
  { name: 'Ziggy', species: 'bird', emoji: '🐦', color: '#7fa8c9', breed: 'Parakeet', age: '3 yrs', note: "Knows one word: \u2018biscotti\u2019.", status: 'On the perch' },
  { name: 'Pepper', species: 'dog', emoji: '🐶', color: '#8a7568', breed: 'French Bulldog', age: '5 yrs', note: 'Professional greeter, snores loudly.', status: 'Greeting guests' },
  { name: 'Marmalade', species: 'cat', emoji: '🐱', color: '#d18a4a', breed: 'Orange tabby', age: '6 yrs', note: 'Senior staff member since 2021.', status: 'Available for cuddles' },
];

const MENU = {
  Drinks: [
    { item: 'House latte', price: '$4.50' },
    { item: 'Pour-over', price: '$3.75' },
    { item: 'Golden milk chai', price: '$4.25' },
    { item: 'Pup cup', price: 'Free with any pet visit' },
  ],
  Bakes: [
    { item: 'Almond croissant', price: '$3.95' },
    { item: 'Cat-shaped shortbread', price: '$2.50' },
    { item: 'Blueberry scone', price: '$3.25' },
  ],
  'Pet treats': [
    { item: 'Salmon bites (cats)', price: '$2.00' },
    { item: 'Peanut butter biscuit (dogs)', price: '$1.75' },
  ],
};

const BOOKINGS = [
  { time: '10:00 AM', name: 'Priya S.', detail: 'Cuddle session with Biscuit', spot: 'Table 4' },
  { time: '11:30 AM', name: 'Alex R.', detail: 'Birthday meetup — bring your own pet', spot: 'Table 2' },
  { time: '1:00 PM', name: 'Group booking', detail: "Kids' pet story hour", spot: 'Reading nook' },
  { time: '3:30 PM', name: 'Jordan K.', detail: 'Quiet hour with Nimbus', spot: 'Window seat' },
];

function renderHero() {
  document.getElementById('heroTagline').textContent = CAFE.tagline;
  document.getElementById('chipAddress').textContent = '📍 ' + CAFE.address;
  document.getElementById('chipHours').textContent = '🕐 ' + CAFE.hours;
  document.getElementById('chipPhone').textContent = '📞 ' + CAFE.phone;
}

function renderPetGallery() {
  const grid = document.getElementById('petGrid');
  grid.innerHTML = PETS.map((p) => `
    <div class="pet-card">
      <div class="pet-avatar" style="background:${p.color}33;">${p.emoji}</div>
      <h4>${p.name}</h4>
      <div class="pet-meta">${p.breed} · ${p.age}</div>
      <div class="pet-note">${p.note}</div>
      <span class="pet-status">${p.status}</span>
    </div>
  `).join('');
}

function renderMenu() {
  const wrap = document.getElementById('menuGroups');
  wrap.innerHTML = Object.entries(MENU).map(([group, items]) => `
    <div class="menu-group">
      <h4>${group}</h4>
      ${items.map((i) => `<div class="menu-row"><span>${i.item}</span><span class="price">${i.price}</span></div>`).join('')}
    </div>
  `).join('');
}

function renderBookings() {
  const body = document.getElementById('bookingsBody');
  body.innerHTML = BOOKINGS.map((b) => `
    <tr><td>${b.time}</td><td>${b.name}</td><td>${b.detail}</td><td>${b.spot}</td></tr>
  `).join('');
}

function renderStaticContent() {
  renderHero();
  renderPetGallery();
  renderMenu();
  renderBookings();
}
