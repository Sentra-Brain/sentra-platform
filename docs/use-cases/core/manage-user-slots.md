# Use Case: Manage User Slots

**Category:** Core  
**Actors:** Administrator, Sentra Brain System  
**Priority:** High  
**Triggers:** Administrator views, adds, or removes user accounts  

## Description

Sentra Brain limits the number of active user accounts through a slot-based system. By default, five user slots are available in Community Edition installations. Administrators can create, update, or delete user accounts through the Admin UI, respecting the slot limit.

## Basic Flow

1. System checks if there are existing users:
    - If no users exist → First registered user is automatically assigned Administrator role.
2. Administrator logs into Sentra Admin.
3. Administrator navigates to the User Management section.
4. The system displays the list of active users and available slots.
5. Administrator adds a new user:
    - Fills in username and password.
    - System verifies that a free slot is available.
    - System creates the user and updates slot count.
6. Administrator removes a user:
    - Selects user.
    - Confirms deletion.
    - System removes user credentials and frees up the slot.

## Notes

- First user created after a fresh install automatically becomes Administrator.
- If all slots are occupied:
    - System prevents creating new users and shows a warning message.
- Slot limits are hardcoded for Community Edition (default: 5).
- In licensed versions, slot count is configurable via database or license key.
- User authentication is handled via JWT or cookie session tokens.
- Passwords must be stored using secure hashing (bcrypt or similar).
