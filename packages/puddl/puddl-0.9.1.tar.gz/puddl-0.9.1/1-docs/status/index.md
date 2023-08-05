---
version: draft
---

Think "What are you up to?" like Twitter, Whatsapp and Facebook have it, but
multi-dimensional. 

# Example: Time
We're mixing styles of representation here. Stuff that is written as a `code
block` contains data puddl already knows or can easily compute. All the other
stuff is what we entered (UI primarily, API as an afterthought). If there is a
shell-like variable in code blocks, it can be given by you, e.g. `blah blah ${x}` 

## Entry(id=1
`Date: 2020-03-23 20:04`

| Past | Time | Story |
| ==== | ==== | ===== |
| this month | 2020-03-02 - 2020-03-23 | work, puddl |
| this week | 03-16 - 03-23 | wait out corona, chill with sis |
| today | since $WAKEUPTIME | wait out corona |
| past hour | 19 - 20 | puddl |

| Future | Time | Plan |
| ====== | ==== | ==== |
| next hour | 19 - 20 | puddl |
| today | until $BEDTIME | wait out corona |
| this week | 03-16 - 03-23 | wait out corona, chill with sis |
| this month | 2020-03-02 - 2020-03-23 | work, puddl |

We tell our stories of the past, but we plan for the future.

Note that in this contrived example, we have a *perfect match*, i.e. future
goals align perfectly with past activities. We can keep going this route.

## Entry(id=2
`Date: 2020-03-23 20:45`

| Future | Time | Plan |
| ====== | ==== | ==== |
| next hour | 20:45 - 21:45 | puddl |

## Entry(id=3
`Date: 2020-03-23 21:50`

| Past   | Time | Story |
| ====== | ==== | ===== |
| 50 min | 21:00 - 21:50 | dance |

Here the past collided with previous future prognosis. If it's good or not, that
is for you to decide.

We simply set "21:00" as `start_date`. The default `end_date` is now. The
difference is computed based on `start_date/end_date`.


## Entry(id=4)
`Date: 2020-03-23 22:13`

| past (custom) | since 21:00 | dance |
| Future | Time | Plan |
| ====== | ==== | ==== |


## Entry(id=4)
`Date: 2020-03-23 21:50`

| Future | Time | Plan |
| ====== | ==== | ==== |
| next 10 min | 21:50 - 20:00 | smoke |
