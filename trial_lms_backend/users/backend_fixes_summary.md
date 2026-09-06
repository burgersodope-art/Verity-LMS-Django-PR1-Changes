<!-- >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 1-64) -->
# Backend Fixes Summary: Authentication & School Assignment

This document outlines the recent bug fixes and code modifications made to the Django backend to repair the user registration, login, and school assignment flows.

## 1. `users/serializers.py`
**The Problem:** 
The application was crashing during user registration because the API was attempting to save a `school` field directly to the `User` database table. However, the database was designed with an intermediary mapping table (`SchoolUser`) instead of a direct column. 

**What Was Changed:**
- **In `RegisterSerializer`:** 
  - Added an explicit `school` field using `serializers.PrimaryKeyRelatedField(..., required=False)` so the API knows to expect an optional School ID.
  - Rewrote the `create()` method. It now securely intercepts the `school` data, creates the `User` object first, and then explicitly creates a `SchoolUser` record in the database linking the two together.
- **In `UserSerializer`:** 
  - Removed the broken `source="school.school_name"` shortcut.
  - Implemented custom `SerializerMethodField`s (`get_school` and `get_school_name`) that safely query the `SchoolUser` table using `obj.schooluser_set.first()` to correctly resolve the school ID and Name.

**What It Fixed:** 
Users can now successfully register from the frontend. The `school` data is correctly processed and a multi-school Role-Based Access Control (RBAC) relationship is successfully established in the database without throwing a `TypeError`.

**Detailed Code Explanation:**
The core issue was that the `User` database table **does not have a `school` column**. 

1. **`source="school.school_name"` vs `SerializerMethodField`**:
   - The old code used `source="school.school_name"`. This tells Django: *"Look at the User model, find a column named `school`, and grab its `school_name`."* Because the User model doesn't actually have a `school` column, Django got confused and threw a `TypeError`.
   - By using `SerializerMethodField()`, we tell Django: *"Don't try to look at the database columns automatically. Instead, run a custom Python function to figure out the value."* The `get_school_name(self, obj)` function manually looks into the `SchoolUser` intermediate table to find the user's school connection, and safely returns the name.

2. **`PrimaryKeyRelatedField`**:
   - We explicitly added `school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), write_only=True, required=False)`.
   - This tells the API to expect an ID string for a school. When it receives it, it checks the database to ensure a School with this ID actually exists. `write_only=True` ensures it's only used when receiving data (registering), and `required=False` allows users to leave it blank (so they can register without a school).

3. **The Custom `create` Logic**:
   - `validated_data` contains all the data the user submitted.
   - Because `User.objects.create_user()` only expects fields that actually exist on the `User` table, passing the `school` ID into it would cause a database crash.
   - So we use `school = validated_data.pop("school", None)` to safely remove the school data from the dictionary *before* we try to create the User.
   - After creating the User safely, the `if school:` block says: *"If the user actually provided a school during registration, take the newly created User and the School, and link them together in the `SchoolUser` mapping table."*

---

## 2. `schools/views.py`
**The Problem:** 
The frontend registration page was crashing and throwing a `401 Unauthorized` error when attempting to fetch the list of schools to populate the dropdown menu.

**What Was Changed:**
- Overrode the `get_permissions()` method on the `SchoolViewSet`.
- Injected logic to allow public access `AllowAny()` strictly for the `list` (get all) and `retrieve` (get one) API actions. 
- Retained the strict `IsAdminOnly` permission class for sensitive database modifications (creating, updating, deleting schools).

**What It Fixed:** 
The registration page now successfully fetches and displays the list of schools to unauthenticated visitors without compromising the security of the broader API.

---

## 3. `users/admin.py`
**The Problem:** 
There were two major issues with the Django Admin panel: 
1. Administrators had no way to assign a school to a user from the interface.
2. Users created from the Admin panel could not log in from the frontend because their passwords were being saved as plain text instead of being securely hashed.

**What Was Changed:**
- **School Assignment:** Imported the `SchoolUser` model, created a `SchoolUserInline` component, and injected it into the `UserAdmin`.
- **Password Security:** Modified the `UserAdmin` class to inherit from Django's highly secure `BaseUserAdmin` (from `django.contrib.auth.admin`) instead of the generic `admin.ModelAdmin`.

**What It Fixed:** 
Administrators now have a dedicated "School users" sub-form at the bottom of the User profile page to easily assign schools. Furthermore, by inheriting the secure `BaseUserAdmin`, the Admin panel now uses specialized cryptographic hashing algorithms when creating users, and provides a safe "Change Password" workflow, completely fixing the `401 Unauthorized` login errors.
