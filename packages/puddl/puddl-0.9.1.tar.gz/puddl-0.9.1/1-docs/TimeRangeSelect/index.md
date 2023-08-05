---
version: draft
---

# Motivation
`puddl-status` needs a way to select time ranges. It is a useful tool to have
anyways - especially when working with a lot of time ranges. :D

I was always unhappy with UI components to select time. The one in Kimai is the
best I know so far, but its separation of hours and minutes always bugged me.


# CLI
In its simplest form, use the full date in the current timezone
```
puddl something --start "2020-03-23 21:00" --end "2020-03-23 21:50"
```

Or use simple time strings:
```
puddl something --start 21:00 --end 21:50
```

If you use those, their nearest neighbor is used. For example, if you create an
entry at 02:30, then `23:00` refers to yesterday, because its nearer to 02:30.
