# We want to sum up the first N even integers
num = 0
for i in range(0, 10, 1):
  if i % 2 != 0:
      print('dont do anything')
  else:
    num = num + i
print('the total is ' + str(num) + ' for the first ' + str(10) + 'integers')
