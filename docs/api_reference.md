# A.L.F.I.E — API Reference (Modular, Multi-Niche)

**Version**: 3.0 | **Date**: 2026-08-04

---

## Architecture: Dynamic Tool Loading

A.L.F.I.E uses a **registry-based tool system**. Tools are stored as documents in the `tool_registry` MongoDB collection with per-tenant scoping. At call start, the agent loads only the tools enabled for the active tenant's niche.

```
Incoming Call → Identify tenant_id → Load agent_config → Load tool_registry
→ Map to @function_tool implementations → Construct Agent(tools=[...])
```

**Core tools** (shared across all niches): `capture_lead`, `schedule_callback`, `transfer_to_human`
**Niche tools**: Loaded dynamically based on `tenant.niche` field

---

## Core Tools (All Niches)

### `capture_lead`
Save caller contact details and preferences to the `leads` collection.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | string | Yes | Caller's full name |
| `phone` | string | Yes | Phone number |
| `email` | string | No | Email address |
| `interests` | string | Yes | Free-text: what they're looking for |

**Side effects**: Upserts into `leads` (keyed by `tenant_id + phone`). If repeat caller, appends to `interaction_history`. Auto-scores lead based on qualification signals from conversation.

**Returns**: Confirmation message.

---

### `schedule_callback`
Book a callback from a human agent at the caller's preferred time.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `preferred_time` | string | Yes | When to call back (e.g., "tomorrow morning") |
| `reason` | string | Yes | What the caller needs help with |

**Side effects**: Creates notification for admin with callback details.

**Returns**: Confirmation with scheduled time.

---

### `transfer_to_human`
Escalate the current call to a live human agent.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `reason` | string | Yes | Why the caller needs human assistance |

**Side effects**: Logs escalation event, triggers SIP transfer or queues callback.

**Returns**: Acknowledgment message.

---

## Real Estate Tools

### `search_properties`
Search listings matching caller criteria.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `city` | string | Yes | City name |
| `area` | string | No | Specific area (e.g., "DHA Phase 2") |
| `bedrooms` | int | No | Number of bedrooms |
| `min_price` | float | No | Minimum price |
| `max_price` | float | No | Maximum price |
| `property_type` | string | No | `house`, `apartment`, `plot`, `commercial` |

**Returns**: Top 3 matching properties with title, area, bedrooms, price, and listing URL.

**Voice behavior**: Agent presents properties one at a time conversationally:
> *"I found a great option in DHA Phase two. It's a three bedroom house for thirty five million rupees with a garden and parking. Would you like to hear more about this one, or should I show you another option?"*

---

### `get_property_details`
Full details for a specific property.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `property_id` | string | Yes | MongoDB ObjectId |

**Returns**: Complete property document (description, amenities, images, floor plan, agent notes).

---

### `compare_properties`
Side-by-side comparison of 2-3 properties.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `property_ids` | string[] | Yes | Array of 2-3 property ObjectIds |

**Returns**: Structured comparison (price, bedrooms, area, amenities differences).

**Voice behavior**: Agent highlights key differences conversationally:
> *"The DHA Phase two house is ten million less, but the Bahria Town one has an extra bedroom and a bigger lawn."*

---

### `get_neighborhood_info`
Area intelligence: schools, safety, amenities, market trends.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `neighborhood_name` | string | Yes | Area name |
| `city` | string | Yes | City |

**Returns**: School ratings, safety score, nearby amenities, avg price trends, commute times.

---

### `check_viewing_availability`
Available time slots for a property viewing.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `property_id` | string | Yes | Property to view |
| `date` | string | Yes | Requested date |

**Returns**: List of available slots (cross-references existing bookings).

---

### `book_viewing`
Schedule appointment + notify admin.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `property_id` | string | Yes | Property to view |
| `date` | string | Yes | Viewing date |
| `time_slot` | string | Yes | Selected time |
| `customer_name` | string | Yes | Caller name |
| `customer_phone` | string | Yes | Phone number |

**Side effects**:
1. Insert into `re_bookings`
2. Upsert `leads` with interaction history
3. POST webhook to `tenant.webhook_urls.new_booking`
4. Log `booking_created` analytics event

---

### `calculate_mortgage`
Monthly payment estimate (pure computation).

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `price` | float | Yes | Property price |
| `down_payment_percent` | float | Yes | e.g., 20 |
| `term_years` | int | Yes | e.g., 15, 20, 25 |
| `interest_rate` | float | Yes | Annual rate, e.g., 12.5 |

**Returns**: Monthly payment in spoken words.

---

### `get_market_trends`
Price trends and demand data for an area.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `city` | string | Yes | City |
| `area` | string | Yes | Area name |

**Returns**: Avg price/marla, YoY change, avg days on market, demand level.

---

## Car Rental Tools

### `search_vehicles`
Find available cars by category, dates, and location.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `category` | string | No | `economy`, `sedan`, `suv`, `luxury`, `van` |
| `pickup_date` | string | Yes | Pickup date |
| `return_date` | string | Yes | Return date |
| `pickup_location` | string | No | Location name or city |
| `max_daily_rate` | float | No | Budget cap per day |

**Returns**: Top 3 available vehicles with make, model, category, daily rate, features.

---

### `get_vehicle_details`
Full specs, features, and photos for a vehicle.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `vehicle_id` | string | Yes | MongoDB ObjectId |

---

### `check_availability`
Verify a specific vehicle for requested dates.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `vehicle_id` | string | Yes | Vehicle to check |
| `pickup_date` | string | Yes | Start date |
| `return_date` | string | Yes | End date |

