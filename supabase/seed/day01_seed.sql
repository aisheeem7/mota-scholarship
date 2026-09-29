-- 3 fake applicants, no real PII, covering an approved/flagged/deficient spread for demo/testing.
insert into students (name, dob, category) values
  ('Test Student One', '2008-05-14', 'ST'),
  ('Test Student Two', '2006-11-02', 'ST'),
  ('Test Student Three', '2009-01-30', 'ST');

-- scheme_id values are the 5 finalized IDs from the scheme config (PR #4, config/schemes.json).
insert into applications (student_id, scheme_id, status, risk_score) values
  ((select id from students where name = 'Test Student One'),   'PRE_MATRIC',  'APPROVED', 5),
  ((select id from students where name = 'Test Student Two'),   'POST_MATRIC', 'FLAGGED_FOR_REVIEW', 55),
  ((select id from students where name = 'Test Student Three'), 'TOP_CLASS',   'DEFICIENT', 20);
