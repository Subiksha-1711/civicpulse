export const CATEGORIES = [
  'Roads',
  'Electricity',
  'Garbage',
  'Water & Drainage',
  'Street Lights',
  'Public Safety',
  'Traffic',
  'Environment',
  'Other',
];

export const SUBCATEGORIES = {
  Roads: ['Pothole', 'Broken Pavement', 'Road Damage', 'Missing Signage'],
  Electricity: ['Power Outage', 'Exposed Wiring', 'Transformer Issue', 'Billing Issue'],
  Garbage: ['Not Collected', 'Overflowing Bin', 'Illegal Dumping', 'Missing Bin'],
  'Water & Drainage': ['Waterlogging', 'Pipe Leakage', 'No Water Supply', 'Sewage Overflow'],
  'Street Lights': ['Light Not Working', 'Flickering Light', 'Missing Pole', 'Damaged Fixture'],
  'Public Safety': ['Open Manhole', 'Unsafe Construction', 'Stray Animals', 'Broken Railing'],
  Traffic: ['Signal Malfunction', 'Illegal Parking', 'Congestion', 'Damaged Signage'],
  Environment: ['Tree Fallen', 'Air Pollution', 'Noise Pollution', 'Water Pollution'],
  Other: ['General Complaint', 'Suggestion', 'Miscellaneous'],
};

export const STATUSES = ['Open', 'In Progress', 'Resolved'];
export const PRIORITIES = ['Low', 'Medium', 'High'];

export const LOCATIONS = [
  { name: 'MG Road', lat: 11.0168, lng: 76.9558 },
  { name: 'City Center', lat: 11.0041, lng: 76.9615 },
  { name: 'Baner Road', lat: 11.0268, lng: 76.9458 },
  { name: 'Shankar Nagar', lat: 11.0098, lng: 76.9702 },
  { name: 'New Town', lat: 11.0301, lng: 76.9812 },
  { name: 'Civil Lines', lat: 11.0155, lng: 76.9490 },
  { name: 'Green Park', lat: 10.9998, lng: 76.9550 },
  { name: 'Ram Nagar', lat: 11.0210, lng: 76.9630 },
  { name: 'Lake View', lat: 11.0320, lng: 76.9700 },
  { name: 'Station Road', lat: 11.0080, lng: 76.9380 },
];

export const STATUS_COLORS = {
  Open: '#ef4444',
  'In Progress': '#f59e0b',
  Resolved: '#22c55e',
};

export const PRIORITY_COLORS = {
  Low: '#22c55e',
  Medium: '#f59e0b',
  High: '#ef4444',
};

export const ISSUE_IMAGES = [
  'https://images.unsplash.com/photo-1594818379496-da1e345b0ded?w=600&q=80',
  'https://images.unsplash.com/photo-1615874959474-d609969a20ed?w=600&q=80',
  'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&q=80',
  'https://images.unsplash.com/photo-1610105080562-9f1e3d76e6ac?w=600&q=80',
  'https://images.unsplash.com/photo-1573497491765-dccce02b29df?w=600&q=80',
  'https://images.unsplash.com/photo-1567359781514-3b964e2b04d6?w=600&q=80',
  'https://images.unsplash.com/photo-1621905252472-943afaa20e20?w=600&q=80',
  'https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=600&q=80',
  'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=600&q=80',
  'https://images.unsplash.com/photo-1590496793929-36417d3117de?w=600&q=80',
  'https://images.unsplash.com/photo-1580795479225-c50ab8c3348d?w=600&q=80',
  'https://images.unsplash.com/photo-1610030181087-540e02f2f9c9?w=600&q=80',
];
