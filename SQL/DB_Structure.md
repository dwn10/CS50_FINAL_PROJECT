# MercadoLocalDB - Database Structure

## Main Tables

### 1. Producers
Stores information about producers/vendors.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Producer's name |
| type | VARCHAR(50) | Type (e.g., 'Farmer', 'Baker') |
| description | TEXT | Business description |
| email | VARCHAR(100) | Contact email |
| phone | VARCHAR(20) | Contact phone |
| created_at | TIMESTAMP | Creation date |
| updated_at | TIMESTAMP | Last update |

### 2. Markets
Information about physical market locations.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Market name |
| address | TEXT | Full address |
| operation_days | VARCHAR(100) | Operating days |
| opening_time | TIME | Opening time |
| closing_time | TIME | Closing time |
| created_at | TIMESTAMP | Creation date |
| updated_at | TIMESTAMP | Last update |

### 3. Products
Products offered by producers.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| producer_id | INTEGER | Foreign key to Producers |
| name | VARCHAR(100) | Product name |
| category | VARCHAR(50) | Category (e.g., 'Vegetable', 'Dairy') |
| price | DECIMAL(10,2) | Unit price |
| description | TEXT | Product description |
| is_organic | BOOLEAN | Is organic? |
| is_seasonal | BOOLEAN | Is seasonal? |
| created_at | TIMESTAMP | Creation date |
| updated_at | TIMESTAMP | Last update |

### 4. Users
System users.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | VARCHAR(50) | Unique username |
| email | VARCHAR(100) | Unique email |
| password_hash | VARCHAR(255) | Hashed password |
| first_name | VARCHAR(50) | First name |
| last_name | VARCHAR(50) | Last name |
| created_at | TIMESTAMP | Creation date |
| updated_at | TIMESTAMP | Last update |

### 5. Certifications
Available product certifications.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Certification name |
| description | TEXT | Description |
| created_at | TIMESTAMP | Creation date |

## Relationship Tables

### 6. Market_Stalls
Many-to-many relationship between Producers and Markets.

| Column | Type | Description |
|--------|------|-------------|
| producer_id | INTEGER | Foreign key to Producers |
| market_id | INTEGER | Foreign key to Markets |
| stall_number | VARCHAR(20) | Stall number |
| created_at | TIMESTAMP | Creation date |

### 7. Product_Certifications
Many-to-many relationship between Products and Certifications.

| Column | Type | Description |
|--------|------|-------------|
| product_id | INTEGER | Foreign key to Products |
| certification_id | INTEGER | Foreign key to Certifications |
| certified_at | DATE | Certification date |
| expires_at | DATE | Expiration date |
| created_at | TIMESTAMP | Creation date |

### 8. Reviews
User reviews of products.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| product_id | INTEGER | Foreign key to Products |
| user_id | INTEGER | Foreign key to Users |
| rating | INTEGER | Rating (1-5) |
| comment | TEXT | Review comment |
| created_at | TIMESTAMP | Creation date |

## Views

### 1. complete_market_view
Shows complete information about markets, producers, and products.

### 2. product_ratings
Shows average ratings and review counts per product.

### 3. organic_products_by_market
List of organic products available by market.

## Indexes

Indexes have been created on the following columns to optimize queries:
- `Products(producer_id)`
- `Products(category)`
- `Products(name)`
- `Reviews(product_id)`
- `Reviews(user_id)`
- `Market_Stalls(market_id)`
- `Product_Certifications(certification_id)`

## Relationships

1. **Producers** → **Products** (One-to-Many)
   - A producer can have many products

2. **Producers** ↔ **Markets** (Many-to-Many through Market_Stalls)
   - A producer can be in many markets
   - A market can have many producers

3. **Products** ↔ **Certifications** (Many-to-Many through Product_Certifications)
   - A product can have many certifications
   - A certification can apply to many products

4. **Users** → **Reviews** (One-to-Many)
   - A user can write many reviews

5. **Products** → **Reviews** (One-to-Many)
   - A product can have many reviews
