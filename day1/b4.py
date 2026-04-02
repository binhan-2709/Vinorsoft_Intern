# Bài 4
# Yêu cầu: Xóa đi phần tử lặp lại 

def removeDuplicates(nums: list[int]) -> int:
    if not nums:
        return 0
    k = 1 
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1]:
            nums[k] = nums[i]  
            k += 1            
            
    return k

if __name__ == "__main__":
    nums1 = [1, 1, 2]
    k1 = removeDuplicates(nums1)
    print(f"   Mang sau khi xoa phan tu trung lap: {nums1[:k1]}")