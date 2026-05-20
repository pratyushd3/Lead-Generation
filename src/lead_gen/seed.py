"""Demo data: a mock prospect pool for the discovery agent + sample buyers/ICPs."""
from __future__ import annotations

PROSPECT_POOL: list[dict] = [
    {
        "company_name": "Northwind Robotics",
        "website": "https://northwind-robotics.com",
        "industry": "Robotics",
        "employee_count": 85,
        "location": "Boston, MA",
        "description": "Warehouse automation and AMR robotics for mid-market 3PLs.",
        "tags": ["warehouse", "automation", "logistics", "AI"],
    },
    {
        "company_name": "Brightline Analytics",
        "website": "https://brightline.io",
        "industry": "SaaS",
        "employee_count": 42,
        "location": "Austin, TX",
        "description": "Customer analytics platform for B2B SaaS revenue teams.",
        "tags": ["analytics", "SaaS", "revenue", "data"],
    },
    {
        "company_name": "Harborlight Health",
        "website": "https://harborlight.health",
        "industry": "Healthtech",
        "employee_count": 130,
        "location": "Seattle, WA",
        "description": "Telehealth platform for chronic-care management.",
        "tags": ["healthtech", "telehealth", "chronic care"],
    },
    {
        "company_name": "Granite Peak Logistics",
        "website": "https://granitepeak.co",
        "industry": "Logistics",
        "employee_count": 220,
        "location": "Denver, CO",
        "description": "Regional freight brokerage scaling its dispatch operations.",
        "tags": ["logistics", "freight", "operations"],
    },
    {
        "company_name": "Lumen FinOps",
        "website": "https://lumenfinops.com",
        "industry": "SaaS",
        "employee_count": 28,
        "location": "Remote",
        "description": "Cloud cost optimization for engineering-led SaaS startups.",
        "tags": ["finops", "SaaS", "cloud", "cost"],
    },
    {
        "company_name": "Cedarwood Manufacturing",
        "website": "https://cedarwoodmfg.com",
        "industry": "Manufacturing",
        "employee_count": 540,
        "location": "Grand Rapids, MI",
        "description": "Custom furniture manufacturer modernizing its supply chain.",
        "tags": ["manufacturing", "supply chain", "ERP"],
    },
    {
        "company_name": "Skyline Property Group",
        "website": "https://skylinepg.com",
        "industry": "Real Estate",
        "employee_count": 95,
        "location": "Miami, FL",
        "description": "Multi-family property management firm investing in proptech.",
        "tags": ["real estate", "proptech", "property management"],
    },
    {
        "company_name": "Mosaic Learning",
        "website": "https://mosaiclearning.edu",
        "industry": "EdTech",
        "employee_count": 60,
        "location": "Toronto, ON",
        "description": "K-12 personalized-learning platform with AI tutors.",
        "tags": ["edtech", "AI", "K-12"],
    },
]


SAMPLE_BUYERS: list[dict] = [
    {"name": "Pipeline Pro Agency", "email": "ops@pipelinepro.example"},
]


SAMPLE_ICPS: list[dict] = [
    {
        "name": "Mid-market SaaS RevOps",
        "industry": "SaaS",
        "company_size": "11-200",
        "geography": "North America",
        "pain_points": "fragmented revenue data, slow lead-to-cash cycles",
        "keywords": ["analytics", "revenue", "SaaS"],
    },
    {
        "name": "Logistics ops modernization",
        "industry": "Logistics",
        "company_size": "50-500",
        "geography": "US",
        "pain_points": "manual dispatch, fragmented carrier data",
        "keywords": ["logistics", "operations", "automation"],
    },
]
