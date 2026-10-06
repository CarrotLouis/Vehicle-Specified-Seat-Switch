# Primary review
The 12 code values/overlap results agree with config.lua (verified by test_review.lua). Side-specific modifiers reject both sides held, as DS correctly says.
Correction: overlap=false for different primary keys does NOT mean they cannot fire in the same poll. F2+F5 or both mouse side keys can have simultaneous rising edges. A dispatcher must reject multiple seat targets independently of parse-time overlap detection.
Standalone CTRL example needs CTRL first, then SHIFT, then HOME; SHIFT-first example needs SHIFT, then CTRL, then HOME. Extra modifiers suppress the standalone binding on later edges.
Existing test_input.lua already explicitly asserts standalone CTRL vs CTRL+1 and LSHIFT vs CTRL+SHIFT+MOUSE4 overlaps. The report's broad missing-coverage wording is not evidence of absent tests. Specific HOME examples were not covered and are checked separately here.
No DS code imported; report remains raw. 0105 is now accepted for installer-host M102 already-local driver routes, not all runtime cases.
