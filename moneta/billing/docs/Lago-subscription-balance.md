# Subscription remaining balance


When we send usage event to Lago, we can get the latest subscription remaining balance from Lago. For example:

```
curl --location --request POST "$LAGO_URL/api/v1/events?sync=true&with_remaining_budget=true" \
--header "Authorization: Bearer $API_KEY" \
--header 'Content-Type: application/json' \
--data-raw '{
      "event": {
          "transaction_id": "__UNIQUE_ID__",
          "external_subscription_id": "__YOUR_SUBSCRIPTION_ID__",
          "code": "__BILLABLE_METRIC_CODE__",
          "timestamp": $(date +%s),
          "properties": {
            "credit_cents": 0.012
          }
      }
  }'
```

The response will be:

```
{
  "subscription_remaining_balance": [
    {
      "billable_metric_id": "__BILLABLE_METRIC_ID__",
      "total_usage": 100,
      "total_deposited_credits": 1000,
      "remaining_balance": 900
    }
  ]
}
```

## How to implement this in Lago

When we send usage event to lago, Lago will check if the billable metric is surpass it threshold to start a charge. I assume to doing that, we need to calculate the `total_usage` of the billable metric and the `total_deposited_credits` (name may be not correct) of the billable metric. the `remaining balance` will be `total_deposited_credits` - `total_usage`.

This calculation is expensive, so it should be cached in the subscription model. let say we will create 2 columns in the subscription model:

- `latest_aggregation_data`: jsonb, store the `total_usage` and `total_deposited_credits` and `remaining_balance`
- `latest_aggregation_data_updated_at`: datetime, store the timestamp when the `latest_aggregation_data` was updated

When the usage event is created, we will update those 2 columns with the latest data with the optimistic lock which will update the `latest_aggregation_data` and `latest_aggregation_data_updated_at` = event.created_at only if the event.created_at > subscription.latest_aggregation_data_updated_at.

in API to create a usage event, we will return by fetching data from the subscription model.

```
{
  "subscription_remaining_balance": [
    {
      "billable_metric_id": "__BILLABLE_METRIC_ID__",
      "total_usage": 100,
      "total_deposited_credits": 1000,
      "remaining_balance": 900
    }
  ]
}
```