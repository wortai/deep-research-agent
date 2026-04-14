"""
Standalone test of the improved report generation pipeline.

Tests the full flow with REAL LLM calls:
1. Design skill selection (with LLM call)
2. Design instructions generation (with LLM call)
3. Chapter generation (with LLM call)

This is standalone — no Writer class imports, no graph state import.
"""

import sys
import os
import json
import uuid
import asyncio
import re

# Add project path
sys.path.insert(0, "/Users/choclate/Desktop/WORT/deep-research-agent")

# Import only the prompt generation functions (pure string generators, no LLM calls)
from writer.prompts_utils.writer_prompts import (
    generate_chapter_prompt,
    choose_design_skill_prompt,
    generate_design_instructions_prompt,
    get_available_design_skills,
    DesignSkillSelection,
    DesignInstructionsResult,
)
from llms import LlmsHouse

# ============================================================
# RICH MOCK RESEARCH DATA
# ============================================================


def sid():
    return str(uuid.uuid4())[:12]


# --- Finance: Tesla Stock Analysis 2024 ---
tesla_sections = [
    {
        "section_id": sid(),
        "section_content": """# Tesla Q1-Q4 2024 Financial Results

Tesla reported record revenue of $97.7 billion for FY2024, up 19% year-over-year from $81.5 billion in FY2023. The revenue breakdown by segment shows:

AUTOMOTIVE REVENUE:
- Q1 2024: $21.3 billion (vs $23.3 billion Q1 2023, -9% YoY)
- Q2 2024: $21.8 billion (vs $24.9 billion Q2 2023, -12% YoY)
- Q3 2024: $22.5 billion (vs $23.4 billion Q3 2023, -4% YoY)
- Q4 2024: $28.1 billion (vs $25.2 billion Q4 2023, +12% YoY)
- Full Year 2024: $93.7 billion automotive revenue

The automotive revenue decline in H1 2024 was driven by price cuts averaging 20% across the Model 3 and Model Y lineup in response to increased competition from BYD and other Chinese EV manufacturers. However, Q4 saw a strong recovery driven by Cybertruck deliveries ramping up and the refreshed Model Y launch in China.

ENERGY GENERATION & STORAGE:
- Q1 2024: $1.6 billion (+7% YoY)
- Q2 2024: $2.4 billion (+100% YoY)
- Q3 2024: $2.4 billion (+52% YoY)
- Q4 2024: $3.5 billion (+120% YoY)
- Full Year 2024: $9.9 billion (up 73% YoY)

Energy storage deployments reached a record 31.4 GWh in 2024, driven by Megapack demand from utilities. This segment now represents 10% of total revenue, up from 6% in 2023.

PROFITABILITY METRICS:
- Gross Margin (automotive): 17.6% (down from 23.8% in 2023)
- Operating Margin: 9.2% (down from 16.8% in 2023)
- Net Income: $12.6 billion (down from $15.0 billion in 2023)
- Free Cash Flow: $4.4 billion (down from $7.5 billion in 2023)
- EPS (diluted): $3.12 (down from $4.07 in 2023)

The margin compression was primarily due to aggressive pricing strategy, increased R&D spend on next-gen platform ($3.7 billion, up 29%), and Cybertruck production ramp costs. However, operating expenses as a percentage of revenue improved to 7.8% from 8.2%.

DELIVERIES:
- Q1 2024: 386,810 vehicles (missed estimates of 449,000)
- Q2 2024: 443,956 vehicles
- Q3 2024: 462,890 vehicles
- Q4 2024: 495,570 vehicles (record quarter)
- Full Year 2024: 1.79 million vehicles (up 1% YoY)

Source: Tesla Q4 2024 Earnings Report — https://ir.tesla.com/press-release/tesla-releases-fourth-quarter-and-full-year-2024-financial-results
Source: Tesla Investor Relations — https://ir.tesla.com
""",
    },
    {
        "section_id": sid(),
        "section_content": """# Tesla Stock Valuation, PE Ratio, and Analyst Price Targets

Tesla's stock (TSLA) traded in a wide range during 2024:
- 52-week low: $138.80 (April 2024)
- 52-week high: $488.54 (December 2024)
- Year-end 2024 close: $379.28

VALUATION METRICS (as of Dec 31, 2024):
- Market Cap: $1.21 trillion
- P/E Ratio (TTM): 121.5x (vs S&P 500 average of 24.3x)
- Forward P/E: 95.2x (based on consensus 2025 EPS of $3.98)
- Price-to-Sales: 12.4x
- EV/EBITDA: 68.3x
- Price-to-Book: 14.8x

The premium valuation reflects investor expectations for:
1. Full Self-Driving (FSD) monetization — currently at $8,000 per vehicle, expanding to subscription model at $199/month
2. Robotaxi network launch — targeted for 2026, estimated TAM of $500 billion+ by 2030
3. Optimus humanoid robot — prototype stage, potential $10+ trillion TAM per Musk
4. Energy business scaling — 31.4 GWh deployed, targeting 100+ GWh by 2026

ANALYST PRICE TARGETS (as of Jan 2025):
- Goldman Sachs: $345 (Neutral) — "Valuation already prices in significant FSD adoption"
- Morgan Stanley: $430 (Overweight) — "Robotaxi optionality worth $200+ per share"
- Wedbush: $515 (Outperform) — "AI on wheels story just beginning"
- JPMorgan: $115 (Underweight) — "Valuation disconnected from automotive fundamentals"
- Bank of America: $220 (Underperform) — "Competition intensifying, margins under pressure"

Consensus Price Target: $285 (implying 25% downside from current levels)
Buy ratings: 14 | Hold: 12 | Sell: 8

INSTITUTIONAL OWNERSHIP:
- Vanguard Group: 7.2%
- BlackRock: 5.8%
- State Street: 3.1%
- Elon Musk: ~13% (including options)
- Short interest: 3.1% of float

Source: Bloomberg Terminal data, January 2025 — https://www.bloomberg.com/quote/TSLA:US
Source: Yahoo Finance analyst estimates — https://finance.yahoo.com/quote/TSLA/analysis/
""",
    },
]

