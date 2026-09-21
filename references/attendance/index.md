# Attendance

Query the current user's attendance/check-in records.

Use `lark-cli schema attendance.user_tasks.query` to inspect parameters, then `lark-cli attendance user_tasks query`. The required scope is `attendance:task:readonly`.

For this personal-record workflow, set `employee_type` to `"employee_no"` in params and `user_ids` to an empty array in data. These are fixed protocol values, not information to request from the user. Obtain the date range from the task and current timezone; do not invent other request fields.
