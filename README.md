The application was deployed and can be accessed here: https://web-app-for-dental-office.onrender.com

A full-stack web application for managing a dental clinic's day-to-day operations, built as a university project using Flask and SQLAlchemy.

The app covers the core needs of a front desk workflow: managing patient records, doctor profiles, and appointments. Scheduling is handled through a custom weekly calendar with drag-to-select time slots and real-time availability checking per doctor. There's also a basic data analysis module that accepts a CSV file and generates descriptive statistics and price distribution charts using pandas and matplotlib.

Tech stack: Python, Flask, SQLAlchemy, Oracle DB (development) / MySQL via Aiven (production), Bootstrap 5, deployed on Render.

What it does well: the calendar UI is functional and avoids the usual plain date-picker approach; the CSV analysis module produces useful visualizations without requiring the user to write any queries.

Limitations: no authentication — the app assumes a single trusted user (the receptionist). 
