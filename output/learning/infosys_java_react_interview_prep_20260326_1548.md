# 🎯 Interview Prep: Infosys Java Full-Stack React Developer
**Interview Date:** Tomorrow
**Location:** Charlotte, NC
**Company:** Infosys

---

## ✅ Your Skill Match Analysis

### 🟢 Strong Matches (You Have These!)
| Required Skill | Your Experience |
|----------------|-----------------|
| Java | ✅ Expert level, 10+ years |
| React JS | ✅ Proficient (React projects) |
| RESTful APIs | ✅ Strong (Kafka, web services) |
| HTML5/CSS3 | ✅ Proficient |
| JavaScript/TypeScript | ✅ Proficient |
| PostgreSQL/MySQL | ✅ Strong database experience |
| Docker/CI-CD | ✅ Strong DevOps background |
| SDLC Experience | ✅ 10+ years |
| Banking Domain | ✅ 4 years at Bank of America |

### 🟡 Areas to Review (Refresh Before Interview)
| Skill | Priority | Focus Area |
|-------|----------|------------|
| Spring Framework | 🔴 HIGH | IoC, DI, @Annotations |
| Hibernate/JPA | 🔴 HIGH | Entity mapping, relationships |
| J2EE Patterns | 🟠 MEDIUM | Service layer, DAO pattern |
| WebSphere/JBoss | 🟢 LOW | Basic deployment concepts |

---

## 📚 CRASH COURSE: Key Topics to Review Tonight

### 1️⃣ Spring Framework Essentials

```java
// IoC Container & Dependency Injection
@Service
public class AccountService {
    
    @Autowired  // Constructor injection preferred
    private AccountRepository accountRepository;
    
    public Account createAccount(AccountDTO dto) {
        Account account = new Account();
        account.setAccountNumber(generateAccountNumber());
        account.setBalance(BigDecimal.ZERO);  // Never use double for money!
        return accountRepository.save(account);
    }
}

@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {
    Optional<Account> findByAccountNumber(String accountNumber);
    List<Account> findByCustomerId(Long customerId);
}

@RestController
@RequestMapping("/api/accounts")
public class AccountController {
    
    @Autowired
    private AccountService accountService;
    
    @PostMapping
    public ResponseEntity<Account> createAccount(@Valid @RequestBody AccountDTO dto) {
        Account account = accountService.createAccount(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(account);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Account> getAccount(@PathVariable Long id) {
        return accountRepository.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
```

**Key Annotations to Know:**
- `@Component` - Generic Spring bean
- `@Service` - Business logic layer
- `@Repository` - Data access layer (auto exception translation)
- `@Controller` / `@RestController` - Web layer
- `@Autowired` - Dependency injection
- `@Configuration` - Java-based configuration
- `@Bean` - Method-level bean definition

---

### 2️⃣ Hibernate/JPA Entity Mapping

```java
@Entity
@Table(name = "accounts")
public class Account {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 20)
    private String accountNumber;
    
    @Column(nullable = false, precision = 19, scale = 4)
    private BigDecimal balance;  // Always BigDecimal for money!
    
    @Enumerated(EnumType.STRING)
    private AccountStatus status;
    
    @ManyToOne(fetch = FetchType.LAZY)  // Lazy to prevent N+1
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;
    
    @OneToMany(mappedBy = "account", cascade = CascadeType.ALL)
    private List<Transaction> transactions = new ArrayList<>();
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    private LocalDateTime updatedAt;
}

@Entity
@Table(name = "transactions")
public class Transaction {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "account_id", nullable = false)
    private Account account;
    
    @Enumerated(EnumType.STRING)
    private TransactionType type;  // DEPOSIT, WITHDRAWAL, TRANSFER
    
    @Column(nullable = false, precision = 19, scale = 4)
    private BigDecimal amount;
    
    private String description;
    
    @CreationTimestamp
    private LocalDateTime transactionDate;
}
```

**Key Concepts to Explain:**
- **Lazy vs Eager Loading** - Lazy loads on access, Eager loads immediately
- **N+1 Problem** - Use `@EntityGraph` or `JOIN FETCH` to solve
- **Cascade Types** - ALL, PERSIST, MERGE, REMOVE, REFRESH
- **Transaction Management** - `@Transactional` for ACID compliance

---

### 3️⃣ REST API Best Practices

```java
// Proper HTTP Status Codes
@RestController
@RequestMapping("/api/v1/transactions")
public class TransactionController {
    
    @PostMapping
    public ResponseEntity<?> createTransaction(@Valid @RequestBody TransactionDTO dto) {
        try {
            Transaction tx = transactionService.process(dto);
            return ResponseEntity.status(HttpStatus.CREATED).body(tx);  // 201
        } catch (InsufficientFundsException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)        // 400
                .body(new ErrorResponse("INSUFFICIENT_FUNDS", e.getMessage()));
        } catch (AccountNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)          // 404
                .body(new ErrorResponse("ACCOUNT_NOT_FOUND", e.getMessage()));
        }
    }
    
    @GetMapping
    public ResponseEntity<Page<Transaction>> getTransactions(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Transaction> transactions = transactionService.findAll(
            PageRequest.of(page, size, Sort.by("transactionDate").descending())
        );
        return ResponseEntity.ok(transactions);  // 200
    }
}

// Global Exception Handler
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest().body(new ErrorResponse("VALIDATION_ERROR", message));
    }
}
```

