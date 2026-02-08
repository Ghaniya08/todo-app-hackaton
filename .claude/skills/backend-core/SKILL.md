---
name: backend-core
description: Build backend functionality including API routes, request/response handling, and database integration. Use for server-side application development.
---

# Backend Core Development

## Instructions

1. **Routing**
   - Define RESTful API routes
   - Use proper HTTP methods (GET, POST, PUT, DELETE)
   - Organize routes by feature or resource

2. **Request & Response Handling**
   - Validate incoming requests
   - Parse request body, params, and query strings
   - Send structured JSON responses
   - Handle success and error responses properly

3. **Database Connection**
   - Connect to database securely
   - Use environment variables for credentials
   - Perform CRUD operations
   - Handle connection errors gracefully

4. **Error Handling**
   - Centralized error handling
   - Meaningful status codes
   - Clear error messages

## Best Practices
- Follow REST API conventions
- Keep controllers thin and reusable
- Never expose sensitive data
- Use async/await for database operations
- Separate routes, controllers, and services
- Validate data before DB operations

## Example Structure
```js
// routes/user.routes.js
import express from "express";
import { createUser, getUsers } from "../controllers/user.controller.js";

const router = express.Router();

router.post("/users", createUser);
router.get("/users", getUsers);

export default router;