# --- Math: Eigenvalues and Eigenvectors ---
math_sections = [
    {
        "section_id": sid(),
        "section_content": """# Mathematical Definition and Theory of Eigenvalues

EIGENVALUES AND EIGENVECTORS — DEFINITION:

Let A be an n×n square matrix. A nonzero vector v is called an eigenvector of A if there exists a scalar λ (lambda) such that:

Av = λv

The scalar λ is called the eigenvalue corresponding to the eigenvector v. Geometrically, this means that the linear transformation represented by A stretches (or compresses) the vector v by a factor of λ without changing its direction. If λ is negative, the direction is reversed. If λ = 0, the vector is mapped to the zero vector.

THE CHARACTERISTIC EQUATION:

To find the eigenvalues of A, we rearrange the equation:
Av = λv
Av - λv = 0
(A - λI)v = 0

For a nonzero solution v to exist, the matrix (A - λI) must be singular, meaning its determinant is zero:

det(A - λI) = 0

This equation is called the characteristic equation of A. The left-hand side, det(A - λI), is a polynomial in λ of degree n, called the characteristic polynomial. The eigenvalues are the roots of this polynomial.

EXAMPLE — 2×2 Matrix:

Consider the matrix:
A = [4  1]
    [2  3]

The characteristic equation is:
det(A - λI) = det([4-λ   1  ]) = (4-λ)(3-λ) - 2 = λ² - 7λ + 10 = 0
               [2    3-λ]

Factoring: (λ - 5)(λ - 2) = 0

So the eigenvalues are λ₁ = 5 and λ₂ = 2.

For λ₁ = 5:
(A - 5I)v = 0
[-1  1][x]   [0]
[2  -2][y] = [0]

This gives -x + y = 0, so y = x. The eigenvector is v₁ = [1, 1]ᵀ (or any scalar multiple).

For λ₂ = 2:
(A - 2I)v = 0
[2  1][x]   [0]
[2  1][y] = [0]

This gives 2x + y = 0, so y = -2x. The eigenvector is v₂ = [1, -2]ᵀ.

KEY THEOREMS:

Theorem 1 (Trace): The sum of eigenvalues equals the trace of A (sum of diagonal elements).
Proof: The characteristic polynomial det(A - λI) = (-1)ⁿλⁿ + tr(A)·(-1)ⁿ⁻¹λⁿ⁻¹ + ... + det(A). By Vieta's formulas, the sum of roots equals the coefficient of λⁿ⁻¹ divided by the coefficient of λⁿ, which is tr(A).

Theorem 2 (Determinant): The product of eigenvalues equals det(A).
Proof: Setting λ = 0 in det(A - λI) gives det(A) = product of all eigenvalues.

Theorem 3 (Spectral Theorem): If A is symmetric (A = Aᵀ), then all eigenvalues are real and eigenvectors corresponding to distinct eigenvalues are orthogonal.

Theorem 4 (Cayley-Hamilton): Every square matrix satisfies its own characteristic equation. If p(λ) = det(A - λI), then p(A) = 0.

Source: Strang, G. (2016). "Introduction to Linear Algebra," 5th Edition. Wellesley-Cambridge Press.
Source: Axler, S. (2015). "Linear Algebra Done Right," 3rd Edition. Springer.
""",
    },
    {
        "section_id": sid(),
        "section_content": """# Computation Methods and Real-World Applications

COMPUTATIONAL METHODS:

For small matrices (n ≤ 4), eigenvalues can be found analytically by solving the characteristic polynomial. For larger matrices, numerical methods are required:

1. POWER ITERATION — Finds the dominant (largest magnitude) eigenvalue:
   - Start with random vector x₀
   - Iterate: xₖ₊₁ = Axₖ / ||Axₖ||
   - The eigenvalue estimate: λ ≈ xₖᵀAxₖ
   - Convergence rate: |λ₂/λ₁|ᵏ where λ₁ is dominant, λ₂ is second-largest
   - Cost per iteration: O(n²) for dense matrices

2. QR ALGORITHM — Finds all eigenvalues:
   - Factorize A = QR (QR decomposition)
   - Set A₁ = RQ
   - Repeat: Aₖ = QₖRₖ, Aₖ₊₁ = RₖQₖ
   - The diagonal of Aₖ converges to eigenvalues
   - Cost: O(n³) per iteration, typically converges in O(n) iterations
   - This is the method used in NumPy's np.linalg.eig()

3. JACOBI METHOD — For symmetric matrices:
   - Apply successive Givens rotations to zero out off-diagonal elements
   - Guaranteed convergence for symmetric matrices
   - Particularly stable numerically

REAL-WORLD APPLICATIONS:

1. GOOGLE PAGERANK ALGORITHM:
   Google's original PageRank algorithm models the web as a directed graph. The PageRank vector is the principal eigenvector of the Google matrix G = αS + (1-α)evᵀ, where S is the stochastic link matrix, α ≈ 0.85 is the damping factor, and v is the teleportation vector. The dominant eigenvalue is λ = 1, and the corresponding eigenvector gives the importance score of each webpage. For the web's ~13 billion pages, the power iteration method is used, converging in approximately 50-100 iterations.

2. PRINCIPAL COMPONENT ANALYSIS (PCA):
   In machine learning, PCA uses the eigendecomposition of the covariance matrix Σ = XᵀX/n to find the directions of maximum variance in data. The eigenvectors are the principal components, and the eigenvalues represent the variance captured by each component. If λ₁ ≥ λ₂ ≥ ... ≥ λₙ are the eigenvalues, then the fraction of total variance explained by the first k components is (λ₁ + ... + λₖ) / (λ₁ + ... + λₙ).

3. STRUCTURAL ENGINEERING — VIBRATION ANALYSIS:
   The natural frequencies of a structure are the square roots of the eigenvalues of the generalized eigenvalue problem Kφ = ω²Mφ, where K is the stiffness matrix, M is the mass matrix, ω is the angular frequency, and φ is the mode shape. The Tacoma Narrows Bridge collapse (1940) was caused by resonance at a natural frequency that matched wind-induced oscillations.

4. QUANTUM MECHANICS:
   In quantum mechanics, observable quantities are represented by Hermitian operators. The possible measurement outcomes are the eigenvalues of the operator, and the system's state after measurement collapses to the corresponding eigenvector. The Schrödinger equation Hψ = Eψ is itself an eigenvalue equation, where H is the Hamiltonian operator, ψ is the wave function, and E is the energy eigenvalue.

Source: Page, L., et al. (1999). "The PageRank Citation Ranking: Bringing Order to the Web." Stanford InfoLab.
Source: Jolliffe, I.T. (2002). "Principal Component Analysis," 2nd Edition. Springer.
""",
    },
]

