import { CATEGORIES, SUBCATEGORIES, STATUSES, PRIORITIES, LOCATIONS, ISSUE_IMAGES } from './constants';

const TITLES = {
  Roads: [
    'Large pothole causing traffic problems',
    'Deep pothole damaging vehicles',
    'Road surface heavily cracked',
    'Broken pavement near market',
    'Road caved in after rain',
  ],
  Electricity: [
    'Frequent power outages in the area',
    'Exposed wiring near school',
    'Transformer sparking at night',
    'Streetlight pole leaking current',
  ],
  Garbage: [
    'Garbage not collected for a week',
    'Overflowing bin attracting stray animals',
    'Illegal dumping near residential area',
    'Missing garbage bin at junction',
  ],
  'Water & Drainage': [
    'Severe waterlogging after rain',
    'Pipe leakage flooding street',
    'No water supply for 3 days',
    'Sewage overflow near houses',
  ],
  'Street Lights': [
    'Street light not working for weeks',
    'Flickering street light at junction',
    'Missing light pole after storm',
    'Damaged light fixture hanging loose',
  ],
  'Public Safety': [
    'Open manhole cover, safety risk',
    'Unsafe construction debris on footpath',
    'Stray dogs causing safety concerns',
    'Broken railing near canal',
  ],
  Traffic: [
    'Traffic signal not functioning',
    'Illegal parking blocking road',
    'Heavy congestion during peak hours',
    'Damaged traffic signage confusing drivers',
  ],
  Environment: [
    'Large tree fallen blocking road',
    'Heavy air pollution from factory',
    'Excessive noise pollution at night',
    'Water body contaminated with waste',
  ],
  Other: ['General complaint about civic maintenance', 'Suggestion to improve public park', 'Miscellaneous civic issue reported'],
};

const REPORTERS = [
  'Arjun Sharma', 'Priya Patel', 'Rahul Verma', 'Sneha Iyer', 'Vikram Singh',
  'Ananya Reddy', 'Karthik Nair', 'Divya Menon', 'Rohan Gupta', 'Meera Krishnan',
  'Aditya Rao', 'Kavya Pillai', 'Sanjay Kumar', 'Nisha Joshi', 'Vivek Chandran',
];

function seededRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

function pick(rand, arr) {
  return arr[Math.floor(rand() * arr.length)];
}

function timeAgo(hoursAgo) {
  return new Date(Date.now() - hoursAgo * 60 * 60 * 1000).toISOString();
}

function generateIssues(count = 45) {
  const rand = seededRandom(42);
  const issues = [];
  const clusters = {};

  for (let i = 0; i < count; i++) {
    const category = pick(rand, CATEGORIES);
    const subcategory = pick(rand, SUBCATEGORIES[category]);
    const location = pick(rand, LOCATIONS);
    const status = pick(rand, STATUSES);
    const priority = pick(rand, PRIORITIES);
    const title = pick(rand, TITLES[category] || TITLES.Other);
    const hoursAgo = Math.floor(rand() * 24 * 30) + 1;
    const relatedComplaints = Math.floor(rand() * 10) + 1;
    const clusterKey = `${category}-${location.name}`;
    if (!clusters[clusterKey]) {
      clusters[clusterKey] = `CLU-${Object.keys(clusters).length + 1}`;
    }

    issues.push({
      id: `ISSUE-2024-${String(i + 1).padStart(3, '0')}`,
      title: `${title} on ${location.name}`,
      description: `${title} reported near ${location.name}. This issue is causing inconvenience to residents and commuters in the area. Immediate attention from the concerned department is requested to resolve this civic issue.`,
      category,
      subcategory,
      location: location.name,
      latitude: location.lat + (rand() - 0.5) * 0.01,
      longitude: location.lng + (rand() - 0.5) * 0.01,
      status,
      priority,
      reportedBy: pick(rand, REPORTERS),
      reportedAt: timeAgo(hoursAgo),
      image: ISSUE_IMAGES[i % ISSUE_IMAGES.length],
      images: [ISSUE_IMAGES[i % ISSUE_IMAGES.length], ISSUE_IMAGES[(i + 3) % ISSUE_IMAGES.length]],
      relatedComplaints,
      clusterId: clusters[clusterKey],
      aiConfidence: Math.floor(85 + rand() * 14),
    });
  }

  return issues.sort((a, b) => new Date(b.reportedAt) - new Date(a.reportedAt));
}

export const MOCK_ISSUES = generateIssues(45);

export const ACTIVITY_LOG = [
  { id: 1, text: 'Issue #ISSUE-2024-001 updated to In Progress', hoursAgo: 2 },
  { id: 2, text: 'New issue reported: Garbage not collected', hoursAgo: 5 },
  { id: 3, text: 'Issue #ISSUE-2024-015 marked as Resolved', hoursAgo: 24 },
  { id: 4, text: 'New issue reported: Broken street light', hoursAgo: 48 },
  { id: 5, text: 'AI clustered 8 complaints into Issue #ISSUE-2024-001', hoursAgo: 50 },
];

export const STATS = {
  issuesReported: '150+',
  issuesResolved: 24,
  activeCitizens: '5K+',
  aiAccuracy: '98%',
};
