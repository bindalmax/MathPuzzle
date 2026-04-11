# AWS Region Decision Guide for MathPuzzle

This guide outlines the criteria for selecting an AWS region to host the MathPuzzle application for commercial use.

## 1. Latency & Proximity (Primary Factor)
Because MathPuzzle uses WebSockets for real-time synchronization, low latency is critical.
- **Target Audience**: Choose a region closest to your primary user base.
- **Goal**: Aim for a Round Trip Time (RTT) of < 100ms.
- **Tool**: Use [cloudping.info](https://www.cloudping.info/) to measure latency from various global locations.

## 2. Cost Optimization
AWS pricing varies by region. 
- **Low-Cost Regions**: `us-east-1` (N. Virginia), `us-east-2` (Ohio), and `us-west-2` (Oregon) are typically the most economical.
- **High-Cost Regions**: `sa-east-1` (São Paulo) or `ap-east-1` (Hong Kong) can be significantly more expensive for data transfer and compute.

## 3. Service Availability
Ensure the chosen region supports the core infrastructure:
- **Compute**: Amazon ECS (Elastic Container Service) or AWS App Runner.
- **Database**: Amazon RDS for PostgreSQL.
- **Caching**: Amazon ElastiCache (if scaling WebSockets with Redis in the future).

## 4. Compliance & Data Sovereignty
Consider legal requirements for data storage:
- **GDPR**: Use `eu-central-1` (Frankfurt) or `eu-west-1` (Ireland) for EU data residency.
- **Local Regulations**: Verify if your target market requires data to be physically stored within their borders.

## Summary Recommendation

| Market | Recommended Region |
| :--- | :--- |
| **North America** | `us-east-1` (N. Virginia) or `us-west-2` (Oregon) |
| **Europe** | `eu-central-1` (Frankfurt) or `eu-west-1` (Ireland) |
| **Asia Pacific** | `ap-southeast-1` (Singapore) or `ap-northeast-1` (Tokyo) |
| **Global Default** | `us-east-1` (N. Virginia) |