# --- Coding: REST API Design ---
coding_sections = [
    {
        "section_id": sid(),
        "section_content": """# REST API Resource Naming Conventions and HTTP Methods

RESOURCE NAMING:

REST APIs should use nouns (not verbs) in URL paths to represent resources. The HTTP method indicates the action.

GOOD:
  GET    /users           — List all users
  GET    /users/123       — Get user 123
  POST   /users           — Create a new user
  PUT    /users/123       — Replace user 123 entirely
  PATCH  /users/123       — Partially update user 123
  DELETE /users/123       — Delete user 123

BAD:
  GET    /getUsers
  POST   /createUser
  POST   /updateUser/123

NESTED RESOURCES:
Use nested paths for resources that belong to a parent:
  GET    /users/123/orders          — List orders for user 123
  GET    /users/123/orders/456      — Get order 456 for user 123
  POST   /users/123/orders          — Create order for user 123

But don't nest more than 2 levels deep. If you need deeper relationships, use query parameters:
  GET    /orders/456/items?include=product,category

COLLECTION vs. RESOURCE:
- Plural nouns for collections: /users, /orders, /products
- Singular for single resource lookups (via ID in path): /users/123
- Sub-resources for relationships: /users/123/orders

HTTP METHODS — SEMANTICS:

| Method  | Idempotent | Safe | Body?   | Use Case                    |
|---------|-----------|------|---------|-----------------------------|
| GET     | Yes       | Yes  | No      | Read/retrieve resource      |
| POST    | No        | No   | Yes     | Create new resource         |
| PUT     | Yes       | No   | Yes     | Full replacement            |
| PATCH   | No*       | No   | Yes     | Partial update              |
| DELETE  | Yes       | No   | Optional| Remove resource             |

*PATCH is technically not idempotent by spec, but should be implemented idempotently in practice.

REQUEST/RESPONSE EXAMPLE:

POST /api/v1/users
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "admin"
}

Response — 201 Created:
{
  "id": "usr_abc123",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "admin",
  "createdAt": "2024-01-15T10:30:00Z",
  "_links": {
    "self": { "href": "/api/v1/users/usr_abc123" },
    "orders": { "href": "/api/v1/users/usr_abc123/orders" }
  }
}

Source: Google API Design Guide — https://cloud.google.com/apis/design
Source: Microsoft REST API Guidelines — https://github.com/microsoft/api-guidelines
""",
    },
    {
        "section_id": sid(),
        "section_content": """# API Versioning Strategies, Error Handling, and Pagination Patterns

VERSIONING STRATEGIES:

1. URL PATH VERSIONING (Most Common):
   GET /api/v1/users
   GET /api/v2/users
   Pros: Simple, explicit, cacheable
   Cons: Clutters URLs, encourages version proliferation

2. HEADER VERSIONING:
   GET /api/users
   Header: API-Version: 2024-01-15
   Pros: Clean URLs, date-based versioning
   Cons: Less discoverable, harder to test in browser

3. QUERY PARAMETER VERSIONING:
   GET /api/users?version=2
   Pros: Easy to test
   Cons: Can be ignored by clients accidentally

RECOMMENDATION: Use URL path versioning for major/breaking changes (v1 → v2), and additive changes (new optional fields, new endpoints) within the same version without incrementing.

ERROR HANDLING — STANDARD RESPONSE FORMAT:

Use consistent error response structure across all endpoints:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request body contains invalid fields",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "code": "INVALID_FORMAT"
      },
      {
        "field": "age",
        "message": "Must be between 18 and 120",
        "code": "OUT_OF_RANGE"
      }
    ],
    "requestId": "req_xyz789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

HTTP STATUS CODES — WHEN TO USE EACH:

| Status | Meaning           | When to Use                                    |
|--------|-------------------|------------------------------------------------|
| 200    | OK                | Successful GET, PUT, PATCH                     |
| 201    | Created           | Successful POST (new resource created)          |
| 204    | No Content        | Successful DELETE                               |
| 400    | Bad Request       | Invalid request body, missing required fields   |
| 401    | Unauthorized      | Missing or invalid authentication token         |
| 403    | Forbidden         | Authenticated but no permission                 |
| 404    | Not Found         | Resource doesn't exist                          |
| 409    | Conflict          | Duplicate resource, version conflict            |
| 422    | Unprocessable     | Valid JSON but semantic errors (validation)     |
| 429    | Too Many Requests | Rate limit exceeded                             |
| 500    | Internal Error    | Unexpected server error                         |

PAGINATION PATTERNS:

1. OFFSET-BASED (Simple but inefficient for large datasets):
   GET /api/v1/users?limit=20&offset=40
   Response:
   {
     "data": [...],
     "pagination": {
       "total": 1247,
       "limit": 20,
       "offset": 40,
       "hasMore": true
     }
   }

2. CURSOR-BASED (Recommended for large datasets):
   GET /api/v1/users?limit=20&cursor=eyJpZCI6MTIzfQ==
   Response:
   {
     "data": [...],
     "pagination": {
       "nextCursor": "eyJpZCI6MTQzfQ==",
       "hasMore": true
     }
   }

3. KEYSET PAGINATION (Best performance, no offset):
   GET /api/v1/users?limit=20&after_id=usr_123&sort=created_at
   Uses indexed columns for efficient range queries.

RATE LIMITING HEADERS:
Include these headers in every response:
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 847
  X-RateLimit-Reset: 1705312200

Source: Stripe API Reference — https://stripe.com/docs/api
Source: GitHub REST API — https://docs.github.com/en/rest
""",
    },
]

