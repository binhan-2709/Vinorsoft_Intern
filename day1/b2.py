#Bài 2: Two Sum (Pythonic version) 
#Yêu cầu:
# Cho mảng số nguyên nums và số target, trả về 2 index sao cho tổng = target.

def twoSum(nums: list[int], target: int) -> list[int]:
    num_map: dict[int, int] = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
        
    return []

numbers = [2, 7, 11, 15]
target = 9
result = twoSum(numbers, target)

# In kết quả ra màn hình
print("Input:", numbers)
print("Target:", target)
print("Result:", result)