# Microservices Platform — Learning Notes

---

## 1. The Database (H2 + JPA)

The project uses **H2**, an in-memory relational database. It works exactly like a real SQL database (Postgres, MySQL) but lives entirely in RAM and resets every time the service restarts.

### H2 Console Access

| Service | URL | JDBC URL |
|---|---|---|
| User Service | http://localhost:8081/h2-console | `jdbc:h2:mem:userdb` |
| Product Service | http://localhost:8082/h2-console | `jdbc:h2:mem:productdb` |
| Order Service | http://localhost:8083/h2-console | `jdbc:h2:mem:orderdb` |

**Login credentials:**
- User Name: `sa`
- Password: *(leave empty)*

### How Tables Get Created

You never write `CREATE TABLE` SQL. Instead, JPA annotations on entity classes tell Hibernate how to generate the table automatically at startup.

The `ddl-auto: create-drop` setting means the table is created on startup and dropped on shutdown — data does not survive restarts.

### Useful H2 Queries

```sql
-- See all your tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'PUBLIC';

-- See all columns in a table
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'USERS';

-- See all indexes
SELECT * FROM information_schema.indexes
WHERE table_name = 'PRODUCTS';

-- See all constraints (primary keys, unique, foreign keys)
SELECT * FROM information_schema.constraints
WHERE table_name = 'USERS';

-- See your actual data
SELECT * FROM USERS;
SELECT * FROM PRODUCTS;
```

### H2 Information Schema

H2 has built-in system tables in `INFORMATION_SCHEMA` — read-only metadata H2 maintains automatically. These are equivalent to `sys.tables` / `sys.columns` in SQL Server.

---

## 2. Hibernate

Hibernate is the **ORM (Object-Relational Mapper)** that sits between your Java objects and the SQL database. You write Java, Hibernate writes the SQL.

### Hibernate vs Entity Framework (.NET)

| Concept | Hibernate (Java) | Entity Framework (.NET) |
|---|---|---|
| Mark a class as a table | `@Entity` | `[Table]` / inherits `DbContext` |
| Primary key | `@Id` | `[Key]` |
| Auto-increment | `@GeneratedValue` | `[DatabaseGenerated]` |
| Column constraints | `@Column(nullable=false)` | `[Required]` |
| The "DbContext" equivalent | `JpaRepository` | `DbContext` |
| Save a record | `repository.save(obj)` | `context.SaveChanges()` |
| LINQ equivalent | JPQL (`@Query`) | LINQ queries |
| Migration strategy | `ddl-auto: create-drop` | `dotnet ef migrations` |
| Lifecycle hooks | `@PrePersist`, `@PreUpdate` | `override SaveChanges()` |

> **Key difference:** EF uses migrations (versioned SQL scripts) to evolve the schema. Hibernate in this project uses `create-drop` which regenerates the schema from scratch on every startup. For production you would switch to **Flyway** or **Liquibase** — the Java equivalent of EF migrations.

### Annotation → Column Mapping

```java
@Entity                          // "this class is a database table"
@Table(name = "products")        // "the table is named 'products'"
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;             // → PRIMARY KEY BIGINT AUTO_INCREMENT

    @Column(nullable = false, length = 200)
    private String name;         // → name VARCHAR(200) NOT NULL

    @Column(columnDefinition = "TEXT")
    private String description;  // → description TEXT (unlimited length)

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;    // → price DECIMAL(10,2) NOT NULL

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;  // updatable=false → never included in UPDATEs
}
```

> **Note on BigDecimal:** Never use `float` or `double` for money. They have binary rounding errors (`0.1 + 0.2 = 0.30000000000000004`). `BigDecimal` is exact.

### Lifecycle Callbacks

Hibernate calls these methods automatically — you never call them yourself:

```java
@PrePersist          // fires just before INSERT
protected void onCreate() {
    createdAt = LocalDateTime.now();
    updatedAt = LocalDateTime.now();
}

@PreUpdate           // fires just before UPDATE
protected void onUpdate() {
    updatedAt = LocalDateTime.now();
}
```

### The Repository Layer

`ProductRepository` is a Java interface with no implementation class. Hibernate + Spring Data generate the implementation at runtime.

**Three ways to query:**

**1. Built-in methods** — inherited from `JpaRepository`, no code needed:
```java
productRepository.findAll()       // SELECT * FROM products
productRepository.findById(id)    // SELECT * FROM products WHERE id = ?
productRepository.save(product)   // INSERT or UPDATE (checks if id exists)
productRepository.deleteById(id)  // DELETE FROM products WHERE id = ?
```