# --- General: Climate Change ---
climate_sections = [
    {
        "section_id": sid(),
        "section_content": """# Scientific Causes and Evidence of Climate Change

Climate change refers to long-term shifts in global temperatures and weather patterns. While natural climate variations have occurred throughout Earth's history, the current warming trend is unequivocally driven by human activities since the Industrial Revolution.

GREENHOUSE EFFECT:
The greenhouse effect is a natural process where certain gases in Earth's atmosphere trap heat from the sun. Without it, Earth's average temperature would be approximately -18°C instead of the current +15°C. However, human activities have intensified this effect by increasing the concentration of greenhouse gases (GHGs).

KEY GREENHOUSE GASES:
- Carbon Dioxide (CO₂): 76% of total GHG emissions. Primary sources: fossil fuel combustion (coal, oil, natural gas), deforestation, cement production. Pre-industrial level: 280 ppm. Current level (2024): 424 ppm — highest in at least 800,000 years.
- Methane (CH₄): 16% of emissions. 28x more potent than CO₂ over 100 years. Sources: agriculture (livestock), landfills, natural gas production.
- Nitrous Oxide (N₂O): 6% of emissions. 265x more potent than CO₂. Sources: fertilizer use, industrial processes.
- Fluorinated Gases: 2% of emissions. Thousands of times more potent. Sources: refrigerants, electronics manufacturing.

TEMPERATURE RECORD:
Global average temperature has risen by approximately 1.2°C above pre-industrial levels (1850-1900 baseline). The warming is not uniform:
- Land areas have warmed faster than oceans (1.6°C vs 0.9°C)
- The Arctic has warmed 3-4x faster than the global average (Arctic amplification)
- 2023 was the hottest year on record, surpassing 2016
- Each of the last 10 years (2014-2023) ranks among the 10 warmest on record

EVIDENCE OF CLIMATE CHANGE:
1. Sea level rise: 3.6mm/year (2006-2015 average), accelerating to 4.5mm/year currently. Total rise since 1900: ~20cm.
2. Ocean warming: The upper 2,000 meters of ocean have absorbed 90% of excess heat. Ocean heat content reached record levels in 2023.
3. Ice sheet loss: Greenland loses ~279 billion tons of ice per year. Antarctica loses ~148 billion tons per year.
4. Glacier retreat: 90% of glaciers worldwide are retreating. The Alps have lost 60% of their ice volume since 1900.
5. Ocean acidification: Ocean pH has decreased by 0.1 units (30% increase in acidity) since the Industrial Revolution.
6. Extreme weather: Heat waves, droughts, heavy precipitation events, and intense hurricanes have all increased in frequency and intensity.

Source: IPCC Sixth Assessment Report (AR6), 2023 — https://www.ipcc.ch/report/ar6/
Source: NASA Global Climate Change — https://climate.nasa.gov
Source: NOAA National Centers for Environmental Information — https://www.ncei.noaa.gov
""",
    },
    {
        "section_id": sid(),
        "section_content": """# Effects on Ecosystems, Economy, and Human Society

ECOSYSTEM IMPACTS:

Coral Reefs: At 1.5°C warming, 70-90% of coral reefs are projected to be lost. At 2°C, virtually all (>99%) coral reefs would disappear. Coral bleaching events have increased 5x since the 1980s.

Biodiversity: Approximately 1 million species face extinction, many within decades. Climate change is now the third-largest direct driver of biodiversity loss, after land/sea use change and direct exploitation. Species are shifting their ranges poleward at an average rate of 17 km per decade.

Arctic Ecosystems: Sea ice extent has declined by 13% per decade since 1979. Polar bear populations are declining as sea ice habitat shrinks. Permafrost thaw is releasing stored carbon, creating a positive feedback loop.

ECONOMIC IMPACTS:

The economic costs of climate change are enormous and growing:
- Global economic damages from extreme weather events: $313 billion in 2022 (up from $50 billion in 1990)
- Projected GDP impact at 2°C warming: 10-23% reduction in global GDP by 2100 (Swiss Re estimate)
- Cost of inaction vs. action: The Stern Review (2006) estimated the cost of inaction at 5-20% of global GDP annually, while mitigation costs would be approximately 1% of global GDP.
- Insurance losses from climate-related disasters have increased 7x since the 1970s.

HUMAN HEALTH:
- Heat-related deaths: Increased by 68% between 2000-2004 and 2017-2021 (WHO)
- Disease spread: Malaria, dengue, and other vector-borne diseases are expanding into new geographic areas as temperatures warm
- Air quality: Climate change worsens air pollution, contributing to 7 million premature deaths annually
- Food security: Crop yields for wheat, rice, and maize are projected to decline by 10-25% at 2°C warming, threatening food security for billions

WHAT CAN BE DONE:

MITIGATION (Reducing emissions):
1. Energy transition: Shift from fossil fuels to renewable energy (solar, wind, hydro, nuclear). Solar and wind now provide 14% of global electricity, up from 2% in 2010.
2. Electrification: Electric vehicles, heat pumps, electric industrial processes.
3. Energy efficiency: Building insulation, efficient appliances, LED lighting.
4. Carbon capture: Direct air capture, carbon capture and storage (CCS), nature-based solutions (reforestation, soil carbon).
5. Policy mechanisms: Carbon pricing (currently covers 23% of global emissions), emissions trading systems, renewable energy mandates.

ADAPTATION (Living with changes):
1. Infrastructure: Sea walls, flood defenses, heat-resistant buildings, drought-resistant crops.
2. Early warning systems: Currently only 50% of countries have adequate early warning systems.
3. Ecosystem-based adaptation: Mangrove restoration, urban green spaces, watershed management.

THE PARIS AGREEMENT:
Adopted in 2015 by 196 parties, the Paris Agreement aims to limit global warming to well below 2°C, preferably to 1.5°C, compared to pre-industrial levels. Current national pledges (NDCs) put the world on track for approximately 2.5-2.9°C of warming by 2100 — significantly above the 1.5°C target.

Source: IPCC AR6 Synthesis Report, 2023 — https://www.ipcc.ch/report/ar6/syr/
Source: World Meteorological Organization — https://public.wmo.int/en
Source: WHO Climate Change and Health — https://www.who.int/health-topics/climate-change
""",
    },
]