---

### 4️⃣ React JS Patterns (Interview Focus)

```jsx
// Modern React with Hooks
import { useState, useEffect, useCallback, useMemo } from 'react';

function AccountDashboard({ customerId }) {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // useCallback prevents unnecessary re-renders
    const fetchAccounts = useCallback(async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/accounts?customerId=${customerId}`);
            if (!response.ok) throw new Error('Failed to fetch accounts');
            const data = await response.json();
            setAccounts(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [customerId]);
    
    useEffect(() => {
        fetchAccounts();
    }, [fetchAccounts]);
    
    // useMemo for expensive calculations
    const totalBalance = useMemo(() => {
        return accounts.reduce((sum, acc) => sum + acc.balance, 0);
    }, [accounts]);
    
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage message={error} />;
    
    return (
        <div className="dashboard">
            <h2>Total Balance: ${totalBalance.toFixed(2)}</h2>
            {accounts.map(account => (
                <AccountCard key={account.id} account={account} />
            ))}
        </div>
    );
}
```

**React Concepts to Know:**
- **useState** - Local state management
- **useEffect** - Side effects (API calls, subscriptions)
- **useCallback** - Memoize functions to prevent re-renders
- **useMemo** - Memoize computed values
- **useContext** - Share state without prop drilling
- **Custom Hooks** - Reusable stateful logic

---

## 🎤 Interview Question Prep

### Technical Questions (Be Ready For These!)

| Topic | Likely Questions |
|-------|-----------------|
| **Spring** | "Explain IoC and DI", "Difference between @Component vs @Bean", "How does @Transactional work?" |
| **Hibernate** | "What is N+1 problem and how to solve it?", "Lazy vs Eager loading?", "How do you handle transactions?" |
| **REST** | "Design an API for bank transfers", "When to use PUT vs PATCH?", "How do you version APIs?" |
| **React** | "Class vs Functional components?", "Explain Virtual DOM", "How do you manage state in large apps?" |
| **System Design** | "Design a payment processing system", "How would you scale this application?" |

### Banking Domain Questions

- **ACID Properties** - Atomicity, Consistency, Isolation, Durability
- **Transaction Isolation Levels** - READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE
- **Idempotency** - Same request produces same result (critical for payments!)
- **Double-entry Bookkeeping** - Every debit has a credit

### Behavioral Questions (STAR Method)

1. **Tell me about a challenging technical problem you solved**
   - *Use: CIDH project with Kafka migration or BEAR compliance dashboard*

2. **How do you handle disagreements with team members?**
   - *Use: Cross-team collaboration at Duke Energy*

3. **Describe a time you mentored someone**
   - *Use: Teaching experience at NC A&T*

4. **How do you stay current with technology?**
   - *Mention: Learning AI/ML, your career goal toward Principal Engineer*

---

## ❓ Questions to Ask Infosys

1. "What does the tech stack look like for this project?"
2. "How is the team structured - onshore/offshore split?"
3. "What's the deployment process and release frequency?"
4. "What opportunities exist for technical growth and mentorship?"
5. "What's a typical day like for this role?"

---

## 🏆 Your Competitive Advantages

| Advantage | How to Position It |
|-----------|-------------------|
| **10+ years experience** | "I bring senior-level judgment and can mentor junior developers" |
| **Bank of America background** | "I understand banking domain, compliance, and audit requirements" |
| **NERC CIP security** | "I apply security-first thinking to API and data design" |
| **Teaching experience** | "I can communicate complex concepts clearly to stakeholders" |
| **Kafka/Event streaming** | "I understand modern distributed architectures" |
| **Automation mindset** | "I reduced manual work by 79% - I look for optimization opportunities" |

---

## ⏰ Tonight's Action Plan

| Time | Task |
|------|------|
| 1 hour | Review Spring + Hibernate code examples above |
| 30 min | Practice explaining IoC, DI, N+1 problem out loud |
| 30 min | Review React hooks (useState, useEffect, useCallback) |
| 30 min | Prepare 3 STAR stories from your experience |
| 15 min | Review your resume - be ready to discuss any project |
| 15 min | Research Infosys recent news/projects |

---

**Good luck tomorrow! You've got this! 🚀**

*Your experience at Duke Energy, Bank of America, and NC A&T gives you a unique combination of technical depth, compliance expertise, and communication skills that sets you apart.*
