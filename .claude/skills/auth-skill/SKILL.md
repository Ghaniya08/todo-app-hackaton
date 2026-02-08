---
name: auth-skill
description: Implement secure authentication systems including signup, sign-in, password hashing, JWT tokens, and auth provider integrations.
---

# Authentication Core Skill

## Instructions

1. **User registration (Signup)**
   - Collect and validate user inputs
   - Enforce strong password rules
   - Prevent duplicate accounts
   - Store credentials securely

2. **User login (Sign-in)**
   - Authenticate users using email/username + password
   - Handle invalid credentials safely
   - Protect against brute-force attacks

3. **Password hashing**
   - Never store plain-text passwords
   - Use modern hashing algorithms (bcrypt, argon2, scrypt)
   - Apply salting and proper cost factors

4. **JWT authentication**
   - Generate access and refresh tokens
   - Sign tokens securely using secrets or private keys
   - Verify and decode tokens on protected routes
   - Handle token expiration and renewal

5. **Auth integrations**
   - Integrate third-party auth providers (Google, GitHub, etc.)
   - Use OAuth flows correctly
   - Normalize external user profiles
   - Support both local and social authentication

## Best Practices
- Always hash passwords before storage
- Use HTTPS for all auth-related requests
- Keep JWT payloads minimal
- Rotate secrets and tokens regularly
- Implement logout and token revocation
- Follow least-privilege access control

## Example Structure

```js
// Signup
const hashedPassword = await bcrypt.hash(password, 12);
await User.create({ email, password: hashedPassword });

// Login
const isValid = await bcrypt.compare(password, user.password);
if (!isValid) throw new Error("Invalid credentials");

// JWT generation
const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: "15m" }
);

// Protected route
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
  req.user = decoded;
  next();
}