# ============================================================
# TEST SCENARIOS
# ============================================================

TEST_SCENARIOS = [
    {
        "name": "Finance — Tesla Stock Analysis 2024",
        "user_query": "Analyze Tesla's stock performance, financial metrics, and growth trajectory for 2024",
        "planner_queries": [
            {
                "query_num": 1,
                "query": "Tesla Q1-Q4 2024 financial results and revenue breakdown",
            },
            {
                "query_num": 2,
                "query": "Tesla stock valuation, PE ratio, and analyst price targets",
            },
        ],
        "sections": tesla_sections,
        "expected_skill": "finance_corporate.md",
    },
    {
        "name": "Math — Eigenvalues and Eigenvectors",
        "user_query": "Explain eigenvalues and eigenvectors — definitions, computation, and applications",
        "planner_queries": [
            {
                "query_num": 1,
                "query": "Mathematical definition and theory of eigenvalues",
            },
            {
                "query_num": 2,
                "query": "Computation methods and real-world applications",
            },
        ],
        "sections": math_sections,
        "expected_skill": "math.md",
    },
    {
        "name": "Coding — REST API Design Best Practices",
        "user_query": "What are the best practices for designing RESTful APIs — resource naming, versioning, error handling, pagination",
        "planner_queries": [
            {
                "query_num": 1,
                "query": "REST API resource naming conventions and HTTP methods",
            },
            {
                "query_num": 2,
                "query": "API versioning strategies, error handling, and pagination patterns",
            },
        ],
        "sections": coding_sections,
        "expected_skill": "coding.md",
    },
    {
        "name": "General — Climate Change Overview",
        "user_query": "What is climate change — causes, effects, and what can be done about it",
        "planner_queries": [
            {
                "query_num": 1,
                "query": "Scientific causes and evidence of climate change",
            },
            {
                "query_num": 2,
                "query": "Effects on ecosystems, economy, and human society",
            },
        ],
        "sections": climate_sections,
        "expected_skill": "general_fallback.md",
    },
]

# ============================================================
# EVALUATION FUNCTIONS
# ============================================================


