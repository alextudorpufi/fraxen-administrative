INSERT INTO executives (title, gender, experience, sector_focus, location)
VALUES (
    'Senior HR Leader | Strategic HR Practitioner ( Dora S. )',
    'Female',
    '30+ years of global HR leadership across various industries and geographies.',
    'FMCG, Manufacturing, Banking, Consulting',
    'Romania (Remote/Hybrid)'
);

-- NOTE: The ID below must be updated manually after the first INSERT executes and returns the new ID.


INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Freelance', 'Founder of a strategic HR consulting firm',
'Provides strategic advisory in HR transformation, talent development, and organizational design.\nLeads initiatives for optimizing workforce performance and cultural alignment.',
1);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Group HR Director', 'Large industrial conglomerate, overseeing HR across multiple entities.',
'Directed HR strategy across several entities, aligning operations with group-wide transformation.\nNegotiated and implemented seven Collective Labor Agreements, ensuring labour harmony.\nDesigned and rolled out a new Group Compensation & Benefits strategy, enhancing retention.',
2);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Group HR Director', 'Global dairy industry leader, managing country-wide HR functions.',
'Led HR integration of ten acquired companies, with 8 factories and multiple commercial teams.\nManaged $40M HR annual budget, contributing to a 14.2% increase in FCF over 5 years.\nReduced voluntary turnover from 25.5% to 10% and improved engagement to 82%.',
3);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Senior Regional HR Manager', 'Global Fortune 500 manufacturing company',
'Progressed through multiple roles, coordinating HR strategy across a region of ten countries.\nLed HR strategy, workforce transformation, and organizational projects across many countries.\nServed as EMEA Compensation & Benefits Subject Matter Expert, managing annual compensation cycles across several countries.\nServed as EMEA Subject Matter Expert for ORACLE- PeopleSoft & SAP- SuccessFactors',
4);


INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'HR Strategy, Transformation & Policy', 1);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Organizational Design & Workforce Optimization', 2);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Compensation & Benefits (EMEA SME)', 3);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Industrial & Employee Relations', 4);