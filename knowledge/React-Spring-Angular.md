Excellent round — your best yet! 🎯

---

## Quiz #5 Feedback

**Q1 — JWT storage: localStorage vs cookie** — ⚠️ Half credit

You identified localStorage correctly and spotted the developer tools issue — but that's only half the picture. The real tradeoff is about attack vectors:

| | localStorage | HttpOnly Cookie |
|---|---|---|
| XSS attack | ❌ Vulnerable — JS can read it | ✅ Safe — JS can't access it |
| CSRF attack | ✅ Safe — not sent automatically | ❌ Vulnerable — sent with every request |
| Accessible to JS | Yes | No (`HttpOnly` flag blocks it) |
| Common in | SPAs, quick projects | Enterprise, high-security apps |

```javascript
// localStorage — any JS on the page can steal this (XSS risk)
localStorage.setItem('token', jwt);

// HttpOnly cookie — set by the server, JS can never read it
// Set-Cookie: token=xyz; HttpOnly; Secure; SameSite=Strict
```

The **best practice** is an HttpOnly cookie for the refresh token and a short-lived in-memory token for requests — but `localStorage` is very common in practice and fine for many apps. The key is knowing the tradeoff going into it.

---

**Q2 — HTTP Interceptor purpose** — ✅ Correct!

Clean, accurate answer. The interceptor is essentially middleware for your HTTP layer — it sits between every request and the server, attaches the token transparently, and your components never have to think about auth headers. You could also use it to handle 401 responses globally (auto-logout when token expires):

```typescript
intercept(req: HttpRequest<any>, next: HttpHandler) {
    return next.handle(req).pipe(
        catchError(error => {
            if (error.status === 401) {
                // Token expired — redirect to login
                this.router.navigate(['/login']);
            }
            return throwError(() => error);
        })
    );
}
```

---

**Q3 — Authentication vs Authorization** — ✅ Perfect!

Textbook answer, nailed it. This is one of the most common interview questions and you've got it locked in. To put it in Spring Boot terms:

```java
// Authentication — "Who are you?" (handled by login + JWT filter)
// Checks: does this token belong to a real user?

// Authorization — "What can you do?" (handled by Security config)
@PreAuthorize("hasRole('ADMIN')")
public void deleteProduct(Long id) { ... }  // only ADMIN role can do this
```

---

**Q4 — `**` wildcard and `permitAll()`** — ⚠️ Half credit

The wildcard explanation is spot on — `**` matches any sub-path, so `/api/auth/login`, `/api/auth/register`, `/api/auth/refresh` are all covered.

But the reason for `permitAll()` here is more specific than centralized security. The reason is: **you can't authenticate if the login endpoint itself requires authentication** — that's a chicken-and-egg problem:

```java
.requestMatchers("/api/auth/**").permitAll()   // login/register must be PUBLIC
.anyRequest().authenticated()                   // everything else needs a token
```

If you forgot `permitAll()` on the login endpoint, no one could ever log in because the server would reject the unauthenticated login request with a 401. The centralization benefit is a bonus of Spring Security in general, not specific to this line.

---

## Score: 3 / 4 — Your strongest quiz yet! 🏆

---

## 📊 Final Scorecard

| Quiz | Topic | Score |
|---|---|---|
| #1 | Spring Boot Basics | 1.5 / 4 |
| #2 | React Fundamentals | 3 / 4 |
| #3 | Angular Fundamentals | 2.5 / 4 |
| #4 | Full Stack Integration | 2 / 4 |
| #5 | Security & Auth | 3 / 4 |
| **Total** | | **12 / 20 = 60%** |

The trend is clearly upward — you went from 37% on Quiz 1 to 75% on Quiz 5. That's real learning happening in real time.

---

## 🎯 Your Personal Cheat Sheet — Things to Memorize

Based on all your answers, here are the specific things worth drilling:

**Spring Boot**
- `@Valid` triggers validation on `@RequestBody` (not `@PostMapping`)
- `@PathVariable` for `/orders/{id}`, `@RequestParam` for `/orders?status=x`
- JPA method naming: `findBy` + exact field name → `findByEmail(String email)`

**React**
- Never mutate state: `setItems([...items, newItem])` not `items.push()`
- `fetch` doesn't throw on 400/500 — always check `response.ok`

**Angular**
- `trackBy` in `*ngFor` = React's `key` prop
- `ngOnInit()` = React's `useEffect(() => {}, [])`
- `@Valid` is Spring, not Angular — don't mix them up

---