def evaluate_chapter_html(html_content, chapter_heading):
    """Evaluate generated chapter HTML against quality metrics."""
    results = {
        "chapter_heading": chapter_heading,
        "html_length": len(html_content),
        "metrics": {},
        "issues": [],
        "warnings": [],
        "passes": [],
    }

    # Check basic structure
    has_report_chapter = '<div class="report-chapter">' in html_content
    has_report_page = '<div class="report-page">' in html_content
    page_count = html_content.count('<div class="report-page">')
    has_h2 = "<h2" in html_content
    has_h3 = "<h3" in html_content

    results["metrics"]["has_report_chapter"] = has_report_chapter
    results["metrics"]["has_report_page"] = has_report_page
    results["metrics"]["page_count"] = page_count
    results["metrics"]["has_h2"] = has_h2
    results["metrics"]["has_h3"] = has_h3

    if not has_report_chapter:
        results["issues"].append("MISSING: <div class='report-chapter'> wrapper")
    if not has_report_page:
        results["issues"].append("MISSING: <div class='report-page'> containers")
    if page_count < 2:
        results["issues"].append(f"FAIL: Only {page_count} page(s), minimum is 2")
    else:
        results["passes"].append(f"OK: {page_count} report-page containers")

    # Check for SVG elements
    svg_count = html_content.count("<svg")
    results["metrics"]["svg_count"] = svg_count
    if svg_count > 0:
        svg_with_title = html_content.count("<title>")
        svg_with_desc = html_content.count("<desc>")
        results["metrics"]["svg_with_title"] = svg_with_title
        results["metrics"]["svg_with_desc"] = svg_with_desc
        if svg_with_title < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_with_title} SVG(s) missing <title>"
            )
        if svg_with_desc < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_with_desc} SVG(s) missing <desc>"
            )
        svg_with_viewbox = html_content.count("viewBox=")
        results["metrics"]["svg_with_viewbox"] = svg_with_viewbox
        if svg_with_viewbox < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_with_viewbox} SVG(s) missing viewBox"
            )
        # Check SVG is wrapped in overflow container
        svg_wrapped = html_content.count("overflow-x:auto")
        results["metrics"]["svg_wrapped"] = svg_wrapped
        if svg_wrapped < svg_count:
            results["warnings"].append(
                f"{svg_count - svg_wrapped} SVG(s) not wrapped in overflow-x:auto"
            )
        results["passes"].append(f"OK: {svg_count} SVG element(s)")

    # Check for Charts.css
    has_charts_css = 'class="charts-css' in html_content
    results["metrics"]["has_charts_css"] = has_charts_css
    if has_charts_css:
        if "show-labels" not in html_content:
            results["warnings"].append("Charts.css table missing show-labels class")
        if "show-data" not in html_content:
            results["warnings"].append("Charts.css table missing show-data class")
        if "<caption>" not in html_content:
            results["warnings"].append("Charts.css table missing <caption>")

    # Check for tables
    table_count = html_content.count("<table")
    results["metrics"]["table_count"] = table_count

    # Check for inline styles
    inline_style_count = html_content.count('style="')
    results["metrics"]["inline_style_count"] = inline_style_count
    if inline_style_count < 5:
        results["warnings"].append(
            f"Only {inline_style_count} inline styles — may not be following design instructions"
        )

    # Check for citations/links
    link_count = html_content.count("<a href=")
    results["metrics"]["citation_count"] = link_count
    if link_count == 0:
        results["warnings"].append("No citations/links found")
    else:
        results["passes"].append(f"OK: {link_count} citation(s)")

    # Check for unclosed tags
    open_divs = html_content.count("<div")
    close_divs = html_content.count("</div>")
    if open_divs != close_divs:
        results["issues"].append(
            f"MISMATCH: {open_divs} opening <div> vs {close_divs} closing </div>"
        )
    else:
        results["passes"].append(f"OK: All divs properly closed ({open_divs} pairs)")

    # Check for content depth
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html_content, re.DOTALL)
    total_words = sum(len(p.split()) for p in paragraphs)
    results["metrics"]["paragraph_count"] = len(paragraphs)
    results["metrics"]["total_words"] = total_words
    if total_words < 300:
        results["issues"].append(f"LOW CONTENT: Only {total_words} words in paragraphs")
    elif total_words < 600:
        results["warnings"].append(
            f"LOW CONTENT: {total_words} words — may not fill pages adequately"
        )
    else:
        results["passes"].append(f"OK: {total_words} words of prose content")

    # Check for visual variety
    visual_types = []
    if svg_count > 0:
        visual_types.append("SVG")
    if has_charts_css:
        visual_types.append("Charts.css")
    if table_count > 0:
        visual_types.append("Table")
    if link_count > 0:
        visual_types.append("Citation")
    if html_content.count("<blockquote") > 0:
        visual_types.append("Blockquote")
    if html_content.count("<details") > 0:
        visual_types.append("Collapsible")
    results["metrics"]["visual_types"] = visual_types
    if len(visual_types) <= 1 and total_words > 200:
        results["warnings"].append(
            f"LOW VISUAL VARIETY: Only {len(visual_types)} visual type(s)"
        )
    elif len(visual_types) >= 2:
        results["passes"].append(
            f"OK: {len(visual_types)} visual types: {', '.join(visual_types)}"
        )

    # Check for repeated visual patterns (same visual 3+ times)
    # Count table occurrences
    if table_count >= 3:
        results["warnings"].append(
            f"POSSIBLE REPETITION: {table_count} tables — consider varying presentation"
        )

    return results