---

### `get_rental_quote`
Calculate total cost with insurance and extras.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `vehicle_id` | string | Yes | Vehicle |
| `pickup_date` | string | Yes | Start |
| `return_date` | string | Yes | End |
| `insurance_plan` | string | No | Plan name (basic/comprehensive) |
| `extras` | string[] | No | e.g., ["GPS", "child_seat"] |

**Returns**: Itemized cost breakdown in spoken words.

---

### `create_reservation`
Book a vehicle + notify admin.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `vehicle_id` | string | Yes | Vehicle to book |
| `pickup_date` | string | Yes | Pickup date/time |
| `return_date` | string | Yes | Return date/time |
| `pickup_location` | string | Yes | Pickup branch |
| `return_location` | string | No | Return branch (defaults to pickup) |
| `customer_name` | string | Yes | Renter name |
| `customer_phone` | string | Yes | Phone |
| `insurance_plan` | string | No | Insurance choice |
| `extras` | string[] | No | Add-ons |

**Side effects**: Insert `cr_reservations`, upsert `leads`, POST webhook, analytics event.

---

### `modify_reservation`
Change dates, vehicle, or location on existing reservation.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `confirmation_number` | string | Yes | e.g., "AR-2026-08-001" |
| `changes` | object | Yes | Fields to update |

---

### `cancel_reservation`
Cancel with policy-aware messaging.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `confirmation_number` | string | Yes | Reservation to cancel |
| `reason` | string | Yes | Cancellation reason |

**Returns**: Cancellation confirmation + any applicable fees.

---

### `get_insurance_plans`
List available protection plans for a vehicle category.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `vehicle_category` | string | No | Filter by category |

---

### `get_locations`
List pickup/return branches.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `city` | string | No | Filter by city |
| `airport_only` | bool | No | Only airport locations |

---

### `check_driver_requirements`
Verify driver eligibility.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `driver_age` | int | Yes | Age of primary driver |
| `nationality` | string | No | For document requirements |

---

### `report_issue`
Log roadside or damage issue during active rental.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `confirmation_number` | string | Yes | Active reservation |
| `issue_type` | string | Yes | `breakdown`, `accident`, `flat_tire`, `other` |
| `description` | string | Yes | What happened |

**Side effects**: Creates urgent notification, escalates to human if severity is high.

---

### `extend_rental`
Extend return date for active rental.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `confirmation_number` | string | Yes | Active reservation |
| `new_return_date` | string | Yes | Extended return date |

**Returns**: Updated cost and confirmation.

---

### `get_loyalty_status`
Check loyalty points, tier, and rewards.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `customer_phone` | string | Yes | Linked phone number |

---

## Webhook Payloads

### Event: `new_booking` (Real Estate)

```json
{
  "event": "new_booking",
  "niche": "real_estate",
  "tenant_id": "alfie_realty_pk",
  "booking": {
    "id": "66b...",
    "customer_name": "Ahmed Khan",
    "customer_phone": "+923211234567",
    "viewing_date": "2026-08-05",
    "time_slot": "2:00 PM",
    "assigned_agent": "Bilal Ahmed",
    "status": "scheduled"
  },
  "property": {
    "id": "66a...",
    "title": "3 Bedroom House in DHA Phase 2",
    "city": "Islamabad",
    "area": "DHA Phase 2",
    "price": 35000000,
    "currency": "PKR"
  },
  "lead": {
    "id": "66c...",
    "lead_score": "hot",
    "qualification": { "budget_confirmed": true, "timeline": "immediate" }
  },
  "call": {
    "id": "alfie-call-f7a2b9c1",
    "caller_number": "+923211234567",
    "language": "ur",
    "duration_seconds": 272
  },
  "timestamp": "2026-08-04T17:03:00Z"
}
```

### Event: `new_reservation` (Car Rental)

```json
{
  "event": "new_reservation",
  "niche": "car_rental",
  "tenant_id": "alfie_rentals_pk",
  "reservation": {
    "id": "66d...",
    "confirmation_number": "AR-2026-08-001",
    "customer_name": "Sara Ahmed",
    "customer_phone": "+923211234567",
    "pickup_date": "2026-08-10",
    "return_date": "2026-08-14",
    "total_days": 4,
    "total_cost": 28400,
    "currency": "PKR",
    "status": "confirmed"
  },
  "vehicle": {
    "id": "66e...",
    "make": "Toyota",
    "model": "Corolla",
    "category": "sedan",
    "license_plate": "ISB-1234"
  },
  "location": {
    "pickup": "Islamabad Airport Branch",
    "return": "Islamabad Airport Branch"
  },
  "call": {
    "id": "alfie-call-a1b2c3d4",
    "caller_number": "+923211234567",
    "language": "en",
    "duration_seconds": 198
  },
  "timestamp": "2026-08-04T18:10:00Z"
}
```

### Event: `urgent_issue` (Car Rental — High Priority)

```json
{
  "event": "urgent_issue",
  "niche": "car_rental",
  "tenant_id": "alfie_rentals_pk",
  "priority": "high",
  "issue": {
    "type": "accident",
    "description": "Minor fender bender in parking lot, no injuries",
    "confirmation_number": "AR-2026-08-001",
    "customer_phone": "+923211234567",
    "reported_at": "2026-08-11T14:30:00Z"
  },
  "timestamp": "2026-08-11T14:30:00Z"
}
```
