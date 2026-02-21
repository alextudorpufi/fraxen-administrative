INSERT INTO executives (title, gender, experience, sector_focus, location)
VALUES (
    'Strategic Finance Officer | Fractional CFO',
    'Male',
    '20+ years, global consulting and Fortune100 financial leadership experience.',
    'Multi-industry (Technology, FMCG, Manufacturing, Advertising, Agriculture, Financial Services, Real Estate)',
    'Eastern Europe & Middle East (Remote/Hybrid/On-site)'
);

-- NOTE: The ID below must be updated manually after the first INSERT executes and returns the new ID.


INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Professional Trainer', 'Expert Educator in Financial Management for Corporate Clients',
'Delivered corporate training sessions on Finance for Non-Finance, Risk Management, and Financial Statement Analysis.\nCustomized training materials for major regional enterprises in energy, banking, and infrastructure sectors.',
1);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Interim CFO & Finance Consultant', 'Strategic Financial Advisor to Diverse Businesses, including Top-Tier Global Platform',
'Provided financial management and consulting advice to numerous SMEs across various sectors.\nExecuted financial audit assignments, acquisition due diligence, and fiscal compliance projects.\nActed as interim CFO for a leading regional producer (EUR 80M sales) and a prominent entertainment group (EUR 10M revenue).',
2);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Chief Financial Officer', 'Financial Architect for an Innovative Technology Startup',
'Revised and improved the original budget and developed a strategic growth plan.\nEstablished the accounting function, managed banking relationships, and implemented procure-to-pay procedures.',
3);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Chief Financial Officer', 'Financial Leader at a Major Global Advertising Group Subsidiary',
'Supported management in achieving revenue and operating income targets, overseeing significant business growth (doubling in size).\nEnsured high-quality financial reporting and successfully integrated accounting data post-merger of multiple agencies.',
4);


INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Financial Strategy & Management', 1);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Financial Reporting & Compliance (IFRS/GAAP)', 2);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Budgeting, Forecasting & Cost Control', 3);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Internal Audit & Control Improvement', 4);