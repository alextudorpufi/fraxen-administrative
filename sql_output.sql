INSERT INTO executives (title, gender, experience, sector_focus, location)
VALUES (
    'Business Lawyer | Real Estate Specialist',
    'Male',
    '20+ years, top-tier law firm and in-house business exposure.',
    'Real Estate, Development, M&A, Corporate, Banking & Finance',
    'Romania (Remote/Hybrid)'
);

-- NOTE: The ID below must be updated manually after the first INSERT executes and returns the new ID.


INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Managing Partner', 'Founder and leader of a specialized legal advisory firm.',
'Advised top-tier clients on real estate, M&A and financing matters exceeding EUR 150 million.\nDirected legal operations, client development, and market positioning.',
1);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Head of Real Estate (Of Counsel)', 'Senior counsel leading real estate practice at a prominent law firm.',
'Led client engagements on complex development, acquisition, and commercial real estate matters.\nCoordinated team development, training, and market-facing initiatives.',
2);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Partner - Head of Real Estate', 'Key leader of the real estate practice at a global law firm.',
'Advised on a landmark real estate transaction valued at over EUR 500 million.\nProvided legal assistance to a national government for a major privatization.',
3);

INSERT INTO executive_highlights (executive_id, position_title, company_description, details, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Senior Associate - Real Estate', 'Experienced legal professional advising major investors in real estate.',
'Advised on office, retail, industrial, and residential projects with aggregate values exceeding EUR 400 million.\nSupported significant development and investment initiatives.',
4);


INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Real Estate & Investments', 1);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'M&A and Strategic Transactions', 2);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Development & Construction Law', 3);

INSERT INTO executive_strengths (executive_id, strength_description, display_order)
VALUES
([EXECUTIVE_ID_PLACEHOLDER], 'Corporate Governance & Finance', 4);