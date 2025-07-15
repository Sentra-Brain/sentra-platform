# Use Case: Initialize System – First User Becomes Administrator

**Category:** Core  
**Actors:** First Registered User, Sentra Brain System  
**Priority:** High  
**Triggers:** No users exist in the system (fresh install or reset)  

## Description

When Sentra Brain is started for the first time and no user accounts exist, the first registered user automatically receives Administrator privileges. This ensures secure initialization without requiring pre-configured credentials.

## Basic Flow

1. Sentra Brain API starts and detects an empty user database.
2. User accesses Sentra Web or Sentra Admin.
3. User submits registration form:
    - Chooses username and password.
    - System checks: no existing users → marks this user as Administrator.
4. System stores user credentials securely and starts normal operation.
5. Any subsequent users created by the Administrator follow normal slot rules.

## Extensions

- If the system already has users:
    - Registration page is replaced by Login form.
- If the first user registration fails (e.g., password validation error):
    - System does not assign Administrator role until successful registration occurs.

## Notes

- First user creation is only possible when `user_count = 0` in the database.
- Administrator role includes access to:
    - User Management
    - MCP Server Management
    - System Configuration (future phases)
- This mechanism applies only in Community and Licensed Editions unless overridden by pre-provisioning.
