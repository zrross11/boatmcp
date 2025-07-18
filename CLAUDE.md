# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BoatMCP is an MCP (Model Context Protocol) server designed to help developers ship code from local development to production using natural language interactions with an LLM client. 

**Mission Statement:** BoatMCP's mission is to eliminate the friction between "it works on my machine" and "it works in production" by providing intelligent tooling that guides developers through deployment workflows using plain English conversations with Claude or other MCP-compatible LLMs.

The core purpose of BoatMCP is to allow developers to describe their deployment goals in natural language, enabling them to go from local repository to production in the cloud through LLM-guided workflows. This includes generating Dockerfiles, building container images, provisioning cloud infrastructure, and managing Kubernetes deployments. The system interprets natural language requests and provides step-by-step guidance to deploy software correctly and efficiently.

## Development Setup

**Prerequisites:**
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- minikube (for Kubernetes cluster management functionality)

**Environment Setup:**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add fastmcp2.0 httpx
```

**Run the FastMCP server:**
```bash
uv run main.py
```

**Test with Claude Desktop:**
The server runs as an MCP server via stdio transport. Configure in Claude Desktop's config file at `/Users/<username>/Library/Application Support/Claude/claude_desktop_config.json`.

**Critical Dependency Note:**
This project uses **fastmcp2.0** from [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp). When implementing new features or modifying existing code, ensure that all interactions with MCP functionality are routed through this specific library.

## Architecture

The project follows a modular MCP server architecture designed to bridge the gap between natural language requests and infrastructure deployment:

- **main.py**: MCP server entrypoint that registers all tools using fastmcp2.0
- **app/**: Application modules containing domain-specific functionality
  - **minikube/**: Kubernetes cluster management via minikube commands
    - **minikube.py**: Core minikube operations (create/delete clusters)
    - **__init__.py**: Module exports

**Key Design Patterns:**
- MCP tools are implemented as async functions and registered via decorators
- Infrastructure commands are wrapped with error handling and timeout protection
- All tools return structured responses with success/failure status
- Natural language interpretation guides users through deployment workflows

**MCP Integration:**
- Uses fastmcp2.0 framework for rapid MCP server development
- Tools are automatically exposed to MCP clients when decorated with `@fastmcp.tool()`
- Server communicates via stdio transport protocol
- Designed to work seamlessly with Claude Desktop and other MCP-compatible clients

## Dependencies

**Core Dependencies (pyproject.toml):**
- `httpx>=0.28.1` - HTTP client library
- `fastmcp2.0` - Model Context Protocol implementation (v2.0 from jlowin/fastmcp)

**System Dependencies:**
- minikube binary must be available in PATH for Kubernetes functionality

## Tool Functions

**Minikube Management:**
- `create_minikube_cluster()`: Creates new Kubernetes clusters with configurable resources
- `delete_minikube_cluster()`: Removes clusters with optional purge functionality

All infrastructure operations include comprehensive error handling and user-friendly response formatting.

# Development Guidelines for Claude

## Core Philosophy

**TEST-DRIVEN DEVELOPMENT IS NON-NEGOTIABLE.** Every single line of production code must be written in response to a failing test. No exceptions. This is not a suggestion or a preference - it is the fundamental practice that enables all other principles in this document.

I follow Test-Driven Development (TDD) with a strong emphasis on behavior-driven testing and functional programming principles. All work should be done in small, incremental changes that maintain a working state throughout development.

## Professional Development Standards

Your development process should adhere to the following professional standards:

1. **Incremental Changes:** Implement changes in small, logical, and atomic commits. This makes code review easier and helps isolate potential issues.
2. **Commit Frequency:** Make commits after implementing new features, fixing bugs, or completing any logical unit of work. As a general guideline, consider creating a commit after changes that are roughly 50 lines of code.
3. **High-Quality Code:**
   - **Documentation:** All new functions, classes, and modules should have clear and concise docstrings explaining their purpose, arguments, and return values.
   - **Comments:** Use inline comments to clarify complex or non-obvious logic. Focus on the *why*, not the *what*.
   - **Design:** Strive for a clean, professional, and maintainable codebase. Follow established software design patterns where appropriate.
4. **Industry Best Practices:** Adhere to Python community standards (e.g., PEP 8) and modern development practices.
5. **Review-Oriented Workflow:** After making a set of changes, present them for review. Explain the changes made and their purpose.

## Quick Reference

**Key Principles:**

- Write tests first (TDD)
- Test behavior, not implementation
- Use type hints everywhere
- Immutable data only
- Small, pure functions
- Use mypy in strict mode
- Use real schemas/types in tests, never redefine them

**Preferred Tools:**

- **Language**: Python 3.11+ with type hints
- **Testing**: pytest + pytest-asyncio
- **Type Checking**: mypy (strict mode)
- **Code Formatting**: ruff
- **Schema Validation**: pydantic

## Testing Principles

### Behavior-Driven Testing

- **No "unit tests"** - this term is not helpful. Tests should verify expected behavior, treating implementation as a black box
- Test through the public API exclusively - internals should be invisible to tests
- No 1:1 mapping between test files and implementation files
- Tests that examine internal implementation details are wasteful and should be avoided
- **Coverage targets**: 100% coverage should be expected at all times, but these tests must ALWAYS be based on business behaviour, not implementation details
- Tests must document expected business behaviour

### Testing Tools

- **pytest** for testing framework
- **pytest-asyncio** for async testing
- **pytest-mock** for mocking when needed
- All test code must follow the same type hint rules as production code

### Test Organization

```
src/
  features/
    payment/
      payment_processor.py
      payment_validator.py
      test_payment_processor.py  # The validator is an implementation detail. Validation is fully covered, but by testing the expected business behaviour
