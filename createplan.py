import payjp
payjp.api_key = 'sk_test_f606684ccf89682213b11a1e'
plan = payjp.Plan.all(limit=3)
# plan = payjp.Plan.create(
#     amount=500,
#     currency='jpy',
#     interval='month',
#     trial_days=0
# )
# plan = payjp.Plan.all(limit=3)
print(plan)
