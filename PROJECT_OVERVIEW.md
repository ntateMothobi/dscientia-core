# Property Sales Intelligence (Mini)

## 1. Project Summary

**Property Sales Intelligence (Mini)** is a portfolio-grade, real-world Python application designed to help **individual property agents and UMKM** manage their sales workflow more efficiently.

The application integrates property listing management, marketing content generation, lead tracking, follow-up reminders, and performance insights into **one lightweight, low-cost system** that can run locally and scale gradually.

This project is built as:

* A **personal productivity tool** for real property selling
* A **Computer Science portfolio project** demonstrating applied software engineering
* A **potential commercial product** for other agents

---

## 2. Problem Statement

Individual property agents commonly face these problems:

* Inconsistent property posting and marketing content
* Leads scattered across WhatsApp, forms, and social media
* No clear prioritization between casual inquiries and serious buyers
* Missed or late follow-ups
* No visibility into which activities actually lead to closings

Existing solutions (marketplaces, CRMs, spreadsheets) are either **too limited, too complex, or too expensive** for individual agents.

---

## 3. Target Users (Persona)

**Primary User:** Individual Property Agent / UMKM

Characteristics:

* Works independently or with a very small team
* Limited technical background
* Relies heavily on WhatsApp and social media
* Handles multiple listings simultaneously

Primary Goals:

* Close deals faster
* Stay organized without complexity
* Focus time on serious buyers

---

## 4. Project Goals

This project is considered successful if:

* It can be used daily without returning to spreadsheets
* Leads and follow-ups are no longer missed
* Marketing content creation becomes faster and more consistent
* Sales performance can be understood through simple metrics

---

## 5. MVP Scope (Strict)

The MVP will focus on **exactly five core features**:

1. **Property Listing Management**

   * Create, update, and track property listings
   * Manage listing status (available, booked, sold)

2. **Smart Content Generator (Rule-based)**

   * Generate marketing captions for Facebook Marketplace
   * Generate WhatsApp follow-up messages

3. **Lead Management (Mini CRM)**

   * Capture and store leads
   * Associate leads with specific listings

4. **Follow-up Assistant**

   * Track follow-up history
   * Provide reminders for pending leads

5. **Sales Performance Dashboard**

   * Visualize total listings, leads, follow-ups, and closed deals

---

## 6. Explicit Non-Goals (Out of Scope for MVP)

The following features will **not** be implemented in the MVP:

* Mobile application
* Paid advertising integrations (Google Ads, Meta Ads)
* Advanced AI or machine learning
* Multi-language support
* Public marketplace functionality

These may be considered in future iterations.

---

## 7. Technical Stack

**Core Technologies:**

* Python 3.10+
* FastAPI (Backend API)
* Streamlit (Web UI / Dashboard)
* SQLite (Local database, upgradeable to MySQL)

**Design Principles:**

* Modular monolith architecture
* Python-first development
* Low operational cost
* Local-first, cloud-ready

---

## 8. Architecture Philosophy

The system is designed as a **single integrated application** with clear module separation:

* Listings
* Content generation
* Leads
* Follow-ups
* Analytics

This approach ensures simplicity for solo development while remaining scalable for future multi-user support.

---

## 9. Portfolio & Learning Objectives

This project demonstrates:

* Applied backend development (FastAPI)
* Database design and data modeling
* Automation and business logic
* Product-oriented thinking
* Clean project structure and documentation

It is intentionally designed to be **explainable in interviews**, not just functional.

---

## 10. Future Roadmap (Post-MVP)

* Multi-user authentication
* Export and reporting features
* Basic lead scoring logic
* Deployment on low-cost VPS
* Commercial packaging for other agents

---

## 11. Author & Context

Built by a Computer Science student as a real-world application combining:

* Software engineering
* Digital marketing automation
* Property sales workflow optimization

This project prioritizes **learning, impact, and practical usability** over premature optimization.
