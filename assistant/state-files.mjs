// Source: states/registry.json. Tests prevent drift when the public guide adds a state.
export const STATES=Object.freeze({
  "OH": "Ohio",
  "PA": "Pennsylvania",
  "NY": "New York",
  "MI": "Michigan",
  "KY": "Kentucky",
  "UT": "Utah",
  "IN": "Indiana",
  "WV": "West Virginia",
  "TX": "Texas",
  "FL": "Florida",
  "CA": "California",
  "VA": "Virginia",
  "NC": "North Carolina"
});
export const STATE_FILES=Object.freeze({
  "OH": [
    "prototype-data.json",
    "data/public/ohio-county-veterans-offices.json"
  ],
  "PA": [
    "data/public/pennsylvania-resources.json",
    "data/public/pennsylvania-county-veterans-offices.json"
  ],
  "NY": [
    "data/public/new-york-resources.json",
    "data/public/new-york-county-veterans-offices.json"
  ],
  "MI": [
    "data/public/michigan-resources.json",
    "data/public/michigan-county-veterans-offices.json"
  ],
  "KY": [
    "data/public/kentucky-resources.json",
    "data/public/kentucky-county-veterans-offices.json"
  ],
  "UT": [
    "data/public/utah-resources.json",
    "data/public/utah-county-veterans-offices.json"
  ],
  "IN": [
    "data/public/indiana-resources.json",
    "data/public/indiana-county-veterans-offices.json"
  ],
  "WV": [
    "data/public/west-virginia-resources.json",
    "data/public/west-virginia-county-veterans-offices.json"
  ],
  "TX": [
    "data/public/texas-resources.json",
    "data/public/texas-county-veterans-offices.json"
  ],
  "FL": [
    "data/public/florida-resources.json",
    "data/public/florida-county-veterans-offices.json"
  ],
  "CA": [
    "data/public/california-resources.json",
    "data/public/california-county-veterans-offices.json"
  ],
  "VA": [
    "data/public/virginia-resources.json",
    "data/public/virginia-county-veterans-offices.json"
  ],
  "NC": [
    "data/public/north-carolina-resources.json",
    "data/public/north-carolina-county-veterans-offices.json"
  ]
});
export const localityLabel=row=>row?(row.county_type==="independent_city"?row.county:row.county+" County"):"";
