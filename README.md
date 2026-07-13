Trekking Management System

Project Overview

This project is a web application designed to handle the complexities of trekking operations. Built using Python and the Flask framework, the system manages trek scheduling, staff resource allocation, and user booking workflows.

The application architecture relies on a Role-Based Access Control (RBAC) model, segregating functionality into distinct groups for Administrators, Trek Staff, and Trekkers (Users). Data persistence and relational integrity are managed using SQLite and SQLAlchemy, ensuring secure, consistent state management across all user interactions and dashboards.

Development Milestones & Architectural Decisions

Milestone 1: Database Architecture & Initialization

ORM Relationships (db.relationship vs. ForeignKey): While a ForeignKey uses relational constraints strictly at the database level (storing raw numerical IDs), db.relationship() is utilized to map these relations directly into Python objects. This allows the backend to interact with related database records intuitively as objects rather than executing manual SQL joins to map IDs.

System Admin Auto Creation: The application is designed to automatically create a root Admin account upon server startup if one does not already exist.

Application Context: Because SQLAlchemy operates independently of the active Flask layer, using app_context() is done during startup. This proxy binds the database configuration (app.config) to the execution environment, allowing database tables and initial users to be created before the web server begins listening for requests.

Milestone 2: Security & Role-Based Access Control (RBAC)
Pending Resolution: A known constraint requires addressing the slot availability counter on the Trek cards to ensure it decrements accurately when a user confirms a booking (to be resolved in the Trekker routing module).
Modular Architecture using Flask Blueprints: The application logic is grouped using Flask Blueprints. This acts as a modular system, allowing distinct domains (Admin, Staff, Trekker, Authentication) to be developed independently and registered to the main application instance, ensuring a clean and maintainable codebase.

Session Security (SECRET_KEY): Because the browser operates purely on the client side, raw requests cannot be trusted. A cryptographic SECRET_KEY is implemented to sign the session cookies. This prevents malicious users from tampering with developer tools to manually change their privileges (e.g., modifying a local session state from 'Trekker' to 'Admin').

Milestone 3: Admin Subsystem & Data Cascading

Route Protection (@before_request): A strict barrier check is implemented on the Admin blueprint. The @before_request hook acts as middleware, verifying the user's role before granting access to any /admin routes, effectively securing the dashboard from unauthorized access by Staff or Trekkers.

Cascading Deletions: When an Admin deletes a Trek record (Parent Table), the system uses cascading rules to automatically clear associated Bookings (Child Table). This prevents orphaned data and database integrity errors.

Staff Deactivation Protocol: Staff members are not hard-deleted from the database to preserve historical booking and trek data. Instead, they are flagged as inactive via an is_blacklisted boolean. Constraint: A staff member cannot be deactivated if they are currently assigned to an 'Active' trek.

Trekker Blacklisting Protocol: When an Admin blacklists a Trekker, that user is immediately removed from all 'Upcoming' treks (completed and currently active treks remain unaffected for historical accuracy).

Payment Logic: Admin-initiated cancellations result in a 'Forfeited' payment status. If a user cancels their own booking, the status reflects 'Refund'.

Milestone 4: Staff Workflows & Analytics Integration

Forced Security Updates: Staff members logging in with temporary, Admin-assigned credentials are intercepted by a routing hook same with staff who self register themselves. They are forced to update their password and profile details before gaining access to the Staff Dashboard.

Active Trek Constraints: Validation logic ensures that a Staff member can only have one 'Active' trek at a time. They cannot activate a new deployment until their current active trek is marked as 'Completed'.

Milestone 5: Trekker Dashboard 

Implemented Simulated Payment Process, no data given to checkout page is saved in Database its just for simulation purpose to give web application a more real world view. 

Milestone 6: Bookings and Track Bookings

This Mileston has been completed Simulataneously side by side while building routes for admin, staff and Trekker.

Optional Milestones 

Data Visualization: Integrated Chart.js on the frontend to render dynamic, visual data metrics (e.g., booking trends, trek statuses) directly on the Admin dashboard.

Login Security: This is handled using Flask's session management and using @before_request hooks in admin.py, staff.py and trekker.py further werkzeug.security to generate Hashed Passwords to be saved in Database and check those hashed passwords befor a user tries to login into system.

Frontend/backend validation: For Frontend HTML5's form validation has been used but to make a robust system backend validation inside routes has also been added.