def evaluate_design_instructions(instructions, expected_skill):
    """Evaluate the design instructions brief."""
    results = {
        "expected_skill": expected_skill,
        "length": len(instructions),
        "metrics": {},
        "issues": [],
        "warnings": [],
        "passes": [],
    }

    required_sections = [
        "COLOR SYSTEM",
        "TYPOGRAPHY",
        "SPACING",
        "VISUAL MOOD",
        "REPORT INTENT",
        "VISUAL DECISION TREE",
        "SVG",
        "CHARTS.CSS",
        "AVOID",
    ]
    for section in required_sections:
        found = section.lower() in instructions.lower()
        results["metrics"][f"has_{section.replace(' ', '_').lower()}"] = found
        if not found:
            results["warnings"].append(f"Missing section: {section}")
        else:
            results["passes"].append(f"Found section: {section}")

    hex_values = re.findall(r"#[0-9A-Fa-f]{6}", instructions)
    results["metrics"]["hex_color_count"] = len(hex_values)
    if len(hex_values) < 5:
        results["issues"].append(f"Only {len(hex_values)} hex colors — should have 10+")
    else:
        results["passes"].append(f"OK: {len(hex_values)} hex color values")

    rem_values = re.findall(r"[\d.]+rem", instructions)
    results["metrics"]["rem_value_count"] = len(rem_values)

    if_then_count = instructions.lower().count("if ") + instructions.lower().count(
        "then "
    )
    results["metrics"]["if_then_indicators"] = if_then_count
    if if_then_count < 4:
        results["warnings"].append(
            f"Few IF/THEN indicators ({if_then_count}) — decision tree may be weak"
        )

    has_viewbox = "viewbox" in instructions.lower()
    results["metrics"]["has_viewbox"] = has_viewbox
    if not has_viewbox:
        results["warnings"].append("No viewBox guidance in design instructions")

    has_show_labels = "show-labels" in instructions
    has_show_data = "show-data" in instructions
    results["metrics"]["has_show_labels"] = has_show_labels
    results["metrics"]["has_show_data"] = has_show_data

    return results


# ============================================================
# MAIN TEST RUNNER
# ============================================================


