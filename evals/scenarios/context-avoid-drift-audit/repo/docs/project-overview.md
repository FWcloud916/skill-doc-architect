# freightd — Project Overview

> **Type:** Explanation
> **Audience:** Developers
> **Last updated:** 2026-07-01

---

## 1. Purpose and Scope
Books freight movements and schedules pickups.
## 2. Technology Stack
Python, standard library only.
## 3. Architecture
Single daemon process; each Delivery is scheduled with a Carrier pickup window.
## 4. Directory Layout
`src/` holds the daemon and models; `tests/` the unit tests.
## 5. Domain Models
See [docs/domain-models.md](domain-models.md).
