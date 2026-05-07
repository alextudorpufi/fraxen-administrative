INSERT INTO executives (title, gender, experience, sector_focus, location)
VALUES (
    'Fractional CFO | Strategic Financial Leader',
    'Female',
    '20+ years, strategic financial leadership across diverse industries.',
    'Technology, Real Estate, Multi-entity Organizations',
    'Europe (Remote/Hybrid)'
);

-- NOTE: The ID below must be updated manually after the first INSERT executes and returns the new ID.


INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Fractional CFO & Investment Advisor', 'Empowering high-growth tech startups and institutional investors with strategic financial leadership.',
'Successfully prepared and supported multiple fundraising rounds, accelerating due diligence.\nLed finance transformation projects, integrating ERP systems and AI automation.\nProvided M&A advisory, valuations, and transaction management.',
1);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Chief Financial Officer', 'Orchestrated financial strategy for a significant real estate development and logistics portfolio.',
'Structured finance organization for a EUR 250M+ development portfolio.\nBuilt multi-project forecasting and cash flow coordination across complex operations.\nIntroduced ERP-based project control and reporting for end-to-end visibility.',
2);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Group Chief Financial Officer', 'Centralized and optimized finance operations for a multi-entity technology and SaaS group.',
'Centralized finance operations for a multi-entity tech group with cross-functional reporting.\nImplemented ERP systems with profitability tracking by client and product line.\nDeveloped performance dashboards linking operational efficiency with profitability metrics.',
3);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Managing Director / CFO', 'Pioneered and led a regional real estate investment platform from its inception.',
'Built a regional real estate investment platform from inception, managing multiple entities.\nNegotiated complex credit restructurings and optimized group cash flow.\nImplemented robust ERP and transfer pricing frameworks for accurate multi-entity reporting.',
4);


INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Strategic Financial Leadership', 1);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Business Growth & Capital Strategy', 2);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Finance Transformation & Automation', 3);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Operational Excellence & M&A', 4);