async def run_tests():
    """Run all test scenarios and collect results."""
    print("=" * 80)
    print("END-TO-END REPORT GENERATION PIPELINE TEST")
    print("=" * 80)

    # Initialize LLMs
    grok_model = LlmsHouse().grok_model("grok-4-1-fast-reasoning", temperature=0.9)
    design_model = LlmsHouse().google_model("gemini-3.1-pro-preview", temperature=1.25)
    available_skills = get_available_design_skills()

    all_results = []

    for scenario in TEST_SCENARIOS:
        print(f"\n{'=' * 80}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"Query: {scenario['user_query'][:80]}...")
        print(f"Expected Skill: {scenario['expected_skill']}")
        print(f"{'=' * 80}")

        scenario_result = {
            "name": scenario["name"],
            "user_query": scenario["user_query"],
            "expected_skill": scenario["expected_skill"],
            "stages": {},
            "design_instructions_path": None,
            "html_output_path": None,
        }

        toc = {f"1. {scenario['name']}": ["1.1 Overview"]}

        # ── Stage 1: Design Skill Selection ──
        print("\n[Stage 1] Selecting design skill...")
        try:
            skill_prompt = await choose_design_skill_prompt(
                user_query=scenario["user_query"],
                planner_queries=scenario["planner_queries"],
                table_of_contents=toc,
                abstract="",
                introduction="",
                available_skills=available_skills,
            )
            routing_model = grok_model.with_structured_output(DesignSkillSelection)
            route_response = await routing_model.ainvoke(skill_prompt)
            selected_skill = route_response.selected_skill_filename.strip()
            selected_rules = available_skills.get(selected_skill, "")
            print(
                f"  Selected: {selected_skill} (expected: {scenario['expected_skill']})"
            )
            match = selected_skill == scenario["expected_skill"]
            print(f"  Match: {'✅' if match else '❌'}")
            scenario_result["stages"]["skill_selection"] = {
                "selected": selected_skill,
                "expected": scenario["expected_skill"],
                "match": match,
            }
        except Exception as e:
            print(f"  ❌ Skill selection failed: {e}")
            scenario_result["stages"]["skill_selection"] = {"error": str(e)}
            selected_skill = "general_fallback.md"
            selected_rules = available_skills.get("general_fallback.md", "")

        # ── Stage 2: Design Instructions ──
        print("\n[Stage 2] Generating design instructions...")
        try:
            design_prompt = await generate_design_instructions_prompt(
                user_query=scenario["user_query"],
                planner_queries=scenario["planner_queries"],
                table_of_contents=toc,
                selected_skill_name=selected_skill,
                selected_skill_rules=selected_rules,
            )
            styled_model = design_model.with_structured_output(DesignInstructionsResult)
            design_response = await styled_model.ainvoke(design_prompt)
            design_instructions = design_response.design_instructions.strip()

            # Save design instructions
            safe_name = (
                scenario["name"].replace(" ", "_").replace("—", "_").replace("/", "_")
            )
            design_path = f"/Users/choclate/Desktop/WORT/deep-research-agent/writer/test_design_{safe_name}.txt"
            with open(design_path, "w") as f:
                f.write(f"SCENARIO: {scenario['name']}\n")
                f.write(f"SELECTED SKILL: {selected_skill}\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(design_instructions)
            print(f"  Design instructions saved to: {design_path}")
            scenario_result["design_instructions_path"] = design_path

            design_eval = evaluate_design_instructions(
                design_instructions, selected_skill
            )
            print(f"  Length: {len(design_instructions)} chars")
            print(f"  Hex colors: {design_eval['metrics'].get('hex_color_count', 0)}")
            print(f"  Passes: {len(design_eval['passes'])}")
            print(f"  Warnings: {len(design_eval['warnings'])}")
            print(f"  Issues: {len(design_eval['issues'])}")
            for w in design_eval["warnings"]:
                print(f"    ⚠️  {w}")
            for i in design_eval["issues"]:
                print(f"    ❌ {i}")

            scenario_result["stages"]["design_instructions"] = {
                "length": len(design_instructions),
                "evaluation": design_eval,
                "preview": design_instructions[:800] + "..."
                if len(design_instructions) > 800
                else design_instructions,
            }
        except Exception as e:
            print(f"  ❌ Design instructions failed: {e}")
            import traceback

            traceback.print_exc()
            scenario_result["stages"]["design_instructions"] = {"error": str(e)}
            design_instructions = ""

        # ── Stage 3: Chapter Generation ──
        print("\n[Stage 3] Generating chapter...")
        try:
            messages = await generate_chapter_prompt(
                chapter_heading=f"1. {scenario['name']}",
                table_of_contents=toc,
                sections_for_chapter=scenario["sections"],
                design_instructions=design_instructions,
                user_query=scenario["user_query"],
                planner_queries=scenario["planner_queries"],
            )
            chapter_response = await grok_model.ainvoke(messages)
            html_content = (
                chapter_response.content
                if hasattr(chapter_response, "content")
                else str(chapter_response)
            )

            # Clean markdown code fences
            if html_content.startswith("```"):
                html_content = re.sub(r"^```(?:html)?\s*\n?", "", html_content)
                html_content = re.sub(r"\n?```\s*$", "", html_content)

            chapter_eval = evaluate_chapter_html(html_content, f"1. {scenario['name']}")
            print(f"  HTML length: {chapter_eval['html_length']}")
            print(f"  Pages: {chapter_eval['metrics'].get('page_count', 0)}")
            print(f"  Words: {chapter_eval['metrics'].get('total_words', 0)}")
            print(f"  SVGs: {chapter_eval['metrics'].get('svg_count', 0)}")
            print(f"  Tables: {chapter_eval['metrics'].get('table_count', 0)}")
            print(f"  Citations: {chapter_eval['metrics'].get('citation_count', 0)}")
            print(f"  Visual types: {chapter_eval['metrics'].get('visual_types', [])}")
            print(
                f"  Inline styles: {chapter_eval['metrics'].get('inline_style_count', 0)}"
            )
            print(f"  Passes: {len(chapter_eval['passes'])}")
            for p in chapter_eval["passes"]:
                print(f"    ✅ {p}")
            print(f"  Warnings: {len(chapter_eval['warnings'])}")
            for w in chapter_eval["warnings"]:
                print(f"    ⚠️  {w}")
            print(f"  Issues: {len(chapter_eval['issues'])}")
            for i in chapter_eval["issues"]:
                print(f"    ❌ {i}")

            scenario_result["stages"]["chapter"] = {
                "html_length": chapter_eval["html_length"],
                "evaluation": chapter_eval,
                "html_preview": html_content[:1000] + "..."
                if len(html_content) > 1000
                else html_content,
            }

            # Save full HTML for inspection
            safe_name = (
                scenario["name"].replace(" ", "_").replace("—", "_").replace("/", "_")
            )
            html_path = f"/Users/choclate/Desktop/WORT/deep-research-agent/writer/test_output_{safe_name}.html"
            with open(html_path, "w") as f:
                f.write(html_content)
            print(f"\n  Full HTML saved to: {html_path}")
            scenario_result["html_output_path"] = html_path

        except Exception as e:
            print(f"  ❌ Chapter generation failed: {e}")
            import traceback

            traceback.print_exc()
            scenario_result["stages"]["chapter"] = {"error": str(e)}

        all_results.append(scenario_result)

    # ── Summary ──
    print(f"\n{'=' * 80}")
    print("FINAL SUMMARY")
    print(f"{'=' * 80}")
    for r in all_results:
        print(f"\n{r['name']}:")
        for stage_name, stage_data in r["stages"].items():
            if "error" in stage_data:
                print(f"  {stage_name}: ❌ {stage_data['error']}")
            elif "evaluation" in stage_data:
                ev = stage_data["evaluation"]
                n_issues = len(ev.get("issues", []))
                n_warnings = len(ev.get("warnings", []))
                n_passes = len(ev.get("passes", []))
                print(
                    f"  {stage_name}: {n_passes} passes, {n_warnings} warnings, {n_issues} issues"
                )
            elif "match" in stage_data:
                status = "✅" if stage_data["match"] else "❌"
                print(f"  {stage_name}: {status} selected={stage_data['selected']}")
            else:
                print(f"  {stage_name}: OK")
        # Print saved file paths
        if r.get("design_instructions_path"):
            print(f"  Design instructions: {r['design_instructions_path']}")
        if r.get("html_output_path"):
            print(f"  HTML output: {r['html_output_path']}")

    # Save detailed results
    output_path = (
        "/Users/choclate/Desktop/WORT/deep-research-agent/writer/test_results.json"
    )

    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(i) for i in obj]
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj

    serializable_results = make_serializable(all_results)
    with open(output_path, "w") as f:
        json.dump(serializable_results, f, indent=2, default=str)
    print(f"\nDetailed results saved to: {output_path}")

    return all_results


if __name__ == "__main__":
    asyncio.run(run_tests())
