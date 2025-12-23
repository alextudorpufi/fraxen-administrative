INSERT INTO executives (title, gender, experience, sector_focus, location)
VALUES (
    'Founder | Strategic Financial Leader',
    'Unknown',
    '20+ years in financial services, NPL, and corporate restructuring.',
    'Financial Services, Non-Performing Loans, Real Estate, Corporate Restructuring, Investment Banking',
    'Europe (Remote/Hybrid)'
);

-- NOTE: The ID below must be updated manually after the first INSERT executes and returns the new ID.


INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Founder & Managing Partner', 'Visionary leader establishing and scaling a specialized financial advisory and investment firm.',
'Successfully launched and grew a boutique advisory firm, delivering bespoke financial solutions.\nProvided expert strategic guidance on complex financial restructuring and asset optimization projects.',
1);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Head of Group Workout Portfolio Management', 'Executive driving NPL sales and repossessed asset management for a leading international banking group.',
'Built and led a high-performing department, establishing critical processes and group standards for NPL transactions.\nOrchestrated multi-asset NPL sales, coordinating investor coverage and complex case support.\nPioneered and implemented a comprehensive strategy for repossessed real estate asset management, from acquisition to sale.',
2);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Executive Director, Head of Portfolio Management', 'Senior leader overseeing NPL portfolio divestment and distressed real estate asset strategies at a major financial institution.',
'Successfully executed numerous NPL portfolio sales, spanning diverse asset classes and investor profiles.\nDirected the structuring and implementation of complex restructuring and recovery solutions for high-value real estate clients.\nDeveloped and coordinated a robust asset management framework for repossessed real estate, optimizing value prior to resale.',
3);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Equity Partner | M&A Lead', 'Strategic partner instrumental in a significant financial sector M&A transaction and subsequent greenfield launch.',
'Spearheaded M&A planning and execution, including strategic carve-out of non-core assets.\nDrove post-merger development from inception, successfully preparing for a new corporate business launch.',
4);


INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Non-Performing Loan (NPL) Management', 1);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Financial Restructuring & Workout', 2);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Real Estate Asset & Portfolio Management', 3);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Strategic Leadership & Business Development', 4);