```

### Test Data Pattern

Use factory functions with optional overrides for test data:

```python
from typing import Optional
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class PaymentRequest:
    card_account_id: str
    amount: int
    source: str
    account_status: str
    last_name: str
    date_of_birth: str
    paying_card_details: PayingCardDetails
    address_details: AddressDetails
    brand: str

def get_mock_payment_request(
    overrides: Optional[dict] = None
) -> PaymentRequest:
    """Create a mock payment request with sensible defaults."""
    base_request = PaymentRequest(
        card_account_id="1234567890123456",
        amount=100,
        source="Web",
        account_status="Normal",
        last_name="Doe",
        date_of_birth="1980-01-01",
        paying_card_details=get_mock_card_details(),
        address_details=get_mock_address_details(),
        brand="Visa",
    )
    
    if overrides:
        return replace(base_request, **overrides)
    return base_request

def get_mock_address_details(
    overrides: Optional[dict] = None
) -> AddressDetails:
    """Create mock address details with sensible defaults."""
    base_address = AddressDetails(
        house_number="123",
        house_name="Test House",
        address_line1="Test Address Line 1",
        address_line2="Test Address Line 2",
        city="Test City",
    )
    
    if overrides:
        return replace(base_address, **overrides)
    return base_address
```

Key principles:

- Always return complete objects with sensible defaults
- Accept optional dict overrides (use `dataclasses.replace`)
- Build incrementally - extract nested object factories as needed
- Compose factories for complex objects
- Use frozen dataclasses for immutability

## Python Guidelines

### Type Hints Requirements

```python
# pyproject.toml
[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
```

- **Type hints everywhere** - No function without type hints
- **No `Any`** - Use `object` or specific types, never `Any`
- **No `# type: ignore`** without explicit explanation
- These rules apply to test code as well as production code

### Type Definitions

- **Prefer `@dataclass` over `TypedDict`** for structured data
- Use explicit typing where it aids clarity, but leverage inference where appropriate
- Utilize generic types effectively (`TypeVar`, `Generic`)
- Create domain-specific types for type safety
- Use pydantic for schemas that need runtime validation

```python
from typing import NewType
from dataclasses import dataclass

# Good - Domain-specific types
UserId = NewType('UserId', str)
PaymentAmount = NewType('PaymentAmount', int)

@dataclass(frozen=True)
class Payment:
    user_id: UserId
    amount: PaymentAmount
    currency: str
```

#### Schema-First Development with Pydantic

Always define your schemas first, then derive types from them:

```python
from pydantic import BaseModel, Field
from typing import Literal
import re

# Define schemas first - these provide runtime validation
class AddressDetails(BaseModel):
    house_number: str
    house_name: str | None = None
    address_line1: str = Field(min_length=1)
    address_line2: str | None = None
    city: str = Field(min_length=1)
    postcode: str = Field(pattern=r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$')

class PayingCardDetails(BaseModel):
    cvv: str = Field(pattern=r'^\d{3,4}$')
    token: str = Field(min_length=1)

class PostPaymentsRequestV3(BaseModel):
    card_account_id: str = Field(min_length=16, max_length=16)
    amount: int = Field(gt=0)
    source: Literal["Web", "Mobile", "API"]
    account_status: Literal["Normal", "Restricted", "Closed"]
    last_name: str = Field(min_length=1)
    date_of_birth: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    paying_card_details: PayingCardDetails
    address_details: AddressDetails
    brand: Literal["Visa", "Mastercard", "Amex"]

# Use schemas at runtime boundaries
def parse_payment_request(data: dict) -> PostPaymentsRequestV3:
    return PostPaymentsRequestV3.model_validate(data)

# Example of schema composition for complex domains
class BaseEntity(BaseModel):
    id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    created_at: datetime
    updated_at: datetime

class Customer(BaseEntity):
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')
    tier: Literal["standard", "premium", "enterprise"]
    credit_limit: int = Field(gt=0)
```

#### Schema Usage in Tests

**CRITICAL**: Tests must use real schemas and types from the main project, not redefine their own.

```python
# ❌ WRONG - Defining schemas in test files
class ProjectSchema(BaseModel):
    id: str
    workspace_id: str
    owner_id: str | None
    name: str
    created_at: datetime
    updated_at: datetime

# ✅ CORRECT - Import schemas from the shared schema module
from boatmcp.schemas import ProjectSchema, Project
```

## Code Style

### Functional Programming

I follow a "functional light" approach:

- **No data mutation** - work with immutable data structures
- **Pure functions** wherever possible
- **Composition** as the primary mechanism for code reuse
- Avoid heavy FP abstractions unless there's a clear advantage
- Use list comprehensions and generator expressions over loops

#### Examples of Functional Patterns

```python
from dataclasses import dataclass, replace
from typing import List

@dataclass(frozen=True)
class OrderItem:
    price: int
    quantity: int

@dataclass(frozen=True)
class Order:
    items: List[OrderItem]
    shipping_cost: int

# Good - Pure function with immutable updates
def apply_discount(order: Order, discount_percent: float) -> Order:
    discounted_items = [
        replace(item, price=int(item.price * (1 - discount_percent / 100)))
        for item in order.items
    ]
    
    total_price = sum(item.price * item.quantity for item in discounted_items)
    
    return replace(
        order,
        items=discounted_items,
    )

# Good - Composition over complex logic
def process_order(order: Order) -> ProcessedOrder:
    return (
        order
        |> validate_order
        |> apply_promotions
        |> calculate_tax
        |> assign_warehouse
    )
```

### Code Structure

- **No nested if/else statements** - use early returns, guard clauses, or composition
- **Avoid deep nesting** in general (max 2 levels)
- Keep functions small and focused on a single responsibility
- Prefer flat, readable code over clever abstractions

### Naming Conventions

- **Functions**: `snake_case`, verb-based (e.g., `calculate_total`, `validate_payment`)
- **Classes**: `PascalCase` (e.g., `PaymentRequest`, `UserProfile`)
- **Constants**: `UPPER_SNAKE_CASE` for true constants, `snake_case` for configuration
- **Files**: `snake_case.py` for all Python files
- **Test files**: `test_*.py`

### No Comments in Code

Code should be self-documenting through clear naming and structure. Comments indicate that the code itself is not clear enough.

```python
# Avoid: Comments explaining what the code does
def calculate_discount(price: int, customer: Customer) -> int:
    # Check if customer is premium
    if customer.tier == "premium":
        # Apply 20% discount for premium customers
        return int(price * 0.8)
    # Regular customers get 10% discount
    return int(price * 0.9)

# Good: Self-documenting code with clear names
PREMIUM_DISCOUNT_MULTIPLIER = 0.8
STANDARD_DISCOUNT_MULTIPLIER = 0.9

def is_premium_customer(customer: Customer) -> bool:
    return customer.tier == "premium"

def calculate_discount(price: int, customer: Customer) -> int:
    discount_multiplier = (
        PREMIUM_DISCOUNT_MULTIPLIER
        if is_premium_customer(customer)
        else STANDARD_DISCOUNT_MULTIPLIER
    )
    
    return int(price * discount_multiplier)
```

### Prefer Keyword Arguments

Use keyword arguments for function parameters as the default pattern. Only use positional parameters when there's a clear, compelling reason.

```python
# Avoid: Multiple positional parameters
def create_payment(
    amount: int,
    currency: str,
    card_id: str,
    customer_id: str,
    description: str | None = None,
    metadata: dict | None = None,
    idempotency_key: str | None = None,
) -> Payment:
    # implementation
    pass

# Calling it is unclear
payment = create_payment(
    100,
    "GBP",
    "card_123",
    "cust_456",
    None,
    {"order_id": "order_789"},
    "key_123"
)

# Good: Clear keyword arguments
@dataclass(frozen=True)
class CreatePaymentRequest:
    amount: int
    currency: str
    card_id: str
    customer_id: str
    description: str | None = None
    metadata: dict | None = None
    idempotency_key: str | None = None

def create_payment(request: CreatePaymentRequest) -> Payment:
    # implementation
    pass

# Clear and readable at call site
payment = create_payment(
    CreatePaymentRequest(
        amount=100,
        currency="GBP",
        card_id="card_123",
        customer_id="cust_456",
        metadata={"order_id": "order_789"},
        idempotency_key="key_123",
    )
)
```

## Development Workflow

### TDD Process - THE FUNDAMENTAL PRACTICE

**CRITICAL**: TDD is not optional. Every feature, every bug fix, every change MUST follow this process:

Follow Red-Green-Refactor strictly:

1. **Red**: Write a failing test for the desired behavior. NO PRODUCTION CODE until you have a failing test.
2. **Green**: Write the MINIMUM code to make the test pass. Resist the urge to write more than needed.
3. **Refactor**: Assess the code for improvement opportunities. If refactoring would add value, clean up the code while keeping tests green.

#### TDD Example Workflow

```python
# Step 1: Red - Start with the simplest behavior
def test_order_total_with_shipping():
    order = create_order(
        items=[{"price": 30, "quantity": 1}],
        shipping_cost=5.99,
    )
    
    processed = process_order(order)
    
    assert processed.total == 35.99
    assert processed.shipping_cost == 5.99

# Step 2: Green - Minimal implementation
def process_order(order: Order) -> ProcessedOrder:
    items_total = sum(item.price * item.quantity for item in order.items)
    
    return ProcessedOrder(
        items=order.items,
        shipping_cost=order.shipping_cost,
        total=items_total + order.shipping_cost,
    )

# Step 3: Red - Add test for free shipping behavior
def test_free_shipping_over_fifty():
    order = create_order(
        items=[{"price": 60, "quantity": 1}],
        shipping_cost=5.99,
    )
    
    processed = process_order(order)
    
    assert processed.shipping_cost == 0
    assert processed.total == 60
```

### Commit Guidelines

- Each commit should represent a complete, working change
- Use conventional commits format:
  ```
  feat: add payment validation
  fix: correct date formatting in payment processor
  refactor: extract payment validation logic
  test: add edge cases for payment validation
  ```
- Include test changes with feature changes in the same commit

### Quality Checks

Before committing, run:

```bash
# Type checking
mypy src/

# Linting and formatting
ruff check src/
ruff format src/

# Tests
pytest

# If these commands exist in the project, run them
uv run pytest  # or similar test command
```

## Common Python Patterns

### Error Handling

Use Result types or early returns:

```python
from typing import Generic, TypeVar, Union
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@dataclass(frozen=True)
class Success(Generic[T]):
    value: T

@dataclass(frozen=True)
class Failure(Generic[E]):
    error: E

Result = Union[Success[T], Failure[E]]

def process_payment(payment: Payment) -> Result[ProcessedPayment, PaymentError]:
    if not is_valid_payment(payment):
        return Failure(PaymentError("Invalid payment"))
    
    if not has_sufficient_funds(payment):
        return Failure(PaymentError("Insufficient funds"))
    
    return Success(execute_payment(payment))

# Also good - early returns with exceptions
def process_payment(payment: Payment) -> ProcessedPayment:
    if not is_valid_payment(payment):
        raise PaymentError("Invalid payment")
    
    if not has_sufficient_funds(payment):
        raise PaymentError("Insufficient funds")
    
    return execute_payment(payment)
```

### Testing Behavior

```python
# Good - tests behavior through public API
class TestPaymentProcessor:
    def test_decline_payment_when_insufficient_funds(self):
        payment = get_mock_payment_request({"amount": 1000})
        account = get_mock_account({"balance": 500})
        
        result = process_payment(payment, account)
        
        assert not result.success
        assert result.error.message == "Insufficient funds"
    
    def test_process_valid_payment_successfully(self):
        payment = get_mock_payment_request({"amount": 100})
        account = get_mock_account({"balance": 500})
        
        result = process_payment(payment, account)
        
        assert result.success
        assert result.data.remaining_balance == 400
```

### Async Function Testing

```python
import pytest

class TestMinikubeOperations:
    @pytest.mark.asyncio
    async def test_create_cluster_success(self):
        result = await create_minikube_cluster(
            profile="test-cluster",
            cpus=2,
            memory="2048mb"
        )
        
        assert "✅ Minikube cluster 'test-cluster' created successfully!" in result
        assert "CPUs: 2" in result
        assert "Memory: 2048mb" in result
    
    @pytest.mark.asyncio
    async def test_create_cluster_failure(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stderr = "Error: driver not found"
        
        result = await create_minikube_cluster(profile="test-cluster")
        
        assert "❌ Failed to create minikube cluster 'test-cluster'" in result
        assert "Error: driver not found" in result
```

## Example Patterns to Avoid

### Anti-patterns

```python
# Avoid: Mutation
def add_item(items: list[Item], new_item: Item) -> list[Item]:
    items.append(new_item)  # Mutates list
    return items

# Prefer: Immutable update
def add_item(items: list[Item], new_item: Item) -> list[Item]:
    return [*items, new_item]

# Avoid: Nested conditionals
if user:
    if user.is_active:
        if user.has_permission:
            # do something
            pass

# Prefer: Early returns
if not user or not user.is_active or not user.has_permission:
    return

# do something

# Avoid: Large functions
def process_order(order: Order) -> ProcessedOrder:
    # 100+ lines of code
    pass

# Prefer: Composed small functions
def process_order(order: Order) -> ProcessedOrder:
    validated_order = validate_order(order)
    priced_order = calculate_pricing(validated_order)
    final_order = apply_discounts(priced_order)
    return submit_order(final_order)
```

## Working with Claude

### Expectations

When working with my code:

1. **ALWAYS FOLLOW TDD** - No production code without a failing test. This is not negotiable.
2. **Think deeply** before making any edits
3. **Understand the full context** of the code and requirements
4. **Ask clarifying questions** when requirements are ambiguous
5. **Think from first principles** - don't make assumptions
6. **Assess refactoring after every green** - Look for opportunities to improve code structure, but only refactor if it adds value

### Code Changes

When suggesting or making changes:

- **Start with a failing test** - always. No exceptions.
- After making tests pass, always assess refactoring opportunities (but only refactor if it adds value)
- After refactoring, verify all tests and static analysis pass, then commit
- Respect the existing patterns and conventions
- Maintain test coverage for all behavior changes
- Keep changes small and incremental
- Ensure all mypy strict mode requirements are met
- Provide rationale for significant design decisions

**If you find yourself writing production code without a failing test, STOP immediately and write the test first.**