**2. Derived queries** — Spring Data reads the method name and generates SQL:
```java
List<Product> findByCategory(String category);
// → SELECT * FROM products WHERE category = ?

List<Product> findByCategoryAndStockQuantityGreaterThan(String category, int minStock);
// → SELECT * FROM products WHERE category = ? AND stock_quantity > ?
```
No SQL written — the method name IS the query.

**3. JPQL** — for complex queries:
```java
@Query("SELECT p FROM Product p WHERE LOWER(p.name) LIKE LOWER(CONCAT('%', :keyword, '%'))")
List<Product> searchByKeyword(@Param("keyword") String keyword);
```
JPQL uses Java class/field names (`Product`, `p.name`) not table/column names. Hibernate translates it to real SQL.

### Transactions

`@Transactional` means every method runs inside a database transaction:
- If anything throws an exception → Hibernate **rolls back** all changes
- If the method completes successfully → Hibernate **commits**
- `@Transactional(readOnly = true)` on read-only methods is a performance optimization — Hibernate skips change tracking

### The Full Stack

```
HTTP Request
     ↓
Controller        (handles HTTP, calls service)
     ↓
Service           (@Transactional, business logic)
     ↓
Repository        (interface — Spring Data generates implementation)
     ↓
Hibernate         (translates Java ↔ SQL)
     ↓
H2 Database       (executes the actual SQL)
```

---

## 3. HATEOAS

**HATEOAS** stands for **Hypermedia As The Engine Of Application State**. It is a REST constraint that says API responses should include links telling clients what they can do next.

### Without HATEOAS
```json
{ "id": 1, "name": "Chair", "price": 299.99 }
```
The client has to already know that to delete this product it should call `DELETE /api/products/1`.

### With HATEOAS
```json
{
  "id": 1, "name": "Chair", "price": 299.99,
  "_links": {
    "self":     { "href": "http://localhost:8082/api/products/1" },
    "update":   { "href": "http://localhost:8082/api/products/1" },
    "delete":   { "href": "http://localhost:8082/api/products/1" },
    "products": { "href": "http://localhost:8082/api/products" }
  }
}
```
The response tells the client what it can do next. The client just follows the `"delete"` link — it never needs to know the URL structure.

### How It Works in the Code

There are two separate classes for each resource:

- **`Product.java`** — the database entity (maps to the table, no links)
- **`ProductModel.java`** — the API response object (copies the data and adds `_links`)

```java
// ProductModel extends RepresentationModel — that's what adds the _links field
public class ProductModel extends RepresentationModel<ProductModel> {

    public static ProductModel from(Product product) {
        ProductModel model = new ProductModel();
        // copy fields from entity...

        // linkTo(methodOn(...)) reads the @GetMapping on the controller
        // and generates the correct URL — no hardcoding
        model.add(linkTo(methodOn(ProductController.class)
                .getProduct(product.getId())).withSelfRel());       // "self"

        model.add(linkTo(methodOn(ProductController.class)
                .deleteProduct(product.getId())).withRel("delete")); // "delete"

        return model;
    }
}
```

In the controller, the entity is converted to a model before returning:
```java
return ResponseEntity.ok(ProductModel.from(product));  // entity → model with links
```

### Collection Responses

For a list of products, `CollectionModel` wraps the list and adds a collection-level self link:

```json
{
  "_embedded": {
    "productModelList": [ ...products, each with their own _links... ]
  },
  "_links": {
    "self": { "href": "http://localhost:8082/api/products" }
  }
}
```

### Key Benefit

If the server-side URL structure ever changes, clients that follow `_links` automatically get the new URLs — no client code changes needed.

---

## Service Ports Reference

| Service | Port | Swagger UI |
|---|---|---|
| Eureka Server | 8761 | http://localhost:8761 |
| Config Server | 8888 | N/A |
| User Service | 8081 | http://localhost:8081/swagger-ui/index.html |
| Product Service | 8082 | http://localhost:8082/swagger-ui/index.html |
| Order Service | 8083 | http://localhost:8083/swagger-ui/index.html |
| API Gateway | 8080 | All external traffic enters here |

## Startup Order

Start services in this order — each depends on the previous:

1. Eureka Server (service registry)
2. Config Server (fetches config from Eureka)
3. User Service, Product Service, Order Service (fetch config from Config Server)
4. API Gateway (needs all services registered in Eureka)
