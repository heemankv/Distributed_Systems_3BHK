from datetime import datetime, timezone, timedelta
leader_lease_timeout=10
abc=datetime.now(timezone.utc) + timedelta(seconds=leader_lease_timeout)
print(abc)
# print("NOW:",datetime.now(timezone.utc))
# new_abc=datetime.strptime(abc, '%Y-%m-%d %H:%M:%S.%f%z')
# print(new_abc)

# while( abc!=None and datetime.now(timezone.utc) < new_abc):
#         pass
# print("THE END: ", datetime.now(timezone.utc))
timedifference=abc-datetime.now((timezone.utc))
xyz=max(0, timedifference.total_seconds())
print(datetime.now(timezone.utc) + timedelta(seconds=xyz))


