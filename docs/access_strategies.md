# Access Strategies

This document describes how clients can keep a local copy of static ParkAPI data up to date and retrieve the according realtime data. Therefore two access patterns are described:

1. **Short-interval updates** to keep realtime information fresh, using `modified_since`.
2. **Daily full downloads** to refresh static information and reconcile the local dataset.

The public API is documented at [ParkAPI documentation](https://api.mobidata-bw.de/park-api/documentation/public.html#/paths/v3-parking-spots/get).

## Endpoints and pagination

Use the v3 list endpoints:

| Endpoint                       | Data                     |
|--------------------------------|--------------------------|
| `/api/public/v3/parking-sites` | Parking sites            |
| `/api/public/v3/parking-spots` | Individual parking spots |

Both endpoints return paginated results. Set `limit` to a value up to `1000` and follow the response's `next_path` to
retrieve subsequent pages. Cursor pagination may return a `next_path` for one final empty page when the preceding page was full; stop when there is no `next_path`.

The current rate limit is **600 requests per minute**. Count every page request toward the limit, including requests
from concurrent jobs, and avoid bursts that exceed it.

## Short-interval updates for realtime information

Poll both list endpoints with `modified_since=<timestamp>` at the frequency needed for realtime freshness (for example,
every few minutes). `modified_since` is an inclusive timestamp filter: it returns records whose `modified_at` is at or
after the supplied time. Parking sites and parking spots have separate modification timestamps, so keep a separate
cursor for each endpoint.

```text
for each endpoint (parking-sites and parking-spots):
    cursor = time of the last successful update (or the time of the initial full download)

    periodically:
        request_started_at = now()
        fetch every page with modified_since=<cursor - small overlap>
        apply the realtime fields from returned records to the local records
        cursor = request_started_at
```

The filter is based on changes to the complete record, not exclusively on realtime fields. A short update can therefore
also return records with static changes; apply those as appropriate, while the daily full download remains the source
for reconciling static data. Use a small overlap (for example, one minute) to account for delayed updates. Reprocessing
a record is expected, so updates should be idempotent.

`modified_since` only returns records that still exist. It does not report deletions, so do not rely on short-interval
updates to remove records from the local dataset.

## Daily full download for static data

Once a day, fetch **all pages** from both `/api/public/v3/parking-sites` and `/api/public/v3/parking-spots` without a
`modified_since` filter. Use the complete result to refresh static fields and reconcile the local dataset:

```text
fetch every page of parking-sites
fetch every page of parking-spots
after both downloads complete successfully:
    refresh local static data from the downloaded records
    remove local records absent from the corresponding complete result
```

Only reconcile or delete records after all pages for both datasets have been fetched successfully. If a download fails
partway through, keep the existing local data and retry rather than treating an incomplete result as a full snapshot.
When applying the snapshot, avoid replacing newer realtime fields with older values from a download that overlapped with
a realtime update; merge static fields separately or run a realtime catch-up after the snapshot.

## Summary

| Access pattern         | Frequency            | Query                               | Purpose                                                 |
|------------------------|----------------------|-------------------------------------|---------------------------------------------------------|
| Short-interval updates | Once every 5 minutes | `modified_since=<cursor - overlap>` | Apply changed records, especially realtime updates      |
| Daily full download    | Once a day           | No `modified_since`                 | Refresh static data, detect deletions, and repair drift |
