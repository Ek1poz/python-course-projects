- **Code Review:** Prompt:

  **Role:** Senior Django Developer and Security Expert.  
  **Context:** A Django Bookstore e-commerce application with session-based
  carts, custom models, Stripe Checkout, and
  email notifications.  
  **Task:** Review `order_create`, `payment_process`, and the three async views
  in `my_app/views.py` for bugs, security concerns, performance bottlenecks,
  and Django best-practice issues. Provide concrete recommendations and
  refactored code where appropriate.  
  **Constraints:** Be concise and focus on PEP 8, Django ORM usage, and
  transaction safety. Do not rewrite working logic unnecessarily. Make
  application-code changes only in `my_app/views.py`; do not modify other
  application files. Save the review, including the original code,
  recommendations, and final code for each reviewed view, in `AI_REVIEW.md`(For 
  each of the 3 views/serializers, provide three clearly separated sections: 
  "Original Code", "AI Recommendations" (bullet points explaining why), and 
  "Refactored Final Code").  
  **Output:** A Markdown review report in `AI_REVIEW.md`.

  The review identified checkout validation and pricing issues, opportunities
  to reduce order-item database queries, and missing handling for invalid
  payment totals and Stripe errors. The two checkout/payment views were updated
  in `views.py`; the three async report/detail views were reviewed and left
  unchanged. The recommendations and changes are documented in `AI_REVIEW.md`.


- **Tests:** Prompt:

  **Role:** QA Automation Engineer and Python Developer.  
  **Context:**  I have a Django Bookstore project with custom models. 
  I need to write unit tests for the following models to ensure data 
  integrity and correct business logic: [Book, Order, OrderItem] (look up the project).  
  **Task:** Write comprehensive Django unit tests for `Book`, `Order`, and
  `OrderItem` in `my_app/tests/test_models.py`. Cover successful creation,
  string representations, and edge cases such as negative prices and omitted
  optional fields. Include necessary imports and setup methods.
  **Constraints:** The generated tests must be thorough enough to achieve ≥ 60% 
  test coverage for these specific models. Cover successful creation, string 
  representations (str), and edge cases (e.g., negative prices, missing optional fields). 
  Do not implement the solution instantly, write the code here for my review and wait for 
  my decision weather to implement it or not. You MUST include the exact comment 
  # Generated with AI, reviewed and modified inside every test method.
  Add short, clear docstrings to test classes and functions.
  Change only the test file.  
  **Output:** A ready-to-run test file and a coverage report.

  The tests cover model creation and defaults, string representations, order
  totals, item cost calculations, validation, negative prices, and cascade
  deletion. Verification: all 20 tests passed, with 100% coverage of
  `my_app.models`.

- **Documentation:** Prompt:

  **Role:** Python developer and technical writer.  
  **Context:** My Django Bookstore project needs professional documentation 
  and docstrings in views.py file.
  **Task:** Generate PEP 257-compliant English docstrings for all views in
  `views.py` and create a comprehensive, professional `README.md`.  
  **Constraints:** Each view docstring should explain what the view does, its
  arguments, and its return value, using type-hint context when necessary. The
  README should include Project Overview, Features, Setup/Installation
  instructions (including Docker/PostgreSQL when applicable), and an `AI Usage`
  section with Code Review, Tests, and Documentation subsections.  
  **Output:** Documented views and a README checked against the project
  structure and configuration.

  AI assistance added PEP 257-style
  docstrings to the views and drafted this README after reviewing the project
  structure and configuration; the output was checked against the codebase.