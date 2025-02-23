# Data Engineering Technical Assessment

## Overview
In this assessment, you'll build a real-time data pipeline that processes events from the Pub/Sub topic using Dataflow (Apache Beam) and stores them in BigQuery and GCS.

This task could take anywhere from 1 to 3 hours depending on your level of experience with Dataflow, Apache Beam, and GCP services.

If you have a private GCP project or Sandbox, you can use and share screenshots from the output.

---

## Pub/Sub Configuration
- **Topic Name:** `backend-events-topic`
- **Subscription Name:** `backend-events-topic-sub`

All events are pushed to a single topic.

---

## Event Schemas

### Order Events Schema
```json
{
  "event_type": "order",
  "order_id": "uuid",
  "customer_id": "uuid",
  "order_date": "timestamp",
  "status": "enum(pending, processing, shipped, delivered)",
  "items": [
    {
      "product_id": "uuid",
      "product_name": "string",
      "quantity": "integer",
      "price": "float"
    }
  ],
  "shipping_address": {
    "street": "string",
    "city": "string",
    "country": "string"
  },
  "total_amount": "float"
}
```

### Inventory Events Schema
```json
{
  "event_type": "inventory",
  "inventory_id": "uuid",
  "product_id": "uuid",
  "warehouse_id": "uuid",
  "quantity_change": "integer(-100 to 100)",
  "reason": "enum(restock, sale, return, damage)",
  "timestamp": "timestamp"
}
```

### User Activity Events Schema
```json
{
  "event_type": "user_activity",
  "user_id": "uuid",
  "activity_type": "enum(login, logout, view_product, add_to_cart, remove_from_cart)",
  "ip_address": "string",
  "user_agent": "string",
  "timestamp": "timestamp",
  "metadata": {
    "session_id": "uuid",
    "platform": "enum(web, mobile, tablet)"
  }
}
```

**Note:** Historical data for these events is stored in JSON format in an Amazon S3 bucket.

---

## Tasks

### Task 1: Data Modeling and Architecture

Design the BigQuery data model that will store these events. Consider:
- **Table structure and relationships**
- **Partitioning and clustering strategies**
- **Tracking historical data and time travel**

**Deliverables:**
- Data model diagram
- DDL statements for creating tables
- Explanation of design decisions

---

### Task 2: Streaming Pipeline

Implement a Dataflow pipeline (using either Python or Java) that:
1. Reads events from Pub/Sub
2. Processes and transforms the data
3. Writes events to:
   - **GCS:** in the following structure:
```
output/
  ├── order/
  │   └── 2025/
  │       └── 02/
  │           └── 08/
  │               └── 13/
  │                   └── 09/
  │                       └── order_2025020813090001.json
  ├── inventory/
  │   └── ...
  └── user_activity/
      └── ...
```
   - **BigQuery:** according to your data model

---

## Additional Information

For any questions or clarifications, feel free to reach out during the assessment process. Good luck!

