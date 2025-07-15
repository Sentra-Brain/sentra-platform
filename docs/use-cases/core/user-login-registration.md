# Use Case: User Login & Registration

**Category:** Core  
**Actors:** User, Administrator, Sentra Brain System  
**Priority:** High  
**Triggers:** User opens Sentra Web or Sentra Admin and is not authenticated  

## Description

Sentra Brain provides a simple authentication system based on fixed user slots. Users can register if slots are available or log in if they already have credentials. The first registered user automatically becomes the Administrator.

## Basic Flow

### Registration Flow

1. User accesses Sentra Web.
2. System checks if users exist:
    - If no users → Shows "Initialize Administrator Account" form.
    - If users exist → Shows Login form, or allows registration if slots are available.
3. User submits registration form with username and password.
4. System checks:
    - Available slots.
    - Valid username/password format.
5. If valid:
    - System creates user account.
    - Assigns Administrator role if first user.
    - Logs the user in automatically.

### Login Flow

1. User accesses Sentra Web or Sentra Admin.
2. System displays login form.
3. User submits username and password.
4. System verifies credentials.
5. If valid:
    - System generates session token (JWT or cookie).
    - Redirects user to main application interface.
6. If invalid:
    - System shows error message.

## Extensions

- If maximum slots are occupied:
    - Registration form is hidden or disabled with a message.
- If user forgets password:
    - Manual admin reset (no automatic recovery in Community Edition).
- If login session expires:
    - System redirects to login page.

## Notes

- Passwords must be stored securely using bcrypt or equivalent hashing.
- Session tokens expire based on configurable TTL.
- In Licensed Editions:
    - Slot count may be dynamic.
    - User roles may include finer-grained permissions.
